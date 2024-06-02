from typing import Optional

from dotenv import load_dotenv
import os
from openai import OpenAI
import re

# Load environment variables from a .env file
load_dotenv()

openai_api_key = os.environ.get('OPENAI_API_KEY')
os.environ['OPENAI_API_KEY'] = openai_api_key

client = OpenAI()

white_cap_detect_system_prompt = """
You are a helpful assistant. You are designed to look at an image and locate on a provided map the grid reference that that object is in. 
You should only return this string, for example "B2" and nothing more. Do not add any fluff or explanation to your answer. 
"""

user_prompt = f"""
        The object you are looking for is: A white cap.
        Remember, only return one classification with the letter first then the number
        """

def white_cap_detect_llm(image_string, map_string)->Optional[str]:
    response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content":white_cap_detect_system_prompt },
                {"role": "user", "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"{image_string}"}
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
        return match.group(0)
    return None
