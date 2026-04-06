# =========================
# VERSION: V4.6
# Base: V4.5 DEBUG
# Changes:
# - Reclassificação estrutural dos 80 itens
# - Itens invertidos aplicados
# - Debug técnico mantido
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
# ESTRUTURA CORRIGIDA
# =========================
AXIS_MAP = {
    "Abertura": [1, 9, 15, 16, 25, 27, 38, 40, 44, 57, 61, 69, 71],
    "Consciencia": [2, 7, 12, 17, 21, 24, 32, 36, 42, 45, 49, 63, 64, 74, 80],
    "Extroversao": [3, 11, 18, 19, 23, 30, 39, 41, 43, 46, 48, 51, 53, 55, 73],
    "Amabilidade": [4, 8, 14, 20, 26, 33, 35, 52, 54, 58, 59, 60],
    "Neuroticismo": [5, 10, 13, 28, 29, 31, 34, 37, 50, 62, 65, 67, 75],
    "Seguranca": [6, 22, 56, 66, 72, 78],
    "Abundancia": [47, 68, 70, 76, 77, 79],
}

# Itens invertidos: score_invertido = 6 - score
REVERSED_ITEMS = {6, 16, 19, 22, 26, 28, 34, 35, 59, 62, 70, 77, 80}

# =========================
# ENGINE
# =========================
def gerar_perfil(respostas: dict) -> dict:
    df = pd.DataFrame(list(respostas.items()), columns=["Q", "Score"])
    df["Score"] = df["Score"].apply(
        lambda x: int(str(x).split(" - ")[0]) if isinstance(x, str) else int(x)
    )

    # Guarda score original e score corrigido para debug
    df["ScoreOriginal"] = df["Score"]
    df["ScoreCorrigido"] = df.apply(
        lambda row: 6 - row["Score"] if row["Q"] in REVERSED_ITEMS else row["Score"],
        axis=1,
    )

    medias = {}
    contagem_itens = {}

    for eixo, perguntas in AXIS_MAP.items():
        subset = df[df["Q"].isin(perguntas)]["ScoreCorrigido"]
        medias[eixo] = round(subset.mean(), 2)
        contagem_itens[eixo] = len(perguntas)

    eixo_mais_alto = max(medias, key=medias.get)
    eixo_mais_baixo = min(medias, key=medias.get)

    ranking_alto = sorted(medias.items(), key=lambda x: x[1], reverse=True)
    ranking_baixo = sorted(medias.items(), key=lambda x: x[1])

    diferencas = {
        "Seguranca_vs_Abundancia": round(medias["Seguranca"] - medias["Abundancia"], 2),
        "Amabilidade_vs_Extroversao": round(medias["Amabilidade"] - medias["Extroversao"], 2),
        "Consciencia_vs_Abertura": round(medias["Consciencia"] - medias["Abertura"], 2),
        "Neuroticismo_vs_Extroversao": round(medias["Neuroticismo"] - medias["Extroversao"], 2),
    }

    media_geral = round(df["ScoreCorrigido"].mean(), 2)
    desvio_padrao = round(float(df["ScoreCorrigido"].std(ddof=0)), 3)
    amplitude = int(df["ScoreCorrigido"].max() - df["ScoreCorrigido"].min())

    tipo_resposta = "discriminante"
    if desvio_padrao == 0 and media_geral == 3:
        tipo_resposta = "neutro_uniforme"
    elif desvio_padrao == 0 and media_geral >= 4.5:
        tipo_resposta = "inflado_uniforme"
    elif desvio_padrao == 0 and media_geral <= 1.5:
        tipo_resposta = "retraido_uniforme"
    elif desvio_padrao < 0.5 and amplitude <= 1:
        tipo_resposta = "baixa_discriminacao"

    confiabilidade = "alta"
    if tipo_resposta in ["neutro_uniforme", "inflado_uniforme", "retraido_uniforme"]:
        confiabilidade = "baixa"
    elif tipo_resposta == "baixa_discriminacao":
        confiabilidade = "média"

    flags = []
    if medias["Seguranca"] > medias["Abundancia"]:
        flags.append("mais orientação à segurança do que à expansão")
    if medias["Amabilidade"] > medias["Extroversao"]:
        flags.append("mais adaptação relacional do que impulso de exposição")
    if medias["Abundancia"] < 3:
        flags.append("baixa percepção de abundância")
    if medias["Neuroticismo"] >= 3:
        flags.append("sensibilidade emocional presente")
    if medias["Consciencia"] >= 3.3:
        flags.append("boa capacidade de estrutura e execução")
    if medias["Extroversao"] < 3.2:
        flags.append("exposição social mais seletiva do que expansiva")

    hipotese_tecnica = []
    if medias["Seguranca"] > medias["Abundancia"]:
        hipotese_tecnica.append("tendência a preservar estabilidade antes de explorar oportunidade")
    if medias["Amabilidade"] > medias["Extroversao"]:
        hipotese_tecnica.append("tendência a manter harmonia relacional acima de autoexposição")
    if medias["Abundancia"] < 3:
        hipotese_tecnica.append("possível restrição na relação com expansão, valor ou oportunidade")
    if medias["Consciencia"] >= 3.3:
        hipotese_tecnica.append("capacidade consistente de organizar, sustentar e entregar")
    if medias["Extroversao"] < 3.2:
        hipotese_tecnica.append("presença social mais medida do que espontaneamente expansiva")

    respostas_brutas = dict(sorted(respostas.items()))
    respostas_corrigidas = {
        int(row["Q"]): int(row["ScoreCorrigido"]) for _, row in df.sort_values("Q").iterrows()
    }

    return {
        "medias": medias,
        "contagem_itens": contagem_itens,
        "eixo_mais_alto": eixo_mais_alto,
        "eixo_mais_baixo": eixo_mais_baixo,
        "top3_altos": ranking_alto[:3],
        "top3_baixos": ranking_baixo[:3],
        "diferencas": diferencas,
        "media_geral": media_geral,
        "desvio_padrao": desvio_padrao,
        "amplitude": amplitude,
        "tipo_resposta": tipo_resposta,
        "confiabilidade": confiabilidade,
        "flags": flags,
        "hipotese_tecnica": hipotese_tecnica,
        "respostas_brutas": respostas_brutas,
        "respostas_corrigidas": respostas_corrigidas,
        "itens_invertidos": sorted(REVERSED_ITEMS),
    }

# =========================
# PROMPT
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
# DEBUG RENDER
# =========================
def render_debug(perfil: dict):
    st.markdown("---")
    st.header("🔍 Debug técnico do perfil")

    st.subheader("1. Respostas brutas")
    st.caption("Mostra a resposta registrada em cada pergunta, exatamente como você marcou.")
    st.json(perfil["respostas_brutas"])

    st.subheader("2. Respostas corrigidas")
    st.caption("Mostra as respostas após aplicar inversão nos itens invertidos. Isso ajuda a verificar se a correção semântica foi feita corretamente.")
    st.json(perfil["respostas_corrigidas"])

    st.subheader("3. Itens invertidos")
    st.caption("Perguntas cuja pontuação foi revertida pela regra: score corrigido = 6 - score.")
    st.write(perfil["itens_invertidos"])

    st.subheader("4. Médias por eixo")
    st.caption("Mostra a média corrigida de cada eixo. Isso revela quais áreas estão mais altas e mais baixas.")
    st.json(perfil["medias"])

    st.subheader("5. Quantidade de itens por eixo")
    st.caption("Mostra quantas perguntas estão alimentando cada eixo na nova estrutura.")
    st.json(perfil["contagem_itens"])

    st.subheader("6. Eixo mais alto e mais baixo")
    st.caption("Mostra o traço com maior média e o traço com menor média.")
    st.write(f"**Eixo mais alto:** {perfil['eixo_mais_alto']}")
    st.write(f"**Eixo mais baixo:** {perfil['eixo_mais_baixo']}")

    st.subheader("7. Top 3 altos e Top 3 baixos")
    st.caption("Mostra os três eixos mais altos e os três mais baixos para facilitar leitura comparativa.")
    st.write("**Top 3 altos:**")
    for eixo, valor in perfil["top3_altos"]:
        st.write(f"- {eixo}: {valor}")
    st.write("**Top 3 baixos:**")
    for eixo, valor in perfil["top3_baixos"]:
        st.write(f"- {eixo}: {valor}")

    st.subheader("8. Diferenças entre eixos")
    st.caption("Ajuda a ver contrastes relevantes, como segurança maior que abundância ou adaptação maior que exposição.")
    st.json(perfil["diferencas"])

    st.subheader("9. Qualidade do dado")
    st.caption("Mostra se as respostas parecem bem discriminadas ou uniformes demais.")
    st.write(f"**Média geral:** {perfil['media_geral']}")
    st.write(f"**Desvio padrão:** {perfil['desvio_padrao']}")
    st.write(f"**Amplitude:** {perfil['amplitude']}")
    st.write(f"**Tipo de resposta:** {perfil['tipo_resposta']}")
    st.write(f"**Confiabilidade:** {perfil['confiabilidade']}")

    st.subheader("10. Flags de atenção")
    st.caption("Alertas simples que resumem padrões relevantes encontrados.")
    for item in perfil["flags"]:
        st.write(f"- {item}")

    st.subheader("11. Hipótese técnica")
    st.caption("Leitura fria e disciplinada que ajuda a entender o que a IA deveria desenvolver no relatório humano.")
    for item in perfil["hipotese_tecnica"]:
        st.write(f"- {item}")

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

    if DEBUG_MODE:
        render_debug(perfil)

    if st.button("🔄 Refazer"):
        st.session_state.responses = {}
        st.session_state.current_question = 1
        st.rerun()