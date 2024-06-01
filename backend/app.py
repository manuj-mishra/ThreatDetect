from flask import Flask, request
import base64
import json
from flask_cors import CORS
from PIL import Image, ImageDraw
from dotenv import load_dotenv
import os
from openai import OpenAI
from io import BytesIO
import re

# Load environment variables from a .env file
load_dotenv()

openai_api_key = os.environ.get('OPENAI_API_KEY')
os.environ['OPENAI_API_KEY'] = openai_api_key

client = OpenAI()


app = Flask(__name__)
CORS(app)

@app.route('/map', methods=['GET','POST'])
def map():
    image_string = request.json["image"]
    with open("map.png", "rb") as map_file:
        map_string = base64.b64encode(map_file.read()).decode('utf-8')
    print('hELLO')
    print (len(image_string))
    print (len(map_string))
    image_string = downsize_base64(image_string)
    print(image_string)
    output = dummy_llm_call(image_string, map_string, "test")
    image_string = place_object()
    return image_string

def place_object():
    with open("coord.txt", "r") as coord_file:
        coord = coord_file.read().strip()
    with open("coord2pixel.json", "r") as json_file:
        coord2pixel = json.load(json_file)
    pixel = coord2pixel[coord]
    
    # Open the image file
    img = Image.open("map.png")
    draw = ImageDraw.Draw(img)
    
    # Draw a red circle at the pixel location
    r = 25
    draw.ellipse((pixel[0]-r, pixel[1]-r, pixel[0]+r, pixel[1]+r), fill ='red')
    
    # Save the image file
    img.save("map_new.png")

    # Convert the image to base64
    with open("map_new.png", "rb") as img_file:
        img_string = base64.b64encode(img_file.read()).decode('utf-8')
        
    return img_string

def downsize_base64(img):
    # Convert the base64 image to a PIL image
    img = Image.open(BytesIO(base64.b64decode(img)))
    
    # Downsize the image
    img.thumbnail((500, 500))
    
    # Convert the downsized image to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_string = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return img_string

system_prompt = """
You are a helpful assistant. You are designed to look at an image and locate on a provided map the grid reference that that object is in. 
You should only return this string, for example "B2" and nothing more. Do not add any fluff or explanation to your answer. 
"""

def dummy_llm_call(image_string, map_string, system_prompt):

    user_prompt = f"""
        The object you are looking for is: A white cap.
        Remember, only return one classification with the letter first then the number
        """

    response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{image_string}"}
                    },
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{map_string}"} 
                    }
                ]}
            ]
        )
    
    text = response.choices[0].message.content
    match = re.search(r'[A-Z]\d', text)
    if match:
        return print(match.group(0))
    else:
        return "No match found"


if __name__ == '__main__':
    app.run()
    #place_object()
    # app.run()
    # place_object()
    # dummy_llm_call(image_string, map_string, system_prompt)



