import streamlit as st
from src.rag_service import generate_response_groq

# UI
st.title("Citações sobre Humanidades Digitais")
pergunta = st.text_input("Pergunta:", value="fale sobre o conhecimento histórico?")

if st.button("Executar"):
    res = generate_response_groq(pergunta)
    st.write(f"**Resposta:**\n\n{res['resposta']}")
    if res['fontes']:
        st.info(f"**Fonte Completa:** {res['fontes']}")
