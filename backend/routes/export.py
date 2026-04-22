# Объявление endpoint для экспорта данных
from fastapi import APIRouter, HTTPException # noqa: F401
from fastapi.responses import FileResponse
from backend.export import SaveDataToCSV
from typing import Any

router = APIRouter(prefix="/export", tags=["Export"])


@router.post("/csv")
async def save_to_csv(payload:dict[str, Any], file_name = "my_dataset.csv"):
    if "data" in payload and isinstance(payload["data"], list):
        data = payload["data"]
        file_name = payload.get("file_name", file_name)
    elif isinstance(payload, list):
        data = payload
    else:
        raise HTTPException(status_code=400, detail="Invalid payload")
    
    if not data:
        raise HTTPException(status_code=400, detail="Data cannot be empty.")

    try:
        saver = SaveDataToCSV(data)
        path = saver.save(file_name)
        return FileResponse(path=path, filename=file_name, media_type="text/csv")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
