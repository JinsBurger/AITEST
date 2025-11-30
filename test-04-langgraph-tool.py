from langchain_core.tools import tool
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated, Literal
import utils


def State(TypedDict):
    messages: Annotated[list, add_messages]
    mode: Literal["movie", "song"]

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
    
@tool(parse_docstring=True)
def get_my_favorite_songs() -> str:
    """Return My favorite song list with its singer.

    Returns:
        str: My favorite song list with its singer.
    """
    return "Hanabata (back number), Ready To Fight (Woodz)"

def continue_to_choice(state: State):

    

def run_langgraph():
    llm = ChatOpenAI(model='gpt-5', api_key=utils.get_api_key("OpenAI")).with_structured_output
    graph = StateGraph(State)
    graph.add_node("Please give me the director name of my favorite move and the singer of my favorite song")

if __name__ == '__main__':
    run_langgraph()
