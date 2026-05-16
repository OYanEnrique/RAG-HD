from src.vector_store import inicializar_chroma
from src.embeddings import embed_texto
from src.config import groq_client

def generate_response_groq(query_bruta: str) -> dict:
    """Orchestrates the RAG process: search DB, build prompt, call LLM."""
    colecao = inicializar_chroma()
    
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
    Sempre cite o autor e o ano ao responder, mas NÃO inclua a referência bibliográfica completa no final do seu texto.

    IMPORTANTE: Caso não encontre a resposta exata no contexto fornecido,
    sua resposta deve ser obrigatoriamente e apenas: "INFORMAÇÃO_NÃO_ENCONTRADA".

    Contexto:
    "{contexto}"
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
