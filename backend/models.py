from pydantic import BaseModel, Field
from typing import List

class InventoryRow(BaseModel):
    size: str
    quantity: int = Field(ge=0)

class ProductCard(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    price: float = Field(ge=0)
    image_file_path: str
    colors: List[str] = Field(default_factory=list)
    inventory: List[InventoryRow] = Field(default_factory=list)
    total_stock: int = Field(default=0, ge=0)

class ChatReply(BaseModel):
    reply: str
    products: List[ProductCard] = Field(default_factory=list)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    history: List[dict] = Field(default_factory=list, max_length=20)

class PageContext(BaseModel):
    page: str = Field(default='home', max_length=80)
    product_id: str | None = Field(default=None, max_length=120)
    product_name: str | None = Field(default=None, max_length=200)
    product_description: str | None = Field(default=None, max_length=1000)

class ChatDeps(BaseModel):
    user_id: int | None = None
    customer_name: str | None = None
    customer_email: str | None = None
    page_context: PageContext = Field(default_factory=PageContext)
