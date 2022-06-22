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
app.include_router(routes.history_balance_router)
app.include_router(routes.login_router)
app.include_router(routes.referal_router)
app.include_router(routes.payment_account_router)
app.include_router(routes.currency_router)

    

@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    """
    Redirect the user to the login page if not logged in
    """
    return RedirectResponse(url='/auth/login')


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    # print(request.auth)
    return RedirectResponse("/users")