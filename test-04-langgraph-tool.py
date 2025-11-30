from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.globals import set_debug, set_verbose

from pydantic import BaseModel, Field
import utils
import langchain


class MyFavoriteMusic(BaseModel):
    song: str = Field(description="The name of one of my favorite songs.")
    singer: str = Field(description="The singer of the `song`")

class MyFavoriteMovie(BaseModel):
    name: str = Field(description="The name of one of my favorite movies.")
    director: str = Field(description="The director of the `movie`")

class MyFavoritesInfo(BaseModel):
    musics:list[MyFavoriteMusic] = Field(description="My favorite songs") 
    movies:list[MyFavoriteMovie] = Field(description="My favorite moives") 

class AgentState(MessagesState):
    final_reposnse: MyFavoritesInfo

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

### AGENT ##

class FavAgent:
    def __init__(self):
        self._graph = StateGraph(AgentState)
        self._tools = [get_my_favorite_movies, get_director_by_movie_name, get_my_favorite_songs]
        self.__llm = ChatOpenAI(model='gpt-5', api_key=utils.get_api_key("OpenAI"))
        self._llm_binded_tools = self.__llm.bind_tools(self._tools)
        

    def agent_proxy(self, state: AgentState):
        response = self._llm_binded_tools.invoke(state["messages"])
        return {"messages": [response]}
    
    def chk_is_tool_need(self, state: AgentState) -> str:
        if state["messages"][-1].tool_calls:
            return "tool"
        else:
            return "continue"
        
    def final_respond(self, state: AgentState):
        final_llm = self.__llm.with_structured_output(MyFavoritesInfo)
        system_message = SystemMessage(
            content=(
                "You are a structured data generator that outputs only JSON "
                "fitting the MyFavoritesInfo schema. Do not include explanations."
            )
        )

        user_message = HumanMessage(
              content="Use all available info to fill MyFavoritesInfo (musics, movies)."
        )


        fav_info: MyFavoritesInfo = final_llm.invoke([system_message] + state["messages"] + [user_message])
        return {"final_reposnse": fav_info}
        
    def run_langgraph(self, init_msg):
        self._graph.add_node('agent', self.agent_proxy)
        self._graph.add_node('call_tools', ToolNode(self._tools))
        self._graph.add_node('final_respond', self.final_respond)

        self._graph.set_entry_point('agent')
        self._graph.add_conditional_edges('agent',  self.chk_is_tool_need,
            {
                "tool": "call_tools",
                "continue": "final_respond"
            }
        )
        self._graph.add_edge('call_tools', 'agent')
        self._graph.add_edge('final_respond', END)
        cg = self._graph.compile()
        print(cg.get_graph().draw_ascii())
        result: AgentState = cg.invoke({
            "messages": [HumanMessage(content=init_msg)]
        })

        return result



if __name__ == '__main__':
    set_debug(True)
    set_verbose(True)
    agent = FavAgent()
    result = agent.run_langgraph("Find the singers of my favorite songs and the directors of my favorite movies")
    print("===========RESPONSE============")
    print(result["final_reposnse"])
