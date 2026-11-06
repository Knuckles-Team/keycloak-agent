"""Helpers shared by the typed Keycloak tools."""

from typing import Any

CONFIRMATION_REQUIRED: dict[str, Any] = {
    "error": "confirmation_required",
    "message": "This call is destructive. Pass confirm=true after the person agrees.",
}


def drop_none(**kwargs: Any) -> dict[str, Any]:
    """Keyword arguments without the unset (None) values."""
    return {k: v for k, v in kwargs.items() if v is not None}
