import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict

Category = Literal[
    "T-shirt",
    "Shirt",
    "Hoodie",
    "Sweater",
    "Jacket",
    "Coat",
    "Dress",
    "Skirt",
    "Jeans",
    "Pants",
    "Shorts",
    "Traditional clothing",
    "Shoes",
    "Accessories",
]
FitType = Literal["slim", "regular", "relaxed", "oversized"]


class ClothingSizeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    size_label: str
    chest_cm: float | None = None
    waist_cm: float | None = None
    hip_cm: float | None = None
    length_cm: float | None = None
    stock_qty: int


class SizeChartRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    category: str
    sizes: list[ClothingSizeRead] = []


class ClothingListItem(BaseModel):
    """Lighter shape for the catalog grid — no description/tags/full
    size chart, just enough to render a product card and let someone
    pick a size."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    brand: str | None
    category: str
    primary_color: str
    available_colors: list[str]
    price: float
    currency: str
    fit_type: FitType | None
    available_sizes: list[str] = []


class ClothingDetailRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    brand: str | None
    category: str
    description: str | None
    primary_color: str
    available_colors: list[str]
    material: str | None
    price: float
    currency: str
    product_url: str | None
    fit_type: FitType | None
    tags: list[str]
    size_chart: SizeChartRead | None = None


class ClothingCreate(BaseModel):
    name: str
    brand: str | None = None
    category: Category
    description: str | None = None
    primary_color: str
    available_colors: list[str] = []
    material: str | None = None
    price: float
    currency: str = "USD"
    product_url: str | None = None
    affiliate_url: str | None = None
    size_chart_id: uuid.UUID | None = None
    fit_type: FitType | None = None
    tags: list[str] = []


class PaginatedClothing(BaseModel):
    items: list[ClothingListItem]
    total: int
    page: int
    page_size: int
