# =========================
# VERSION: V4.9
# FOCO: Escrita com comportamento real + situações do cotidiano
# =========================

import streamlit as st
import pandas as pd
from openai import OpenAI

DEBUG_MODE = True

st.set_page_config(page_title="Mind Insight Advanced AI", layout="wide")

def get_openai_client():
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

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

if "responses" not in st.session_state:
    st.session_state.responses = {}
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "mode_selected" not in st.session_state:
    st.session_state.mode_selected = False

questions = {i: f"Pergunta {i}" for i in range(1,81)}

scale = [
    "1 - Discordo totalmente",
    "2 - Discordo",
    "3 - Neutro",
    "4 - Concordo",
    "5 - Concordo totalmente",
]

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
# PROMPT V4.9 (ALTO IMPACTO)
# =========================
def gerar_relatorio(perfil):

    client = get_openai_client()
    if client is None:
        return "Erro API"

    prompt = f"""
Você está analisando uma pessoa real.

DADOS:
{perfil}

ANTES DE ESCREVER:
- Identifique os padrões dominantes
- Identifique os pontos de maior tensão
- Identifique onde essa pessoa SE SABOTA na prática

REGRA MAIS IMPORTANTE:
Você NÃO está descrevendo traços.
Você está descrevendo comportamento real observável.

---

ESCREVA COMO SE:
Você tivesse acompanhado essa pessoa por meses no trabalho, em casa e em situações sociais.

---

PROIBIDO:
- linguagem genérica
- "você tende a"
- "em alguns casos"
- "pode indicar"
- texto de teste psicológico

---

OBRIGATÓRIO:

1. Use situações reais:
- reuniões
- decisões financeiras
- conversas difíceis
- oportunidades perdidas
- momentos de pressão

2. Mostre CONTRADIÇÃO:
- o que a pessoa sabe vs o que ela faz
- onde ela segura vs onde deveria avançar

3. Mostre CUSTO REAL:
- oportunidades perdidas
- espaço que outros ocupam
- decisões que não aconteceram

4. Use padrões do perfil:
- baixa liderança
- baixa exposição
- evita conflito
- adaptação alta
- segurança > expansão

---

ESTRUTURA:

1. COMO VOCÊ FUNCIONA DE VERDADE
(com cenas reais)

2. COMO VOCÊ TOMA DECISÕES
(com exemplos de decisões reais)

3. COMO VOCÊ SE RELACIONA
(com dinâmica social real)

4. O QUE ACONTECE DENTRO DE VOCÊ
(pensamentos reais, não genéricos)

5. SEU PADRÃO MAIS FORTE
(mostrar repetição na vida real)

6. SUAS FORTALEZAS REAIS
(concretas, observáveis)

7. SUAS ÁREAS DE DESAFIO
(sem suavizar)

8. O PONTO CENTRAL
(um só — o mais crítico)

9. DIREÇÃO PRÁTICA
(orientações específicas, não clichê)

---

ESTILO:
- direto
- humano
- específico
- sem floreio
- sem parecer relatório

---

RESULTADO FINAL:
A pessoa deve ler e pensar:

"isso aconteceu comigo"
"isso sou eu"
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.65,
    )

    return response.choices[0].message.content


# =========================
# UI
# =========================
st.title("🧠 Mind Insight Advanced AI")

if not st.session_state.mode_selected:

    escolha = st.radio(
        "Modo:",
        ["Usar respostas salvas", "Responder manualmente"]
    )

    if st.button("Continuar"):
        st.session_state.mode_selected = True

        if "salvas" in escolha:
            st.session_state.responses = HARDCODED.copy()
            st.session_state.current_question = 81
        else:
            st.session_state.current_question = 1

        st.rerun()

elif st.session_state.current_question <= 80:

    q = st.session_state.current_question
    st.write(questions[q])

    resposta = st.radio("Resposta:", scale, index=None)

    if st.button("Próxima"):
        if resposta:
            st.session_state.responses[q] = int(resposta.split(" ")[0])
            st.session_state.current_question += 1
            st.rerun()

else:

    perfil = gerar_perfil(st.session_state.responses)

    relatorio = gerar_relatorio(perfil)

    st.markdown(relatorio)

    if st.button("Refazer"):
        st.session_state.responses = {}
        st.session_state.current_question = 0
        st.session_state.mode_selected = False
        st.rerun()
