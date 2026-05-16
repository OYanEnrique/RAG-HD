import streamlit as st
from groq import Groq
from google import genai

# Initialize clients using secrets
client_gemini = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
