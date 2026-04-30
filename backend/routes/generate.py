from fastapi import APIRouter, HTTPException, Body
from backend.models import GenerateTask, GeneratorSettings, AIRequest
from backend.utils.parser import parse_dicts
from backend.generation import DataGenerationFaker, DataGeneratorAI


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
        all_data = []
        chunk_size = 50
        remaining_rows = request.rows

        filed_config = [{"name": f, "type": "text"} for f in request.fields]

        while remaining_rows > 0:
            current_batch_size = min(chunk_size, remaining_rows)
            batch_settings = GeneratorSettings(rows=current_batch_size, fields=filed_config)
            generator = DataGeneratorAI(batch_settings)

            chunk_data = generator.run_generation()

            start_id = len(all_data) + 1
            for idx, row in enumerate(chunk_data):
                row["ID"] = str(start_id + idx)
            
            all_data.extend(chunk_data)
            remaining_rows  -= current_batch_size
            
            print(f"--- Сгенерировано {len(all_data)} из {request.rows} ---")
    
        return {"data": all_data, "count": len(all_data)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
