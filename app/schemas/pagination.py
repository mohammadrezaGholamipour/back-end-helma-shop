from pydantic import BaseModel


class PaginationMeta(BaseModel):
    current_page: int
    per_page: int
    total: int
    last_page: int