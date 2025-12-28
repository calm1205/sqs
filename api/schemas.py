from enum import Enum

from pydantic import BaseModel


class ReportType(str, Enum):
    SALES = "sales"
    INVENTORY = "inventory"
    USERS = "users"


class ReportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"


class ReportRequest(BaseModel):
    report_type: ReportType
    format: ReportFormat = ReportFormat.CSV
