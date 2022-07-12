from fastapi import Request
import middlewares
from loader import app
import handlers
import routes
from utils.exceptions import NotAuthenticatedException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(routes.event_router)
app.include_router(routes.user_router)
app.include_router(routes.auth_router)
app.include_router(routes.payments_router)
app.include_router(routes.currency_router)
app.include_router(routes.order_by_router)
app.include_router(routes.order_router)
app.include_router(routes.lang_router)

    

@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    """
    Redirect the user to the login page if not logged in
    """
    return RedirectResponse(url='/auth/login')


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return RedirectResponse("/users")