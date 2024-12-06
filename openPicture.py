from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Fetch the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Function to generate an image using DALL·E 3
def generate_image(prompt):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_API_KEY}'
        }

        data = {
            "model": "dall-e-3",
            'prompt': prompt,
            'n': 1,  # Number of images to generate
            'size': '1024x1024'  # Image size
        }

        # Make POST request to OpenAI API
        response = requests.post('https://api.openai.com/v1/images/generations', headers=headers, json=data)

        # Check if the response is successful
        if response.status_code == 200:
            image_url = response.json()['data'][0]['url']
            return image_url
        else:
            error_message = response.json().get('error', {}).get('message', 'Unknown error')
            print(f"Error from API: {error_message}")
            return None

    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def refine_prompt(user_input):
    # Predefined structure for DALL·E 3 image generation with enhanced instructions
    refined_prompt = (
        f"Design an eye-catching, modern social media advertisement poster for a product. "
        f"Brand Name: '{user_input.get('Brand Name', 'a premium brand')}' should be very visible and stand out. "
        f"Product Description: '{user_input.get('Product Description', 'an innovative product')}', emphasizing the product’s unique features. "
        "Generate a compelling, catchy tagline that appeals to the audience and aligns with the brand's voice. "
        "The ad should feature a clean, minimalistic layout with balanced colors and typography that conveys professionalism and high quality. "
        "Ensure the design is engaging, with the brand name prominently displayed, the tagline capturing attention, and the overall style modern and visually striking."
    )
    return refined_prompt

@app.route('/generate_poster', methods=['POST'])
def generate_poster_route():
    # Get the user input from the request body
    data = request.json
    
    # Check if required fields are provided
    required_fields = ['Product Description', 'Brand Name']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f'Missing fields: {", ".join(missing_fields)}'}), 400
    
    # Refine the prompt using the provided input
    refined_prompt = refine_prompt(data)
    print(refined_prompt)
    
    # Generate the image using the refined prompt
    image_url = generate_image(refined_prompt)
    
    if image_url:
        return jsonify({'image_url': image_url}), 200
    else:
        return jsonify({'error': 'Failed to generate image'}), 500

if __name__ == '__main__':
    # Ensure app runs on the correct host and port for Render
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
