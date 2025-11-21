from openai import OpenAI
import base64

client = OpenAI()

def extract_text_from_image(file):
    # Convert uploaded file to base64
    image_bytes = file.read()
    b64 = base64.b64encode(image_bytes).decode()

    # Use GPT-4o-mini Vision API
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Extract all readable text from this image."},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{b64}"
                    }
                ]
            }
        ]
    )

    # Extract plain text output
    text = response.output_text
    return text
