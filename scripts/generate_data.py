"""Build the raw seed CSVs for the data engineering assessment from the
real Olist Brazilian E-Commerce dataset (Kaggle: olistbr/brazilian-ecommerce).

Olist's own data has no customer names/emails/signup dates, and no
per-product price (price lives on each order_item, not on the product
catalog) -- those fields are Faker-filled deterministically on top of the
real customer/product/order/order_item IDs so the seed schema (and the
dbt models built on it) stay unchanged. The usual data-quality issues
(duplicate customer rows, blank emails, a negative price, a few
zero/negative quantities, a few orphaned order_items) are still injected
on top, same as before.

Usage (from the project root, /Users/gzenkner/projects/de_assessment):
    "$(pwd)/.venv/bin/python" scripts/generate_data.py
"""

import csv
import random
from pathlib import Path

import kagglehub
import pandas as pd
from faker import Faker

SEED = 42
N_ORDERS = 2000
KAGGLE_DATASET = "olistbr/brazilian-ecommerce"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "dbt" / "seeds"

fake = Faker()
Faker.seed(SEED)
random.seed(SEED)

# Olist's real order_status values don't match the four this assessment's
# models/tests expect -- map them down so the seed schema's contract holds.
STATUS_MAP = {
    "delivered": "completed",
    "shipped": "shipped",
    "canceled": "cancelled",
    "invoiced": "pending",
    "processing": "pending",
    "created": "pending",
    "approved": "pending",
    "unavailable": "cancelled",
}


def download_olist() -> Path:
    """Download (or reuse the cached copy of) the Olist dataset.

    Returns:
        Path to the local directory containing the dataset's CSV files.
    """
    return Path(kagglehub.dataset_download(KAGGLE_DATASET))


def load_sample(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load a deterministic sample of Olist orders and everything they touch.

    Args:
        data_dir: Directory containing the extracted Olist CSV files.

    Returns:
        A tuple of (orders, order_items, customers, products) DataFrames,
        already filtered down to the sampled orders.
    """
    orders = pd.read_csv(data_dir / "olist_orders_dataset.csv")
    orders = orders.sample(n=N_ORDERS, random_state=SEED).reset_index(drop=True)

    order_items = pd.read_csv(data_dir / "olist_order_items_dataset.csv")
    order_items = order_items[order_items["order_id"].isin(orders["order_id"])].reset_index(
        drop=True
    )

    customers = pd.read_csv(data_dir / "olist_customers_dataset.csv")
    customers = customers[customers["customer_id"].isin(orders["customer_id"])].reset_index(
        drop=True
    )

    products = pd.read_csv(data_dir / "olist_products_dataset.csv")
    products = products[
        products["product_id"].isin(order_items["product_id"])
    ].reset_index(drop=True)

    return orders, order_items, customers, products


def build_customers(customers: pd.DataFrame) -> tuple[list[dict], dict[str, int]]:
    """Build raw customer rows, Faker-filling the PII Olist doesn't have.

    Args:
        customers: Real Olist customers, already filtered to the sample.

    Returns:
        A tuple of (rows, id_map) where id_map maps Olist's string
        customer_id to the integer surrogate key used in the seed.
    """
    customers = customers.sort_values("customer_id").reset_index(drop=True)
    id_map = {raw_id: i + 1 for i, raw_id in enumerate(customers["customer_id"])}

    rows = []
    for _, customer in customers.iterrows():
        rows.append(
            {
                "customer_id": id_map[customer["customer_id"]],
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                # ~4% of emails missing, as would happen with an optional signup field.
                "email": fake.unique.email() if random.random() > 0.04 else "",
                "signup_date": fake.date_between(start_date="-3y", end_date="-1d").isoformat(),
                # Real field: Olist is domestic-only, so this holds the customer's
                # Brazilian state rather than a country -- there's no real country column.
                "country": customer["customer_state"],
            }
        )

    # Duplicate a handful of customer rows verbatim, simulating an upstream export bug.
    duplicates = random.sample(rows, k=min(15, len(rows)))
    rows.extend(duplicates)
    random.shuffle(rows)
    return rows, id_map


def build_products(
    products: pd.DataFrame, order_items: pd.DataFrame
) -> tuple[list[dict], dict[str, int]]:
    """Build raw product rows, deriving price from real order_item prices.

    Args:
        products: Real Olist products, already filtered to the sample.
        order_items: Real Olist order items, used to derive unit_price
            since Olist's product catalog has no price column.

    Returns:
        A tuple of (rows, id_map) where id_map maps Olist's string
        product_id to the integer surrogate key used in the seed.
    """
    products = products.sort_values("product_id").reset_index(drop=True)
    id_map = {raw_id: i + 1 for i, raw_id in enumerate(products["product_id"])}
    avg_price = order_items.groupby("product_id")["price"].mean()

    rows = []
    for _, product in products.iterrows():
        category = product["product_category_name"]
        category = category.replace("_", " ").title() if isinstance(category, str) else "Unknown"
        rows.append(
            {
                "product_id": id_map[product["product_id"]],
                # Real field: Olist has no product name, so this is Faker-filled.
                "product_name": fake.word().capitalize() + " " + fake.word().capitalize(),
                "category": category,
                "unit_price": round(float(avg_price.get(product["product_id"], 0)), 2),
            }
        )

    # One data-entry typo: a negative price that should never happen downstream.
    if rows:
        rows[random.randrange(len(rows))]["unit_price"] = -19.99
    return rows, id_map


def build_orders(orders: pd.DataFrame, customer_id_map: dict[str, int]) -> list[dict]:
    """Build raw order rows from real Olist orders.

    Args:
        orders: Real Olist orders, already filtered to the sample.
        customer_id_map: Mapping from Olist's string customer_id to the
            integer surrogate key used in the seed.

    Returns:
        The raw order rows.
    """
    rows = []
    for order_id, order in enumerate(orders.itertuples(), start=1):
        rows.append(
            {
                "order_id": order_id,
                "customer_id": customer_id_map[order.customer_id],
                "order_date": str(order.order_purchase_timestamp)[:10],
                "status": STATUS_MAP[order.order_status],
            }
        )
    return rows


def build_order_items(
    order_items: pd.DataFrame,
    orders: pd.DataFrame,
    product_id_map: dict[str, int],
) -> list[dict]:
    """Build raw order_item rows from real Olist order items.

    Each Olist order_item row already represents a single unit, so
    quantity is 1 per row unless an injected data-quality issue overrides it.

    Args:
        order_items: Real Olist order items, already filtered to the sample.
        orders: Real Olist orders, used to map Olist's string order_id to
            the integer surrogate key used in the seed.
        product_id_map: Mapping from Olist's string product_id to the
            integer surrogate key used in the seed.

    Returns:
        The raw order_item rows, including a few injected bad records.
    """
    order_id_map = {
        raw_id: i + 1 for i, raw_id in enumerate(orders["order_id"])
    }

    rows = []
    item_id = 1
    for item in order_items.itertuples():
        quantity = 1
        # Rare bad record: a zero/negative quantity that slipped through upstream.
        if random.random() < 0.01:
            quantity = random.choice([0, -1])
        rows.append(
            {
                "order_item_id": item_id,
                "order_id": order_id_map[item.order_id],
                "product_id": product_id_map[item.product_id],
                "quantity": quantity,
            }
        )
        item_id += 1

    # A handful of order_items pointing at an order_id that doesn't exist --
    # simulates a late-arriving/out-of-order upstream load.
    product_ids = list(product_id_map.values())
    for _ in range(8):
        rows.append(
            {
                "order_item_id": item_id,
                "order_id": len(order_id_map) + random.randint(1000, 9999),
                "product_id": random.choice(product_ids),
                "quantity": random.randint(1, 3),
            }
        )
        item_id += 1

    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    """Write rows to a CSV file, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Download the Olist dataset and write all raw seed CSVs under dbt/seeds/."""
    fake.unique.clear()
    data_dir = download_olist()
    orders_raw, order_items_raw, customers_raw, products_raw = load_sample(data_dir)

    customers, customer_id_map = build_customers(customers_raw)
    products, product_id_map = build_products(products_raw, order_items_raw)
    orders = build_orders(orders_raw, customer_id_map)
    order_items = build_order_items(order_items_raw, orders_raw, product_id_map)

    write_csv(customers, OUTPUT_DIR / "raw_customers.csv")
    write_csv(products, OUTPUT_DIR / "raw_products.csv")
    write_csv(orders, OUTPUT_DIR / "raw_orders.csv")
    write_csv(order_items, OUTPUT_DIR / "raw_order_items.csv")

    print(
        f"Wrote {len(customers)} customers, {len(products)} products, "
        f"{len(orders)} orders, {len(order_items)} order_items to {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()
