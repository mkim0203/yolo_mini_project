WAREHOUSE_API_URL = "http://127.0.0.1:8000"
WAREHOUSE_AI_URL = "http://127.0.0.1:18000"

# 스케줄링 작업 설정
SCHEDULE_JOBS = [
    {
        "id": "storage_classification",
        "name": "적재 요청 상품 분류",
        "cron": "* * * * *",
        "enabled": True
    }
    # ,{
    #     "id": "expiry_release",
    #     "name": "유통기한 임박 상품 자동 반출",
    #     "cron": "10 * * * *",
    #     "enabled": True
    # }
]