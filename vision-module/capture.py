import cv2
import requests
import time
from datetime import datetime
from detector import ForkliftDetector
from config import BACKEND_URL, CAMERA_INDEX, DETECTION_THRESHOLD, DISTANCE_THRESHOLD, SOURCE_ID


def send_event_to_backend(event_data: dict):
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/events",
            json=event_data,
            timeout=5
        )
        
        if response.status_code == 201:
            print(f"✓ Event sent: {event_data['type']} (severity: {event_data['severity']})")
        else:
            print(f"✗ Failed to send event: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"✗ Error sending event to backend: {e}")


def main():
    print("Initializing SafeLift-AI Vision Module...")
    
    detector = ForkliftDetector(conf_threshold=DETECTION_THRESHOLD)
    
    print(f"Opening camera (index: {CAMERA_INDEX})...")
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    if not cap.isOpened():
        print("✗ Error: Could not open camera")
        return
    
    print(f"✓ Camera opened successfully")
    print(f"✓ Backend URL: {BACKEND_URL}")
    print(f"✓ Detection threshold: {DETECTION_THRESHOLD}")
    print(f"✓ Distance threshold: {DISTANCE_THRESHOLD} pixels")
    print("\nStarting detection loop... Press 'q' to quit\n")
    
    frame_count = 0
    last_event_time = {}
    event_cooldown = 3
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("✗ Failed to read frame")
            break
        
        frame_count += 1
        
        if frame_count % 5 == 0:
            detections = detector.detect_frame(frame)
            
            risks = detector.detect_risks(detections, distance_threshold=DISTANCE_THRESHOLD)
            
            current_time = time.time()
            
            for risk in risks:
                risk_key = f"{risk['type']}_{risk['severity']}"
                
                if risk_key not in last_event_time or (current_time - last_event_time[risk_key]) > event_cooldown:
                    event_data = {
                        "type": risk["type"],
                        "severity": risk["severity"],
                        "source": SOURCE_ID,
                        "metadata": {
                            "distance_pixels": risk["distance"],
                            "person_confidence": risk["person_confidence"],
                            "forklift_confidence": risk["forklift_confidence"],
                            "person_bbox": risk["person_bbox"],
                            "forklift_bbox": risk["forklift_bbox"],
                            "frame_number": frame_count
                        }
                    }
                    
                    send_event_to_backend(event_data)
                    last_event_time[risk_key] = current_time
            
            for detection in detections:
                bbox = detection["bbox"]
                label = detection["label"]
                confidence = detection["confidence"]
                
                color = (0, 255, 0)
                if label == "person":
                    color = (255, 0, 0)
                elif label in ["forklift", "truck"]:
                    color = (0, 0, 255)
                
                cv2.rectangle(
                    frame,
                    (int(bbox["x1"]), int(bbox["y1"])),
                    (int(bbox["x2"]), int(bbox["y2"])),
                    color,
                    2
                )
                
                cv2.putText(
                    frame,
                    f"{label} {confidence:.2f}",
                    (int(bbox["x1"]), int(bbox["y1"]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2
                )
        
        cv2.putText(
            frame,
            f"Frame: {frame_count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        cv2.imshow("SafeLift-AI - Vision Module", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nShutting down...")
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✓ Vision module stopped")


if __name__ == "__main__":
    main()
