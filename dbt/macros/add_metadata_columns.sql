{% macro add_metadata_columns() %}
    current_timestamp as dbt_loaded_at
    -- TODO: add a comma above and a second column here, `'{{ invocation_id }}' as dbt_invocation_id`,
    -- so every row also records which dbt run produced it
{% endmacro %}
