import math

class SpatialAnalyzer:
    def __init__(self):
        pass

    def _get_center(self, box):
        x1, y1, x2, y2 = box
        return (x1 + x2) / 2, (y1 + y2) / 2

    def _get_area(self, box):
        return (box[2] - box[0]) * (box[3] - box[1])

    def _calculate_iou(self, box1, box2):
        x_left = max(box1[0], box2[0])
        y_top = max(box1[1], box2[1])
        x_right = min(box1[2], box2[2])
        y_bottom = min(box1[3], box2[3])

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        box1_area = self._get_area(box1)
        box2_area = self._get_area(box2)
        
        union_area = box1_area + box2_area - intersection_area
        if union_area == 0: return 0
        return intersection_area / union_area

    def analyze_relationships(self, detections, image_width, image_height):
        relationships = []
        num_objects = len(detections)
        
        # 1. General Scene Layout (Only major objects)
        # We define "major" as taking up significant space or being central
        for obj in detections:
            box = obj['box']
            area_pct = self._get_area(box) / (image_width * image_height)
            if area_pct > 0.10: # Only describe position if object is > 10% of image
                cx, _ = self._get_center(box)
                h_pos = "left" if cx < image_width/3 else "right" if cx > 2*image_width/3 else "center"
                relationships.append(f"A large {obj['label']} is dominated the {h_pos} side.")

        # 2. Smart Pairwise Analysis
        # Store significant pairs to sort by distance later
        significant_pairs = []

        for i in range(num_objects):
            for j in range(i + 1, num_objects): # i+1 ensures we don't check A vs A or B vs A
                obj_a = detections[i]
                obj_b = detections[j]
                
                # Skip if both are the same label and far apart (e.g. two distant cars)
                # But keep them if they are different (e.g. Person vs Car)
                
                dist = math.dist(self._get_center(obj_a['box']), self._get_center(obj_b['box']))
                
                # dynamic threshold: 15% of image width
                threshold = image_width * 0.15 
                
                if dist < threshold:
                    # Check for overlap
                    iou = self._calculate_iou(obj_a['box'], obj_b['box'])
                    type_rel = "close to"
                    if iou > 0.05: type_rel = "overlapping/interacting with"
                    
                    significant_pairs.append({
                        "text": f"The {obj_a['label']} is {type_rel} the {obj_b['label']}.",
                        "score": dist - (iou * 1000) # Prefer high overlap, low distance
                    })

        # 3. Sort and Filter
        # Sort by "importance" (closest/most overlapping first)
        significant_pairs.sort(key=lambda x: x['score'])
        
        # Keep only top 15 interesting relationships to avoid flooding the LLM
        for item in significant_pairs[:15]:
            relationships.append(item['text'])

        return relationships