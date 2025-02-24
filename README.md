# edgar-sec-mcp

**edgar-sec-mcp** is an MCP (Modular Computing Platform) server designed
to facilitate AI agents in accessing and interacting with EDGAR Data
from the SEC. This project provides tools, endpoints, and data
processing utilities to streamline the retrieval and analysis of SEC filings,
such as proxy statements which hold information about executive compensation,
or form 4 to understand inside selling.

## Tools

- **GetProxyStatementTablesByTicker**
- **GetForm4ByTicker**

## Configuration

### [Goose](https://github.com/block/goose)

```yaml
extensions:
  edgar-sec-mcp:
    args:
    - --from
    - git+https://github.com/flothjl/edgar-sec-mcp@main
    - edgar-sec-mcp
    cmd: uvx
    enabled: true
    envs: {}
    name: edgar-sec 
    type: stdio
GOOSE_MODEL: gpt-4o-mini
GOOSE_PROVIDER: openai
```
