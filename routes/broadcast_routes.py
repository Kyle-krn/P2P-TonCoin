from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from starlette import status
from jinja_func import flash
from utils.notification_telegram import broadcaster

broadcast_router = APIRouter()

@broadcast_router.post("/broadcast")
async def update_pdf_scheme(request: Request,
                            redirect_url: str = Form(),
                            rus_text: str = Form(),
                            eng_text: str = Form()):
    if len(rus_text) > 4000 or len(eng_text) > 4000:
        flash(request, "Message too long", 'danger')
    elif len(rus_text) == 0 and len(eng_text) == 0:
        flash(request, "Message empty", 'danger')
    else:
        if len(rus_text) == 0 and len(eng_text) != 0:
            rus_text = eng_text
        elif  len(eng_text) == 0 and len(rus_text) != 0:
            eng_text = rus_text
        await broadcaster(rus_text=rus_text, eng_text=eng_text)
        flash(request,"Success", "success")
    return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    