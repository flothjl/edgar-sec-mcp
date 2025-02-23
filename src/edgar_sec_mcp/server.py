from typing import List

import mcp.types as mcp_types
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from pydantic import BaseModel, Field

from edgar_sec_mcp.edgar.filings import CompanyFilings

mcp = FastMCP("edgar-sec-mcp")

APP_NAME = "edgar-mcp"
EMAIL = "test@test.com"


class GetForm4ByTickerReq(BaseModel):
    ticker: str = Field(pattern=r"^[A-Z]{1,5}([.-][A-Z0-9]{1,3})?$")


@mcp.tool(name="GetForm4ByTicker")
async def get_gov_spending_by_fiscal_year(
    args: GetForm4ByTickerReq,
) -> List[str]:
    """Get a list of URLs for to latest Form 4 filings for a given ticker symbol"""
    try:
        filings = CompanyFilings(APP_NAME, EMAIL, args.ticker).form4.get()
        return filings
    except Exception as e:
        raise McpError(
            mcp_types.ErrorData(
                code=mcp_types.INTERNAL_ERROR,
                message=f"Error fetching form 4 filings for {args.ticker}: {e}",
            )
        )


if __name__ == "__main__":
    mcp.run()
