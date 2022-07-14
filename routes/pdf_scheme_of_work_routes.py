from fastapi import APIRouter, Request, File, UploadFile, Form
from fastapi.responses import RedirectResponse
from starlette import status
import shutil
from jinja_func import flash

pdf_router = APIRouter()


@pdf_router.post("/update_pdf_scheme")
async def update_pdf_scheme(request: Request,
                            redirect_url: str = Form(),
                            file: UploadFile = File(...)):
    if file.filename.split('.')[-1].lower() != "pdf":
        flash(request,"Accept only PDF format", "danger")
    else:
        with open("static/scheme_of_work.pdf", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        flash(request,"PDF update success", "success")
    return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    
