# api/routes/recognize.py
import shutil, uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from api.schemas import RecognizeResponse, IngredientItem
from api.dependencies import get_recognizer
from models.vision.recognizer import FoodRecognizer
from PIL import Image

router = APIRouter(prefix="/recognize", tags=["vision"])

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/image", response_model=RecognizeResponse)
async def recognize_image(
    file:       UploadFile = File(...),
    recognizer: FoodRecognizer = Depends(get_recognizer),
):
    # 檢查副檔名
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400,
                            detail="只支援 JPG / PNG 格式")

    # 暫存上傳圖片
    tmp_path = UPLOAD_DIR / f"{uuid.uuid4().hex}.jpg"
    with tmp_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # 取得原始圖片尺寸
        with Image.open(tmp_path) as img:
            w, h = img.size

        # 呼叫辨識模型
        detections = recognizer.recognize(str(tmp_path))

        return RecognizeResponse(
            ingredients=[
                IngredientItem(**d) for d in detections
            ],
            raw_image_size=[w, h],
        )
    finally:
        tmp_path.unlink(missing_ok=True)  # 推理完馬上刪暫存