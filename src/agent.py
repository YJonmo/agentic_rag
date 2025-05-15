import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import BaseTool
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from .rags import create_rag_chain
from .utils import embeddings, get_retriever
from .config import persistent_directory

load_dotenv()
load_dotenv(".env") # make sure the API keys are loaded correctly
if not os.getenv("LANGSMITH_API_KEY") or not os.getenv("LANGSMITH_API_KEY"):
    raise Exception("Environment variables not loaded. Check .env in the project root exist and contains the API keys.")

app = FastAPI()

# Define the retrievers using filters
faq_retriever = get_retriever(persistent_directory=persistent_directory,
                                     embedder=embeddings,
                                     filters={"type": "faq"})

product_retriever = get_retriever(persistent_directory=persistent_directory,
                                     embedder=embeddings,
                                     filters={"type": "product"})

occup_retriever = get_retriever(persistent_directory=persistent_directory,
                                     embedder=embeddings,
                                     filters={"type": "occupation"})

# Initialize a Chat model
llm = ChatNVIDIA(model="mistralai/mixtral-8x7b-instruct-v0.1")

# Define the RAGs based on the retrievers
faq_chain = create_rag_chain(faq_retriever, llm)
product_chain = create_rag_chain(product_retriever, llm)
occup_chain = create_rag_chain(occup_retriever, llm)


# Define the tools based on the task of FAQ, Products details, and Occupation details
class AnswerFAQ(BaseTool):
    """
    Tool for answering FAQ questions using a RAG chain.
    """
    name:str = "FAQ"
    description:str = """
        Useful for answering general questions. 
        Try to answer the questiong first using this tool. If there was not enough information, then look into the other tools.
    """

    def _run(self, input:str="don't do any thing", **kwargs)->str:
        try:
            return faq_chain.invoke({"input": input, 
                                     "chat_history": kwargs.get("chat_history", [])})
        except Exception as e:
            error_message = f"Error occurred while searching for occupation: {e}"
            print(error_message)  # Log the error
            return "I encountered an error while searching for that occupation."
        
class AnswerProducts(BaseTool):
    """
    Tool for answering details on insurance products using a RAG chain.
    """
    name:str = "product_related"
    description:str = """
        Useful only if the details of an insurance product was asked for.
    """

    def _run(self, input:str="don't do any thing", **kwargs)->str:
        try:
            return product_chain.invoke({"input": input, 
                                         "chat_history": kwargs.get("chat_history", [])})
        except Exception as e:
            error_message = f"Error occurred while searching for occupation: {e}"
            print(error_message)  # Log the error
            return "I encountered an error while searching for that occupation."

class AnswerOccupation(BaseTool):
    """
    Tool for answering occupated-related products using a RAG chain.
    """
    name:str = "occupation_related"
    description:str = """
        Useful for searching and finding information about occupations. 
        Use this if the user mentions about an occupation title. 
        Look for the "occupations" keyword in the stored data to find the appropriate answer.
    """

    def _run(self, input:str="don't do any thing", **kwargs)->str:
        try:
            return occup_chain.invoke({"input": input, 
                                       "chat_history": kwargs.get("chat_history", [])})
        except Exception as e:
            error_message = f"Error occurred while searching for occupation: {e}"
            print(error_message)  # Log the error
            return "I encountered an error while searching for that occupation."

tools = [AnswerOccupation(),
         AnswerProducts(),
         AnswerFAQ()
         ]


# Load the correct JSON Chat Prompt from the hub
prompt = hub.pull("hwchase17/structured-chat-agent")
agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,
    verbose=True,
    # memory_key="chat_history", # Add memory key to track chat history,
    max_iterations=5,
)

chat_history = []  # Collect chat history here (a sequence of messages)
initial_message = """You are an AI assistant that can provide helpful answers using available tools.
                     Answer the question only using the tools provided to you.  
                     You could use the combinations of these tools to get your answer. 
                     But do not rely solely on your knowledge to answer the questions.
                """
chat_history.append(HumanMessage(content=""))
chat_history.append(AIMessage(content=initial_message))

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Renders the root endpoint with the index.html template.
    
    Args:
        request (Request): The incoming FastAPI request object
        
    Returns:
        TemplateResponse: The rendered index.html template
    """
    return templates.TemplateResponse("index.html", {"request": request})   


# Chat Loop to interact with the user
@app.post("/chat/")
async def chat(request: Request):
    data = await request.json()
    message = data["message"]
    response = agent_executor.invoke({"input": message, "chat_history": chat_history})

    chat_history.append(HumanMessage(content=message))
    chat_history.append(AIMessage(content=str(response['output'])))
    return {"response": response['output']}
