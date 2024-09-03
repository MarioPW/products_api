from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from os import getenv

from src.components.routes import router

load_dotenv()
app = FastAPI(
    title="Products API",
    description="API for managing products",
    version="0.0.1"
)

ORIGINS = getenv('ALLOWED_ORIGINS').split(",")
# print(f'Clientes autorizados: {ORIGINS}.\nSi notas que no se actualizan las URL al modificarlas en la variable de entorno ALLOWED_ORIGINS del archivo .env,\ntrata cerrando la consola y abre una diferente para levantar el servidor nuevamente.')

app.include_router(router, prefix="/api/v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.mount("/static", StaticFiles(directory="static"), name="static")

jinja2_templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse, tags=["Docs"])
def docs_layout(request: Request):
    return jinja2_templates.TemplateResponse("api_docs.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    host = getenv('HOST', '127.0.0.1')
    port = int(getenv("PORT", 8000))
    uvicorn.run(app, host="host", port=port)