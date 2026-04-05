import streamlit as st
import pandas as pd
from openai import OpenAI

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
# QUESTIONS
# =========================
questions = {
    i: f"Pergunta {i}" for i in range(1, 81)
}

scale = [
    "1 - Discordo totalmente",
    "2 - Discordo",
    "3 - Neutro",
    "4 - Concordo",
    "5 - Concordo totalmente",
]

# =========================
# ENGINE
# =========================
def gerar_perfil(respostas: dict) -> dict:
    df = pd.DataFrame(list(respostas.items()), columns=["Q", "Score"])

    df["Score"] = df["Score"].apply(
        lambda x: int(str(x).split(" - ")[0]) if isinstance(x, str) else int(x)
    )

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

    media_geral = round(df["Score"].mean(), 2)
    desvio_padrao = round(float(df["Score"].std(ddof=0)), 3)
    amplitude = int(df["Score"].max() - df["Score"].min())

    eixo_mais_alto = max(medias, key=medias.get)
    eixo_mais_baixo = min(medias, key=medias.get)

    perfil = {
        "medias": medias,
        "media_geral": media_geral,
        "desvio_padrao": desvio_padrao,
        "amplitude": amplitude,
        "eixo_mais_alto": eixo_mais_alto,
        "eixo_mais_baixo": eixo_mais_baixo,
    }

    return perfil

# =========================
# AI REPORT V4.2
# =========================
def gerar_relatorio(perfil: dict) -> str:
    client = get_openai_client()
    if client is None:
        return "Erro: OPENAI_API_KEY não encontrada em Secrets."

    prompt = f"""
Você é um especialista em leitura comportamental.

Sua função é gerar um retrato humano preciso, concreto e útil.

DADOS:
{perfil}

REGRAS:

1. Não invente traços que não estão sustentados nos dados.
2. Não use linguagem genérica.
3. Não escreva como teste.
4. Toda afirmação deve poder ser observada no comportamento.
5. Não romantize.
6. Não use frases vagas como "pode indicar".
7. Use exemplos reais de comportamento.
8. Mostre consequências práticas.
9. Sempre inclua:
   - fortaleza (quando funciona)
   - desafio (quando limita)

ESTRUTURA:

1. COMO VOCÊ FUNCIONA DE VERDADE  
Descreva comportamento visível.

2. COMO VOCÊ TOMA DECISÕES  
Mostre onde funciona e onde trava.

3. COMO VOCÊ SE RELACIONA  
Mostre comportamento real com pessoas.

4. DINÂMICA INTERNA  
Descreva padrão mental/emocional sem exagerar.

5. SEU PADRÃO MAIS FORTE  
Use o eixo mais alto e mostre como aparece na prática.

6. SUAS FORTALEZAS REAIS  
Específicas e aplicáveis.

7. SUAS ÁREAS DE DESAFIO  
Mostre impacto real na vida.

8. O PONTO MAIS IMPORTANTE  
Aprofunde sem suavizar.

9. DIREÇÃO PRÁTICA  
Simples, aplicável, direto.

ESTILO:
- direto
- humano
- específico
- sem clichê
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Erro ao gerar relatório:\n\n{str(e)}"

# =========================
# UI
# =========================
st.title("🧠 Mind Insight Advanced AI")

if st.session_state.current_question <= 80:
    q = st.session_state.current_question

    st.subheader(f"Pergunta {q}/80")
    st.write(questions[q])

    resposta = st.radio(
        "Resposta:",
        scale,
        index=None,
        key=f"q_{q}",
    )

    if st.button("Próxima"):
        if resposta is not None:
            valor = int(resposta.split(" - ")[0])
            st.session_state.responses[q] = valor
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