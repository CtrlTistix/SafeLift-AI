from ultralytics import YOLO
import numpy as np
from typing import List, Tuple, Dict
import os


class ForkliftDetector:
    def __init__(self, model_path: str = "models/yolov8n.pt", conf_threshold: float = 0.5):
        self.conf_threshold = conf_threshold
        
        if not os.path.exists(model_path):
            print(f"Model not found at {model_path}. Downloading YOLOv8n...")
            self.model = YOLO("yolov8n.pt")
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            self.model.save(model_path)
        else:
            self.model = YOLO(model_path)
        
        self.forklift_classes = ["forklift", "truck"]
        self.person_class = "person"

    def detect_frame(self, frame: np.ndarray) -> List[Dict]:
        results = self.model(frame, conf=self.conf_threshold, verbose=False)
        
        detections = []
        
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                confidence = float(box.conf[0])
                
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                detection = {
                    "label": class_name,
                    "confidence": confidence,
                    "bbox": {
                        "x1": float(x1),
                        "y1": float(y1),
                        "x2": float(x2),
                        "y2": float(y2)
                    },
                    "center": {
                        "x": float((x1 + x2) / 2),
                        "y": float((y1 + y2) / 2)
                    }
                }
                
                detections.append(detection)
        
        return detections

    def calculate_distance(self, bbox1: Dict, bbox2: Dict) -> float:
        center1 = bbox1["center"]
        center2 = bbox2["center"]
        
        dx = center1["x"] - center2["x"]
        dy = center1["y"] - center2["y"]
        
        return np.sqrt(dx**2 + dy**2)

    def detect_risks(self, detections: List[Dict], distance_threshold: float = 200) -> List[Dict]:
        risks = []
        
        people = [d for d in detections if d["label"] == self.person_class]
        forklifts = [d for d in detections if d["label"] in self.forklift_classes]
        
        for person in people:
            for forklift in forklifts:
                distance = self.calculate_distance(person["bbox"], forklift["bbox"])
                
                if distance < distance_threshold:
                    severity = 5 if distance < 100 else 4 if distance < 150 else 3
                    
                    risk = {
                        "type": "person_near_forklift",
                        "severity": severity,
                        "distance": distance,
                        "person_confidence": person["confidence"],
                        "forklift_confidence": forklift["confidence"],
                        "person_bbox": person["bbox"],
                        "forklift_bbox": forklift["bbox"]
                    }
                    
                    risks.append(risk)
        
        return risks
