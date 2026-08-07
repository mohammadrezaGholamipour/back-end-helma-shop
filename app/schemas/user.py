import re

from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationInfo,
    field_validator,
)

from pydantic_core import PydanticCustomError

from app.models.user import UserRole


# =====================================================
# REGISTER
# =====================================================

class UserCreate(BaseModel):
    mobile: str

    username: str

    password: str

    repeat_password: str


    @field_validator("username")
    @classmethod
    def username_length(cls, v: str) -> str:

        v = v.strip()

        if len(v) < 3:
            raise PydanticCustomError(
                "username",
                "نام کاربری حداقل باید ۳ حرف باشد",
            )

        return v


    @field_validator("mobile")
    @classmethod
    def valid_mobile(cls, v: str) -> str:

        v = v.strip()

        pattern = r"^09\d{9}$"

        if not re.match(pattern, v):
            raise PydanticCustomError(
                "mobile",
                "شماره موبایل وارد شده معتبر نمی‌باشد",
            )

        return v


    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:

        if len(v) < 6:
            raise PydanticCustomError(
                "password",
                "رمز عبور حداقل باید ۶ کاراکتر داشته باشد",
            )

        if not re.search(r"[A-Za-z]", v):
            raise PydanticCustomError(
                "password",
                "رمز عبور باید شامل حروف باشد",
            )

        if not re.search(r"\d", v):
            raise PydanticCustomError(
                "password",
                "رمز عبور باید شامل اعداد باشد",
            )

        if not re.search(
            r"[!@#$%^&*(),.?\":{}|<>]",
            v
        ):
            raise PydanticCustomError(
                "password",
                "رمز عبور باید شامل کاراکتر ویژه باشد",
            )

        return v


    @field_validator("repeat_password")
    @classmethod
    def passwords_match(
        cls,
        v: str,
        info: ValidationInfo,
    ) -> str:

        password = info.data.get("password")

        if password and v != password:
            raise PydanticCustomError(
                "repeat_password",
                "رمز عبور تکرار شده صحیح نمی‌باشد",
            )

        return v



# =====================================================
# USER OUTPUT
# =====================================================

class UserOut(BaseModel):

    id: int

    mobile: str

    username: str

    role: UserRole

    is_active: bool

    is_verified: bool


    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
    )



# =====================================================
# TOKEN
# =====================================================

class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

    model_config = ConfigDict(
        from_attributes=True
    )