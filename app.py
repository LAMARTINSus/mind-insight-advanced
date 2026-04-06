# =========================
# VERSION: V4.8 CORRIGIDA
# Base: V4.6 + modo rápido
# Changes:
# - Debug restaurado
# - Prompt mais humano e menos mecânico
# - Mantidas perguntas originais, engine corrigida e respostas hardcoded
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
    1:4, 2:1, 3:3, 4:4, 5:4, 6:4, 7:1, 8:5, 9:4, 10:3,
    11:1, 12:4, 13:3, 14:5, 15:5, 16:3, 17:4, 18:1, 19:5, 20:4,
    21:3, 22:4, 23:5, 24:3, 25:5, 26:1, 27:1, 28:4, 29:3, 30:4,
    31:3, 32:1, 33:5, 34:3, 35:1, 36:5, 37:4, 38:4, 39:1, 40:3,
    41:3, 42:4, 43:5, 44:4, 45:1, 46:5, 47:4, 48:4, 49:4, 50:1,
    51:1, 52:5, 53:4, 54:3, 55:1, 56:5, 57:4, 58:4, 59:1, 60:4,
    61:3, 62:1, 63:4, 64:4, 65:5, 66:5, 67:3, 68:5, 69:4, 70:5,
    71:4, 72:5, 73:3, 74:1, 75:3, 76:4, 77:5, 78:1, 79:1, 80:1
}

# =========================
# SESSION STATE
# =========================
if "responses" not in st.session_state:
    st.session_state.responses = {}

if "current_question" not in st.session_state:
    st.session_state.current_question = 0  # começa na escolha de modo

if "mode_selected" not in st.session_state:
    st.session_state.mode_selected = False

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

REVERSED_ITEMS = {6, 16, 19, 22, 26, 28, 34, 35, 59, 62, 70, 77, 80}

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

    temas = {
        "lideranca_baixa": respostas.get(51, 3) <= 2,
        "opiniao_publica_baixa": respostas.get(55, 3) <= 2,
        "evita_conflito": respostas.get(8, 3) >= 4,
        "adaptacao_alta": respostas.get(20, 3) >= 4,
        "aversao_risco": respostas.get(22, 3) >= 4,
    }

    flags = []
    if medias["Seguranca"] > medias["Abundancia"]:
        flags.append("mais orientação à segurança do que à expansão")
    if medias["Amabilidade"] > medias["Extroversao"]:
        flags.append("mais adaptação relacional do que impulso de exposição")
    if medias["Abundancia"] < 3:
        flags.append("baixa percepção de abundância")
    if medias["Neuroticismo"] >= 3:
        flags.append("sensibilidade emocional presente")
    if medias["Extroversao"] < 3.2:
        flags.append("exposição social mais seletiva do que expansiva")

    hipotese_tecnica = []
    if medias["Seguranca"] > medias["Abundancia"]:
        hipotese_tecnica.append("tendência a preservar estabilidade antes de explorar oportunidade")
    if medias["Amabilidade"] > medias["Extroversao"]:
        hipotese_tecnica.append("tendência a manter harmonia relacional acima de autoexposição")
    if medias["Abundancia"] < 3:
        hipotese_tecnica.append("possível restrição na relação com expansão, valor ou oportunidade")
    if respostas.get(51, 3) <= 2:
        hipotese_tecnica.append("baixa disposição para liderança pública ou papéis de comando visível")
    if respostas.get(55, 3) <= 2:
        hipotese_tecnica.append("baixa tendência a defender opinião em contexto público ou de debate")

    respostas_brutas = dict(sorted(respostas.items()))
    respostas_corrigidas = {
        int(row["Q"]): int(row["ScoreCorrigido"])
        for _, row in df.sort_values("Q").iterrows()
    }

    extremos_altos = [int(q) for q in df[df["ScoreCorrigido"] >= 4]["Q"].tolist()]
    extremos_baixos = [int(q) for q in df[df["ScoreCorrigido"] <= 2]["Q"].tolist()]

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
        "extremos_altos": extremos_altos,
        "extremos_baixos": extremos_baixos,
        "temas_criticos": temas,
    }

# =========================
# PROMPT V4.8 CORRIGIDO
# =========================
def gerar_relatorio(perfil: dict) -> str:
    client = get_openai_client()
    if client is None:
        return "Erro: OPENAI_API_KEY não encontrada em Secrets."

    prompt = f"""
Você está analisando uma pessoa real.

BASE TÉCNICA:
{perfil}

ANTES DE ESCREVER:
- Identifique o eixo mais alto e o mais baixo
- Observe os principais contrastes
- Observe os temas críticos
- Observe os itens extremos que merecem aparecer no texto

PRINCÍPIO:
Só escreva o que os dados sustentam.
Não invente biografia, trauma, passado ou motivação escondida.

REGRAS CRÍTICAS:
- Fale sempre em "você"
- Não use linguagem técnica
- Não use frases genéricas
- Não escreva como teste
- Não escreva em blocos repetitivos como "comportamento / vantagem / custo"
- Não suavize demais
- Não transforme tudo em cautela genérica
- Se houver baixa liderança, baixa defesa de opinião pública, aversão a confronto ou adaptação excessiva, isso deve aparecer de forma clara

OBRIGATÓRIO:
- incluir situações do cotidiano
- incluir decisões reais
- incluir comportamento em grupo
- incluir trabalho
- incluir dinheiro/oportunidade
- incluir liderança
- incluir opinião pública
- incluir confronto
- incluir adaptação vs imposição
- incluir risco vs segurança

ESTRUTURA OBRIGATÓRIA:

1. COMO VOCÊ FUNCIONA DE VERDADE
Descreva como você entra em ambientes, reage, se posiciona e administra sua energia.

2. COMO VOCÊ TOMA DECISÕES
Mostre onde você decide bem e onde tende a adiar, evitar ou ceder.

3. COMO VOCÊ SE RELACIONA
Mostre como você cria conexão, onde se adapta demais e onde pode perder espaço.

4. O QUE ACONTECE DENTRO DE VOCÊ
Descreva pensamentos, tensões e padrões internos que os dados realmente sustentam.

5. SEU PADRÃO MAIS FORTE
Use o eixo mais alto e mostre como ele aparece em diferentes situações reais.

6. SUAS FORTALEZAS REAIS
Liste fortalezas específicas, em linguagem concreta, mostrando como elas aparecem na prática.

7. SUAS ÁREAS DE DESAFIO
Mostre o custo real dos padrões, sem suavizar demais.

8. O PONTO QUE MAIS MERECE ATENÇÃO
Escolha o ponto central mais custoso e aprofunde com clareza.

9. DIREÇÃO PRÁTICA
Dê orientações claras, úteis e aplicáveis.

ESTILO:
- direto
- humano
- específico
- vivo
- sem clichê
- sem floreio
- sem parecer relatório corporativo

Faça a pessoa pensar: "isso sou eu".
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
    st.caption("Mostra a resposta registrada em cada pergunta.")
    st.json(perfil["respostas_brutas"])

    st.subheader("2. Respostas corrigidas")
    st.caption("Mostra as respostas após aplicar inversão nos itens invertidos.")
    st.json(perfil["respostas_corrigidas"])

    st.subheader("3. Itens invertidos")
    st.caption("Perguntas cuja pontuação foi revertida.")
    st.write(perfil["itens_invertidos"])

    st.subheader("4. Médias por eixo")
    st.caption("Mostra a média corrigida de cada eixo.")
    st.json(perfil["medias"])

    st.subheader("5. Quantidade de itens por eixo")
    st.caption("Mostra quantas perguntas estão alimentando cada eixo.")
    st.json(perfil["contagem_itens"])

    st.subheader("6. Eixo mais alto e mais baixo")
    st.write(f"**Eixo mais alto:** {perfil['eixo_mais_alto']}")
    st.write(f"**Eixo mais baixo:** {perfil['eixo_mais_baixo']}")

    st.subheader("7. Top 3 altos e Top 3 baixos")
    st.write("**Top 3 altos:**")
    for eixo, valor in perfil["top3_altos"]:
        st.write(f"- {eixo}: {valor}")
    st.write("**Top 3 baixos:**")
    for eixo, valor in perfil["top3_baixos"]:
        st.write(f"- {eixo}: {valor}")

    st.subheader("8. Diferenças entre eixos")
    st.json(perfil["diferencas"])

    st.subheader("9. Qualidade do dado")
    st.write(f"**Média geral:** {perfil['media_geral']}")
    st.write(f"**Desvio padrão:** {perfil['desvio_padrao']}")
    st.write(f"**Amplitude:** {perfil['amplitude']}")
    st.write(f"**Tipo de resposta:** {perfil['tipo_resposta']}")
    st.write(f"**Confiabilidade:** {perfil['confiabilidade']}")

    st.subheader("10. Extremos altos")
    st.write(perfil["extremos_altos"])

    st.subheader("11. Extremos baixos")
    st.write(perfil["extremos_baixos"])

    st.subheader("12. Temas críticos")
    st.json(perfil["temas_criticos"])

    st.subheader("13. Flags de atenção")
    for item in perfil["flags"]:
        st.write(f"- {item}")

    st.subheader("14. Hipótese técnica")
    for item in perfil["hipotese_tecnica"]:
        st.write(f"- {item}")

# =========================
# UI
# =========================
st.title("🧠 Mind Insight Advanced AI")

# Escolha de modo
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

elif st.session_state.current_question <= 80:
    q = st.session_state.current_question
    st.subheader(f"Pergunta {q}/80")
    st.write(questions[q])

    resposta = st.radio("Resposta:", scale, index=None, key=f"q_{q}")

    if st.button("Próxima"):
        if resposta is not None:
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
        st.session_state.current_question = 0
        st.session_state.mode_selected = False
        st.rerun()