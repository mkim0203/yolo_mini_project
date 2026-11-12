from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import SCHEDULE_JOBS
from jobs.storage_job import storage_classification_job
from jobs.expiry_job import expiry_release_job


scheduler = AsyncIOScheduler(
    timezone="Asia/Seoul"
)

# 작업 ID와 실제 실행 함수 연결
JOB_FUNCTIONS = {
    "storage_classification": storage_classification_job,
    "expiry_release": expiry_release_job
}


def register_jobs():

    for job_config in SCHEDULE_JOBS:

        if not job_config["enabled"]:
            continue

        job_id = job_config["id"]
        job_func = JOB_FUNCTIONS.get(job_id)

        if job_func is None:
            print(f"[스케줄 등록 실패] 등록되지 않은 작업: {job_id}")
            continue

        trigger = CronTrigger.from_crontab(
            job_config["cron"],
            timezone="Asia/Seoul"
        )

        scheduler.add_job(
            job_func,
            trigger=trigger,
            id=job_id,
            name=job_config["name"],
            replace_existing=True,
            max_instances=1, # 동일 Job의 동시 실행을 1개로 제한합니다.
            coalesce=True # 실행이 지연되어 여러 실행 시점이 밀렸을 때, 누적된 실행을 하나로 합칩니다.
        )

        print(
            f"[스케줄 등록] {job_id} / {job_config['cron']}"
        )