# ziwei calculation core

Bundled in the `shunshi-ziwei-mcp` distribution. Import `ziwei` without starting the MCP server.

See the root README for installation, input conventions and capability limits, and SOURCE.md for calculation provenance.

```python
import ziwei
chart = ziwei.by_solar("1990-03-24", ziwei.time_to_index(10), "男")
print(chart.to_dict())
```
