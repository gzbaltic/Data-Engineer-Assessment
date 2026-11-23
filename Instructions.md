Hi

Ahead of the assessment, here's what to expect. We'll share the repo
link separately, closer to the session.

It's a small dbt + DuckDB project on real, anonymised e-commerce data
(customers, products, orders, order items) from the
Olist dataset, https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce.

You'll write a SQL staging model, finish a dbt macro and, if time permits, write a simple parsing script in Python. Everything's kept simple given the time available; we're looking at how you work, not how much you build and intentionally added more content than the available time permits.

Rough timeframe:
- ~5 min — clone the repo
- ~15 min — set up Python, dependencies and the dot project
- ~30 min — dbt macro, seed, build, tests
- ~15 min — additional SQL queries on the database, simple aggregation and window functions, etc, subject to time-constraints
- Python parsing — extra, subject to time-constraints

In the absence of Docker, we've tried to create a consistent environment 
using pyenv and a Python virtualenv to give
you an isolated environment pinned to this project's versions, without
touching anything else on your machine.

What to prepare beforehand:
- Git
- A code editor — VS Code recommended

That's all we need beforehand — you'll get the repo link at the start
of the session and do the rest of the setup there.