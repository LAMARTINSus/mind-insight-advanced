import streamlit as st
import pandas as pd
from openai import OpenAI

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Mind Insight Advanced AI", layout="wide")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# =========================
# SESSION STATE
# =========================
if "responses" not in st.session_state:
    st.session_state.responses = {}

if "current_question" not in st.session_state:
    st.session_state.current_question = 1

# =========================
# QUESTIONS
# =========================
questions = {i: f"Pergunta {i}" for i in range(1, 81)}

scale = [1, 2, 3, 4, 5]

# =========================
# ENGINE (SIMPLIFICADA)
# =========================
def gerar_perfil(respostas):

    df = pd.DataFrame(list(respostas.items()), columns=["Q", "Score"])

    blocos = {
        "Abertura": (1, 15),
        "Consciencia": (16, 27),
        "Extroversao": (28, 37),
        "Amabilidade": (38, 49),
        "Neuroticismo": (50, 61),
        "Seguranca": (62, 71),
        "Abundancia": (72, 80),
    }

    medias = {
        k: round(df[(df["Q"] >= i) & (df["Q"] <= f)]["Score"].mean(), 2)
        for k, (i, f) in blocos.items()
    }

    perfil = {
        "energia_social": "baixa" if medias["Extroversao"] < 3 else "alta",
        "forma_decisao": "analitica" if medias["Abertura"] >= 3 else "pratica",
        "nivel_estrutura": "alto" if medias["Consciencia"] >= 3.5 else "baixo",
        "sensibilidade_emocional": "alta" if medias["Neuroticismo"] >= 3 else "baixa",
        "tendencia_relacional": "adaptativa" if medias["Amabilidade"] >= 3 else "direta",
        "relacao_dinheiro": "seguranca" if medias["Seguranca"] > medias["Abundancia"] else "expansao"
    }

    return perfil

# =========================
# AI REPORT
# =========================
def gerar_relatorio(perfil):

    prompt = f"""
Você é um especialista em comportamento humano.

Escreva um relatório profundo, humano e altamente preciso.

IMPORTANTE:
- Não use frases genéricas
- Não escreva como teste
- Fale diretamente com a pessoa
- Traga nuances e contradições
- Gere identificação emocional real

Perfil:
{perfil}

Estrutura:
1. Como essa pessoa funciona
2. Como pensa e decide
3. Como se relaciona
4. Dinâmica interna
5. Conflitos principais
6. Forças reais
7. Pontos de atenção
8. Direção de crescimento

Escreva em português.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )

    return response.choices[0].message.content

# =========================
# UI
# =========================
st.title("🧠 Mind Insight Advanced AI")

if st.session_state.current_question <= 80:

    q = st.session_state.current_question

    st.subheader(f"Pergunta {q}/80")
    st.write(questions[q])

    resposta = st.radio("Resposta:", scale, index=None, key=f"q_{q}")

    if st.button("Próxima"):
        if resposta is not None:
            st.session_state.responses[q] = resposta
            st.session_state.current_question += 1
            st.rerun()
        else:
            st.warning("Selecione uma resposta")

else:

    st.title("🪞 Seu Relatório")

    perfil = gerar_perfil(st.session_state.responses)

    with st.spinner("🧠 Gerando leitura profunda..."):
        relatorio = gerar_relatorio(perfil)

    st.markdown(relatorio)

    if st.button("🔄 Refazer"):
        st.session_state.responses = {}
        st.session_state.current_question = 1
        st.rerun()
