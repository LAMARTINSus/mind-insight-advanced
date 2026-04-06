# =========================
# VERSION: V4.7
# Base: V4.6
# Changes:
# - Camada de sinais salientes (itens extremos)
# - Prompt com exigência de situações reais
# - Inclusão de liderança, opinião, confronto
# - Debug ampliado
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
# SESSION STATE
# =========================
if "responses" not in st.session_state:
    st.session_state.responses = {}

if "current_question" not in st.session_state:
    st.session_state.current_question = 1

# =========================
# QUESTIONS (INALTERADAS)
# =========================
questions = { ... }  # (mantido igual V4.6 para não alterar nada)

scale = [
    "1 - Discordo totalmente",
    "2 - Discordo",
    "3 - Neutro",
    "4 - Concordo",
    "5 - Concordo totalmente",
]

# =========================
# ESTRUTURA
# =========================
AXIS_MAP = { ... }  # (igual V4.6)

REVERSED_ITEMS = {6,16,19,22,26,28,34,35,59,62,70,77,80}

# =========================
# ENGINE
# =========================
def gerar_perfil(respostas: dict) -> dict:
    df = pd.DataFrame(list(respostas.items()), columns=["Q", "Score"])

    df["Score"] = df["Score"].apply(
        lambda x: int(str(x).split(" - ")[0]) if isinstance(x, str) else int(x)
    )

    df["ScoreOriginal"] = df["Score"]

    df["ScoreCorrigido"] = df.apply(
        lambda row: 6 - row["Score"] if row["Q"] in REVERSED_ITEMS else row["Score"],
        axis=1,
    )

    # =========================
    # MÉDIAS
    # =========================
    medias = {}
    for eixo, perguntas in AXIS_MAP.items():
        medias[eixo] = round(
            df[df["Q"].isin(perguntas)]["ScoreCorrigido"].mean(), 2
        )

    # =========================
    # EXTREMOS (NOVO)
    # =========================
    extremos_altos = df[df["ScoreCorrigido"] >= 4]
    extremos_baixos = df[df["ScoreCorrigido"] <= 2]

    sinais_altos = [int(q) for q in extremos_altos["Q"].tolist()]
    sinais_baixos = [int(q) for q in extremos_baixos["Q"].tolist()]

    # =========================
    # DETECÇÃO DE TEMAS CRÍTICOS (NOVO)
    # =========================
    temas = {
        "lideranca_baixa": respostas.get(51, 3) <= 2,
        "opiniao_publica_baixa": respostas.get(55, 3) <= 2,
        "evita_conflito": respostas.get(8, 3) >= 4,
        "adaptacao_alta": respostas.get(20, 3) >= 4,
        "aversao_risco": respostas.get(22, 3) >= 4,
    }

    eixo_mais_alto = max(medias, key=medias.get)
    eixo_mais_baixo = min(medias, key=medias.get)

    return {
        "medias": medias,
        "eixo_mais_alto": eixo_mais_alto,
        "eixo_mais_baixo": eixo_mais_baixo,
        "extremos_altos": sinais_altos,
        "extremos_baixos": sinais_baixos,
        "temas_criticos": temas,
        "respostas_brutas": respostas,
    }

# =========================
# PROMPT V4.7
# =========================
def gerar_relatorio(perfil: dict) -> str:
    client = get_openai_client()
    if client is None:
        return "Erro: API KEY não encontrada."

    prompt = f"""
Você está analisando uma pessoa real.

BASE:
{perfil}

REGRA CENTRAL:
Mostre comportamento real. Não descreva traço abstrato.

OBRIGATÓRIO:
- Usar situações do cotidiano
- Mostrar decisões reais
- Mostrar conversas reais
- Mostrar comportamento em grupo
- Mostrar comportamento em trabalho
- Mostrar comportamento em dinheiro/oportunidade

INCLUA OBRIGATORIAMENTE:
- liderança (mesmo que baixa)
- opinião em público
- confronto
- adaptação vs imposição
- risco vs segurança

IMPORTANTE:
Se houver baixa liderança ou baixa exposição, você DEVE falar disso claramente.

FORMATO:
Cada ponto deve seguir:
→ o que você faz
→ quando isso aparece
→ onde funciona
→ onde custa

NÃO USE:
- frases genéricas
- linguagem técnica
- texto neutro

ESTRUTURA:

1 COMO VOCÊ FUNCIONA DE VERDADE
2 COMO VOCÊ TOMA DECISÕES
3 COMO VOCÊ SE RELACIONA
4 O QUE ACONTECE DENTRO DE VOCÊ
5 SEU PADRÃO MAIS FORTE
6 SUAS FORTALEZAS REAIS
7 SUAS ÁREAS DE DESAFIO
8 O PONTO MAIS IMPORTANTE
9 DIREÇÃO PRÁTICA

ESTILO:
Direto. Humano. Específico. Sem clichê.

A pessoa deve pensar:
"como você sabe disso?"
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
    )

    return response.choices[0].message.content

# =========================
# DEBUG
# =========================
def render_debug(perfil):
    st.markdown("---")
    st.header("🔍 Debug técnico")

    st.subheader("Extremos altos")
    st.write(perfil["extremos_altos"])

    st.subheader("Extremos baixos")
    st.write(perfil["extremos_baixos"])

    st.subheader("Temas críticos")
    st.json(perfil["temas_criticos"])

    st.subheader("Médias")
    st.json(perfil["medias"])

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
        if resposta:
            st.session_state.responses[q] = int(resposta.split(" - ")[0])
            st.session_state.current_question += 1
            st.rerun()
        else:
            st.warning("Selecione uma resposta")

else:
    perfil = gerar_perfil(st.session_state.responses)

    with st.spinner("Gerando relatório..."):
        relatorio = gerar_relatorio(perfil)

    st.markdown(relatorio)

    if DEBUG_MODE:
        render_debug(perfil)

    if st.button("Refazer"):
        st.session_state.responses = {}
        st.session_state.current_question = 1
        st.rerun()