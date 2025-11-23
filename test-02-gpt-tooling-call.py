import utils
import code
import json
from openai import OpenAI

client = OpenAI(api_key=utils.get_api_key("OpenAI"))

def get_my_favorite_movies() -> str:
    return "Wonderful Life (1998), Big Short (2015), Jin Jzz Python Movie (2025)"

def get_director_by_movie_name(movie_name: str) -> str:
    movies = {
        "Wonderful Life": "是枝 裕和",
        "Big Short": "Steve Carell",
        "Great": "Lee"
    }
    if movie_name in movies:
        return movies[movie_name]
    else:
        return "Not Found"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_my_favorite_movies",
            "description": "The function returns my favorite movites with a year",
            "parameters": { },
        },
    }, {
        "type": "function",
        "function": {
            "name": "get_director_by_movie_name",
            "description": 
            "The function finds the director name of the passed movie's name and returns it."
            "The movie_name parameter must not contain the movie's year",
            "parameters": {
                "type": "object",
                "properties": {"movie_name": {"type": "string"}},
                "required": ["movie_name"]
            },
        },
    }
]


if __name__ == '__main__':
    messages = [
        {"role": "user", "content": "Find the names of the directors of my favorite movies"}
    ]

    while True:
        resp = client.chat.completions.create(
            model="gpt-5",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        message = resp.choices[0].message
        messages.append(message)
        print("Resp: ", message)

        if message.tool_calls:
            for tool_call in message.tool_calls:
                print("\t- Tool Calling: ", tool_call.function)
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                response = locals()[func_name](**args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": response
                })
        elif message.content:
            print("Final Response: ", message.content)
            break

    code.interact(local=locals())