from enum import Enum


class ProductType(str, Enum):
    SOHAN = "SOHAN"
    GAZ = "GAZ"


class ProductModel(str, Enum):
    HOBEH = "HOBEH"
    BAGHLAVAEI = "BAGHLAVAEI"
    GOL = "GOL"
    SEKKEI = "SEKKEI"
    LOGHMEH = "LOGHMEH"
    MEDADI = "MEDADI"
    COMBINATION = "COMBINATION"
    

class OilType(str, Enum):
    ANIMAL_OIL = "ANIMAL_OIL"
    VEGETABLE_BUTTER = "VEGETABLE_BUTTER"
    NABATI_OIL = "NABATI_OIL"    
