import os
import cv2
import numpy as np
import base64
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from ultralytics import YOLO

app = FastAPI(title="Garbage YOLO API")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "yolo_train/garbage_yolo.pt")

model = None
try:
    if os.path.exists(MODEL_PATH):
        print(f"Loading model from {MODEL_PATH}")
        model = YOLO(MODEL_PATH)
    else:
        print(f"Warning: Model file not found at {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {e}")

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    if model is None:
        return JSONResponse(status_code=500, content={"error": "Model not loaded properly on the server."})
    
    contents = await file.read()
    
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return JSONResponse(status_code=400, content={"error": "Could not decode the provided image file."})
    
    results = model(img)
    
    detections = []
    
    res = results[0]
    boxes = res.boxes
    names = model.names
    
    for box in boxes:
        xyxy = box.xyxy[0].tolist() 
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        cls_name = names[cls_id]
        
        detections.append({
            "class_name": cls_name,
            "class_id": cls_id,
            "confidence": conf,
            "bbox": {
                "x_min": xyxy[0],
                "y_min": xyxy[1],
                "x_max": xyxy[2],
                "y_max": xyxy[3]
            }
        })
        
    annotated_img = res.plot()
    
    _, buffer = cv2.imencode(".jpg", annotated_img)
    
    img_base64 = base64.b64encode(buffer).decode("utf-8")
    
    return {
        "detections": detections,
        "image_base64": img_base64
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
