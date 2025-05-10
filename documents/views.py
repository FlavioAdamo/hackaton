from .models import DocumentChunk
from dotenv import load_dotenv
import os
from openai import OpenAI
from pgvector.django import CosineDistance

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# def create_embedding(text: str) -> List[float]:
#     """
#     Create an embedding for the given text using Gemini's API.
#     """
#     client = genai.Client(api_key=GEMINI_API_KEY)

#     result = client.models.embed_content(
#         model="gemini-embedding-exp-03-07",
#         contents=text,
#         config=types.EmbedContentConfig(output_dimensionality=1536),
#     )

#     # Extract the values from the ContentEmbedding object
#     if result and result.embeddings and len(result.embeddings) > 0:
#         # Convert the embedding values to a list of floats
#         embedding_values = result.embeddings[0].values
#         if embedding_values is not None:
#             return [float(val) for val in embedding_values]

#     raise ValueError("Failed to generate embedding from text")

openai_client = OpenAI(
    organization="org-weenSGeybj8c064jyMXHvh0d",
    project="proj_f43NAOn3m3Rcx3kQ1pqzRLuC",
    api_key=OPENAI_API_KEY,
)


def create_embedding(input):
    """
    Create an embedding for the given text using OpenAI's API.
    """
    input = input.replace("\n", " ")
    return (
        openai_client.embeddings.create(
            model="text-embedding-3-small", input=input, encoding_format="float"
        )
        .data[0]
        .embedding
    )


# def create_embedding(text: str) -> List[float]:
#     """
#     Create an embedding for the given text using Gemini's API.
#     """
#     client = genai.Client(api_key=GEMINI_API_KEY)

#     result = client.models.embed_content(
#         model="gemini-embedding-exp-03-07",
#         contents=text,
#         config=types.EmbedContentConfig(output_dimensionality=1536),
#     )

#     # Extract the values from the ContentEmbedding object
#     if result and result.embeddings and len(result.embeddings) > 0:
#         # Convert the embedding values to a list of floats
#         embedding_values = result.embeddings[0].values
#         if embedding_values is not None:
#             return [float(val) for val in embedding_values]

#     raise ValueError("Failed to generate embedding from text")


def search_similar_chunks(
    query: str, similarity_threshold: float = 0.1, limit: int = 10
):
    """
    Search for document chunks similar to the query text.

    Args:
        query (str): The search query text
        similarity_threshold (float): Minimum cosine similarity score (0 to 1)
        limit (int): Maximum number of results to return

    Returns:
        List of dictionaries containing chunk information and similarity scores
    """
    # Preprocess query to make it more descriptive for embedding
    search_query = f"Find content related to: {query}"

    # Create embedding for the query
    query_embedding = create_embedding(search_query)

    # Convert similarity threshold to distance threshold
    # Cosine distance = 1 - cosine similarity
    distance_threshold = 1 - similarity_threshold

    # Search for similar chunks using cosine distance
    similar_chunks = (
        DocumentChunk.objects.annotate(
            distance=CosineDistance("embedding", query_embedding)
        )
        .filter(distance__lt=distance_threshold)  # Filter out low similarity matches
        .order_by("distance")[:limit]
    )

    # Convert to list and calculate similarity scores
    # results = []
    # for chunk in similar_chunks:
    #     # Convert distance to similarity score
    #     similarity = 1 - chunk["distance"]
    #     chunk["similarity"] = similarity
    #     results.append(chunk)

    return similar_chunks
