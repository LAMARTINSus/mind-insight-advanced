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

    def faixa(score: float) -> str:
        if score >= 4.5:
            return "extremamente alto"
        elif score >= 4.0:
            return "alto"
        elif score >= 3.0:
            return "médio"
        elif score >= 2.0:
            return "baixo"
        return "extremamente baixo"

    faixas = {k: faixa(v) for k, v in medias.items()}

    media_geral = round(df["Score"].mean(), 2)
    desvio_padrao = round(float(df["Score"].std(ddof=0)), 3)
    amplitude = int(df["Score"].max() - df["Score"].min())

    valores_unicos = sorted(df["Score"].unique().tolist())
    quantidade_valores_unicos = len(valores_unicos)
    medias_unicas_blocos = len(set(medias.values()))

    tipo_resposta = "discriminante"

    if desvio_padrao == 0 and media_geral == 3:
        tipo_resposta = "neutro_uniforme"
    elif desvio_padrao == 0 and media_geral >= 4.5:
        tipo_resposta = "inflado_uniforme"
    elif desvio_padrao == 0 and media_geral <= 1.5:
        tipo_resposta = "retraido_uniforme"
    elif desvio_padrao < 0.35 and quantidade_valores_unicos <= 2:
        tipo_resposta = "baixa_discriminacao"
    elif desvio_padrao < 0.5 and amplitude <= 1:
        tipo_resposta = "baixa_discriminacao"
    elif media_geral >= 4.3 and desvio_padrao < 0.7:
        tipo_resposta = "inflado"
    elif media_geral <= 1.7 and desvio_padrao < 0.7:
        tipo_resposta = "retraido"
    elif amplitude >= 4 and desvio_padrao >= 1.2:
        tipo_resposta = "muito_variavel"

    confiabilidade = "alta"
    if tipo_resposta in ["neutro_uniforme", "inflado_uniforme", "retraido_uniforme"]:
        confiabilidade = "baixa"
    elif tipo_resposta in ["baixa_discriminacao", "inflado", "retraido", "muito_variavel"]:
        confiabilidade = "média"

    conflitos_detectados = []

    if medias["Seguranca"] >= 4 and medias["Abundancia"] >= 4:
        conflitos_detectados.append("expansão versus segurança")

    if medias["Extroversao"] >= 4 and medias["Neuroticismo"] >= 4:
        conflitos_detectados.append("alta exposição com alta reatividade emocional")

    if medias["Consciencia"] >= 4 and medias["Abertura"] >= 4:
        conflitos_detectados.append("estrutura alta com abertura alta")

    if medias["Amabilidade"] >= 4 and medias["Extroversao"] >= 4:
        conflitos_detectados.append("forte orientação relacional com presença social intensa")

    if medias["Consciencia"] >= 4 and medias["Neuroticismo"] >= 4:
        conflitos_detectados.append("alto controle com alta tensão interna")

    eixo_mais_alto = max(medias, key=medias.get)
    eixo_mais_baixo = min(medias, key=medias.get)

    perfil = {
        "medias": medias,
        "faixas": faixas,
        "media_geral": media_geral,
        "desvio_padrao": desvio_padrao,
        "amplitude": amplitude,
        "valores_unicos": valores_unicos,
        "quantidade_valores_unicos": quantidade_valores_unicos,
        "medias_unicas_blocos": medias_unicas_blocos,
        "tipo_resposta": tipo_resposta,
        "confiabilidade": confiabilidade,
        "energia_social": (
            "alta" if medias["Extroversao"] >= 4
            else "baixa" if medias["Extroversao"] < 3
            else "moderada"
        ),
        "forma_decisao": (
            "mais reflexiva" if medias["Abertura"] >= 3
            else "mais prática"
        ),
        "nivel_estrutura": (
            "alto" if medias["Consciencia"] >= 4
            else "baixo" if medias["Consciencia"] < 3
            else "moderado"
        ),
        "sensibilidade_emocional": (
            "alta" if medias["Neuroticismo"] >= 4
            else "baixa" if medias["Neuroticismo"] < 3
            else "moderada"
        ),
        "tendencia_relacional": (
            "adaptativa" if medias["Amabilidade"] >= 3
            else "direta"
        ),
        "relacao_dinheiro": (
            "segurança" if medias["Seguranca"] > medias["Abundancia"]
            else "expansão" if medias["Abundancia"] > medias["Seguranca"]
            else "equilíbrio entre segurança e expansão"
        ),
        "conflitos_detectados": conflitos_detectados,
        "eixo_mais_alto": eixo_mais_alto,
        "eixo_mais_baixo": eixo_mais_baixo,
    }

    return perfil

# =========================
# AI REPORT
# =========================
def gerar_relatorio(perfil: dict) -> str:
    client = get_openai_client()
    if client is None:
        return "Erro: OPENAI_API_KEY não encontrada em Secrets."

    prompt = f"""
Você é um especialista em leitura comportamental profunda.

Sua missão é traduzir dados em IDENTIDADE de forma mais precisa, concreta e humana.

BASE DE DADOS:
{perfil}

REGRAS CRÍTICAS:
1. Use os dados, mas NÃO repita números no texto final, exceto se for indispensável.
2. Transforme dados em comportamento observável do dia a dia.
3. Toda afirmação relevante deve ser ancorada em algo do perfil.
4. Evite inferências psicológicas fortes demais se os dados não sustentarem isso.
5. Evite frases genéricas que serviriam para quase qualquer pessoa.
6. Não use linguagem técnica.
7. Se os dados forem pouco confiáveis, diga isso claramente.
8. Se houver um eixo mais alto ou mais baixo, use isso como parte central da leitura.
9. Todo traço deve ser tratado com dualidade:
   - fortaleza quando bem usado
   - desafio quando mal calibrado
10. Não trate perfil baixo como defeito automático.
11. Não trate perfil alto como vantagem automática.
12. Dê exemplos concretos de comportamento sempre que possível.
13. Não escreva como teste, escreva como leitura humana.
14. Não romantize.
15. Não faça “texto bonito vazio”.

ESTRUTURA OBRIGATÓRIA:

1. COMO VOCÊ FUNCIONA DE VERDADE
Descreva como essa pessoa tende a entrar em ambientes, reagir, se posicionar e administrar a própria energia.

2. COMO VOCÊ TOMA DECISÕES
Mostre:
- onde essa pessoa costuma decidir bem
- onde tende a atrasar, ceder ou travar

3. COMO VOCÊ SE RELACIONA
Mostre:
- como cria conexão
- onde se adapta demais
- onde pode perder posição ou voz

4. DINÂMICA INTERNA
Mostre:
- o que parece acontecer por dentro
- qual tensão emocional ou mental aparece com mais frequência
- sem inventar trauma ou patologia

5. SEU PADRÃO MAIS FORTE
Use o eixo mais alto como referência principal e explique como ele aparece concretamente.

6. SUAS FORTALEZAS REAIS
Faça uma lista clara, específica e concreta.
Nada genérico.

7. SUAS ÁREAS DE DESAFIO
Mostre onde o padrão cobra preço na prática.
Nada de suavizar demais.

8. O PONTO QUE MAIS MERECE ATENÇÃO
Escolha UMA coisa principal e aprofunde com clareza.

9. DIREÇÃO PRÁTICA
Dê direção realista, útil e aplicável.
Sem clichês.

ESTILO:
- direto
- humano
- específico
- concreto
- lúcido
- sem floreio
- sem clichê
- sem horóscopo

Faça a pessoa se reconhecer sem parecer um texto pronto.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.55,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Erro ao gerar relatório com a OpenAI:\n\n{str(e)}"

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
            valor = int(resposta.split(" - ")[0]) if isinstance(resposta, str) else int(resposta)
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