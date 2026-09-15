import os
import cv2
import mediapipe as mp
from pathlib import Path

def extract_golden_frame():
    # Настраиваем пути с помощью Pathlib
    BASE_DIR = Path(__file__).resolve().parent.parent
    video_dir = BASE_DIR / "media" / "videos"
    output_dir = BASE_DIR / "media" / "thumbnails"
    
    # Создаем папку для превью, если её нет
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Находим самое последнее загруженное видео
    videos = list(video_dir.glob("*.*"))
    if not videos:
        print("❌ Видео для обработки не найдены в media/videos/")
        return
    
    video_path = max(videos, key=os.path.getmtime)
    print(f"🎬 Анализирую файл: {video_path.name}")
    
    # Инициализируем MediaPipe Face Detection
    mp_face_detection = mp.solutions.face_detection
    
    cap = cv2.VideoCapture(str(video_path))
    best_frame = None
    max_confidence = 0.0
    
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Переводим кадр в RGB для нейросети
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(rgb_frame)
            
            # Если лицо найдено, проверяем уверенность нейросети (четкость)
            if results.detections:
                for detection in results.detections:
                    confidence = detection.score[0]
                    if confidence > max_confidence:
                        max_confidence = confidence
                        best_frame = frame.copy()
                        
        cap.release()
        
    # Сохраняем лучший результат
    if best_frame is not None:
        output_path = output_dir / f"golden_{video_path.stem}.jpg"
        cv2.imwrite(str(output_path), best_frame)
        print(f"🎯 УСПЕХ: 'Золотой Кадр' вырезан! Уверенность: {max_confidence:.2f}")
        print(f"📂 Сохранено в: media/thumbnails/{output_path.name}")
    else:
        print("⚠️ Лицо на видео не распознано. Проверь освещение или ракурс.")

if __name__ == "__main__":
    extract_golden_frame()
