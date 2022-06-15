import middlewares
from loader import app
import handlers
import routes

from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(routes.event_router)

    

