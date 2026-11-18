FROM python:3.12-slim

# 로그 버퍼링 변경 print 출력 안되는 이슈가 있을때..
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]