from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse 
from backend.models import GenerateTask, GeneratorSettings, AIRequest
from backend.utils.parser import parse_dicts
from backend.generation import DataGenerationFaker, DataGeneratorAI
import asyncio
import json

router = APIRouter(prefix="/generate", tags=["Generation"])


def to_settings(task: GenerateTask) -> GeneratorSettings:
    return GeneratorSettings(
        rows=task.rows,
        fields=parse_dicts(task.fields)
    )


@router.post("/faker")
async def faker(task: GenerateTask):
    try:
        settings = to_settings(task)
        generator = DataGenerationFaker(settings)
        generator.field_preparation(task.methods)
        data = generator.run_generation()
        
        return {"data": data, "count": len(data)}   
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ai")
async def gen_ai(request: AIRequest = Body(...)):
    if request.rows <= 0:
        raise HTTPException(status_code=400, detail="Number of rows must be greater than zero.")
    if not request.fields:
        raise HTTPException(status_code=400, detail="Fields list cannot be empty.")
    
    try:
        filed_config = [{"name": f, "type": "text"} for f in request.fields]
        async def event_generator():
            chunk_size = 10
            remaining_rows = request.rows
            all_generate_count = 0

            while remaining_rows > 0:
                current_batch_size = min(chunk_size, remaining_rows)
                batch_settings = GeneratorSettings(rows=current_batch_size, fields=filed_config)
                generator = DataGeneratorAI(batch_settings)

                loop = asyncio.get_event_loop()
                chunk_data = await loop.run_in_executor(None, lambda: list(generator.run_generation()))

                if not chunk_data:
                    break

                for row in chunk_data:
                    row["ID"] = str(all_generate_count + 1)
                    all_generate_count += 1

                print(f"--- Сгенерировано {all_generate_count} из {request.rows} ---")
                yield json.dumps({
                    "chunk": chunk_data,
                    "progress": all_generate_count,
                    "total": request.rows
                }, ensure_ascii=False) + "\n"

                remaining_rows  -= len(chunk_data)    
        return StreamingResponse(event_generator(), media_type="application/x-ndjson")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
