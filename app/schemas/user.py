from pydantic import BaseModel, field_validator, FieldValidationInfo
from pydantic_core import PydanticCustomError
from typing import Annotated
import re

class UserCreate(BaseModel):
    mobile: str
    userName: str
    password: str
    repeatPassword: str

    @field_validator("userName")
    @classmethod
    def username_length(cls, v):
        if len(v) < 3:
            raise PydanticCustomError("userName", "نام و نام خانوادگی حداقل باید ۳ حرف باشد")
        return v

    @field_validator("mobile")
    @classmethod
    def valid_mobile(cls, v):
        pattern = r"^09\d{9}$"
        if not re.match(pattern, v):
            raise PydanticCustomError("mobile", "شماره موبایل وارد شده معتبر نمیباشد")
        return v

    @field_validator("password")
    @classmethod
    def strong_password(cls, v):
        if len(v) < 6:
            raise PydanticCustomError("password", "رمز عبور حداقل باید ۶ اجزا داشته باشد")
        if not re.search(r"[A-Za-z]", v):
            raise PydanticCustomError("password", "رمز عبور باید شامل حروف باشد")
        if not re.search(r"\d", v):
            raise PydanticCustomError("password", "رمز عبور باید شامل اعداد باشد")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise PydanticCustomError("password", "رمز عبور باید شامل کاراکتر باشد")
        return v

    @field_validator("repeatPassword")
    @classmethod
    def passwords_match(cls, v, info: FieldValidationInfo):
        password = info.data.get("password")
        if password and v != password:
            raise PydanticCustomError("repeatPassword", "رمز عبور تکرار شده صحیح نمیباشد")
        return v

class UserOut(BaseModel):
    id: int
    mobile: str
    userName: str
    application_id: int
    model_config = {
        "from_attributes": True
    }

class TokenResponse(BaseModel):
    access_token: str
    token_type: Annotated[str, "bearer"]
