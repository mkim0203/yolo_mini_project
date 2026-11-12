import tensorflow as tf
import numpy as np
import base64
import io

from PIL import Image
from tensorflow.keras.applications.vgg16 import preprocess_input

model = tf.keras.models.load_model(
    "./models/vgg16_food_classifier.keras"
)


def exec_predict(request_id: int, image_type: str, image_data: str, food_score_threshold:float = 0.4):
    print(f"{request_id} / {image_type} / {len(image_data)} / {food_score_threshold}")
    # 1. Base64 문자열 디코딩
    image_data = base64.b64decode(image_data, validate=True)

    # 2. 이미지 데이터 읽기
    img = Image.open(io.BytesIO(image_data))

    # 3. 이미지 타입 검증
    allowed_types = {
        "image/jpeg": "JPEG",
        "image/png": "PNG",
        "image/webp": "WEBP"
    }

    if image_type not in allowed_types:
        raise ValueError("지원하지 않는 이미지 타입입니다.")

    # 이미지 타입이 다른경우 로그만 출력
    #if img.format != allowed_types[image_type]:
    #    raise ValueError(f"전달된 이미지 타입과 실제 이미지 형식이 다릅니다. 전달 : {image_type} => 실제 : {img.format}")
    print(f"전달된 이미지 타입과 실제 이미지 형식이 다릅니다. 전달 : {image_type} => 실제 : {img.format}")

    # 4. RGB 변환 및 크기 조정
    img = img.convert("RGB")
    img = img.resize((224, 224))

    # 5. NumPy 배열 변환
    img_array = tf.keras.utils.img_to_array(img)

    # 6. 배치 차원 추가
    img_array = np.expand_dims(img_array, axis=0)

    # 7. VGG16 전처리
    img_array = preprocess_input(img_array)

    # 8. 모델 예측
    prediction = model.predict(img_array, verbose=0)

    score = prediction[0][0]

    if score >= food_score_threshold:
        classification = "Non-Food"
    else:
        classification = "Food"

    print(f"{request_id} => {classification}, 예측값: {score:.5f}")
    print("*" * 20)

    return {
        "request_id": request_id,
        "is_food": True if classification == "Food" else False,
        "score": float(score)
    }