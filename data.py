
import pandas as pd
from mssql_python import connect


server = r"(LocalDB)\LocalDBali"
database = "tempo"


cost_by_dep_query = """
SELECT
    department_name,
    period,
    cost_set
FROM manual_input_forecasted_budget_by_department
"""


cost_by_dep_query_set = """
MERGE INTO manual_input_forecasted_budget_by_department AS target
USING (
    VALUES (?, ?, ?)
) AS source (department_name, period, cost_set)

ON
    target.department_name = source.department_name
    AND target.period = source.period

WHEN MATCHED THEN
    UPDATE SET
        target.cost_set = source.cost_set

WHEN NOT MATCHED THEN
    INSERT (department_name, period, cost_set)
    VALUES (
        source.department_name,
        source.period,
        source.cost_set
    );
"""


def connect_db():

    conn = connect(
        f"Server={server};"
        f"Database={database};"
        "Trusted_Connection=yes;"
        "Encrypt=no;"
    )

    return conn


def select_costs_by_dept():

    columns = [
        "Department Name",
        "Period",
        "Cost Value"
    ]

    conn = connect_db()

    try:
        cursor = conn.cursor()

        try:
            cursor.execute(cost_by_dep_query)
            records = cursor.fetchall()

            return pd.DataFrame(
                records,
                columns=columns
            )

        finally:
            cursor.close()

    finally:
        conn.close()


def add_value(data_tuple: tuple):

    add_values([data_tuple])


def add_values(records: list):

    if not records:
        return

    conn = connect_db()

    try:
        cursor = conn.cursor()

        try:
            for record in records:
                cursor.execute(
                    cost_by_dep_query_set,
                    record
                )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()

    finally:
        conn.close()
