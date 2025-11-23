import utils
import code
from openai import OpenAI

if __name__ == '__main__':
    client = OpenAI(api_key=utils.get_api_key("OpenAI"))
    resp = client.chat.completions.create(
        model = "gpt-5",
        messages=[
            {"role":"user", "content": "Please calculate 1+2"}
        ]
    )
    print("GPT Resp:", resp.choices[0].message.content)
    code.interact(local=locals())
  