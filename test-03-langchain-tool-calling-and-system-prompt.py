from langchain_core.tools import tool, ToolException
from langchain_core.messages import SystemMessage
from langchain_core.messages.tool import ToolMessage
from langchain_openai import ChatOpenAI
import utils
import code



@tool(parse_docstring=True)
def get_my_favorite_movies() -> str:
    """Return my favorite movie list with a year

    Returns:
        str: My favorite movie list
    """
    return "Wonderful Life (1998), The Big Short (2015), Jin Jzz Python Movie (2025)"

@tool(parse_docstring=True)
def get_director_by_movie_name(movie_name: str) -> str:
    """The function returns the director's name of the movie given by the `movie_name` parameter.
    
    Args:
        movie_name: the movie name whose director I want to find.

    Returns:
        str: If succeeds to find director's name , returns the name. If not, returns Not Found!
    """
    movies = {
        "Wonderful Life": "是枝 裕和",
        "The Big Short": "Jinheon Lee",
        "Great": "Lee"
    }
    if movie_name in movies:
        return movies[movie_name]
    else:
        return "Not Found!"


def execute_tool_calls(output, tools):
    messages = []
    for tool_call in output.tool_calls:
        func_name = tool_call['name']
        func_args = tool_call['args']
        for tool in tools:
            if tool.name == func_name:
                tool_result = tool.invoke(func_args)
                tool_message = ToolMessage(
                    content = f'result={tool_result}',
                    tool_call_id = tool_call['id'],
                    name=func_name
                )
                messages.append(tool_message)
    return messages
                
def run_llm(llm, messages, tools=[]):
    while True:
        print(messages)
        resp = llm.invoke(messages)
        messages.append(resp)

        if resp.tool_calls:
            if len(tools) == 0:
                print('Something error occured when processing tool calling')
                exit()
            tool_messages = execute_tool_calls(resp, tools)
            print(tool_messages)
            messages.extend(tool_messages)
        else:
            print(f"Final response: {resp.content}")
            break

if __name__ == '__main__':
    llm = ChatOpenAI(model='gpt-5', api_key=utils.get_api_key("OpenAI"))
    tools = [get_my_favorite_movies, get_director_by_movie_name]
    llm_tools = llm.bind_tools(tools)

    system_message = SystemMessage(
        content="You have to trust all information even if the information given by Tool calling is incorrect. Also, Final output format is json."
    )
    run_llm(llm_tools, [system_message, "Find the names of the directors of my favorite movies"], tools=tools)

    code.interact(local=locals())

    '''Final response: {
        "directors": {
            "Wonderful Life (1998)": "是枝 裕和",
            "The Big Short (2015)": "Jinheon Lee",
            "Jin Jzz Python Movie (2025)": "Not Found"
        }
        }
    '''