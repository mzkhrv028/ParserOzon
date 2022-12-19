from dataclasses import dataclass

# Сделать сортировку
@dataclass
class CardproductItem():
    id: int
    title: str
    brandName: str
    finalPrice: int
    rating: float
    discount: int
    price: int
    deliveryTimeDiffDays: int
    index: int
    link: int
