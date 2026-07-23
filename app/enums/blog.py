from enum import Enum


class BlogStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"