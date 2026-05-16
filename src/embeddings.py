from google.genai import types
from src.config import client_gemini

def embed_texto(texto: str) -> list[float]:
    """Generates an embedding for the given text using Gemini."""
    result = client_gemini.models.embed_content(
        model="gemini-embedding-2",
        contents=texto,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )
    return result.embeddings[0].values
