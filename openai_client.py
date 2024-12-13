from openai import OpenAI
import os
import base64

openai_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def diff_image(target_file_name: str, try_file_name: str) -> str:
    encoded_image_1 = encode_image(target_file_name)
    encoded_image_2 = encode_image(try_file_name)

    chat_completion = openai_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """You are a helpful AI teacher that will help a student replicate a target website.
                You will be given images of two websites. 
                The first image is the target website, the second image is the student's attempt at replicating the target website.
                You will understand the top 3 key differences in the two images. Using this, only suggest a list of improvemnts to the student.
                Do not explain your thought process to the student. Be specific about what improvements to make.
                Refer to the student in the first person.
                Only focus on the content of the web page and not on differences in the browser or operating system.
                """
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "The target website is shown in the first image. The student's attempt is shown in the second image."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{encoded_image_1}"},
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{encoded_image_2}"},
                    }
                ],
            }
        ],
        model="gpt-4o-mini",
    )

    return chat_completion.choices[0].message.content


def generate_html_code(image_path: str, attempt_code: str = None, feedback: str = None) -> str:
    encoded_image_1 = encode_image(image_path)

    messages = [{
                "role": "system",
                "content": """You are a helpful HTML coder. You will be given an image of a website in a web browser.
                You will use the image to generate the HTML code for the website.
                Focus on replicating the design of the website, and not the content.
                Only return the HTML code, in a block quote. 
                Any styling should be included as inline CSS within the HTML file.
                """
                },
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": "You are given the image of a website, generate the HTML code for the website."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{encoded_image_1}"},
                    },
                ]}
                ]

    # Has there been a past attempt?
    if attempt_code is not None and attempt_code != "":
        print("There has been a past attempt at writing code")
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": "Here is the code that I have generated so far."},
                {"type": "text", "text": attempt_code},
                {"type": "text", "text": "Here is the feedback that I received on this code, can you improve it by accounting for the feedback?"},
                {"type": "text", "text": feedback},
            ],
        })

    chat_completion = openai_client.chat.completions.create(messages=messages,
                                                            model="gpt-4o",
                                                            )

    return chat_completion.choices[0].message.content
