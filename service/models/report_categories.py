from typing import List
from pydantic import BaseModel

class SubCategory:
    category_id: int
    sub_category_id: int
    category_name: str
    subcategory_name: str
    def __init__(self, category_id: int, sub_category_id: int, category_name: str, subcategory_name: str):
        self.category_id = category_id
        self.sub_category_id = sub_category_id
        self.category_name = category_name
        self.subcategory_name = subcategory_name


class SubCategoryDto (BaseModel):
    subcategory_id: int
    subcategory_name: str


class CategoryDto(BaseModel):
    category_id: int
    category_name: str
    sub_categories: List[SubCategoryDto] = []