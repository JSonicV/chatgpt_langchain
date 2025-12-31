from langchain.tools import StructuredTool
from pydantic.v1 import BaseModel

def write_report(filename, html):
	with open(filename, "w") as f:
		f.write(html)

class WriteReportArgsSchema(BaseModel):
	filename: str
	html: str

write_report_tool = StructuredTool.from_function(
	func=write_report,
	name="write_report",
	description="Write the provided HTML content to a file with the given filename. Use this tool whenever someone asks for a report.",
	args_schema=WriteReportArgsSchema
)