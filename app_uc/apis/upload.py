from fastapi import APIRouter, File, UploadFile, HTTPException
from services.mongo_service import insert_or_update_transactions
from utils.csv_parser import parse_csv

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        async for chunk in parse_csv(file.file):
            if chunk:
                await insert_or_update_transactions(chunk, batch_size=5000)

        return {"message": f"Successfully uploaded {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process the file: {str(e)}")

