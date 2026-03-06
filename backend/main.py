from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.scan_routes import router as scan_router

app = FastAPI(
    title="Secret Scanner API",
    version="1.0.0",
    description="API для сканирования кода на утечки секретов."
)

# Разрешаем фронтенду на React общаться с нашим API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрируем роуты
app.include_router(scan_router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Secret Scanner Backend is running!"}