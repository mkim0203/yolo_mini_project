from fastapi import APIRouter, Depends, Depends, UploadFile, File, Form, HTTPException

from schemas.predict import PredictFoodRequest, PredictFoodResponse
from services.food import exec_predict

router = APIRouter(
    prefix="/predicts",
    tags=["predicts"]
)

@router.post("/food", description="food/no food 분류", response_model=PredictFoodResponse)
async def predict_food(data: PredictFoodRequest):
    result = exec_predict(data.request_id, data.image_type, data.image_data, data.food_score_threshold)

    return PredictFoodResponse(
        request_id=result["request_id"], 
        is_food=result["is_food"], 
        score=result["score"]
    )
    