import streamlit as st
import chromadb
from data.database import topics
from src.embeddings import embed_texto

@st.cache_resource
def inicializar_chroma():
    """Initializes ChromaDB and populates it if empty."""
    chroma_client = chromadb.Client()
    colecao = chroma_client.get_or_create_collection(name="humanidades_digitais")

    if colecao.count() == 0:
        ids = [t['id'] for t in topics]
        documents = [t['citacao'] for t in topics]
        embeddings = [embed_texto(t['citacao']) for t in topics]
        metadatas = [{
            "autores": t['autores'],
            "ano": t['ano'],
            "pagina": t['pagina'],
            "dia_da_leitura": t['dia_da_leitura'],
            "nome_do_artigo": t['nome_do_artigo']
        } for t in topics]

        colecao.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
    return colecao
