import uvicorn
from fastapi import FastAPI
from backend.routes import main_router, generate_router, export_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    root_path="/api",
    title="Astra_prog API",
    version="0.1.0",
    description="API for parsing logs and saving datasets (DB/CSV).",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(main_router)
app.include_router(generate_router)
app.include_router(export_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
