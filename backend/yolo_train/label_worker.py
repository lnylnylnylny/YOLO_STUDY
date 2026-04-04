import os
import sys
import torch
import cv2
import transformers
from transformers.models.bert.modeling_bert import BertModel
from autodistill_grounding_dino import GroundingDINO
from autodistill.detection import CaptionOntology

def patched_get_head_mask(self, head_mask, num_hidden_layers, is_attention_chunked=False):
    return [None] * num_hidden_layers
BertModel.get_head_mask = patched_get_head_mask

def patched_get_extended_attention_mask(self, attention_mask, input_shape, device=None, dtype=None):
    if not isinstance(dtype, torch.dtype) and (isinstance(dtype, torch.device) or isinstance(dtype, str)):
        device, dtype = dtype, None
    if dtype is None: dtype = self.dtype
    if attention_mask.dim() == 3: extended_attention_mask = attention_mask[:, None, :, :]
    elif attention_mask.dim() == 2: extended_attention_mask = attention_mask[:, None, None, :]
    extended_attention_mask = extended_attention_mask.to(dtype=dtype)
    extended_attention_mask = (1.0 - extended_attention_mask) * torch.finfo(dtype).min
    return extended_attention_mask
BertModel.get_extended_attention_mask = patched_get_extended_attention_mask

# 클래스 설정
CLASS_NAMES = [
    "battery", "biological", "cardboard", "clothes", "glass", 
    "metal", "paper", "plastic", "shoes", "trash"
]

def main():
    if len(sys.argv) < 3:
        print("Usage: uv run label_worker.py [input_dir] [output_dir]")
        return

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    # YOLO 학습 구조 생성
    img_out_dir = os.path.join(output_dir, "train", "images")
    lbl_out_dir = os.path.join(output_dir, "train", "labels")
    os.makedirs(img_out_dir, exist_ok=True)
    os.makedirs(lbl_out_dir, exist_ok=True)

    print(f"🚀 라벨링 시작: {input_dir} -> {output_dir}")
    print(f"🖥️ 사용 중인 장치: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")

    # 이미지 목록 스캔
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    total_files = len(image_files)

    for idx, img_name in enumerate(image_files):
        # 파일명에서 클래스 추출 (예: battery_1.jpg -> battery)
        try:
            target_class = img_name.split('_')[0].lower()
            if target_class not in CLASS_NAMES:
                continue
        except:
            continue

        img_path = os.path.join(input_dir, img_name)
        
        # 해당 클래스만 찾도록 온톨로지 설정 (박스 문턱값 0.5 권장)
        ontology = CaptionOntology({target_class: target_class})
        base_model = GroundingDINO(ontology=ontology, box_threshold=0.5)

        try:
            # 추론 실행
            detections = base_model.predict(img_path)
            
            if len(detections.xyxy) > 0:
                # 1. 이미지 복사 (학습 폴더로)
                img = cv2.imread(img_path)
                cv2.imwrite(os.path.join(img_out_dir, img_name), img)
                
                # 2. YOLO .txt 라벨 저장
                h, w, _ = img.shape
                txt_name = os.path.splitext(img_name)[0] + ".txt"
                
                with open(os.path.join(lbl_out_dir, txt_name), "w") as f:
                    for i in range(len(detections.xyxy)):
                        # 중요: 전체 리스트에서의 인덱스를 ID로 저장
                        full_class_id = CLASS_NAMES.index(target_class)
                        x1, y1, x2, y2 = detections.xyxy[i]
                        
                        # 정규화 좌표 계산
                        x_c = ((x1 + x2) / 2) / w
                        y_c = ((y1 + y2) / 2) / h
                        bw = (x2 - x1) / w
                        bh = (y2 - y1) / h
                        
                        f.write(f"{full_class_id} {x_c:.6f} {y_c:.6f} {bw:.6f} {bh:.6f}\n")
            
            # 진행 상황 출력
            if (idx + 1) % 10 == 0 or (idx + 1) == total_files:
                print(f" 진행 중: [{idx + 1}/{total_files}] ({(idx + 1)/total_files*100:.1f}%)")

        except Exception as e:
            print(f"❌ 에러 발생 ({img_name}): {e}")

    print(f"✨ {input_dir} 작업 완료!")

if __name__ == "__main__":
    main()