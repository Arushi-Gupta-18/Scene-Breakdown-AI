import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMInterface:
    def __init__(self):
        # Fetch key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file!")
            
        # Configure the library
        genai.configure(api_key=api_key)
        
        # Using Gemini 1.5 Pro
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def generate_narrative(self, scene_type, detections, spatial_analysis):
        """
        Sends structured data to Gemini to get a human-like description.
        """
        
        # 1. Format object list
        obj_summary = ", ".join([f"{d['label']} ({d['confidence']:.2f} conf)" for d in detections])
        if not obj_summary:
            obj_summary = "No specific objects detected."
        
        # 2. Format spatial details
        spatial_summary = "\n".join(["- " + s for s in spatial_analysis])
        if not spatial_summary:
            spatial_summary = "- No specific spatial relationships observed."
        
        # 3. Construct the Prompt
        prompt = f"""
        You are an intelligent vision assistant. I will provide you with data derived from an image. 
        Your job is to synthesize this information into a clear, natural, and descriptive paragraph 
        summarizing the scene. 

        DATA:
        - **Overall Scene Type:** {scene_type}
        - **Detected Objects:** {obj_summary}
        - **Spatial Relationships & Events:**
        {spatial_summary}

        INSTRUCTIONS:
        - Start by setting the scene.
        - Describe the main objects and their positions/interactions.
        - Infer the context (e.g., "A person near a dog in a park implies walking the dog").
        - Keep it concise (2-3 sentences).
        """

        try:
            # 4. Generate Content
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"LLM Error: {str(e)}"

# --- TEST BLOCK ---
if __name__ == "__main__":
    print("Testing Gemini Interface (using .env)...")
    
    try:
        # Initialize (Key is loaded automatically now)
        llm = LLMInterface()
        
        # Dummy Data
        scene = "Park / Outdoors"
        objs = [{'label': 'person', 'confidence': 0.9}, {'label': 'dog', 'confidence': 0.85}]
        spatial = [
            "A person is located at the center.", 
            "A dog is to the right of the person.",
            "The person is very close to the dog."
        ]
        
        print("Sending prompt to Gemini...")
        result = llm.generate_narrative(scene, objs, spatial)
        
        print("\n--- Gemini Output ---")
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")