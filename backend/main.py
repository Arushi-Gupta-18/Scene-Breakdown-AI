from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import io
import base64
from PIL import Image, ImageDraw, ImageFont

# Import our custom modules
from perception import PerceptionEngine
from spatial import SpatialAnalyzer
from llm_interface import LLMInterface

# Initialize App
app = FastAPI(title="Intelligent Scene Breakdown")

# Enable CORS (Allows React to talk to this Python server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your React URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Models (Load them once on startup)
print("Initializing System Modules...")
perception = PerceptionEngine()
spatial = SpatialAnalyzer()
llm = LLMInterface() # API Key loads from .env automatically
print("System Ready.")

def draw_boxes(image: Image.Image, detections: list):
    """
    Draws bounding boxes and labels on the image.
    Returns the image converted to Base64 string.
    """
    draw = ImageDraw.Draw(image)
    
    # Try to load a font, fallback to default if fails
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    for obj in detections:
        box = obj['box']
        label = f"{obj['label']} {obj['confidence']}"
        
        # Draw Box (Red, width 3)
        draw.rectangle(box, outline="red", width=3)
        
        # Draw Label Background
        text_bbox = draw.textbbox((box[0], box[1]), label, font=font)
        draw.rectangle(text_bbox, fill="red")
        
        # Draw Text (White)
        draw.text((box[0], box[1]), label, fill="white", font=font)

    # Convert to Base64 for Frontend
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

@app.post("/analyze")
async def analyze_scene(file: UploadFile = File(...)):
    """
    Main Endpoint: Upload image -> Get Analysis + Labeled Image
    """
    try:
        # 1. Read Image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        original_width, original_height = image.size

        # 2. Run Perception
        detections = perception.detect_objects(image)
        scene_type = perception.classify_scene(image)

        # 3. Run Spatial Analysis
        spatial_relationships = spatial.analyze_relationships(detections, original_width, original_height)

        # 4. Run Gemini Narrative
        narrative = llm.generate_narrative(scene_type, detections, spatial_relationships)

        # 5. Draw Boxes & Prepare Image
        labeled_image_base64 = draw_boxes(image.copy(), detections)

        # 6. Return JSON Response
        return JSONResponse(content={
            "status": "success",
            "scene_type": scene_type,
            "narrative": narrative,
            "object_count": len(detections),
            "spatial_data": spatial_relationships,
            "image_data": f"data:image/jpeg;base64,{labeled_image_base64}"
        })

    except Exception as e:
        print(f"Server Error: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

if __name__ == "__main__":
    # Start the Server
    uvicorn.run(app, host="127.0.0.1", port=8000)