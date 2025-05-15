from typing import Dict, Any, Union
from pydantic import BaseModel, Field
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma


# Creates an embedding model
embeddings = NVIDIAEmbeddings(
    model="NV-Embed-QA", #"nvidia/llama-3.2-nv-embedqa-1b-v2"
    embed_batch_size=512,
    truncate="END",
)    

# Creates a text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

def get_retriever(persistent_directory:str,
                  embedder:NVIDIAEmbeddings,
                  filters:Union[Dict,None]=None)->Any:
    """
    Creates and returns a Chroma retriever with specified settings.
    
    Args:
        persistent_directory (str): Directory path for Chroma persistence
        embeder (NVIDIAEmbeddings): Embedding model to use
        filters (Dict, optional): Optional filters to apply to search
        
    Returns:
        Chroma retriever object
    """
    db = Chroma(persist_directory=persistent_directory,
                embedding_function=embedder,
                )
    search_kwargs = {"k": 3, "score_threshold": 0.3}
    if filters:
        search_kwargs['filter'] = filters
    retriever = db.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs=search_kwargs,
    )
    return retriever


def concatenator(data_class:BaseModel)->str:
    """
    Concatenates all fields of a Pydantic BaseModel instance into a single string.
    Example:
        >>> model = SomeModel(field1="value1", field2="value2")
        >>> concatenated = concatenator(model)
        >>> print(concatenated)
        field1: value1
        field2: value2
    """
    concatenated = "\n"
    for field in data_class.__fields__:
        conctent = getattr(data_class, field)
        field = field.replace("_", " ")
        field = field.title() 
        if isinstance(conctent, list):           
            concatenated += f"{field}: \n"
            concatenated += "• " + "\n• ".join(conctent) + "\n\n"
        elif isinstance(conctent, Dict):
            concatenated += f"{field}: {conctent['min']} - {conctent['max']}  {conctent['currency']}\n"
        else:
            concatenated += f"{field}: {conctent}\n"
    return concatenated
