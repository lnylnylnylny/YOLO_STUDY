import os
import cv2
import albumentations as A
import numpy as np
from tqdm import tqdm
import random

# 설정
TARGET_COUNT = 2000
BASE_DIR = "garbage_training_upgrade/train"
IMAGE_DIR = os.path.join(BASE_DIR, "images")
LABEL_DIR = os.path.join(BASE_DIR, "labels")

# 클래스 이름 (확인용)
CLASS_NAMES = ["glass", "metal", "paper", "plastic", "trash"]

# Albumentations 파이프라인
transform = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.3),
    A.RandomRotate90(p=0.5),
    A.SafeRotate(limit=15, p=0.5),
    A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
    A.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=20, val_shift_limit=10, p=0.3),
    A.GaussianBlur(blur_limit=(3, 5), p=0.2),
    A.GridDistortion(p=0.2),
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

def get_counts():
    counts = {i: 0 for i in range(len(CLASS_NAMES))}
    label_files = [f for f in os.listdir(LABEL_DIR) if f.endswith('.txt')]
    for lf in label_files:
        with open(os.path.join(LABEL_DIR, lf), 'r') as f:
            for line in f:
                cls = int(line.split()[0])
                if cls in counts:
                    counts[cls] += 1
    return counts

def augment():
    counts = get_counts()
    print("초기 클래스 분포:", {CLASS_NAMES[i]: counts[i] for i in counts})
    
    needed = {i: max(0, TARGET_COUNT - counts[i]) for i in range(len(CLASS_NAMES))}
    if sum(needed.values()) == 0:
        print("이미 모든 클래스가 목표치를 달성했습니다.")
        return

    label_files = [f for f in os.listdir(LABEL_DIR) if f.endswith('.txt') and not f.startswith('aug_')]
    random.shuffle(label_files)

    pbar = tqdm(total=sum(needed.values()), desc="데이터 증강 중")
    
    aug_id = 0
    while sum(needed.values()) > 0:
        for lf in label_files:
            if sum(needed.values()) <= 0:
                break
                
            label_path = os.path.join(LABEL_DIR, lf)
            image_name = lf.replace('.txt', '.jpg')
            image_path = os.path.join(IMAGE_DIR, image_name)
            
            if not os.path.exists(image_path):
                # .png 등 다른 확장자 체크
                image_name = lf.replace('.txt', '.png')
                image_path = os.path.join(IMAGE_DIR, image_name)
                if not os.path.exists(image_path):
                    continue

            # 이 파일에 포함된 클래스 확인
            file_classes = set()
            bboxes = []
            class_labels = []
            with open(label_path, 'r') as f:
                for line in f:
                    parts = line.split()
                    cls = int(parts[0])
                    file_classes.add(cls)
                    bboxes.append([float(x) for x in parts[1:]])
                    class_labels.append(cls)

            # 증강이 필요한 클래스가 포함되어 있는지 확인
            if not any(needed.get(c, 0) > 0 for c in file_classes):
                continue

            # 이미지 로드
            image = cv2.imread(image_path)
            if image is None:
                continue
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # 증강 수행
            try:
                augmented = transform(image=image, bboxes=bboxes, class_labels=class_labels)
            except Exception as e:
                print(f"Error augmenting {image_path}: {e}")
                continue
                
            aug_image = augmented['image']
            aug_bboxes = augmented['bboxes']
            aug_class_labels = augmented['class_labels']

            if len(aug_bboxes) == 0 and len(bboxes) > 0:
                continue # 객체가 사라진 경우 건너뜀

            # 결과 저장
            new_name = f"aug_{aug_id}_{image_name}"
            new_label_name = f"aug_{aug_id}_{lf}"
            
            cv2.imwrite(os.path.join(IMAGE_DIR, new_name), cv2.cvtColor(aug_image, cv2.COLOR_RGB2BGR))
            
            with open(os.path.join(LABEL_DIR, new_label_name), 'w') as f:
                for bbox, cls in zip(aug_bboxes, aug_class_labels):
                    f.write(f"{cls} {' '.join([f'{x:.6f}' for x in bbox])}\n")
                    if needed.get(cls, 0) > 0:
                        needed[cls] -= 1
                        pbar.update(1)
            
            aug_id += 1
            
            if sum(needed.values()) <= 0:
                break

    pbar.close()
    final_counts = get_counts()
    print("최종 클래스 분포:", {CLASS_NAMES[i]: final_counts[i] for i in final_counts})

if __name__ == "__main__":
    augment()
