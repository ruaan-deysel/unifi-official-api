"""Point of Sale (POS) models for UniFi Protect."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class POSLineItem(BaseModel):
    """POS transaction line item."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    title: str
    quantity: int = 1


class POSLocation(BaseModel):
    """POS register location."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str | None = None


class POSTransactionRequest(BaseModel):
    """POS transaction ingestion payload."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    type: str = "sale"
    external_id: str = Field(alias="externalId")
    amount: float
    currency: str = "USD"
    line_items: list[POSLineItem] = Field(default_factory=list, alias="lineItems")
    location: POSLocation | None = None
    payment_types: list[str] = Field(default_factory=list, alias="paymentTypes")
    timestamp: int | None = None
