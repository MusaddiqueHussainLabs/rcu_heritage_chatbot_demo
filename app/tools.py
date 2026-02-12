import os
import chromadb
import open_clip
import torch

from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.tools import tool

from llm_model import llm


# HuggingFace embedding (Arabic + English)
embeddings = HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-base",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

# TEXT COLLECTION
text_vector_store = Chroma(
    collection_name="heritage_text",
    embedding_function=embeddings,
    persist_directory="./data/chroma_langchain_db"
)

# IMAGE COLLECTION (raw chroma client)
client = chromadb.PersistentClient(path="./data/chroma_langchain_db")

image_collection = client.get_or_create_collection(
    name="heritage_images"
)

# @tool(response_format="content_and_artifact")
# def retrieve_text_context(query: str):
#     """Retrieve object metadata and descriptions from AlUla collections."""
    
#     docs = text_vector_store.similarity_search(query, k=3)

#     serialized = "\n\n".join(
#         f"Inventory: {doc.metadata.get('inv_no')}\n"
#         f"Content:\n{doc.page_content}"
#         for doc in docs
#     )

#     return serialized, docs

@tool(response_format="content_and_artifact")
def retrieve_text_context(query: str):
    """Retrieve object metadata and descriptions from AlUla collections."""

    docs = text_vector_store.similarity_search(query, k=3)

    if not docs:
        return "No matching objects found.", []

    serialized = "\n\n".join(
        f"Inventory: {doc.metadata.get('inv_no')}\n"
        f"Images: {doc.metadata.get('images')}\n"
        f"Content:\n{doc.page_content}"
        for doc in docs
    )

    return serialized, docs


# @tool(response_format="content_and_artifact")
# def retrieve_by_inventory(inv_no: str):
#     """Retrieve object details using exact inventory number."""
    
#     docs = text_vector_store.similarity_search(
#         inv_no,
#         k=1,
#         filter={"inv_no": inv_no}
#     )

#     if not docs:
#         return "No object found with this inventory number.", []

#     doc = docs[0]

#     serialized = (
#         f"Inventory: {doc.metadata.get('inv_no')}\n"
#         f"{doc.page_content}"
#     )

#     return serialized, docs

@tool(response_format="content_and_artifact")
def retrieve_by_inventory(inv_no: str):
    """Retrieve object details using exact inventory number."""

    docs = text_vector_store.similarity_search(
        inv_no,
        k=1,
        filter={"inv_no": inv_no}
    )

    if not docs:
        return "No object found with this inventory number.", []

    doc = docs[0]

    serialized = (
        f"Inventory: {doc.metadata.get('inv_no')}\n"
        f"Images: {doc.metadata.get('images')}\n\n"
        f"{doc.page_content}"
    )

    return serialized, docs

device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="laion2b_s34b_b79k"
)
clip_model = clip_model.to(device)
clip_model.eval()

def embed_text_for_image_search(text):
    tokens = open_clip.tokenize([text]).to(device)
    with torch.no_grad():
        features = clip_model.encode_text(tokens)
    features /= features.norm(dim=-1, keepdim=True)
    return features.cpu().numpy()[0]

@tool(response_format="content_and_artifact")
def search_image_by_text(query: str):
    """Find similar artifact images based on textual description."""
    
    embedding = embed_text_for_image_search(query)

    results = image_collection.query(
        query_embeddings=[embedding.tolist()],
        n_results=3
    )

    serialized = ""
    for meta in results["metadatas"][0]:
        serialized += (
            f"Inventory: {meta.get('inv_no')}\n"
            f"Image Path: {meta.get('image_path')}\n\n"
        )

    return serialized, results

@tool(response_format="content_and_artifact")
def hybrid_search(query: str):
    """Perform both metadata and image-based search."""
    
    text_docs = text_vector_store.similarity_search(query, k=2)
    image_results = search_image_by_text.invoke(query)[0]

    serialized = "TEXT RESULTS:\n"
    for doc in text_docs:
        serialized += f"{doc.page_content}\n\n"

    serialized += "\nIMAGE RESULTS:\n"
    serialized += image_results

    return serialized, text_docs

from langchain.tools import tool
from PIL import Image

def embed_image(image_path):
    image = preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(device)

    with torch.no_grad():
        features = clip_model.encode_image(image)

    features /= features.norm(dim=-1, keepdim=True)

    return features.cpu().numpy()[0]

@tool(response_format="content_and_artifact")
def search_by_image_and_explain(image_path: str):
    """
    Search similar artifact by image and explain it using retrieved metadata.
    """

    if not os.path.exists(image_path):
        return "Image path not found.", []

    # Step 1: Embed query image
    embedding = embed_image(image_path)

    # Step 2: Search similar images
    results = image_collection.query(
        query_embeddings=[embedding.tolist()],
        n_results=1
    )

    if not results["metadatas"][0]:
        return "No similar artifact found.", []

    top_meta = results["metadatas"][0][0]
    inv_no = top_meta.get("inv_no")

    # Step 3: Retrieve full object metadata from text collection
    docs = text_vector_store.similarity_search(
        inv_no,
        k=1,
        filter={"inv_no": inv_no}
    )

    if not docs:
        return "Metadata not found for matched artifact.", []

    doc = docs[0]

    # Step 4: Ask LLM to explain artifact
    explanation_prompt = f"""
You are an expert cultural heritage assistant for AlUla.

An uploaded image was matched to the following artifact:

Inventory Number: {inv_no}

Artifact Details:
{doc.page_content}

Explain:
1. What this artifact is
2. Its historical significance
3. Material and period
4. Why it may be culturally important to AlUla
5. If relevant, explain visible features in the image

Be concise but informative.
"""

    explanation = llm.invoke(explanation_prompt)

    return explanation.content, docs

