import torch
from torchvision import models, transforms
from ultralytics import YOLO
from PIL import Image
import os
import urllib.request

# --- CONFIGURATION ---
# Using YOLO11 Large as discussed
YOLO_MODEL_NAME = 'yolov8l.pt' 
LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
LABELS_FILE = "imagenet_classes.txt"

class PerceptionEngine:
    def __init__(self):
        print("Loading Perception Models...")
        
        # 1. Load Object Detector (YOLO)
        self.yolo_model = YOLO(YOLO_MODEL_NAME)
        
        # 2. Load Scene Classifier (ResNet50)
        self.scene_model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        self.scene_model.eval()

        # 3. Define Image Transforms
        self.scene_transforms = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        # 4. Load Scene Labels (Download if missing)
        self.scene_labels = self._load_labels()
        print("Models and Labels Loaded Successfully.")

    def _load_labels(self):
        """Helper to download and read ImageNet labels."""
        if not os.path.exists(LABELS_FILE):
            print(f"Downloading scene labels to {LABELS_FILE}...")
            try:
                urllib.request.urlretrieve(LABELS_URL, LABELS_FILE)
            except Exception as e:
                print(f"Warning: Could not download labels. {e}")
                return []
        
        with open(LABELS_FILE, "r") as f:
            categories = [s.strip() for s in f.readlines()]
        return categories

    def detect_objects(self, image: Image.Image):
        """
        Returns a list of detected objects with bounding boxes.
        """
        # Run YOLO inference
        results = self.yolo_model(image, verbose=False) 
        detections = []
        
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                class_id = int(box.cls[0])
                label = self.yolo_model.names[class_id]
                conf = float(box.conf[0])
                
                detections.append({
                    "label": label,
                    "box": [int(x1), int(y1), int(x2), int(y2)],
                    "confidence": round(conf, 2)
                })
        
        return detections

    def classify_scene(self, image: Image.Image):
        """
        Returns the top predicted scene label.
        """
        input_tensor = self.scene_transforms(image).unsqueeze(0)
        
        with torch.no_grad():
            output = self.scene_model(input_tensor)
            
        _, predicted_idx = torch.max(output, 1)
        idx = predicted_idx.item()
        
        # Return text label if available, else ID
        if self.scene_labels and idx < len(self.scene_labels):
            return self.scene_labels[idx]
        return f"Class_ID_{idx}"

# --- TEST BLOCK ---
if __name__ == "__main__":
    print("Testing Perception Engine...")
    try:
        engine = PerceptionEngine()
        
        # Create a dummy image for testing
        dummy_img = Image.new('RGB', (640, 640), color='white')
        
        print("Running detection...")
        objects = engine.detect_objects(dummy_img)
        scene = engine.classify_scene(dummy_img)
        
        print(f"Success! System detected {len(objects)} objects.")
        print(f"Scene Classification Result: {scene}")
        
    except Exception as e:
        print(f"Error occurred: {e}")