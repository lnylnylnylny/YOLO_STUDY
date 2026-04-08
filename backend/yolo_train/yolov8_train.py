"""
YOLOv8m 쓰레기 분류 학습 스크립트
- 모델: yolov8m (medium)
- 데이터셋: garbage_training (10 classes)
- 디스코드 알림: 10% 진행마다 + 시작/완료 시 전송
"""

import json
import time
from urllib.request import Request, urlopen
from ultralytics import YOLO

# 디스코드 웹훅 URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1489638619575750656/SoDDRCVcUixDtN_ogRKcfBaNstoobBB6IkeN9WMT5O09HbFjZhIl4VdhCqrrK6TMM3SO"


def send_discord(message):
    """디스코드 웹훅으로 메시지를 전송합니다."""
    data = {"content": message}
    req = Request(
        WEBHOOK_URL,
        data=json.dumps(data).encode(),
        headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"},
    )
    try:
        with urlopen(req) as res:
            pass
    except Exception as e:
        print(f"디스코드 전송 에러: {e}")


def main():
    # 설정
    total_epochs = 100
    notify_interval = 10  # 10% 마다 알림

    # 알림 전송 완료 추적
    notified_milestones = set()

    # 사전 학습된 YOLOv8m 모델 로드
    model = YOLO("yolov8m.pt")

    # === 콜백 등록 ===
    def on_train_epoch_end(trainer):
        """매 에폭 종료 시 호출되는 콜백"""
        current_epoch = trainer.epoch + 1  # 0-indexed → 1-indexed
        progress_pct = int((current_epoch / total_epochs) * 100)

        milestone = (progress_pct // notify_interval) * notify_interval
        if milestone > 0 and milestone < 100 and milestone not in notified_milestones:
            notified_milestones.add(milestone)

            loss_items = trainer.label_loss_items(trainer.tloss)
            box_loss = loss_items.get("train/box_loss", "N/A")
            cls_loss = loss_items.get("train/cls_loss", "N/A")
            
            metrics = trainer.metrics
            map50 = metrics.get("metrics/mAP50(B)", "N/A")
            map50_95 = metrics.get("metrics/mAP50-95(B)", "N/A")

            box_str = f"{float(box_loss):.4f}" if isinstance(box_loss, (float, int)) or (hasattr(box_loss, "item") and isinstance(box_loss.item(), float)) else str(box_loss)
            cls_str = f"{float(cls_loss):.4f}" if isinstance(cls_loss, (float, int)) or (hasattr(cls_loss, "item") and isinstance(cls_loss.item(), float)) else str(cls_loss)
            map50_str = f"{float(map50):.4f}" if isinstance(map50, (float, int)) else str(map50)
            map95_str = f"{float(map50_95):.4f}" if isinstance(map50_95, (float, int)) else str(map50_95)

            msg = (
                f"📊 **학습 진행: {milestone}%** ({current_epoch}/{total_epochs} 에폭)\n"
                f"```\n"
                f"Box Loss  : {box_str}\n"
                f"Cls Loss  : {cls_str}\n"
                f"mAP50     : {map50_str}\n"
                f"mAP50-95  : {map95_str}\n"
                f"```"
            )
            send_discord(msg)

    model.add_callback("on_train_epoch_end", on_train_epoch_end)

    # === 학습 시작 알림 ===
    send_discord(
        f"🚀 **YOLOv8m 학습 시작!**\n"
        f"```\n"
        f"모델       : yolov8m\n"
        f"데이터셋   : garbage (10 classes)\n"
        f"에폭       : {total_epochs}\n"
        f"배치       : 32\n"
        f"이미지 크기: 640\n"
        f"```\n"
        f"📢 {notify_interval}% 단위로 진행 알림을 보내드립니다."
    )

    # === 학습 실행 ===
    start_time = time.time()

    results = model.train(
        data="/home/work/seongjun/seongjun/YOLO_train/garbage_training/data.yaml",
        epochs=total_epochs,
        batch=32,               
        imgsz=640,
        device=0,               
        workers=4,              
        patience=20,            
        save=True,              
        save_period=10,         
        project="runs/detect",      
        name="garbage_yolov8m",     
        exist_ok=True,          
        pretrained=True,        
        optimizer="Adam",        
        lr0=1e-4,               
        lrf=0.01,               
        cos_lr=True,            
        amp=False,              
        verbose=True,
    )

    elapsed = time.time() - start_time
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)

    # === 학습 완료 후 검증 ===
    best_model = YOLO("runs/detect/garbage_yolov8m/weights/best.pt")
    metrics = best_model.val()

    # === 완료 알림 ===
    send_discord(
        f"✅ **YOLOv8m 학습 완료!**\n"
        f"```\n"
        f"소요 시간  : {int(hours)}h {int(minutes)}m {int(seconds)}s\n"
        f"mAP50      : {metrics.box.map50:.4f}\n"
        f"mAP50-95   : {metrics.box.map:.4f}\n"
        f"Best 모델  : runs/detect/garbage_yolov8m/weights/best.pt\n"
        f"```"
    )

    print("\n" + "=" * 50)
    print("학습 완료!")
    print(f"소요 시간: {int(hours)}h {int(minutes)}m {int(seconds)}s")
    print(f"mAP50:    {metrics.box.map50:.4f}")
    print(f"mAP50-95: {metrics.box.map:.4f}")
    print(f"Best 모델: runs/detect/garbage_yolov8m/weights/best.pt")
    print("=" * 50)


if __name__ == "__main__":
    main()
