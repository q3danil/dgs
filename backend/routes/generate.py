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
        settings = GeneratorSettings(rows=request.rows, fields=[{"name": f, "type": "text"} for f in request.fields])
        generator = DataGeneratorAI(settings)
        data = generator.run_generation()
    
        return {"data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
