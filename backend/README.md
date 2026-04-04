# Garbage YOLO Backend

FastAPI 기반의 쓰레기 분류 모델(YOLOv8) 추론 API 서버입니다.

## 🚀 시작하기

이 프로젝트는 패키지 관리자로 `uv`를 사용합니다.

### 1. 패키지 설치

아래 명령어를 통해 파이썬 환경 및 필요한 패키지들을 다운로드하고 동기화합니다.

```bash
uv sync
```

### 2. 서버 실행

아래 명령어를 통해 FastAPI 서버를 실행합니다.
**(※ 주의: 처음 실행할 때는 모델을 불러오고 환경을 구성하느라 시간이 다소 오래 걸릴 수 있습니다.)**

```bash
uv run main.py
```

서버가 정상적으로 켜지면 `http://0.0.0.0:8000` 주소에서 대기 상태로 진입합니다.

---

## 📖 API 문서 및 테스트 (Swagger UI)

서버가 실행된 상태에서, 웹 브라우저를 열고 아래 주소로 접속하면 API를 테스트해볼 수 있는 공식 문서(Swagger) 페이지가 나타납니다.

👉 **Swagger 주소:** [http://localhost:8000/docs](http://localhost:8000/docs)

이 페이지에서 직접 이미지를 업로드하여 API 요청(`POST /predict`)을 보내볼 수 있으며, 바운딩 박스 결과와 베이스64(Base64)로 인코딩된 출력 이미지를 곧바로 확인하실 수 있습니다.

---

## 📡 주요 API 엔드포인트

### `POST /predict`

- **설명**: 이미지를 업로드받아 쓰레기 객체를 탐지하고, 객체의 정보(클래스, 정확도, Bounding Box 좌표)와 바운딩 박스가 렌더링된 이미지(Base64)를 JSON 형태로 반환합니다.
- **Content-Type**: `multipart/form-data`
- **요청(Request)**:
  - `file`: (필수) 사진/이미지 파일
- **응답(Response) 예시**:

```json
{
  "detections": [
    {
      "class_name": "plastic",
      "class_id": 1,
      "confidence": 0.98,
      "bbox": {
        "x_min": 10.0,
        "y_min": 20.0,
        "x_max": 200.0,
        "y_max": 180.0
      }
    }
  ],
  "image_base64": "/9j/4AAQSkZJRgABAQ..."
}
```

- **Front-end 응답 활용 팁**: 응답으로 받은 엄청 긴 `image_base64` 문자열은 프론트엔드 측에서 아래처럼 작성하면 별도로 이미지를 저장/다운로드 할 필요 없이 바로 화면에 띄울 수 있습니다.

```html
<img src="data:image/jpeg;base64,여기에_받아온_문자열_그대로_삽입" />
```
