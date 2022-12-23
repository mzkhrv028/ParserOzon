from dataclasses import dataclass, field


@dataclass
class CardproductItem:
    id: int
    title: str
    brandName: str
    finalPrice: int
    rating: float
    discount: int
    price: int
    deliveryTimeDiffDays: int
    countItems: int
    index: int
    link: int


@dataclass
class ProductItem:
    link: str = field(default=None)
    productTitle: str = field(default=None)
    characteristics: dict = field(default_factory=dict)
