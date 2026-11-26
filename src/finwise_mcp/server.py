"""Finwise MCP Server - Connect your Finwise personal finance data to LLMs."""

import os
from datetime import datetime
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from finwise import FinWise

mcp = FastMCP("Finwise Personal Finance")

# All tools are read-only queries against the Finwise API
READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)


def get_client() -> FinWise:
    """Get authenticated Finwise client."""
    api_key = os.environ.get("FINWISE_API_KEY")
    if not api_key:
        raise ValueError("FINWISE_API_KEY environment variable is required")
    return FinWise(api_key=api_key)


@mcp.tool(annotations=READ_ONLY)
def list_accounts() -> list[dict[str, Any]]:
    """List all financial accounts with names, types, currencies, and balances.

    Returns account ID, name, type, currency, current balance, and available balance
    for each account. For credit cards and access bonds the available balance is the
    amount that can still be drawn, which differs from the current balance owed.
    """
    client = get_client()
    response = client.accounts.list()

    return [
        {
            "id": account.id,
            "name": account.name,
            "type": account.type,
            "sub_type": account.sub_type,
            "currency": account.current_balance.currency_code if account.current_balance else None,
            "balance": float(account.current_balance.amount) if account.current_balance else None,
            "available_balance": (
                float(account.available_balance.amount) if account.available_balance else None
            ),
            "emoji": account.emoji,
            "is_archived": account.is_archived,
        }
        for account in response.data
    ]


@mcp.tool(annotations=READ_ONLY)
def list_categories() -> list[dict[str, Any]]:
    """List all transaction categories with IDs and names.

    Returns category IDs needed for filtering transactions by category.
    """
    client = get_client()
    response = client.transaction_categories.list()

    return [
        {
            "id": category.id,
            "name": category.name,
            "color": getattr(category, "color", None),
            "icon": getattr(category, "icon", None),
            "is_subcategory": getattr(category, "is_subcategory", False),
        }
        for category in response.data
    ]


def parse_datetime(date_str: str | None) -> datetime | None:
    """Parse YYYY-MM-DD string to datetime object."""
    if not date_str:
        return None
    return datetime.fromisoformat(date_str)


@mcp.tool(annotations=READ_ONLY)
def list_transactions(
    from_date: str | None = None,
    to_date: str | None = None,
    transaction_types: list[str] | None = None,
    category_ids: list[str] | None = None,
    page_number: int | None = None,
    page_size: int | None = None,
) -> list[dict[str, Any]]:
    """List transactions with optional filters and pagination.

    Args:
        from_date: Filter transactions from this date (YYYY-MM-DD format).
        to_date: Filter transactions up to this date (YYYY-MM-DD format).
        transaction_types: Filter by types, e.g. ["debit", "credit"].
        category_ids: Filter by category IDs. Use list_categories to get IDs.
        page_number: Page number for pagination (starts at 1).
        page_size: Number of results per page.

    Returns:
        List of transactions with date, amount, description, and category.
    """
    client = get_client()

    # Build kwargs, excluding None values (SDK doesn't accept explicit nulls)
    kwargs: dict[str, Any] = {}
    if from_date:
        kwargs["from_date"] = parse_datetime(from_date)
    if to_date:
        kwargs["to_date"] = parse_datetime(to_date)
    if transaction_types:
        kwargs["transaction_types"] = transaction_types
    if category_ids:
        kwargs["category_ids"] = category_ids
    if page_number is not None:
        kwargs["page_number"] = page_number
    if page_size is not None:
        kwargs["page_size"] = page_size

    response = client.transactions.list(**kwargs)

    return [
        {
            "id": tx.id,
            "date": str(tx.transaction_date),
            "amount": tx.amount.format() if tx.amount else None,
            "description": tx.description,
            "category_id": getattr(tx, "category_id", None),
            "account_id": getattr(tx, "account_id", None),
            "type": getattr(tx, "type", None),
        }
        for tx in response.data
    ]


@mcp.tool(annotations=READ_ONLY)
def get_category_budgets(currency_code: str = "ZAR") -> list[dict[str, Any]]:
    """Get budget totals grouped by category and transaction type.

    Args:
        currency_code: Currency for aggregation (default: ZAR).

    Returns:
        List of budgets with category ID, transaction type, and amount.
    """
    client = get_client()
    budgets = client.category_budgets.aggregated(currency_code=currency_code)

    return [
        {
            "category_id": budget.category_id,
            "transaction_type": budget.transaction_type,
            "amount": float(budget.amount) if budget.amount else None,
        }
        for budget in budgets
    ]


@mcp.tool(annotations=READ_ONLY)
def get_net_worth(currency: str = "ZAR") -> dict[str, Any]:
    """Get aggregated net worth over time.

    Args:
        currency: Currency code to aggregate by (default: ZAR)

    Returns:
        Historical balance snapshots showing net worth over time.
    """
    client = get_client()
    snapshots = client.account_balances.aggregated(currency=currency)

    return {
        "currency": currency,
        "snapshots": [
            {
                "date": str(snapshot.date),
                "amount": snapshot.amount.format() if snapshot.amount else None,
                "amount_raw": float(snapshot.amount.amount) if snapshot.amount else None,
            }
            for snapshot in snapshots[-30:]  # Last 30 snapshots
        ],
        "latest": {
            "date": str(snapshots[-1].date) if snapshots else None,
            "amount": snapshots[-1].amount.format() if snapshots and snapshots[-1].amount else None,
            "amount_raw": float(snapshots[-1].amount.amount) if snapshots and snapshots[-1].amount else None,
        } if snapshots else None,
        "total_snapshots": len(snapshots),
    }


def main():
    """Run the Finwise MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
