from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from json import JSONDecodeError
from fastapi import Request

# ---------------- ERROR ---------------- #
error_messages = {
    # body/query errors
    "string_too_short": "طول مقدار وارد شده کمتر از حد مجاز است",
    "string_type": "مقدار باید از نوع متن باشد",
    "missing": "اطلاعات ارسال شده کامل نمیباشد",
    "enum": "مقدار واردشده معتبر نیست",
    "datetime_type": "فرمت تاریخ و زمان معتبر نیست",
    "datetime_from_date_parsing": "فرمت تاریخ و زمان معتبر نیست",
    "date_type": "فرمت تاریخ معتبر نیست",
    "type_error": "نوع داده واردشده صحیح نیست",
    "json_invalid": "فرمت بدنه درخواست نامعتبر است",

    # path / number constraints
    "greater_than": "مقدار واردشده باید بزرگ‌تر باشد",
    "greater_than_equal": "مقدار واردشده کمتر از حد مجاز است",
    "less_than": "مقدار واردشده بیشتر از حد مجاز است",
    "less_than_equal": "مقدار واردشده بیشتر از حد مجاز است",

    "int_parsing": "مقدار باید عدد صحیح باشد",
    "int_type": "مقدار باید عدد صحیح باشد",
    "missing_path": "پارامتر مسیر الزامی است",

    # method errors
    "method_not_allowed": "متد درخواستی مجاز نمی‌باشد",

    # token
    "token_invalid": "لطفا ابتدا احراز هویت خود را انجام دهید",
}


# ---------------- Handlers ---------------- #
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = []

    has_body = (
            request.method in ("POST", "PUT", "PATCH")
            and request.headers.get("content-length")
            and int(request.headers["content-length"]) > 0
    )

    body_invalid = False

    # ---------- BODY JSON CHECK ----------
    if has_body:
        try:
            body = await request.json()

            if not isinstance(body, dict):
                error.append({
                    "field": "body",
                    "message": "بدنه درخواست باید یک JSON object باشد"
                })
                body_invalid = True

        except JSONDecodeError:
            error.append({
                "field": "body",
                "message": "JSON نامعتبر است"
            })
            body_invalid = True

        except UnicodeDecodeError:
            error.append({
                "field": "body",
                "message": "Encoding بدنه درخواست معتبر نیست"
            })
            body_invalid = True

    if body_invalid:
        return JSONResponse(status_code=422, content={"error": error})

    # ---------- PYDANTIC ERRORS ----------
    for err in exc.errors():
        loc = err.get("loc", [])
        error_type = err.get("type", "")
        message = err.get("msg", "")

        if loc and loc[0] == "path" and error_type == "missing":
            error_type = "missing_path"

        message = error_messages.get(error_type, message)

        field_name = loc[-1]

        error.append({
            "field": field_name,
            "message": message
        })

    return JSONResponse(status_code=422, content={"error": error})


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # ------------------ JSON خراب ------------------
    if exc.status_code == 400:
        if isinstance(exc.detail, str) and (
                "parsing the body" in exc.detail.lower()
                or "invalid json" in exc.detail.lower()
        ):
            return JSONResponse(
                status_code=400,
                content={
                    "error": [
                        {"field": "body", "message": error_messages["json_invalid"]}
                    ]
                }
            )

    # ------------------ UNAUTHORIZED ------------------
    if exc.status_code == 401:
        detail = getattr(exc, "detail", "")

        detail_str = str(detail).lower()

        if "token" in detail_str or "authenticated" in detail_str:
            return JSONResponse(
                status_code=401,
                content={"error": [{"message": error_messages["token_invalid"]}]})

        return JSONResponse(
            status_code=401,
            content={"error": [detail]}
        )

    # ------------------ NOT FOUND (Dynamic) ------------------
    if exc.status_code == 404:

        if exc.detail == "Not Found":
            return JSONResponse(
                status_code=404,
                content={"error": [{"message": "آدرس وارد شده معتبر نمی‌باشد"}]}
            )

        if isinstance(exc.detail, dict):
            return JSONResponse(
                status_code=404,
                content=[{"error": exc.detail}]
            )

    # ------------------ METHOD NOT ALLOWED ------------------
    if exc.status_code == 405:
        return JSONResponse(
            status_code=405,
            content={
                "error": [
                    {"field": "method", "message": error_messages["method_not_allowed"]}
                ]
            }
        )

    # ------------------ سایر HTTPException ها ------------------
    if isinstance(exc.detail, dict):
        error = exc.detail
    else:
        error = [{"field": "نامشخص", "message": "خطای غیرمنتظره‌ای رخ داده است"},
                 {"field": "general", "message": str(exc.detail)}]

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": [error]}
    )
