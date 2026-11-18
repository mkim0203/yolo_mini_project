import os
from dotenv import load_dotenv

if not os.getenv("DOCKER_ENV"):
    load_dotenv()

WAREHOUSE_API_URL = os.getenv("WAREHOUSE_API_URL")
WAREHOUSE_AI_URL = os.getenv("WAREHOUSE_AI_URL")

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