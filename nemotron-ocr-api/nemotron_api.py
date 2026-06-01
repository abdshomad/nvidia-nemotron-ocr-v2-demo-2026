import base64
import io
import os
import sys
import logging
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("nemotron-api")

# Add nemotron-ocr-v2 folder to path to import app.py and nemotron_ocr
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nemotron-ocr-v2"))

# Monkey-patch Gradio launch method to be a no-op before importing app
import gradio as gr
logger.info("Mocking gr.Blocks.launch to prevent app.py from blocking...")
gr.Blocks.launch = lambda *args, **kwargs: logger.info("gr.Blocks.launch was mocked and skipped successfully.")

try:
    import nemotron_ocr
except ImportError:
    import subprocess
    logger.info("Installing nemotron_ocr wheel...")
    wheel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nemotron-ocr-v2/nemotron_ocr-1.0.0-cp312-cp312-linux_x86_64.whl")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-deps", wheel_path])

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import numpy as np

from nemotron_ocr.inference.pipeline_v2 import NemotronOCRV2
from app import _get_pipeline, draw_boxes, space_layout, format_text, MODELS

app = FastAPI(title="Nemotron OCR v2 API")

# Enable CORS for Next.js app communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OCRRequest(BaseModel):
    file: str  # Base64 string of the image (can contain data URI prefix or be raw base64)
    model: Optional[str] = "Multilingual (en, zh, ja, ko, ru, …)"
    merge_level: Optional[str] = "layout"

def decode_base64_image(b64_str: str) -> Image.Image:
    if "," in b64_str:
        b64_str = b64_str.split(",")[1]
    img_data = base64.b64decode(b64_str)
    return Image.open(io.BytesIO(img_data)).convert("RGB")

def encode_image_to_base64_data_url(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_str}"

@app.post("/layout-parsing")
async def layout_parsing(req: OCRRequest):
    try:
        logger.info(f"Received OCR request - Model: {req.model}, Output Mode: {req.merge_level}")
        
        # 1. Decode image
        image = decode_base64_image(req.file)
        
        # 2. Get the appropriate model name matching app.py KEYS
        model_name = req.model
        if model_name not in MODELS:
            # Fallback mappings if short name is passed
            if model_name == "multi":
                model_name = "Multilingual (en, zh, ja, ko, ru, …)"
            elif model_name == "en":
                model_name = "English-only"
            elif model_name == "v1":
                model_name = "v1 (legacy, English-only)"
            else:
                model_name = "Multilingual (en, zh, ja, ko, ru, …)"
                
        lang_key = MODELS[model_name]
        ocr = _get_pipeline(lang_key)
        img_array = np.array(image)
        
        # 3. Perform OCR
        merge_level = req.merge_level
        if merge_level not in ["layout", "word", "sentence", "paragraph"]:
            merge_level = "layout"
            
        if merge_level == "layout":
            words = ocr(img_array, merge_level="word")
            annotated = draw_boxes(image, words)
            result_text = space_layout(words)
        else:
            display_preds = ocr(img_array, merge_level=merge_level)
            annotated = draw_boxes(image, display_preds)
            result_text = format_text(display_preds, merge_level)
            
        # 4. Convert output image to base64
        annotated_b64 = encode_image_to_base64_data_url(annotated)
        
        # 5. Build response structure compatible with NextJS page.tsx
        return {
            "errorCode": 0,
            "errorMsg": "",
            "result": {
                "layoutParsingResults": [
                    {
                        "markdown": {
                            "text": result_text
                        },
                        "outputImages": {
                            "visualization": annotated_b64
                        }
                    }
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error processing OCR request: {e}", exc_info=True)
        return {
            "errorCode": 1,
            "errorMsg": str(e),
            "result": {}
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
