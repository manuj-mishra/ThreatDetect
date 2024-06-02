from flask import Flask, request
import base64
import json
from flask_cors import CORS
from PIL import Image, ImageDraw
from dotenv import load_dotenv
import os
from openai import OpenAI
from llm import white_cap_detect_llm

# Load environment variables from a .env file
load_dotenv()

openai_api_key = os.environ.get('OPENAI_API_KEY')
os.environ['OPENAI_API_KEY'] = openai_api_key

client = OpenAI()


app = Flask(__name__)
CORS(app)

# List to store the previous prediction
last_prediction = []

@app.route('/map', methods=['POST'])
def map():
    print("Request received")
    image_string = request.json["image"]
    with open("map.png", "rb") as map_file:
        map_string = base64.b64encode(map_file.read()).decode('utf-8')
    white_cap_location = white_cap_detect_llm(image_string, map_string, model_name='sonnet', previous_prediction=last_prediction[-1])
    if white_cap_location is None or "null" in white_cap_location.lower():
        print("No white cap detected")
        return map_string
    print(f"White cap detected at {white_cap_location}")
    # Store the prediction
    last_prediction.append(white_cap_location)
    image_string = place_object(white_cap_location)
    return image_string

def place_object(white_cap_cord):
    with open("coord2pixel.json", "r") as json_file:
        coord2pixel = json.load(json_file)
    pixel = coord2pixel[white_cap_cord]
    
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

if __name__ == '__main__':
    app.run()
