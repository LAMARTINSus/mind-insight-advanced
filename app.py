# =========================
# VERSION: V4.4
# Base: V4.1
# Changes: Prompt refinado (mais concreto + mais humano + mais preciso)
# =========================

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
# QUESTIONS (INALTERADAS)
# =========================
questions = {
    1: "Gosto de experimentar novas ideias e atividades.",
    2: "Sou organizado e planejo minhas tarefas com antecedência.",
    3: "Me sinto energizado em grupos grandes de pessoas.",
    4: "Sou compassivo e priorizo as necessidades dos outros.",
    5: "Fico ansioso em situações de incerteza.",
    6: "Prefiro rotinas previsíveis a mudanças inesperadas.",
    7: "Tenho facilidade para me concentrar em uma tarefa por horas.",
    8: "Evito conflitos para manter a harmonia.",
    9: "Sou criativo e penso fora da caixa.",
    10: "Me irrito facilmente com erros alheios.",
    11: "Gosto de ser o centro das atenções.",
    12: "Sou disciplinado com prazos e compromissos.",
    13: "Me preocupo excessivamente com o futuro.",
    14: "Valorizo a lealdade acima de tudo nas relações.",
    15: "Busco conhecimento por prazer, não por obrigação.",
    16: "Tomo decisões rápidas baseadas em intuição.",
    17: "Analiso todos os detalhes antes de agir.",
    18: "Sou direto e falo o que penso, mesmo que incomode.",
    19: "Prefiro trabalhar sozinho a em equipe.",
    20: "Adapto meu comportamento conforme o ambiente.",
    21: "Sou persistente mesmo diante de fracassos.",
    22: "Evito riscos desnecessários.",
    23: "Expresso emoções abertamente.",
    24: "Planejo conversas importantes com antecedência.",
    25: "Sou flexível com mudanças de planos.",
    26: "Priorizo eficiência acima de relações.",
    27: "Aprendo mais observando do que fazendo.",
    28: "Em crises, mantenho a calma e foco na solução.",
    29: "Fico paralisado quando algo dá errado.",
    30: "Sob estresse, busco apoio de outros.",
    31: "Reajo com raiva quando provocado.",
    32: "Transformo pressão em motivação.",
    33: "Evito confrontos diretos em tensões.",
    34: "Recupero equilíbrio emocional rapidamente.",
    35: "Culpo os outros por meus erros.",
    36: "Aumento a produtividade sob prazos apertados.",
    37: "Fico ansioso com críticas.",
    38: "Tenho facilidade para aprender novas habilidades técnicas.",
    39: "Sou bom em liderar grupos para resultados.",
    40: "Resolvo problemas matemáticos ou lógicos intuitivamente.",
    41: "Crio conteúdo persuasivo (escrita, vídeo).",
    42: "Organizo espaços e rotinas de forma eficiente.",
    43: "Negocio bem preços e acordos.",
    44: "Sou criativo em soluções cotidianas.",
    45: "Gerencio múltiplas tarefas sem perder o foco.",
    46: "Inspiro confiança em negociações.",
    47: "Identifico oportunidades de negócio rapidamente.",
    48: "Ensino ou explico conceitos complexos com clareza.",
    49: "Melhoro processos existentes de forma inovadora.",
    50: "Meu valor depende da aprovação dos outros.",
    51: "Me sinto confortável em papéis de liderança.",
    52: "Priorizo família acima de carreira.",
    53: "Construo redes de contatos facilmente.",
    54: "Sou influenciado por normas do meu grupo social.",
    55: "Defendo minhas opiniões em debates públicos.",
    56: "Valorizo tradições culturais da minha família.",
    57: "Me adapto bem a culturas diferentes.",
    58: "Sou generoso com tempo e recursos.",
    59: "Competição me motiva mais que colaboração.",
    60: "Meu papel social ideal é de cuidador.",
    61: "Questiono normas sociais estabelecidas.",
    62: "Estou satisfeito com minha vida atual.",
    63: "Sei exatamente o que quero mudar nos próximos 6 meses.",
    64: "Minhas ações diárias me aproximam dos meus objetivos.",
    65: "Sinto que desperdiço potencial.",
    66: "Tenho clareza sobre minha identidade principal.",
    67: "Me comparo frequentemente com outros.",
    68: "Estou em uma fase de crescimento.",
    69: "Visualizo meu 'eu ideal' com detalhes.",
    70: "Falta de recursos me impede de avançar.",
    71: "Sou proativo em buscar mudanças.",
    72: "Dinheiro é fonte de segurança emocional para mim.",
    73: "Gosto de exibir bens para impressionar.",
    74: "Planejo finanças com 5+ anos de visão.",
    75: "Perdas financeiras me afetam por semanas.",
    76: "Sou generoso e dou sem esperar retorno.",
    77: "Prefiro guardar para emergências que investir.",
    78: "Meu trabalho é valorizado financeiramente.",
    79: "Dinheiro 'circula' naturalmente na minha vida.",
    80: "Gastei impulsivamente nos últimos 6 meses."
}

scale = [
    "1 - Discordo totalmente",
    "2 - Discordo",
    "3 - Neutro",
    "4 - Concordo",
    "5 - Concordo totalmente",
]

# =========================
# ENGINE (INALTERADA)
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

    eixo_mais_alto = max(medias, key=medias.get)
    eixo_mais_baixo = min(medias, key=medias.get)

    return {
        "medias": medias,
        "eixo_mais_alto": eixo_mais_alto,
        "eixo_mais_baixo": eixo_mais_baixo,
    }

# =========================
# PROMPT V4.4 (REFINADO)
# =========================
def gerar_relatorio(perfil: dict) -> str:
    client = get_openai_client()
    if client is None:
        return "Erro: OPENAI_API_KEY não encontrada em Secrets."

    prompt = f"""
Você está analisando uma pessoa real.

BASE DE DADOS:
{perfil}

ANTES DE ESCREVER:
- Identifique os eixos mais altos e mais baixos
- Observe contrastes importantes
- Identifique o que diferencia esse perfil

PRINCÍPIO:
Só escreva o que os dados sustentam.

REGRAS:
- Fale sempre em "você"
- Não use linguagem técnica
- Não use frases genéricas
- Não escreva como teste
- Não romantize
- Não invente traços

IMPORTANTE:
Mostre comportamento real em situações:
conversas, decisões, trabalho, dinheiro, relações.

ESTRUTURA:

1. COMO VOCÊ FUNCIONA DE VERDADE
2. COMO VOCÊ TOMA DECISÕES
3. COMO VOCÊ SE RELACIONA
4. O QUE ACONTECE DENTRO DE VOCÊ
5. SEU PADRÃO MAIS FORTE
6. SUAS FORTALEZAS REAIS
7. SUAS ÁREAS DE DESAFIO
8. O PONTO QUE MAIS MERECE ATENÇÃO
9. DIREÇÃO PRÁTICA

ESTILO:
- direto
- humano
- específico
- sem clichê

Faça a pessoa se reconhecer.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
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