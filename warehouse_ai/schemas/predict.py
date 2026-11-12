from pydantic import BaseModel

class PredictFoodRequest(BaseModel):
    request_id : int
    image_data : str
    image_type: str
    food_score_threshold: float | None=None

class PredictFoodResponse(BaseModel):
    request_id : int
    is_food: bool
    score: float