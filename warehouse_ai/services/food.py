import tensorflow as tf
import numpy as np
import base64
import io

from PIL import Image
from tensorflow.keras.applications.vgg16 import preprocess_input

CLASS_NAMES = [
    "fruit_vegetable",
    "sea_food",
    "meat",
    "grain_nut_legume",
    "dairy",
    "etc"
]

food_model = tf.keras.models.load_model(
    "./models/vgg16_food_classifier.keras"
)


item_model = tf.keras.models.load_model(
    "./models/vgg16_item_classifier.keras",
    custom_objects={
        "preprocess_input": preprocess_input
    }
)

def exec_predict(request_id: int, image_type: str, image_data: str, food_score_threshold:float = 0.4):
    print(f"{request_id} / {image_type} / {len(image_data)} / {food_score_threshold}")
    if food_score_threshold is None:
        food_score_threshold= 0.4
        print("set food_score_threshold 0.4")

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
    food_prediction = food_model.predict(img_array, verbose=0)

    score = food_prediction[0][0]

    print(f"{request_id}, 예측값: {score:.5f}")

    dic_item_score = {}  # 또는 dict() 사용

    if score >= food_score_threshold:
        classification = "Non-Food"
    else:
        classification = "Food"

        item_prediction = item_model.predict(img_array)
        item_score = item_prediction[0][0]
    
        print(f"{request_id} => 예측값:{item_score:.5f}")
        class_idx = np.argmax(item_prediction[0])

        for index, temp in enumerate(item_prediction[0]):
            print(f"\t{CLASS_NAMES[index]} {float(temp) * 100:.2f}%")
            dic_item_score[CLASS_NAMES[index]] = float(temp)
    
        print("\t예측 클래스:", CLASS_NAMES[class_idx])
        print("\t예측 확률:", item_prediction[0][class_idx])

    
    print("*" * 20)

    return {
        "request_id": request_id,
        "is_food": True if classification == "Food" else False,
        "score": float(score),
        "classification_result": dic_item_score
    }