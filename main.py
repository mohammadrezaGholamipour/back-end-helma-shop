from app.core.exceptions import validation_exception_handler, http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from app.models import Category, Product, User,Store
from starlette.staticfiles import StaticFiles
from app.api.v1 import __path__ as api_path
from fastapi import APIRouter
from fastapi import FastAPI
import importlib
import pkgutil
import uvicorn

# /////////////////////////////////////////////////
app = FastAPI(title="helma", description="API for helma shop", version="1.0.0",docs_url="/docs",
    openapi_url="/openapi.json", responses={
    422: {
        "description": "Validation Error Example",
        "content": {
            "application/json": {
                "example": {
                    "error": [
                        {"field": "نام فیلد", "message": "متن خطا"}
                    ]
                }
            }
        }
    },
    409: {
        "description": "The resource already exists or violates a unique constraint",
        "content": {
            "application/json": {
                "example": {
                    "error": [
                        {"field": "نام فیلد", "message": "متن خطا"}
                    ]
                }
            }
        }
    },
    401: {
        "description": "The request requires authentication or the provided credentials are invalid",
        "content": {
            "application/json": {
                "example": {
                    "error": [
                        {"field": "نام فیلد", "message": "متن خطا"}
                    ]
                }
            }
        }
    },
    404: {
        "description": "The requested resource was not found on the server",
        "content": {
            "application/json": {
                "example": {
                    "error": [
                        {"field": "نام فیلد", "message": "متن خطا"}
                    ]
                }
            }
        }
    },
    403: {
        "description": "The client does not have permission to access this resource",
        "content": {
            "application/json": {
                "example": {
                    "error": [
                        {"field": "نام فیلد", "message": "متن خطا"}
                    ]
                }
            }
        }
    }
})
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# /////////////////////////////////////////////////
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# /////////////////////////////////////////////////
api_router = APIRouter()

for module_info in pkgutil.iter_modules(api_path):
    module = importlib.import_module(f"app.api.v1.{module_info.name}")

    if hasattr(module, "router"):
        api_router.include_router(module.router)

app.include_router(api_router)
# /////////////////////////////////////////////////
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
# /////////////////////////////////////////////////


# uvicorn.run(app, host="0.0.0.0", port=8000)
