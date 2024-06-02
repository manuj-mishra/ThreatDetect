from typing import Optional

from dotenv import load_dotenv
import os
from openai import OpenAI
import re
import anthropic

# Load environment variables from a .env file
load_dotenv()

openai_api_key = os.environ.get('OPENAI_API_KEY')
os.environ['OPENAI_API_KEY'] = openai_api_key

anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key

client = OpenAI()
client_a = anthropic.Anthropic()

white_cap_detect_system_prompt = """
You are a helpful assistant. You are designed to look at an image and locate on a provided map the grid reference that that object is in. 
You should only return this string, for example "B2" and nothing more. Do not add any fluff or explanation to your answer. 
"""

user_prompt = f"""
        The object you are looking for is: A white cap.
        You are provided with an image, which is a snapshot from a video, of the object, and a map. 
        You need to return the grid that this object can be found at on the map.
        If the white cap is not in the image, return '<NULL>'.
        Remember, only return one classification with the letter first then the number
        """

def white_cap_detect_llm(image_string, map_string, model_name='sonnet', previous_prediction: Optional[str] = None) -> Optional[str]:
    if previous_prediction:
        user_prompt_with_prev = user_prompt + f"\nPrevious predictions are provided in this list: {previous_prediction}. The most recent prediction is the rightmost value in the array. Note that it is likely that the object is in the same location as before, but if it has very obvioulsy moved then change your classification. Else, do not. "
    else:
        user_prompt_with_prev = user_prompt

    if model_name == 'gpt4':
        response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": white_cap_detect_system_prompt},
                    {"role": "user", "content": [
                        {"type": "text", "text": user_prompt_with_prev},
                        {"type": "image_url", "image_url": {"url": f"{image_string}"}},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{map_string}"}}
                    ]}
                ]
            )
        
        text = response.choices[0].message.content

    elif model_name == 'sonnet':
        img_string = image_string.replace("data:image/png;base64,", "")
        map_string = map_string.replace("data:image/png;base64,", "")
        response = client_a.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system=white_cap_detect_system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_string,
                            },
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": map_string
                            },
                        },
                        {
                            "type": "text",
                            "text": user_prompt_with_prev,
                        }
                    ],
                }
            ],
        )
        text = response.content[0].text

    match = re.search(r'[A-Z]\d', text)
    if match:
        return match.group(0)
    return None
