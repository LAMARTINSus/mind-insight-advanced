import streamlit as st
from openai import OpenAI

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(page_title="Teste Comportamental", layout="centered")

# ⚠️ COLOQUE SUA API KEY AQUI
client = OpenAI(api_key="SUA_API_KEY_AQUI")

st.title("Teste Comportamental")
st.write("Responda de 1 (Discordo totalmente) a 5 (Concordo totalmente)")

# =========================
# PERGUNTAS (ESTRUTURA ESCALÁVEL)
# =========================

questions = [
    {"text": "Evito conflitos sempre que possível", "trait": "conflito", "reverse": False},
    {"text": "Prefiro me manter em silêncio em situações difíceis", "trait": "conflito", "reverse": False},
    {"text": "Tenho dificuldade em dizer não", "trait": "conflito", "reverse": False},
    {"text": "Falo o que penso mesmo que desagrade", "trait": "assertividade", "reverse": False},
]

responses = []

# =========================
# CAPTURA RESPOSTAS
# =========================

for i, q in enumerate(questions):
    r = st.slider(f"{i+1}. {q['text']}", 1, 5, 3)
    responses.append({
        "value": r,
        "trait": q["trait"],
        "reverse": q["reverse"]
    })

# =========================
# PROCESSAMENTO
# =========================

def process_responses(responses):
    scores = {}

    for r in responses:
        value = r["value"]

        # Correção de inversão (se existir)
        if r["reverse"]:
            value = 6 - value

        trait = r["trait"]

        if trait not in scores:
            scores[trait] = []

        scores[trait].append(value)

    # Média por traço
    final_scores = {k: sum(v)/len(v) for k, v in scores.items()}
    return final_scores

# =========================
# INTERPRETAÇÃO
# =========================

def generate_profile(scores):
    conflito = scores.get("conflito", 0)
    assertividade = scores.get("assertividade", 0)

    if conflito > 3.5 and assertividade < 3:
        return "Perfil evitador de conflitos. Tende a se calar e evitar confrontos."
    
    elif conflito < 2.5 and assertividade > 3.5:
        return "Perfil altamente assertivo. Se posiciona com clareza e firmeza."
    
    else:
        return "Perfil equilibrado entre cautela e assertividade."

# =========================
# BOTÃO RESULTADO
# =========================

if st.button("Ver Resultado"):

    scores = process_responses(responses)

    st.subheader("Pontuação por Perfil")
    for k, v in scores.items():
        st.write(f"{k}: {round(v,2)}")

    profile = generate_profile(scores)

    st.subheader("Resultado")
    st.write(profile)

    # =========================
    # GPT (ANÁLISE AVANÇADA)
    # =========================

    prompt = f"""
    Analise o seguinte perfil comportamental:

    Scores: {scores}
    Interpretação base: {profile}

    Gere uma análise profunda, prática e direta.
    Explique forças, riscos e recomendações claras.
    """

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        analysis = response.output[0].content[0].text

        st.subheader("Análise Avançada")
        st.write(analysis)

    except Exception as e:
        st.error(f"Erro ao gerar análise: {e}")