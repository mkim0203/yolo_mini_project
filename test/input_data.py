
import asyncio
import base64
import mimetypes
import re
import httpx

from pathlib import Path
from datetime import datetime, timedelta, timezone


# 설정
IMAGE_DIR = Path("./images")
API_URL = "http://127.0.0.1:8000/requests/request"


def get_file_info(file_path: Path):
    """
    파일명 분석
    예: 10d_고추가루.jpg
    """

    match = re.match(r"^(\d+)d_(.+)$", file_path.stem)

    if match:
        expiry_days = int(match.group(1))
        info = match.group(2)
    else:
        expiry_days = 30
        info = file_path.stem

    expiry_date = (
        datetime.now(timezone.utc)
        + timedelta(days=expiry_days)
    )

    return info, expiry_date



async def send_request(client: httpx.AsyncClient, file_path: Path):

    try:
        # 파일 정보 생성
        info, expiry_date = get_file_info(file_path)

        # 이미지 MIME 타입 확인
        image_type, _ = mimetypes.guess_type(file_path)

        if image_type is None:
            print(f"[실패] 지원하지 않는 이미지 형식: {file_path.name}")
            return

        # 일반 폼 데이터
        data = {
            "info": info,
            "expiry_date": expiry_date.isoformat(),
            "image_type": image_type
        }

        # info: str | None = Form(None),
        # expiry_date: datetime = Form(...),
        # image: UploadFile = File(...),

        # 이미지 파일 데이터
        with file_path.open("rb") as image_file:

            files = {
                "image": (
                    file_path.name,
                    image_file,
                    image_type
                )
            }

            response = await client.post(
                API_URL,
                data=data,
                files=files
            )

        response.raise_for_status()

        print(f"[성공] {file_path.name} -> {info}")

    except httpx.HTTPStatusError as e:
        print(
            f"[API 실패] {file_path.name}: "
            f"{e.response.status_code} / {e.response.text}"
        )

    except httpx.RequestError as e:
        print(f"[통신 오류] {file_path.name}: {e}")

    except Exception as e:
        print(f"[오류] {file_path.name}: {e}")


async def main():

    extensions = {".jpg", ".jpeg", ".png", ".webp"}

    if not IMAGE_DIR.exists():
        print(f"폴더가 존재하지 않습니다: {IMAGE_DIR}")
        return

    # 이미지 파일 검색
    image_files = [
        path for path in IMAGE_DIR.iterdir()
        if path.is_file()
        and path.suffix.lower() in extensions
    ]

    print(f"전체 이미지: {len(image_files)}개")

    async with httpx.AsyncClient(timeout=30.0) as client:

        for file_path in image_files:
            await send_request(client, file_path)


if __name__ == "__main__":
    asyncio.run(main())
