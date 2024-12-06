from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import openai  # Ensure you have the OpenAI Python package installed

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Fetch the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

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
    data = request.json
    
    required_fields = ['Product Description', 'Brand Name']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f'Missing fields: {", ".join(missing_fields)}'}), 400
    
    refined_prompt = refine_prompt(data)
    print(refined_prompt)
    
    image_url = generate_image(refined_prompt)
    
    if image_url:
        return jsonify({'image_url': image_url}), 200
    else:
        return jsonify({'error': 'Failed to generate image'}), 500

# Define system instructions for ad generation
system_instructions = """
Generate an engaging ad description for the provided product, complete with relevant hashtags.

You will be given a simple product description, and your task is to create a captivating promotional message that highlights its benefits and sets it apart in the market. The ad should be vibrant, designed to catch the user's attention, and include a blend of eye-catching emojis and persuasive phrases.

# Steps

1. **Title & Hook**: Start with a powerful and enticing title for the ad. This should grab attention immediately and convey the product's value in an exciting way.
2. **Product Highlights**: Describe the key features and benefits of the product focusing on how it solves a problem or meets a need for the customer. Keep the tone enthusiastic and positive.
   - Use a few bullet points to highlight specific features.
3. **Call to Action**: End with an effective call to action, encouraging the reader to act ("Get yours today!", "Don't miss out!", etc.).
4. **Hashtags**: Add a set of relevant and catchy hashtags related to the product and the audience. Ensure hashtags are relevant, and balance between popular and unique tags.

# Output Format

- **Bold title** to capture attention.
- Short paragraph (3-5 sentences) detailing product features and benefits.
- Features should also include 2-3 bullet points if possible.
- At the end, include 5-7 **relevant hashtags**.

# Notes

- Ensure each ad description contains both an emotional pull and practical features.
- Always include emojis to enhance the visual appeal without overwhelming the text.
- Balance creativity with clarity—ensure every feature is easy to understand and clearly valuable.
"""

# Function to generate ad content
def generate_ad(product_description):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": f"Create an ad for: '{product_description}'"}
            ]
        )

        ad_content = response['choices'][0]['message']['content']
        return ad_content
    except Exception as e:
        print(f"Error generating ad content: {e}")
        return None

@app.route('/generate_content', methods=['POST'])
def generate_content_route():
    data = request.json
    
    if 'Product Description' not in data:
        return jsonify({'error': "Missing field: 'Product Description'"}), 400
    
    product_description = data['Product Description']
    ad_content = generate_ad(product_description)
    
    if ad_content:
        return jsonify({'ad_content': ad_content}), 200
    else:
        return jsonify({'error': 'Failed to generate ad content'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
