from enum import Enum


class ProductType(str, Enum):
    SOHAN = "سوهان"
    GAZ = "گز"


class ProductModel(str, Enum):
    HOBEH = "حبه ای"
    BAGHLAVAEI = "باقلوایی"
    GOL = "گل"
    SEKKEI = "سکه‌ای"
    LOGHMEH = "لقمه ای"
    MEDADI = "مدادی"
    COMBINATION = "ترکیبی از چند مدل"
    

class OilType(str, Enum):
    ANIMAL = "روغن حیوانی"
    VEGETABLE_BUTTER = "کره گیاهی"
    NABATI_OIL = "روغن نباتی"    
