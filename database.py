from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from databricks import sql

import polars as pl
import os

mcp = FastMCP("Databricks Database")

@mcp.prompt()
def databricks_prompt(table: str, columns: str) -> str:
    """
    Query Databricks SQL endpoint and return the result as a Polars DataFrame.
    """
    columns = columns.split()
    columns = [column.strip() for column in columns]
    columns = ', '.join(columns)
    query = f"SELECT {columns} FROM {table}\n\n"
    return query

@mcp.tool()
def query_databricks(query: str) -> pl.DataFrame:
    """
    Query Databricks SQL endpoint and return the result as a Polars DataFrame.

    Args:
        query (str): SQL query to be executed.

    Returns:
        pl.DataFrame: Result of the query as a Polars DataFrame
    """
    load_dotenv()

    with sql.connect(
        server_hostname=os.getenv("DATABRICKS_HOST"),
        http_path=os.getenv("DATABRICKS_HTTP_PATH"),
        access_token=os.getenv("DATABRICKS_TOKEN"),
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        if not result:
            return pl.DataFrame()
        
        # Convert all rows to dictionaries first
        result_dicts = [row.asDict() for row in result]

        df = pl.DataFrame(
            result_dicts, 
            infer_schema_length=None  # None = use all rows for schema inference
        )

        columns = df.columns

        values = df.head(10).to_dicts()

        values_str = ' '.join([str(row.values()) for row in values])

        return f'{columns}\n{values_str}'
    

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')