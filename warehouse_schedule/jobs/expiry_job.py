from services.warehouse_client import WarehouseClient


async def expiry_release_job():

    warehouse = WarehouseClient()

    # 1. 자동 반출 기준 조회
    policy = await warehouse.get("/settings/auto-release")

    if not policy["enabled"]:
        print("[자동 반출] 기능이 비활성화되어 있습니다.")
        return

    days = policy["expiry_days"]

    # 2. 반출 대상 조회
    targets = await warehouse.get(
        "/storage/expiry",
        params={"option": days}
    )

    for item in targets:

        try:
            # 3. 반출 등록
            await warehouse.post(
                "/release",
                {
                    "slot_id": item["slot_id"]
                }
            )

            print(
                f"[자동 반출 완료] "
                f"slot_id={item['slot_id']}"
            )

        except Exception as e:
            print(
                f"[자동 반출 실패] "
                f"slot_id={item['slot_id']}, error={e}"
            )