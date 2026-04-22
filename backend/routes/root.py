from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def get_hello():
    return {"message": "Hi, this is Data Generator System!"}
