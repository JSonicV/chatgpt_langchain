import sqlite3
from langchain.tools import Tool
from pydantic.v1 import BaseModel
from typing import List


conn = sqlite3.connect('db.sqlite')


def run_sqlite_query(query: str):
	c = conn.cursor()
	try:
		c.execute(query)
		return c.fetchall()
	except sqlite3.OperationalError as err:
		return f"The following error occurred: {err}"


def list_tables():
	c = conn.cursor()
	c.execute("SELECT name FROM sqlite_master WHERE type='table';")
	rows = c.fetchall()
	return "\n".join([row[0] for row in rows if row[0] is not None])


def describe_tables(table_names):
	c = conn.cursor()
	tables = ", ".join([f"'{name}'" for name in table_names])
	rows = c.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name IN ({tables});").fetchall()
	return "\n".join([row[0] for row in rows if row[0] is not None])


class RunQueryArgsSchema(BaseModel):
	query: str
	
run_query_tool = Tool(
	name="run_sqlite_query",
	description="Run a SQLite query on the connected database and return the results.",
	func=run_sqlite_query,
	args_schema=RunQueryArgsSchema
)


class DescribeTablesArgsSchema(BaseModel):
	table_names: List[str]

describe_tables_tool = Tool(
	name="describe_tables",
	description="Given a list of table names, return the schema of those tables.",
	func=describe_tables,
	args_schema=DescribeTablesArgsSchema
)
