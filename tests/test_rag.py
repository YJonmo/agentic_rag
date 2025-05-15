import os 
import sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'src'))
from config import persistent_directory
from utils import embeddings, get_retriever

load_dotenv()

def test_retriever():
    """
    Tests the document retriever functionality.
    
    This test function verifies that:
    1. The retriever can successfully retrieve documents based on a query
    2. The retrieved documents contain the expected metadata fields
    3. The first result matches the expected occupation
    
    Returns:
        None
        
    Raises:
        AssertionError: If any of the test conditions fail
    """
    
    retriever = get_retriever(persistent_directory=persistent_directory,
                                     embedder=embeddings)
    query = "What occupations are at risk level around 1.8?"
    relevant_docs = retriever.invoke(query)

    # Test that we get results back
    assert len(relevant_docs) > 0

    # Test that first result has expected metadata
    assert 'occupation' in relevant_docs[0].metadata
    assert relevant_docs[0].metadata['occupation'] == 'Accountant'

