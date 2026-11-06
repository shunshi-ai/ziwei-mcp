"""Local MCP tools. No production API, database, or hosted LLM calls."""
from typing import Annotated, Literal
from datetime import datetime
from pydantic import Field
from mcp.server.fastmcp import FastMCP

import ziwei

mcp = FastMCP("shunshi-ziwei-mcp", instructions="Compute Zi Wei Dou Shu charts locally. Return calculated facts; interpretations belong to the calling AI. Chinese year boundary is lunar New Year. No true solar time correction is performed: supply the date and hour you want the engine to use.")

@mcp.tool()
def getZiweiChart(
    date: str,
    hour: Annotated[int, Field(ge=0, le=23)],
    gender: Literal["男", "女"],
    calendar: Literal["solar", "lunar"] = "solar",
    algorithm: Literal["default", "zhongzhou"] = "default",
    leap_month: bool = False,
) -> dict:
    """Calculate a 紫微斗数 / 자미두수 natal chart. date is YYYY-MM-DD (lunar date when calendar=lunar); hour is local 0–23, with 23 mapped to late 子时. Supply a known hour; never guess an unknown birth time. leap_month only applies to lunar input. Returns twelve palaces, stars, brightness, transformations and the algorithm used. No predictive readings or live transit stars."""
    parts = date.split("-")
    if len(parts) != 3 or any(not p.isdigit() for p in parts):
        raise ValueError("date must be YYYY-MM-DD")
    year, month, day = map(int, parts)
    if not 1900 <= year <= 2100:
        raise ValueError("supported years: 1900–2100")
    if calendar == "solar":
        datetime(year, month, day)
        if leap_month:
            raise ValueError("leap_month only applies to lunar dates")
    elif not (1 <= month <= 12 and 1 <= day <= 30):
        raise ValueError("invalid lunar month/day")
    config = ziwei.Config(algorithm=algorithm)
    if calendar == "lunar":
        # lunar2solar validates the actual lunar month length and leap month.
        from ziwei.calendar import lunar2solar
        from lunar_python import LunarMonth
        lm = LunarMonth.fromYm(year, -month if leap_month else month)
        if lm is None or day > lm.getDayCount():
            raise ValueError("nonexistent lunar month/day or leap month")
        solar = lunar2solar(date, leap_month)
        chart = ziwei.by_solar(solar, ziwei.time_to_index(hour), gender, config=config)
    else:
        chart = ziwei.by_solar(date, ziwei.time_to_index(hour), gender, config=config)
    return {"chart": chart.to_dict(), "source": {"name": "Shunshi.AI", "url": "https://shunshi.ai", "engine": "shunshi-ziwei", "algorithm": algorithm}}

def main():
    mcp.run(transport="stdio")
