import streamlit as st
from openai import OpenAI

# =========================
# 🔐 OPENAI (CORRIGIDO)
# =========================

def get_openai_client():
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

# =========================
# 🧠 V6.1 MOTOR
# =========================

def extrair_padroes(perfil, followups):
    padroes = []

    if perfil["conscienciosidade"] >= 3.5 and perfil["extroversao"] <= 3.2:
        padroes.append({"nome": "merito_subcomunicado", "peso": 9})

    if perfil["abertura"] - perfil["extroversao"] >= 0.7:
        padroes.append({"nome": "clareza_interna_maior_que_presenca", "peso": 8})

    if perfil["seguranca"] >= 3.4 and perfil["risco"] <= 3.0:
        padroes.append({"nome": "prudencia_funcional", "peso": 8})

    if perfil["conscienciosidade"] >= 3.5:
        padroes.append({"nome": "execucao_consistente", "peso": 7})

    if perfil["pct_3_4"] >= 75:
        padroes.append({"nome": "economia_de_extremos", "peso": 7})

    if followups.get("posicionamento_social") == "Depende muito da pessoa e do contexto":
        padroes.append({"nome": "exposicao_seletiva", "peso": 8})

    return sorted(padroes, key=lambda x: x["peso"], reverse=True)


def extrair_tensoes(perfil):
    tensoes = []

    if perfil["conscienciosidade"] >= 3.5 and perfil["extroversao"] <= 3.2:
        tensoes.append("valor_real_vs_presenca_percebida")

    if perfil["seguranca"] >= 3.4 and perfil["risco"] <= 3.0:
        tensoes.append("seguranca_vs_expansao")

    if perfil["abertura"] > perfil["extroversao"]:
        tensoes.append("complexidade_interna_vs_expressao_externa")

    return tensoes


def extrair_comportamentos(padroes):
    mapa = {
        "merito_subcomunicado": "Entrega valor consistente, mas comunica menos do que poderia.",
        "clareza_interna_maior_que_presenca": "Tem mais clareza interna do que presença externa visível.",
        "prudencia_funcional": "Prefere segurança e consistência antes de expandir.",
        "execucao_consistente": "Mantém padrão de execução mesmo sem motivação alta.",
        "economia_de_extremos": "Evita posições extremas e tende à moderação nas decisões.",
        "exposicao_seletiva": "Se expõe mais ou menos dependendo do ambiente e das pessoas."
    }

    comportamentos = []

    for p in padroes:
        if p["nome"] in mapa:
            comportamentos.append({
                "descricao": mapa[p["nome"]],
                "peso": p["peso"]
            })

    return sorted(comportamentos, key=lambda x: x["peso"], reverse=True)


def gerar_prompt(perfil, padroes, tensoes, comportamentos):
    return f"""
Você é um analista de comportamento humano altamente preciso.

Seu objetivo é gerar um relatório profundo, específico e não genérico.

REGRAS CRÍTICAS:
- NÃO use termos como "alta abertura", "baixa extroversão"
- NÃO parafraseie perguntas
- NÃO escreva frases genéricas
- Foque em comportamento observável
- Seja direto e específico

DADOS:

PADRÕES PRINCIPAIS:
{padroes}

TENSÕES:
{tensoes}

COMPORTAMENTOS:
{comportamentos}

TAREFA:

1. Comece pelo padrão mais forte
2. Descreva o comportamento dominante
3. Explique a principal tensão
4. Mostre o custo invisível
5. Diga onde isso aparece na vida real
6. Finalize com direção prática

Gere o relatório agora.
"""


# =========================
# 🎯 EXEMPLO DE PERFIL (TESTE)
# =========================

# ⚠️ Substitua isso pelo seu cálculo real
perfil = {
    "abertura": 4.0,
    "extroversao": 3.0,
    "conscienciosidade": 3.7,
    "seguranca": 3.5,
    "risco": 2.8,
    "pct_3_4": 92
}

followups = {
    "posicionamento_social": "Depende muito da pessoa e do contexto"
}

# =========================
# 🚀 EXECUÇÃO
# =========================

st.title("Mind Insight V6.1")

client = get_openai_client()

if client is None:
    st.error("Configure OPENAI_API_KEY nos Secrets.")
    st.stop()

if st.button("Gerar Relatório"):

    padroes = extrair_padroes(perfil, followups)
    tensoes = extrair_tensoes(perfil)
    comportamentos = extrair_comportamentos(padroes)

    prompt = gerar_prompt(perfil, padroes, tensoes, comportamentos)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    resultado = response.output[0].content[0].text

    st.subheader("Resultado:")
    st.write(resultado)
