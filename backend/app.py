from flask import Flask, request
import base64
import json
from PIL import Image, ImageDraw

app = Flask(__name__)

@app.route('/map', methods=['POST'])
def map():
    image_string = request.form.get('image')
    with open("map.png", "rb") as map_file:
        map_string = base64.b64encode(map_file.read()).decode('utf-8')
    output = dummy_llm_call(image_string, map_string, "test")
    return output

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

def dummy_llm_call(image_string, map_string, prompt):
    # This is a dummy function, so we're not actually using the inputs.
    # In a real implementation, you would use these inputs to generate some output.
    return "default output"

if __name__ == '__main__':
    # app.run()
    place_object()
