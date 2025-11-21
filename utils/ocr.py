from openai import OpenAI
import base64

client = OpenAI()

def extract_text_from_image(file):
    # Convert file to base64
    image_bytes = file.read()
    b64 = base64.b64encode(image_bytes).decode()

    # Call OpenAI Vision
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Extract all text from this screenshot."},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{b64}"
                    }
                ]
            }
        ]
    )

    return response.choices[0].message.content
