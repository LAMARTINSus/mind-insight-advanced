# ==========================================
# Mind Insight™
# VERSÃO: V6.3
# Sistema de Inferência Comportamental
# ==========================================

import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ==========================================
# CONFIG
# ==========================================
st.set_page_config(page_title="Mind Insight V6.3", layout="wide")

st.title("Mind Insight™")
st.caption("Versão V6.3 | Engine multi-dimensional anti-repetição")

# ==========================================
# TENSION LIBRARY (PADRONIZADO)
# ==========================================
TENSION_LIBRARY = {
    "valor_vs_visibilidade": {
        "texto": "Você gera mais valor do que projeta externamente.",
        "peso": 9
    },
    "seguranca_vs_expansao": {
        "texto": "Existe conflito entre estabilidade e expansão.",
        "peso": 8
    },
    "interno_vs_externo": {
        "texto": "Sua complexidade interna não aparece proporcionalmente.",
        "peso": 8
    }
}

# ==========================================
# EXTRAÇÃO DE PADRÕES
# ==========================================
def extrair_padroes(perfil):
    padroes = []

    if perfil["conscienciosidade"] >= 3.5:
        padroes.append({"nome": "execucao_consistente", "peso": 9, "tag": "execucao"})

    if perfil["extroversao"] <= 3.2:
        padroes.append({"nome": "baixa_exposicao", "peso": 8, "tag": "expressao"})

    if perfil["abertura"] >= 3.8:
        padroes.append({"nome": "alta_complexidade", "peso": 8, "tag": "interno"})

    if perfil["seguranca"] >= 3.4:
        padroes.append({"nome": "prudencia", "peso": 7, "tag": "risco"})

    return sorted(padroes, key=lambda x: x["peso"], reverse=True)

# ==========================================
# EXTRAÇÃO DE TENSÕES
# ==========================================
def extrair_tensoes(perfil):
    tensoes = []

    if perfil["conscienciosidade"] >= 3.5 and perfil["extroversao"] <= 3.2:
        tensoes.append("valor_vs_visibilidade")

    if perfil["seguranca"] >= 3.4:
        tensoes.append("seguranca_vs_expansao")

    if perfil["abertura"] > perfil["extroversao"]:
        tensoes.append("interno_vs_externo")

    return tensoes

# ==========================================
# DISTRIBUIÇÃO POR DIMENSÃO
# ==========================================
def distribuir(padroes):
    mapa = {"execucao": [], "expressao": [], "interno": [], "risco": []}

    for p in padroes:
        mapa[p["tag"]].append(p)

    return mapa

# ==========================================
# PROMPT V6.3
# ==========================================
def gerar_prompt(perfil, dist, tensoes):
    return f"""
Você é um analista altamente preciso.

REGRAS:
- Não repetir ideias
- Cada seção deve abordar dimensão diferente

1. EIXO CENTRAL
2. EXECUÇÃO
3. EXPRESSÃO
4. INTERNO
5. RISCO/EXPANSÃO
6. POTENCIAL
7. DIREÇÃO

DADOS:

EXECUÇÃO: {dist["execucao"]}
EXPRESSÃO: {dist["expressao"]}
INTERNO: {dist["interno"]}
RISCO: {dist["risco"]}

TENSÕES: {tensoes}

Gere um relatório direto, específico e não genérico.
"""

# ==========================================
# DEBUG
# ==========================================
def render_debug(perfil, padroes, tensoes):
    st.subheader("DEBUG")

    st.write("Perfil:", perfil)
    st.write("Padrões:", padroes)

    st.subheader("Tensões")
    for t in tensoes:
        info = TENSION_LIBRARY.get(t, {})
        texto = info.get("texto", t)
        peso = info.get("peso", "-")
        st.write(f"→ {texto} (peso {peso})")

# ==========================================
# INPUT SIMPLES (SIMULAÇÃO)
# ==========================================
perfil = {
    "abertura": 4.0,
    "conscienciosidade": 3.7,
    "extroversao": 3.0,
    "seguranca": 3.4
}

# ==========================================
# PIPELINE V6.3
# ==========================================
padroes = extrair_padroes(perfil)
tensoes = extrair_tensoes(perfil)
dist = distribuir(padroes)

prompt = gerar_prompt(perfil, dist, tensoes)

if st.button("Gerar Relatório"):
        response = client.responses.create(
    model="gpt-5-4-auto-thinking",
    input=prompt
)

    resultado = response.output[0].content[0].text

    st.subheader("Relatório")
    st.write(resultado)

    render_debug(perfil, padroes, tensoes)
