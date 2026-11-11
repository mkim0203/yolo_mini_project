### api 기능작업
### ai 관련 기능

# 분석
	적제요청 이미지 체크 (딥러닝) 학습된것 사용
		VGG16 기반 상품 이미지 식품/비식품 분류
		추후 식품이 어떤 상품인지 구분하는것도 추가해볼 예정
	LLM 으로 음식 아닌 이미지 추가 검증(필요시 작업)

POST http://localhost:19000/predict
요청
{
    "request_id": 10,
    "image_base64": "이미지 Base64 데이터"
}

응답
{
    "request_id": 10,
    "classification": "food",
    "confidence": 0.98,
    "model_version": "v1.0"
}