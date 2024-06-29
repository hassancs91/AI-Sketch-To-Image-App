import base64
from io import BytesIO
import requests
import io
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')
OPEN_AI_API_KEY = os.getenv('OPEN_AI_API_KEY')

vision_model_prompt = """Describe this sketch, 
focusing on the main elements and their arrangements.
 Provide a description that could be used as a prompt
   for an Stabe Diffusion AI to recreate this sketch as a
     realistic image. the prompt should be max 3-4 sentences."""


def generate_realistic_image(sketch_image, prompt):
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
    sketch_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    response = requests.post(
        "https://api.stability.ai/v2beta/stable-image/control/sketch",
        headers={
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Accept": "image/*"
        },
        files={
            "image": img_byte_arr
        },
        data={
            "prompt": prompt,
            "control_strength": 0.7,
            "output_format": "webp"
        },
    )

    if response.status_code == 200:
        return response.content
    else:
        raise Exception(str(response.json()))

def get_image_description(image):
    # Convert PIL Image to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Prepare the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPEN_AI_API_KEY}"
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": vision_model_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_str}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    # Make the API call
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        description = response.json()['choices'][0]['message']['content']
        return description.strip()
    else:
        raise Exception(f"Error in API call: {response.text}")