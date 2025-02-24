from typing import List

import mcp.types as mcp_types
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from pydantic import BaseModel, Field

from edgar_sec_mcp.edgar.filings import CompanyFilings

mcp = FastMCP("edgar-sec-mcp")

APP_NAME = "edgar-mcp"
EMAIL = "test@test.com"


class BaseReq(BaseModel):
    ticker: str = Field(pattern=r"^[A-Z]{1,5}([.-][A-Z0-9]{1,3})?$")
    limit: int = Field(default=10, le=20)


class GetForm4ByTickerReq(BaseReq): ...


@mcp.tool(name="GetForm4ByTicker")
async def get_form4_by_ticker(
    args: GetForm4ByTickerReq,
) -> List[str]:
    """Get data from form 4 filings. Useful if looking for insider trades"""
    try:
        filings = CompanyFilings(APP_NAME, EMAIL, args.ticker).form4.get(args.limit)
        return filings
    except Exception as e:
        raise McpError(
            mcp_types.ErrorData(
                code=mcp_types.INTERNAL_ERROR,
                message=f"Error fetching form 4 filings for {args.ticker}: {e}",
            )
        )


class GetProxyStatementsByTickerReq(BaseReq):
    limit: int = Field(le=1, default=1)


@mcp.tool(name="GetProxyStatementTablesByTicker")
async def get_proxy_statement_table_data_by_ticker(
    args: GetProxyStatementsByTickerReq,
) -> List[List[str]]:
    """Get table data from proxy statements by ticker. Useful if looking for annual executive compensation plans.
    IMPORTANT NOTE - the returned value is a list of csv strings of all tables in the proxy statement. Some
    of the tables will be relevant to compensation and some will not"""
    try:
        filings = CompanyFilings(APP_NAME, EMAIL, args.ticker).proxy_statements.get(
            args.limit
        )
        return filings
    except Exception as e:
        raise McpError(
            mcp_types.ErrorData(
                code=mcp_types.INTERNAL_ERROR,
                message=f"Error fetching proxy statements filings for {args.ticker}: {e}",
            )
        )


if __name__ == "__main__":
    mcp.run()
