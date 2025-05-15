import os
from dotenv import load_dotenv
import json
import pandas as pd
from langchain_community.vectorstores import Chroma
from utils import embeddings, text_splitter, concatenator
from data_classes import FAQ, ProductDetails, OccupationDetails
from config import persistent_directory, faq_file, prod_occu_file

load_dotenv( ".env") # make sure the API keys are loaded correctly
if not os.getenv("LANGSMITH_API_KEY"):
    raise Exception("Environment variables not loaded. Check .env in the project root exist and contains the API keys.")


def load_faqs(file_path):
    """Load and process FAQs from CSV file."""
    df = pd.read_csv(file_path)
    documents = []
    for _, row in df.iterrows():
        # Combine question and answer
        faq = FAQ(question=row['question'],
                  answer=row['answer'],
                  category=row['category'])
        documents.append({
            "text": concatenator(faq),
            "metadata": faq.__dict__
        })
    return documents

def load_products(file_path:str)->list[dict]:
    """Load and process products/occupations from JSON file."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    documents = []
    for key, val in data.items():
        if key == "products":
            obj = ProductDetails(type="product")
        elif key == "occupation_data":
            obj = OccupationDetails(type="occupation")
        else:
            raise ValueError(f"Invalid type: {key}. Must be 'product' or 'occupation'")

        for obj_key, obj_val in val[0].items():
            setattr(obj, obj_key, obj_val)

        # add the metadata
        if key == "products":
            documents.append({
                "text": concatenator(obj),
                "metadata": {
                    "type": obj.type,
                    "product_id": obj.product_id,
                    "name": obj.name,
                }
            })
        else:
            documents.append({
                "text": concatenator(obj),
                "metadata": {
                    "type": obj.type,
                    "industry": obj.industry,
                    "occupation": obj.occupation,
                    "claim_likelihood": str(obj.claim_likelihood),
                }
            })
    return documents


def create_vector_db(persistent_directory:str, faq_file:str, prod_occu_file:str)->None:
    """Create a vector database from FAQs and products/occupations."""
    if not os.path.exists(persistent_directory):
        os.makedirs(persistent_directory)

    # Load and process documents
    faq_docs = load_faqs(faq_file)
    product_docs = load_products(prod_occu_file)

    # Combine all documents
    all_docs = faq_docs + product_docs

    # Split documents into chunks
    texts = []
    metadatas = []
    for doc in all_docs:
        chunks = text_splitter.split_text(doc["text"])
        texts.extend(chunks)
        metadatas.extend([doc["metadata"]] * len(chunks))

    # Create vector store
    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=persistent_directory
    )

    # Persist the database
    vectorstore.persist()
    print("Vector database created and persisted successfully!")

if __name__ == "__main__":
    create_vector_db(persistent_directory, faq_file, prod_occu_file)
