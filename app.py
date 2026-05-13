import streamlit as st
import chromadb
from groq import Groq
from google.genai import types
from google import genai
from database import topics

client_gemini = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# embedding
def embed_texto(texto):
    result = client_gemini.models.embed_content(
        model="gemini-embedding-2",
        contents=texto,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )
    return result.embeddings[0].values

@st.cache_resource
def inicializar_chroma():
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

colecao = inicializar_chroma()

def generate_response_groq(query_bruta):
    # realizando busca
    query_emb = embed_texto(f"task: question answering | query: {query_bruta}")
    results = colecao.query(query_embeddings=[query_emb], n_results=1)

    res = results['metadatas'][0][0]
    contexto = results['documents'][0][0]
    fonte = f"{res['autores']}, \"{res['nome_do_artigo']}\" ({res['ano']}), Página: {res['pagina']}"

    # prompt do sistema
    prompt = f"""
    Você é um assistente acadêmico especializado em Humanidades Digitais.
    Use estritamente o contexto abaixo para responder à pergunta do usuário.
    Sempre cite o autor e o ano ao responder.

    IMPORTANTE: Caso não encontre a resposta exata no contexto fornecido,
    sua resposta deve ser obrigatoriamente e apenas: \"INFORMAÇÃO_NÃO_ENCONTRADA\".

    Contexto:
    \"{contexto}\"
    (Fonte: {fonte}).

    Pergunta:
    {query_bruta}

    Resposta:
    """

    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    texto_resposta = completion.choices[0].message.content.strip()

    if "INFORMAÇÃO_NÃO_ENCONTRADA" in texto_resposta:
        return {"resposta": "Informação não encontrada na base.", "fontes": ""}

    return {"resposta": texto_resposta, "fontes": fonte}

# UI
st.title("Citações sobre Humanidades Digitais")
pergunta = st.text_input("Pergunta:", value="fale sobre o conhecimento histórico?")

if st.button("Executar"):
    res = generate_response_groq(pergunta)
    st.text(f"Resposta:\n{res['resposta']} - Fonte: {res['fontes']}")
