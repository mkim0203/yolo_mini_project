from services.warehouse_client import WarehouseClient
from services.ai_client import WarehouseAIClient


async def storage_classification_job():
    print("exec storage_classification_job")

    warehouse = WarehouseClient()
    ai = WarehouseAIClient()

    # 0. configs/config?key=food_score_threshold config 정보 조회
    config_food_score_threshold = await warehouse.get("/configs/config?key=food_score_threshold")

    food_score_threshold = float(config_food_score_threshold["config_value"])
    print(f"food_score_threshold => {food_score_threshold}")

    # 1. 적재 요청 목록 조회
    requests = await warehouse.get("/requests")

    if requests.get("total", 0) == 0:
        print("처리할 적재 요청이 없습니다.")
        return

    # 2. 미분류 요청만 필터링
    pending_items = [
        item for item in requests.get("items", [])
        if item.get("classification_status") is None or item.get("classification_status") == "pending" 
    ]

    if not pending_items:
        print("분류 대기 중인 요청이 없습니다.")
        return

    

    # 3. 요청별 상세 조회 및 AI 분류
    for item in pending_items:
        request_id = item["request_id"]

        # 요청 항목 작업 진행 update processing
        await update_classification_status(request_id, "processing")

        try:
            # 상세 정보 조회
            detail = await warehouse.get(
                f"/requests/{request_id}"
            )

            

            # AI 분류 요청
            result = await ai.post(
                "/predicts/food",
                data={
                    "request_id": request_id,
                    "image_type": detail["image_type"],
                    "image_data": detail["image_data"],
                    "food_score_threshold": food_score_threshold
                }
            )

            print(f"분류 완료: {request_id} / {detail["info"]}, 결과: {result["is_food"]} / {result["score"]:.5f}")

            # 요청 항목 작업 진행 update completed
            # 분류 결과 저장
            await update_classification_status(request_id, "completed", result["score"])


        except Exception as e:
            print(f"분류 실패: {request_id}, 오류: {e}")
            # 요청 항목 작업 진행 update failed
            await update_classification_status(request_id, "failed")


async def update_classification_status(request_id:int, status:str, score:float=None):
    warehouse = WarehouseClient()

    update_url = f"/requests/{request_id}"
    await warehouse.put(update_url,
        data={
            "classification_status": status,
            "food_score": score
        }
    )