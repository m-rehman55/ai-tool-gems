"""Product catalog access."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


CATALOG_PATH = Path(__file__).resolve().parent / "data" / "products.json"


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    category: str
    price: int
    old_price: int
    duration: str
    access: str
    delivery: str
    warranty: str
    best_for: tuple[str, ...]

    @property
    def saving(self) -> int:
        return max(0, self.old_price - self.price)

    @property
    def discount_percent(self) -> int:
        return round(self.saving / self.old_price * 100) if self.old_price else 0


PRODUCT_FIELDS = {"id", "name", "category", "price", "old_price", "duration", "access", "delivery", "warranty", "best_for"}


def load_products(path: Path = CATALOG_PATH) -> list[Product]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    result = []
    for row in rows:
        filtered = {k: v for k, v in row.items() if k in PRODUCT_FIELDS}
        filtered["best_for"] = tuple(filtered["best_for"])
        result.append(Product(**filtered))
    return result


def get_product(product_id: str) -> Product:
    for product in load_products():
        if product.id == product_id:
            return product
    raise KeyError(f"Unknown product: {product_id}")
