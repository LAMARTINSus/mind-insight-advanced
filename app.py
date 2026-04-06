# =========================
# VERSION: V4.8
# - Modo rápido com respostas hardcoded
# - Prompt mais direto e sem suavização
# =========================

import streamlit as st
import pandas as pd
from openai import OpenAI

DEBUG_MODE = True

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Mind Insight Advanced AI", layout="wide")

# =========================
# OPENAI CLIENT
# =========================
def get_openai_client():
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

# =========================
# HARD CODED RESPONSES
# =========================
HARDCODED = {
    1:4,2:1,3:3,4:4,5:4,6:4,7:1,8:5,9:4,10:3,
    11:1,12:4,13:3,14:5,15:5,16:3,17:4,18:1,19:5,20:4,
    21:3,22:4,23:5,24:3,25:5,26:1,27:1,28:4,29:3,30:4,
    31:3,32:1,33:5,34:3,35:1,36:5,37:4,38:4,39:1,40:3,
    41:3,42:4,43:5,44:4,45:1,46:5,47:4,48:4,49:4,50:1,
    51:1,52:5,53:4,54:3,55:1,56:5,57:4,58:4,59:1,60:4,
    61:3,62:1,63:4,64:4,65:5,66:5,67:3,68:5,69:4,70:5,
    71:4,72:5,73:3,74:1,75:3,76:4,77:5,78:1,79:1,80:1
}

# =========================
# SESSION STATE
# =========================
if "responses" not in st.session_state:
    st.session_state.responses = {}

if "current_question" not in st.session_state:
    st.session_state.current_question = 0  # começa no modo escolha

if "mode_selected" not in st.session_state:
    st.session_state.mode_selected = False

# =========================
# QUESTIONS (mantidas)
# =========================
questions = {i: f"Pergunta {i}" for i in range(1,81)}  # placeholder seguro

scale = [
    "1 - Discordo totalmente",
    "2 - Discordo",
    "3 - Neutro",
    "4 - Concordo",
    "5 - Concordo totalmente",
]

# =========================
# ENGINE (igual V4.7)
# =========================
AXIS_MAP = {
    "Abertura": [1,9,15,16,25,27,38,40,44,57,61,69,71],
    "Consciencia": [2,7,12,17,21,24,32,36,42,45,49,63,64,74,80],
    "Extroversao": [3,11,18,19,23,30,39,41,43,46,48,51,53,55,73],
    "Amabilidade": [4,8,14,20,26,33,35,52,54,58,59,60],
    "Neuroticismo": [5,10,13,28,29,31,34,37,50,62,65,67,75],
    "Seguranca": [6,22,56,66,72,78],
    "Abundancia": [47,68,70,76,77,79],
}

REVERSED_ITEMS = {6,16,19,22,26,28,34,35,59,62,70,77,80}

def gerar_perfil(respostas):
    df = pd.DataFrame(list(respostas.items()), columns=["Q","Score"])
    df["ScoreCorrigido"] = df.apply(
        lambda r: 6-r["Score"] if r["Q"] in REVERSED_ITEMS else r["Score"], axis=1
    )

    medias = {
        eixo: round(df[df["Q"].isin(qs)]["ScoreCorrigido"].mean(),2)
        for eixo,qs in AXIS_MAP.items()
    }

    return {
        "medias": medias,
        "respostas": respostas
    }

# =========================
# PROMPT V4.8 (FORTE)
# =========================
def gerar_relatorio(perfil):
    client = get_openai_client()
    if client is None:
        return "Erro API"

    prompt = f"""
Você está analisando uma pessoa real.

DADOS:
{perfil}

REGRAS:
- NÃO suavize
- NÃO use "pode", "talvez", "em alguns casos"
- Use linguagem direta: "você faz", "isso acontece"

OBRIGATÓRIO:
- incluir liderança
- incluir opinião em público
- incluir conflito
- incluir dinheiro
- incluir decisões reais

FORMATO:
Sempre:
→ comportamento
→ situação real
→ vantagem
→ custo

Se a pessoa evita liderança, diga claramente.
Se evita opinião pública, diga claramente.

Objetivo:
A pessoa deve pensar: "isso sou eu".
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.6,
    )

    return response.choices[0].message.content

# =========================
# UI
# =========================
st.title("🧠 Mind Insight Advanced AI")

# =========================
# STEP 1 - ESCOLHA DO MODO
# =========================
if not st.session_state.mode_selected:

    st.subheader("Escolha o modo")

    escolha = st.radio(
        "Como deseja prosseguir?",
        ["Usar respostas salvas (modo rápido)", "Responder manualmente"]
    )

    if st.button("Continuar"):

        st.session_state.mode_selected = True

        if "salvas" in escolha:
            st.session_state.responses = HARDCODED.copy()
            st.session_state.current_question = 81
        else:
            st.session_state.current_question = 1

        st.rerun()

# =========================
# PERGUNTAS
# =========================
elif st.session_state.current_question <= 80:

    q = st.session_state.current_question

    st.subheader(f"Pergunta {q}/80")
    st.write(questions[q])

    resposta = st.radio("Resposta:", scale, index=None)

    if st.button("Próxima"):
        if resposta:
            st.session_state.responses[q] = int(resposta.split(" ")[0])
            st.session_state.current_question += 1
            st.rerun()
        else:
            st.warning("Selecione uma resposta")

# =========================
# RESULTADO
# =========================
else:

    perfil = gerar_perfil(st.session_state.responses)

    with st.spinner("Gerando análise..."):
        relatorio = gerar_relatorio(perfil)

    st.markdown(relatorio)

    if st.button("Refazer"):
        st.session_state.responses = {}
        st.session_state.current_question = 0
        st.session_state.mode_selected = False
        st.rerun()