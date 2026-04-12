import streamlit as st
from openai import OpenAI

# 🔐 CONFIGURE SUA API KEY AQUI
client = OpenAI(api_key="COLE_SUA_API_KEY_AQUI")

st.set_page_config(page_title="Teste de Perfil", layout="centered")

st.title("Teste Comportamental")

st.write("Responda as perguntas abaixo de 1 a 5")

# ---------------------------
# PERGUNTAS (EXEMPLO BASE)
# ---------------------------
questions = [
    "Evito conflitos sempre que possível",
    "Prefiro me manter em silêncio em situações difíceis",
    "Tenho dificuldade em dizer não",
    "Falo o que penso mesmo que desagrade",
]

# Armazena respostas
responses = []

for i, q in enumerate(questions):
    r = st.slider(f"{i+1}. {q}", 1, 5, 3)
    responses.append(r)

# ---------------------------
# LÓGICA DE PERFIL
# ---------------------------
def analyze_profile(responses):
    evita_conflito = (responses[0] + responses[1] + responses[2]) / 3
    assertividade = responses[3]

    if evita_conflito > 3.5 and assertividade < 3:
        return "Você tende a evitar conflitos e pode ter dificuldade em se posicionar."
    elif evita_conflito < 2.5 and assertividade > 3.5:
        return "Você é assertivo e se posiciona com facilidade."
    else:
        return "Você possui um perfil equilibrado entre evitar conflitos e assertividade."

# ---------------------------
# BOTÃO DE RESULTADO
# ---------------------------
if st.button("Ver Resultado"):
    resultado = analyze_profile(responses)

    st.subheader("Resultado:")
    st.write(resultado)

    # ---------------------------
    # GPT (RELATÓRIO AVANÇADO)
    # ---------------------------
    prompt = f"""
    O usuário respondeu o seguinte perfil:
    {resultado}

    Gere um relatório comportamental profundo, claro e prático.
    """

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        texto = response.output[0].content[0].text

        st.subheader("Análise Detalhada")
        st.write(texto)

    except Exception as e:
        st.error(f"Erro ao gerar análise: {e}")