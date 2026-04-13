from openai import OpenAI

client = OpenAI(api_key="SUA_API_KEY_AQUI")

# -----------------------------
# 1. PERFIL MOCK (SUBSTITUIR PELO SEU FLUXO REAL)
# -----------------------------
perfil = {
    "eixos": {
        "abertura": 4.0,
        "conscienciosidade": 3.7,
        "extroversao": 3.0,
        "seguranca": 3.5
    },
    "derivados": {
        "auto_reconhecimento": 2.5,
        "visibilidade_pessoal": 2.7,
        "tolerancia_risco": 2.7,
        "pct_3_4": 82.0
    },
    "followups": {
        "posicionamento_social": "Depende muito da pessoa e do contexto"
    }
}

# -----------------------------
# 2. PADRÕES
# -----------------------------
def extrair_padroes(perfil):
    p = perfil["eixos"]
    d = perfil["derivados"]
    f = perfil["followups"]

    padroes = []

    if p["conscienciosidade"] >= 3.5 and p["extroversao"] <= 3.2:
        padroes.append({"nome": "merito_subcomunicado", "peso": 9})

    if p["abertura"] - p["extroversao"] >= 0.7:
        padroes.append({"nome": "clareza_interna_maior_que_presenca", "peso": 8})

    if p["seguranca"] >= 3.4 and d["tolerancia_risco"] <= 3.0:
        padroes.append({"nome": "prudencia_funcional", "peso": 8})

    if p["conscienciosidade"] >= 3.5:
        padroes.append({"nome": "execucao_consistente", "peso": 7})

    if d["pct_3_4"] >= 75:
        padroes.append({"nome": "economia_de_extremos", "peso": 7})

    if f.get("posicionamento_social") == "Depende muito da pessoa e do contexto":
        padroes.append({"nome": "exposicao_seletiva", "peso": 8})

    return sorted(padroes, key=lambda x: x["peso"], reverse=True)

# -----------------------------
# 3. TENSÕES
# -----------------------------
def extrair_tensoes(perfil):
    p = perfil["eixos"]
    d = perfil["derivados"]

    tensoes = []

    if p["conscienciosidade"] >= 3.5 and p["extroversao"] <= 3.2:
        tensoes.append("valor_real_vs_presenca_percebida")

    if p["seguranca"] >= 3.4 and d["tolerancia_risco"] <= 3.0:
        tensoes.append("seguranca_vs_expansao")

    if p["abertura"] > p["extroversao"]:
        tensoes.append("complexidade_interna_vs_expressao_externa")

    return tensoes

# -----------------------------
# 4. COMPORTAMENTOS
# -----------------------------
def extrair_comportamentos(padroes):
    mapa = {
        "merito_subcomunicado": "Entrega valor consistente, mas comunica menos do que poderia.",
        "clareza_interna_maior_que_presenca": "Tem mais clareza interna do que presença externa visível.",
        "prudencia_funcional": "Prefere segurança antes de expandir.",
        "execucao_consistente": "Mantém execução mesmo sem alta motivação.",
        "economia_de_extremos": "Evita posições extremas ao se definir.",
        "exposicao_seletiva": "Se posiciona de forma diferente dependendo do contexto."
    }

    comportamentos = []

    for p in padroes:
        if p["nome"] in mapa:
            comportamentos.append({
                "descricao": mapa[p["nome"]],
                "peso": p["peso"]
            })

    return sorted(comportamentos, key=lambda x: x["peso"], reverse=True)

# -----------------------------
# 5. PROMPT
# -----------------------------
def gerar_prompt(perfil, padroes, tensoes, comportamentos):
    return f"""
Você é um analista de comportamento humano extremamente preciso.

REGRAS:
- Não use termos técnicos de personalidade
- Não generalize
- Não repita perguntas
- Seja específico

PADRÕES:
{padroes}

TENSÕES:
{tensoes}

COMPORTAMENTOS:
{comportamentos}

TAREFA:
1. Comece pelo padrão mais forte
2. Explique o comportamento dominante
3. Mostre a principal tensão
4. Explique o custo invisível
5. Diga onde isso aparece na vida real
6. Dê direção prática

Escreva de forma direta, humana e específica.
"""

# -----------------------------
# 6. EXECUÇÃO
# -----------------------------
padroes = extrair_padroes(perfil)
tensoes = extrair_tensoes(perfil)
comportamentos = extrair_comportamentos(padroes)

prompt = gerar_prompt(perfil, padroes, tensoes, comportamentos)

response = client.responses.create(
    model="gpt-4.1-mini",
    input=prompt
)

print(response.output[0].content[0].text)