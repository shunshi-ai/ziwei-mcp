import pytest
from shunshi_ziwei_mcp.server import getZiweiChart


def test_lunar_leap_date_matches_its_solar_date():
    from ziwei.calendar import lunar2solar
    solar = lunar2solar("2023-02-01", True)
    lunar_chart = getZiweiChart("2023-02-01", 23, "女", calendar="lunar", leap_month=True)
    solar_chart = getZiweiChart(solar, 23, "女")
    assert lunar_chart == solar_chart


@pytest.mark.parametrize("date,leap", [("2026-02-01", True), ("2023-02-30", True)])
def test_invalid_lunar_dates_are_rejected(date, leap):
    with pytest.raises(ValueError):
        getZiweiChart(date, 10, "男", calendar="lunar", leap_month=leap)
