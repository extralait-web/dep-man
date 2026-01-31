import sys

import pytest


@pytest.fixture(autouse=True)
def fake_starlette(mocker):
    starlette = type(sys)("starlette")
    starlette.middleware = type(sys)("middleware")
    starlette.middleware.base = type(sys)("base")
    starlette.middleware.base.BaseHTTPMiddleware = type("BaseHTTPMiddleware", (), {})
    mocker.patch.dict(
        "sys.modules",
        {
            "starlette": starlette,
            "starlette.middleware": starlette.middleware,
            "starlette.middleware.base": starlette.middleware.base,
        },
    )


@pytest.fixture(autouse=True)
def fake_django(mocker):
    django = type(sys)("django")
    django.utils = type(sys)("utils")
    django.utils.decorators = type(sys)("decorators")
    django.utils.decorators.sync_and_async_middleware = lambda f: f
    mocker.patch.dict(
        "sys.modules",
        {
            "django": django,
            "django.utils": django.utils,
            "django.utils.decorators": django.utils.decorators,
        },
    )
