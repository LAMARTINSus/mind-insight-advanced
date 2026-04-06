# =============================================================

# MIND INSIGHT ADVANCED AI

# Version: V5.0

# Built with: Claude (Anthropic) — claude-sonnet-4-20250514

# Architecture designed in collaboration with Claude AI

# 

# Changes from V4.5:

# - 74 new questions, fully reclassified by trait

# - 31 score inversions implemented correctly

# - Blocks redefined with correct question ranges

# - Upgraded to gpt-4o for report generation

# - New structured prompt with intensity scale,

# axis definitions, and combination logic

# - Debug mode: full transparency on data, logic, and AI input

# - Temperature reduced to 0.5 for more precise output

# =============================================================

import streamlit as st
import pandas as pd
import json
from openai import OpenAI

DEBUG_MODE = True

# =============================================================

# CONFIG

# =============================================================

st.set_page_config(
page_title=“Mind Insight AI”,
page_icon=“🧠”,
layout=“wide”
)

st.markdown(”””

<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'IBM Plex Mono', monospace;
    }
    .stButton>button {
        background-color: #1a1a1a;
        color: #f0f0f0;
        border: 1px solid #444;
        border-radius: 4px;
        padding: 0.5rem 2rem;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        letter-spacing: 0.05em;
    }
    .stButton>button:hover {
        background-color: #333;
        border-color: #888;
    }
    .stRadio > label {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    .debug-box {
        background-color: #0d0d0d;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        color: #b0b0b0;
    }
    .eixo-bar {
        margin: 0.3rem 0;
    }
</style>

“””, unsafe_allow_html=True)

# =============================================================

# OPENAI CLIENT

# =============================================================

def get_openai_client():
api_key = st.secrets.get(“OPENAI_API_KEY”, “”)
if not api_key:
return None
return OpenAI(api_key=api_key)

# =============================================================

# SESSION STATE

# =============================================================

if “responses” not in st.session_state:
st.session_state.responses = {}

if “current_question” not in st.session_state:
st.session_state.current_question = 1

# =============================================================

# QUESTIONS

# 74 questions — 10 or 11 per axis

# (I) = inverted scoring

# 

# ABERTURA        Q1–Q10   (10 questions)

# CONSCIENCIA     Q11–Q20  (10 questions)

# EXTROVERSAO     Q21–Q30  (10 questions)

# AMABILIDADE     Q31–Q41  (11 questions)

# NEUROTICISMO    Q42–Q52  (11 questions)

# SEGURANCA       Q53–Q63  (11 questions)

# ABUNDANCIA      Q64–Q74  (11 questions)

# =============================================================

questions = {
# — ABERTURA —
1:  “Fico genuinamente curioso quando encontro uma ideia que contradiz o que eu penso.”,
2:  “Prefiro soluções já testadas a experimentar abordagens novas.”,           # (I)
3:  “Busco conhecimento em assuntos novos por prazer, não por obrigação.”,
4:  “Me incomoda quando conversas ficam muito abstratas ou filosóficas.”,      # (I)
5:  “Consigo encontrar conexões entre assuntos que parecem não ter nada a ver.”,
6:  “Prefiro que as coisas sejam diretas e práticas, sem muita especulação.”,  # (I)
7:  “Já mudei uma opinião importante por causa de um argumento bem fundamentado.”,
8:  “Me atrai explorar áreas onde ainda não tenho domínio.”,
9:  “Acho desgastante quando alguém fica questionando como as coisas sempre foram feitas.”, # (I)
10: “Tenho imaginação ativa — frequentemente visualizo cenários, histórias ou possibilidades.”,

```
# --- CONSCIENCIOSIDADE ---
11: "Quando assumo um compromisso, cumpro — mesmo quando não tenho mais vontade.",
12: "Começo tarefas importantes só quando estou com disposição para isso.",     # (I)
13: "Tenho um sistema claro para organizar minhas prioridades do dia.",
14: "Deixo para decidir na hora em vez de planejar com antecedência.",         # (I)
15: "Quando começo algo, tenho dificuldade de parar antes de terminar.",
16: "Frequentemente percebo que deixei algo importante para a última hora.",   # (I)
17: "Reviso meu trabalho antes de entregar, mesmo quando estou confiante.",
18: "Tenho clareza sobre o que precisa ser feito hoje para chegar onde quero em um ano.",
19: "Me distraio com facilidade quando deveria estar focado em algo importante.", # (I)
20: "Mantenho meus compromissos mesmo quando surgem opções mais atraentes.",

# --- EXTROVERSÃO ---
21: "Me sinto com mais energia depois de passar tempo com pessoas do que antes.",
22: "Em grupos, costumo tomar a iniciativa de falar primeiro.",
23: "Prefiro pensar sozinho antes de discutir ideias com outros.",              # (I)
24: "Me sinto confortável sendo o porta-voz de um grupo em situações formais.",
25: "Depois de um dia social intenso, preciso de tempo sozinho para recarregar.", # (I)
26: "Busco ativamente conhecer pessoas novas em ambientes sociais.",
27: "Prefiro me comunicar por escrito a falar ao vivo quando tenho algo importante a dizer.", # (I)
28: "Me sinto bem em ambientes barulhentos e movimentados.",
29: "Em conversas em grupo, frequentemente fico mais ouvindo do que falando.",  # (I)
30: "Quando tenho uma opinião, não tenho dificuldade de expressá-la mesmo que outros discordem.",

# --- AMABILIDADE ---
31: "Quando alguém está passando por algo difícil, meu primeiro instinto é ajudar.",
32: "Tenho facilidade para identificar como o outro está se sentindo, mesmo sem ele dizer.",
33: "Em desacordos, prefiro ceder do que prolongar o conflito.",               # (I)
34: "Me importo mais com o resultado certo do que com o que as pessoas vão pensar de mim.", # (I)
35: "Fico desconfortável quando percebo que decepcionei alguém.",
36: "Consigo discordar de alguém sem que isso afete a relação.",
37: "Evito dar feedback negativo para não criar tensão.",                       # (I)
38: "Confio nas pessoas até que me provem o contrário.",
39: "Quando preciso dizer algo difícil, costumo adiar mais do que deveria.",   # (I)
40: "Me preocupo genuinamente com o bem-estar das pessoas ao meu redor, não só das próximas.",
41: "Frequentemente coloco as necessidades dos outros à frente das minhas, mesmo quando isso me custa.",

# --- NEUROTICISMO ---
42: "Quando algo dá errado, fico remoendo o que aconteceu por horas ou dias.",
43: "Me recupero emocionalmente rápido depois de situações difíceis.",         # (I)
44: "Frequentemente me preocupo com coisas que ainda não aconteceram.",
45: "Consigo manter a calma em situações de pressão alta.",                    # (I)
46: "Pequenos contratempos do dia me afetam mais do que deveriam.",
47: "Quando estou sob estresse, minha capacidade de tomar decisões piora visivelmente.",
48: "Me sinto estável emocionalmente na maior parte do tempo.",                # (I)
49: "Fico ansioso quando não sei o que esperar de uma situação.",
50: "Críticas, mesmo construtivas, me afetam emocionalmente por um tempo.",
51: "Consigo separar o que sinto do que preciso fazer, mesmo em momentos difíceis.", # (I)
52: "Quando cometo um erro, fico muito mais tempo me cobrando do que a situação justificaria.",

# --- SEGURANÇA ---
53: "Me sinto mais confortável quando sei exatamente o que esperar de uma situação.",
54: "Consigo agir com confiança mesmo quando não tenho todas as informações.", # (I)
55: "Mudanças inesperadas nos meus planos me deixam mais incomodado do que a maioria.",
56: "Prefiro uma oportunidade menor mas garantida a uma maior mas incerta.",
57: "Me sinto bem entrando em situações onde não sei exatamente o que vai acontecer.", # (I)
58: "Demoro para confiar em pessoas ou ambientes novos.",
59: "Quando estou numa rotina que funciona, resisto a mudar mesmo que haja opções melhores.",
60: "Consigo me comprometer com algo antes de ter certeza absoluta de que vai dar certo.", # (I)
61: "Sinto desconforto real quando preciso tomar decisões sem um plano claro.",
62: "Me sinto seguro mesmo em fases de transição ou incerteza na minha vida.", # (I)
63: "Minha sensação de estabilidade depende mais do que eu penso sobre mim do que do que os outros pensam.", # (I)

# --- ABUNDÂNCIA ---
64: "Quando vejo alguém bem-sucedido, meu primeiro pensamento é de inspiração, não de comparação.",
65: "Sinto que as oportunidades disponíveis para mim são limitadas.",          # (I)
66: "Consigo gastar dinheiro em algo que vale a pena sem sentir culpa depois.",
67: "Frequentemente sinto que estou ficando para trás em relação a onde deveria estar.", # (I)
68: "Acredito que há espaço para todo mundo crescer — o sucesso dos outros não diminui o meu.",
69: "Pensar em dinheiro me gera mais ansiedade do que clareza.",               # (I)
70: "Quando surge uma oportunidade nova, meu primeiro instinto é ver o que posso ganhar.",
71: "Tenho dificuldade de investir em mim mesmo quando não vejo retorno garantido.", # (I)
72: "Me sinto à vontade para pedir o que acredito que meu trabalho vale.",
73: "Sinto que, independente do que faço, nunca é suficiente.",                # (I)
74: "A possibilidade de perder o que já tenho me preocupa mais do que a possibilidade de ganhar algo novo.", # (I)
```

}

scale = [
“1 — Discordo totalmente”,
“2 — Discordo”,
“3 — Neutro”,
“4 — Concordo”,
“5 — Concordo totalmente”,
]

# =============================================================

# SCORE INVERSION

# Perguntas onde concordar = traço BAIXO

# Lógica: score_invertido = 6 - score_original

# Exemplo: resposta 5 → vira 1 / resposta 4 → vira 2

# =============================================================

PERGUNTAS_INVERTIDAS = {
2, 4, 6, 9,           # Abertura
12, 14, 16, 19,       # Conscienciosidade
23, 25, 27, 29,       # Extroversão
33, 34, 37, 39,       # Amabilidade
43, 45, 48, 51,       # Neuroticismo
54, 57, 60, 62, 63,   # Segurança
65, 67, 69, 71, 73, 74  # Abundância
}

def aplicar_inversao(q: int, score: int) -> int:
“””
Inverte o score de perguntas onde concordar = traço baixo.
Escala 1–5: 5→1, 4→2, 3→3, 2→4, 1→5
O 3 permanece 3 — é neutro em ambas as direções.
“””
if q in PERGUNTAS_INVERTIDAS:
return 6 - score
return score

# =============================================================

# ENGINE

# =============================================================

def gerar_perfil(respostas: dict) -> dict:

```
# Aplicar inversão antes de qualquer cálculo
respostas_ajustadas = {
    q: aplicar_inversao(q, s)
    for q, s in respostas.items()
}

df = pd.DataFrame(
    list(respostas_ajustadas.items()),
    columns=["Q", "Score"]
)

# Blocos corretos — cada pergunta no eixo que realmente mede
blocos = {
    "Abertura":          (1,  10),
    "Conscienciosidade": (11, 20),
    "Extroversao":       (21, 30),
    "Amabilidade":       (31, 41),
    "Neuroticismo":      (42, 52),
    "Seguranca":         (53, 63),
    "Abundancia":        (64, 74),
}

medias = {
    k: round(df[(df["Q"] >= i) & (df["Q"] <= f)]["Score"].mean(), 2)
    for k, (i, f) in blocos.items()
}

eixo_mais_alto = max(medias, key=medias.get)
eixo_mais_baixo = min(medias, key=medias.get)

# Contrastes entre eixos relevantes
diferencas = {
    "Seguranca_vs_Abundancia":     round(medias["Seguranca"] - medias["Abundancia"], 2),
    "Amabilidade_vs_Extroversao":  round(medias["Amabilidade"] - medias["Extroversao"], 2),
    "Conscienciosidade_vs_Abertura": round(medias["Conscienciosidade"] - medias["Abertura"], 2),
    "Neuroticismo_vs_Extroversao": round(medias["Neuroticismo"] - medias["Extroversao"], 2),
    "Neuroticismo_vs_Seguranca":   round(medias["Neuroticismo"] - medias["Seguranca"], 2),
}

# Qualidade estatística do dado
media_geral = round(df["Score"].mean(), 2)
desvio_padrao = round(float(df["Score"].std(ddof=0)), 3)
amplitude = int(df["Score"].max() - df["Score"].min())

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
    confiabilidade = "media"

# Flags automáticas — padrões detectados
flags = []
if medias["Seguranca"] > medias["Abundancia"]:
    flags.append("mais orientação à segurança do que à expansão")
if medias["Amabilidade"] > medias["Extroversao"]:
    flags.append("mais adaptação relacional do que impulso de exposição")
if medias["Abundancia"] < 3:
    flags.append("baixa percepção de abundância")
if medias["Neuroticismo"] >= 3.5:
    flags.append("reatividade emocional elevada")
elif medias["Neuroticismo"] >= 3.0:
    flags.append("sensibilidade emocional presente")
if medias["Seguranca"] >= 3.5:
    flags.append("forte orientação à estabilidade e previsibilidade")
if medias["Conscienciosidade"] >= 3.5:
    flags.append("alto senso de responsabilidade e disciplina")
if medias["Abertura"] >= 3.5:
    flags.append("abertura intelectual e curiosidade acima da média")
if medias["Extroversao"] < 3:
    flags.append("introversão predominante — energia social mais contida")
if medias["Amabilidade"] >= 4.0:
    flags.append("amabilidade muito alta — possível custo em assertividade")

# Hipótese técnica — leitura fria para o AI
hipotese_tecnica = []
if medias["Seguranca"] > medias["Abundancia"]:
    hipotese_tecnica.append(
        "tendência a preservar estabilidade antes de explorar oportunidade"
    )
if medias["Amabilidade"] >= 3.5:
    hipotese_tecnica.append(
        "forte tendência a manter harmonia relacional — possível custo em assertividade e limites"
    )
if medias["Extroversao"] < 3:
    hipotese_tecnica.append(
        "introversão predominante — processa internamente antes de externalizar"
    )
if medias["Abundancia"] < 3:
    hipotese_tecnica.append(
        "possível restrição na relação com expansão, valor ou oportunidade — mentalidade de escassez"
    )
if medias["Neuroticismo"] >= 3.5:
    hipotese_tecnica.append(
        "reatividade emocional elevada — pode impactar decisões sob pressão e sob crítica"
    )
if medias["Conscienciosidade"] >= 3.5:
    hipotese_tecnica.append(
        "alto padrão de entrega e responsabilidade — possível rigidez ou autocrítica excessiva"
    )
if medias["Abertura"] >= 3.5 and medias["Conscienciosidade"] < 3:
    hipotese_tecnica.append(
        "gerador de ideias com dificuldade de execução sistemática"
    )
if medias["Abertura"] < 3 and medias["Conscienciosidade"] >= 3.5:
    hipotese_tecnica.append(
        "executor confiável com resistência a mudança de rota ou método"
    )

# Intensidade de cada eixo — label para o AI
def intensidade(valor):
    if valor >= 4.3:
        return "muito alto — traço dominante"
    elif valor >= 3.5:
        return "alto — padrão consistente"
    elif valor >= 3.0:
        return "moderado — contextual"
    elif valor >= 2.1:
        return "abaixo da média — tendência limitante"
    else:
        return "muito baixo — ausência marcante"

intensidades = {k: intensidade(v) for k, v in medias.items()}

return {
    "medias": medias,
    "intensidades": intensidades,
    "eixo_mais_alto": eixo_mais_alto,
    "eixo_mais_baixo": eixo_mais_baixo,
    "diferencas": diferencas,
    "media_geral": media_geral,
    "desvio_padrao": desvio_padrao,
    "amplitude": amplitude,
    "tipo_resposta": tipo_resposta,
    "confiabilidade": confiabilidade,
    "flags": flags,
    "hipotese_tecnica": hipotese_tecnica,
    "respostas_brutas": dict(sorted(respostas.items())),
    "respostas_ajustadas": dict(sorted(respostas_ajustadas.items())),
}
```

# =============================================================

# PROMPT + REPORT GENERATION

# =============================================================

def gerar_relatorio(perfil: dict) -> str:
client = get_openai_client()
if client is None:
return “Erro: OPENAI_API_KEY não encontrada em Secrets.”

```
medias = perfil["medias"]
intensidades = perfil["intensidades"]
eixo_mais_alto = perfil["eixo_mais_alto"]
eixo_mais_baixo = perfil["eixo_mais_baixo"]
diferencas = perfil["diferencas"]
flags = perfil["flags"]
hipotese_tecnica = perfil["hipotese_tecnica"]

prompt = f"""
```

Você está analisando uma pessoa real com base em dados precisos de perfil comportamental.

═══════════════════════════════════════
DADOS DO PERFIL
═══════════════════════════════════════

MÉDIAS POR EIXO (escala 1.0 a 5.0):

- Abertura:          {medias[“Abertura”]}  → {intensidades[“Abertura”]}
- Conscienciosidade: {medias[“Conscienciosidade”]}  → {intensidades[“Conscienciosidade”]}
- Extroversão:       {medias[“Extroversao”]}  → {intensidades[“Extroversao”]}
- Amabilidade:       {medias[“Amabilidade”]}  → {intensidades[“Amabilidade”]}
- Neuroticismo:      {medias[“Neuroticismo”]}  → {intensidades[“Neuroticismo”]}
- Segurança:         {medias[“Seguranca”]}  → {intensidades[“Seguranca”]}
- Abundância:        {medias[“Abundancia”]}  → {intensidades[“Abundancia”]}

EIXO MAIS ALTO: {eixo_mais_alto}
EIXO MAIS BAIXO: {eixo_mais_baixo}

CONTRASTES ENTRE EIXOS:

- Segurança vs Abundância:        {diferencas[“Seguranca_vs_Abundancia”]}  (positivo = mais segurança que expansão)
- Amabilidade vs Extroversão:     {diferencas[“Amabilidade_vs_Extroversao”]}  (positivo = cuida mais do que se expõe)
- Conscienciosidade vs Abertura:  {diferencas[“Conscienciosidade_vs_Abertura”]}  (positivo = executa mais do que explora)
- Neuroticismo vs Extroversão:    {diferencas[“Neuroticismo_vs_Extroversao”]}  (positivo = mais reativo que expansivo)
- Neuroticismo vs Segurança:      {diferencas[“Neuroticismo_vs_Seguranca”]}  (positivo = ansioso apesar da busca por controle)

FLAGS IDENTIFICADAS:
{chr(10).join(f”- {f}” for f in flags)}

HIPÓTESE TÉCNICA:
{chr(10).join(f”- {h}” for h in hipotese_tecnica)}

═══════════════════════════════════════
COMO INTERPRETAR OS DADOS
═══════════════════════════════════════

ESCALA DE INTENSIDADE:

- 1.0 a 2.0 → traço muito baixo — ausência marcante, impacto direto no comportamento
- 2.1 a 2.9 → traço abaixo da média — tendência presente com limitações claras
- 3.0 a 3.4 → traço moderado — presente mas contextual, não dominante
- 3.5 a 4.2 → traço alto — padrão consistente, aparece com frequência
- 4.3 a 5.0 → traço muito alto — dominante, define comportamento em múltiplos contextos

DEFINIÇÃO DE CADA EIXO:

- Abertura: curiosidade intelectual, apreciação por novidade, imaginação, flexibilidade mental
- Conscienciosidade: organização, disciplina, planejamento, responsabilidade, foco
- Extroversão: energia social, assertividade, sociabilidade, busca por estímulo externo
- Amabilidade: empatia, cooperação, evitar conflito, confiança nos outros, generosidade
- Neuroticismo: ansiedade, instabilidade emocional, ruminação, reatividade a estresse
- Segurança: orientação para estabilidade, necessidade de previsibilidade, aversão a risco
- Abundância: mentalidade de escassez vs. fartura, relação emocional com recursos e oportunidades

COMO LER COMBINAÇÕES:

- Segurança alta + Abundância baixa = protege o que tem, dificuldade de expandir
- Amabilidade alta + Extroversão baixa = cuida dos outros mas evita exposição social
- Amabilidade alta + Neuroticismo alto = sensível às relações, ansioso com conflitos
- Conscienciosidade alta + Abertura baixa = executa bem, resiste a mudança de rota
- Neuroticismo alto + Segurança alta = ansioso internamente, busca controle externo como alívio
- Abertura alta + Conscienciosidade baixa = gerador de ideias, dificuldade de executar
- Extroversão alta + Amabilidade baixa = assertivo, pode ser percebido como insensível

═══════════════════════════════════════
REGRAS CRÍTICAS
═══════════════════════════════════════

SOBRE OS DADOS:

- Cada afirmação deve ser sustentada por um dado específico do perfil
- Se um eixo está entre 3.0 e 3.4, não afirme que é alto nem baixo — é moderado e contextual
- Se um eixo está acima de 4.0 ou abaixo de 2.0, trate com peso proporcional — é dominante
- Contrastes entre eixos são tão importantes quanto os valores absolutos
- Não invente traços. Não suavize traços que os dados mostram com clareza.

SOBRE A ESCRITA:

- Fale sempre em “você”
- Proibido usar linguagem técnica ou nomear os eixos diretamente no texto
- Proibido frases que servem para qualquer pessoa
- Proibido romantizar ou elogiar sem fundamento nos dados
- Proibido suavizar pontos difíceis que os dados sustentam
- Cada traço deve mostrar onde funciona bem E onde cobra um preço

SOBRE O ESTILO:

- Direto. Sem rodeio.
- Humano. Sem jargão.
- Específico. Cada frase pertence a esta pessoa, não a qualquer pessoa.
- Concreto. Mostre o traço em situações reais do dia a dia.
- Sem clichê. Nenhuma frase de calendário ou post motivacional.

FORMATO OBRIGATÓRIO DE CADA BLOCO:
→ O que você faz (comportamento concreto)
→ Em qual situação isso aparece (contexto real do dia a dia)
→ Onde isso funciona bem
→ Onde isso começa a cobrar um preço

═══════════════════════════════════════
ESTRUTURA OBRIGATÓRIA DO RELATÓRIO
═══════════════════════════════════════

**1. COMO VOCÊ FUNCIONA DE VERDADE**
Use os dois eixos mais altos para descrever o padrão central desta pessoa.
Mostre como ela entra em ambientes novos, como reage sob pressão, como se posiciona.
Se houver contraste forte entre eixos, mostre a tensão que isso cria no dia a dia.

**2. COMO VOCÊ TOMA DECISÕES**
Use Conscienciosidade, Segurança e Abertura para construir esse bloco.
Mostre onde decide bem, onde trava, onde cede, onde insiste.
Seja específico sobre o tipo de decisão onde o padrão aparece mais forte.
Se Segurança for alta e Abundância baixa, mostre o custo real nas decisões.

**3. COMO VOCÊ SE RELACIONA**
Use Amabilidade, Extroversão e Neuroticismo para construir esse bloco.
Mostre como cria conexão, o que faz para manter harmonia, onde vai além do que deveria.
Mostre o que as pessoas percebem nela que ela talvez não perceba em si mesma.
Se Amabilidade for alta e Extroversão baixa, mostre essa tensão específica.

**4. O QUE ACONTECE DENTRO DE VOCÊ**
Use Neuroticismo e o contraste com Segurança para construir esse bloco.
Descreva o padrão de pensamento mais frequente.
Quais perguntas ela se faz antes de agir?
Qual é o ruído interno mais comum?
O que ela raramente fala em voz alta mas sente com frequência?

**5. SEU PADRÃO MAIS FORTE**
Pegue o eixo mais alto.
Mostre como ele aparece em pelo menos 3 situações diferentes do cotidiano.
Mostre onde é um trunfo real com exemplo concreto.
Mostre onde se torna um problema real com exemplo concreto.

**6. SUAS FORTALEZAS REAIS**
Máximo 5 itens. Cada um ancorado em um eixo específico.
Formato obrigatório: “Você [verbo concreto] quando [situação específica]”
Proibido: adjetivos soltos como “você é empático” ou “você é organizado”
Obrigatório: mostrar a fortaleza em ação em contexto real

**7. SUAS ÁREAS DE DESAFIO**
Máximo 5 itens. Cada um com impacto real, não só o traço isolado.
Formato obrigatório: “Porque você tende a [padrão], o que acontece na prática é [consequência concreta]”
Não suavize. Se o dado indica limitação forte, diga com clareza.

**8. O PONTO QUE MAIS MERECE ATENÇÃO**
Escolha UM ponto — o que os dados indicam como mais custoso para esta pessoa.
Aprofunde em 4 dimensões:

- Como esse padrão aparece no dia a dia
- O que ele protege
- O que ele custa
- O sinal de que está acontecendo

**9. DIREÇÃO PRÁTICA**
4 a 5 orientações concretas, derivadas diretamente dos desafios identificados.
Formato obrigatório: ação específica + por quê faz sentido para este perfil.
Proibido: “saia da zona de conforto”, “pratique autoconhecimento”, “busque equilíbrio”
Obrigatório: instrução que esta pessoa consegue executar na próxima semana.

═══════════════════════════════════════
CRITÉRIO FINAL
═══════════════════════════════════════

A pessoa deve ler e pensar: “como você sabia disso?”
Não: “faz sentido para muita gente.”

Se uma frase poderia estar no relatório de outra pessoa com perfil diferente,
reescreva até que só caiba neste perfil.
“””

```
try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um analista de comportamento humano. "
                    "Sua função é traduzir dados de perfil em leituras precisas, humanas e específicas. "
                    "Você nunca generaliza. Você nunca inventa. "
                    "Você só escreve o que os dados sustentam. "
                    "Cada frase deve pertencer unicamente ao perfil que está sendo analisado."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.5,
    )
    return response.choices[0].message.content
except Exception as e:
    return f"Erro ao gerar relatório:\n\n{str(e)}"
```

# =============================================================

# DEBUG RENDER

# Exibe toda a lógica usada para gerar o perfil.

# Permite verificar se engine, dados e AI estão funcionando.

# Para desativar: mude DEBUG_MODE = False no topo do arquivo.

# =============================================================

def render_debug(perfil: dict):
st.markdown(”—”)
st.header(“🔍 Modo Debug — Transparência Total do Perfil”)
st.caption(
“Este painel mostra todos os dados, cálculos e lógica usados para gerar o relatório. “
“Permite validar se a engine, as inversões e a hipótese técnica estão corretas. “
“Para desativar: mude DEBUG_MODE = False no topo do arquivo.”
)

```
# --- 1. Respostas brutas ---
st.subheader("1. Respostas Brutas")
st.caption(
    "Score original da pessoa em cada pergunta, sem nenhuma transformação. "
    "Use para verificar se o app registrou corretamente cada resposta."
)
brutas = perfil["respostas_brutas"]
df_brutas = pd.DataFrame([
    {
        "Q": q,
        "Pergunta": questions.get(q, "—"),
        "Score Bruto": s,
        "Invertida?": "✅ sim" if q in PERGUNTAS_INVERTIDAS else "—"
    }
    for q, s in brutas.items()
])
st.dataframe(df_brutas, use_container_width=True)

# --- 2. Respostas ajustadas ---
st.subheader("2. Respostas Após Inversão de Score")
st.caption(
    "Score após aplicar a inversão nas perguntas marcadas. "
    "Perguntas invertidas: concordar = traço baixo → score é transformado por 6 - score. "
    "Este é o dado que entra nos cálculos de média."
)
ajustadas = perfil["respostas_ajustadas"]
df_ajustadas = pd.DataFrame([
    {
        "Q": q,
        "Pergunta": questions.get(q, "—"),
        "Score Bruto": brutas[q],
        "Score Ajustado": ajustadas[q],
        "Diferença": ajustadas[q] - brutas[q]
    }
    for q in brutas
])
st.dataframe(df_ajustadas, use_container_width=True)

# --- 3. Médias por eixo ---
st.subheader("3. Médias por Eixo")
st.caption(
    "Média dos scores ajustados de cada bloco. "
    "Este é o número central do perfil — o que o AI usa para gerar o relatório."
)

blocos_info = {
    "Abertura":          (1,  10),
    "Conscienciosidade": (11, 20),
    "Extroversao":       (21, 30),
    "Amabilidade":       (31, 41),
    "Neuroticismo":      (42, 52),
    "Seguranca":         (53, 63),
    "Abundancia":        (64, 74),
}

medias = perfil["medias"]
intensidades = perfil["intensidades"]

for eixo, (q_ini, q_fim) in blocos_info.items():
    media = medias[eixo]
    intensidade = intensidades[eixo]
    pct = (media - 1) / 4  # normaliza 1–5 para 0–1
    bar_filled = int(pct * 30)
    bar = "█" * bar_filled + "░" * (30 - bar_filled)
    st.markdown(
        f"**{eixo}** (Q{q_ini}–Q{q_fim})  \n"
        f"`{bar}` **{media}** — {intensidade}"
    )

# --- 4. Eixos extremos ---
st.subheader("4. Eixos Extremos")
st.caption("Eixo com maior e menor média — os polos do perfil.")
col1, col2 = st.columns(2)
with col1:
    st.metric("Eixo Mais Alto", perfil["eixo_mais_alto"], f"{medias[perfil['eixo_mais_alto']]}")
with col2:
    st.metric("Eixo Mais Baixo", perfil["eixo_mais_baixo"], f"{medias[perfil['eixo_mais_baixo']]}")

# --- 5. Contrastes entre eixos ---
st.subheader("5. Contrastes Entre Eixos")
st.caption(
    "Diferença entre pares de eixos. "
    "Contrastes altos revelam tensões comportamentais importantes. "
    "Um valor positivo significa que o primeiro eixo é mais alto que o segundo."
)
diferencas = perfil["diferencas"]
for par, valor in diferencas.items():
    direcao = "↑" if valor > 0 else ("↓" if valor < 0 else "=")
    st.write(f"**{par}**: {valor:+.2f} {direcao}")

# --- 6. Qualidade do dado ---
st.subheader("6. Qualidade Estatística das Respostas")
st.caption(
    "Avalia se as respostas são discriminantes (pessoa respondeu de forma variada e honesta) "
    "ou uniformes demais (possível viés de aquiescência ou desatenção)."
)
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Média Geral", perfil["media_geral"])
col2.metric("Desvio Padrão", perfil["desvio_padrao"])
col3.metric("Amplitude", perfil["amplitude"])
col4.metric("Tipo de Resposta", perfil["tipo_resposta"])
col5.metric("Confiabilidade", perfil["confiabilidade"])

# --- 7. Flags ---
st.subheader("7. Flags Automáticas")
st.caption(
    "Padrões detectados automaticamente pela engine com base nas médias e contrastes. "
    "Essas flags alimentam a hipótese técnica enviada ao AI."
)
for flag in perfil["flags"]:
    st.write(f"🔶 {flag}")

# --- 8. Hipótese técnica ---
st.subheader("8. Hipótese Técnica")
st.caption(
    "Leitura fria e disciplinada gerada pela engine. "
    "É o que o AI recebe como base para construir o relatório. "
    "Se a hipótese estiver errada, o relatório estará errado — verifique aqui primeiro."
)
for h in perfil["hipotese_tecnica"]:
    st.write(f"→ {h}")

# --- 9. Prompt completo enviado ao AI ---
st.subheader("9. Prompt Completo Enviado ao AI")
st.caption(
    "O texto exato que foi enviado ao modelo de linguagem para gerar o relatório. "
    "Use para verificar se os dados estão chegando corretamente e se as instruções fazem sentido."
)
medias = perfil["medias"]
intensidades = perfil["intensidades"]
eixo_mais_alto = perfil["eixo_mais_alto"]
eixo_mais_baixo = perfil["eixo_mais_baixo"]
diferencas = perfil["diferencas"]
flags = perfil["flags"]
hipotese_tecnica = perfil["hipotese_tecnica"]

prompt_preview = f"""
```

[SYSTEM]
Você é um analista de comportamento humano. Sua função é traduzir dados de perfil em leituras precisas, humanas e específicas. Você nunca generaliza. Você nunca inventa. Você só escreve o que os dados sustentam. Cada frase deve pertencer unicamente ao perfil que está sendo analisado.

[USER]
MÉDIAS POR EIXO:

- Abertura:          {medias[“Abertura”]}  → {intensidades[“Abertura”]}
- Conscienciosidade: {medias[“Conscienciosidade”]}  → {intensidades[“Conscienciosidade”]}
- Extroversão:       {medias[“Extroversao”]}  → {intensidades[“Extroversao”]}
- Amabilidade:       {medias[“Amabilidade”]}  → {intensidades[“Amabilidade”]}
- Neuroticismo:      {medias[“Neuroticismo”]}  → {intensidades[“Neuroticismo”]}
- Segurança:         {medias[“Seguranca”]}  → {intensidades[“Seguranca”]}
- Abundância:        {medias[“Abundancia”]}  → {intensidades[“Abundancia”]}

EIXO MAIS ALTO: {eixo_mais_alto}
EIXO MAIS BAIXO: {eixo_mais_baixo}

CONTRASTES:
{chr(10).join(f”- {k}: {v:+.2f}” for k, v in diferencas.items())}

FLAGS:
{chr(10).join(f”- {f}” for f in flags)}

HIPÓTESE TÉCNICA:
{chr(10).join(f”- {h}” for h in hipotese_tecnica)}

[Estrutura e regras completas enviadas — ver função gerar_relatorio() no código]
“””
st.code(prompt_preview, language=“text”)

```
# --- 10. Configuração do modelo ---
st.subheader("10. Configuração do Modelo AI")
st.caption("Parâmetros usados na chamada à API.")
st.json({
    "model": "gpt-4o",
    "temperature": 0.5,
    "perguntas_invertidas_count": len(PERGUNTAS_INVERTIDAS),
    "total_perguntas": len(questions),
    "eixos": list(blocos_info.keys()),
})
```

# =============================================================

# UI

# =============================================================

st.title(“🧠 Mind Insight AI”)
st.caption(“Análise de perfil comportamental • V5.0 • Desenvolvido com Claude (Anthropic)”)

TOTAL = len(questions)

if st.session_state.current_question <= TOTAL:
q_num = st.session_state.current_question
progresso = (q_num - 1) / TOTAL

```
st.progress(progresso)
st.caption(f"Pergunta {q_num} de {TOTAL}")
st.markdown(f"### {questions[q_num]}")

resposta = st.radio(
    "Sua resposta:",
    scale,
    index=None,
    key=f"q_{q_num}",
)

if st.button("Próxima →"):
    if resposta is not None:
        valor = int(resposta.split(" — ")[0])
        st.session_state.responses[q_num] = valor
        st.session_state.current_question += 1
        st.rerun()
    else:
        st.warning("Por favor, selecione uma resposta antes de continuar.")
```

else:
st.title(“🪞 Seu Relatório de Perfil”)

```
perfil = gerar_perfil(st.session_state.responses)

with st.spinner("Gerando sua análise..."):
    relatorio = gerar_relatorio(perfil)

st.markdown(relatorio)

if DEBUG_MODE:
    render_debug(perfil)

st.markdown("---")
if st.button("🔄 Refazer o teste"):
    st.session_state.responses = {}
    st.session_state.current_question = 1
    st.rerun()
```