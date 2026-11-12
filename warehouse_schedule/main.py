import asyncio

from scheduler import scheduler, register_jobs


async def main():

    register_jobs()

    scheduler.start()

    print("[Scheduler] 실행 시작")

    try:
        while True:
            await asyncio.sleep(60)

    except (KeyboardInterrupt, asyncio.CancelledError):
        print("[Scheduler] 종료")

    finally:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    asyncio.run(main())