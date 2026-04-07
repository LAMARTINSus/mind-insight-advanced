# -*- coding: utf-8 -*-

# =============================================================
# MIND INSIGHT ADVANCED AI
# Version: V5.4
# Criado com: Claude (Anthropic)
# Aperfeicoado por: Manus AI
#
# Historico de versoes:
# V5.0 - Versao original: 74 questoes, 7 eixos, gpt-4o
# V5.1 - Prompt recalibrado: 5 regras de validacao cruzada,
#         ranking de eixos, maior contraste obrigatorio
# V5.2 - Acentuacao completa em portugues
#       - Opcao de reutilizar respostas do ultimo teste
#       - Cabecalho atualizado com credito ao Manus AI
#       - Debug mantido ativo para fase de calibracao
# V5.3 - Engine: calcula todos os 21 contrastes (antes: 4 fixos)
#       - Engine: maior contraste real sempre capturado
#       - Engine: hipotese de combinacao Abertura+Extroversao adicionada
#       - Prompt: regra 3 agora usa contraste real (nao pre-definido)
#       - Prompt: regra 6 anti-contradicao de combinacao alta+baixa
#       - Prompt: secao 5 proibe comportamento extrovertido se Extroversao < 3.5
#       - Debug: exibe todos os 21 contrastes no painel
#       - Aviso de amplitude comprimida quando > 60% respostas sao 3-4
#       - Q63 removida das invertidas (semantica ambigua revisada)
# V5.4 - Q63 REESCRITA: nova pergunta mede aversao a risco/imprevisibilidade
#       - Q63 volta a ser invertida (semantica agora clara)
#       - Engine: scores diagnosticos por eixo passados ao prompt
#       - Prompt: completamente reformulado com linguagem humana e motivadora
#       - Prompt: nova estrutura orientada a forcas, lideranca e crescimento
#       - Prompt: proibido usar termos tecnicos (introversao, neuroticismo, etc)
#       - Prompt: relatorio deve fazer a pessoa se identificar e querer agir
# =============================================================

import streamlit as st
import pandas as pd
from openai import OpenAI

DEBUG_MODE = True

# =============================================================
# RESPOSTAS DO ULTIMO TESTE (para reutilizacao rapida)
# Remover esta secao apos a fase de calibracao
# =============================================================

ULTIMO_TESTE = {
    1: 4, 2: 2, 3: 4, 4: 2, 5: 4, 6: 2, 7: 4, 8: 4, 9: 2, 10: 4,
    11: 4, 12: 2, 13: 3, 14: 2, 15: 3, 16: 3, 17: 4, 18: 3, 19: 3, 20: 4,
    21: 3, 22: 3, 23: 3, 24: 3, 25: 3, 26: 3, 27: 3, 28: 3, 29: 3, 30: 3,
    31: 4, 32: 4, 33: 3, 34: 3, 35: 4, 36: 3, 37: 3, 38: 4, 39: 3, 40: 4, 41: 3,
    42: 3, 43: 3, 44: 4, 45: 3, 46: 3, 47: 3, 48: 3, 49: 4, 50: 3, 51: 3, 52: 3,
    53: 4, 54: 4, 55: 4, 56: 4, 57: 3, 58: 3, 59: 4, 60: 3, 61: 4, 62: 3, 63: 4,
    64: 4, 65: 2, 66: 3, 67: 3, 68: 4, 69: 3, 70: 3, 71: 3, 72: 3, 73: 3, 74: 3,
}

# =============================================================
# CONFIG
# =============================================================

st.set_page_config(
    page_title="Mind Insight AI",
    page_icon="\U0001f9e0",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
h1, h2, h3 { font-family: 'IBM Plex Mono', monospace; }
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
.stButton>button:hover { background-color: #333; border-color: #888; }
.manus-badge {
    font-size: 0.75rem;
    color: #888;
    font-family: 'IBM Plex Mono', monospace;
    margin-top: -0.5rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# =============================================================
# OPENAI CLIENT
# =============================================================

def get_openai_client():
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

# =============================================================
# SESSION STATE
# =============================================================

if "responses" not in st.session_state:
    st.session_state.responses = {}
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "modo_selecionado" not in st.session_state:
    st.session_state.modo_selecionado = False

# =============================================================
# PERGUNTAS
# 74 questoes - 10 ou 11 por eixo
# (I) = pontuacao invertida
# ABERTURA        Q1-Q10   (10 questoes)
# CONSCIENCIA     Q11-Q20  (10 questoes)
# EXTROVERSAO     Q21-Q30  (10 questoes)
# AMABILIDADE     Q31-Q41  (11 questoes)
# NEUROTICISMO    Q42-Q52  (11 questoes)
# SEGURANCA       Q53-Q63  (11 questoes)
# ABUNDANCIA      Q64-Q74  (11 questoes)
# =============================================================

questions = {
    # ABERTURA
    1:  "Fico genuinamente curioso quando encontro uma ideia que contradiz o que eu penso.",
    2:  "Prefiro solucoes ja testadas a experimentar abordagens novas.",
    3:  "Busco conhecimento em assuntos novos por prazer, nao por obrigacao.",
    4:  "Me incomoda quando conversas ficam muito abstratas ou filosoficas.",
    5:  "Consigo encontrar conexoes entre assuntos que parecem nao ter nada a ver.",
    6:  "Prefiro que as coisas sejam diretas e praticas, sem muita especulacao.",
    7:  "Ja mudei uma opiniao importante por causa de um argumento bem fundamentado.",
    8:  "Me atrai explorar areas onde ainda nao tenho dominio.",
    9:  "Acho desgastante quando alguem fica questionando como as coisas sempre foram feitas.",
    10: "Tenho imaginacao ativa - frequentemente visualizo cenarios, historias ou possibilidades.",
    # CONSCIENCIOSIDADE
    11: "Quando assumo um compromisso, cumpro - mesmo quando nao tenho mais vontade.",
    12: "Comeco tarefas importantes so quando estou com disposicao para isso.",
    13: "Tenho um sistema claro para organizar minhas prioridades do dia.",
    14: "Deixo para decidir na hora em vez de planejar com antecedencia.",
    15: "Quando comeco algo, tenho dificuldade de parar antes de terminar.",
    16: "Frequentemente percebo que deixei algo importante para a ultima hora.",
    17: "Reviso meu trabalho antes de entregar, mesmo quando estou confiante.",
    18: "Tenho clareza sobre o que precisa ser feito hoje para chegar onde quero em um ano.",
    19: "Me distraio com facilidade quando deveria estar focado em algo importante.",
    20: "Mantenho meus compromissos mesmo quando surgem opcoes mais atraentes.",
    # EXTROVERSAO
    21: "Me sinto com mais energia depois de passar tempo com pessoas do que antes.",
    22: "Em grupos, costumo tomar a iniciativa de falar primeiro.",
    23: "Prefiro pensar sozinho antes de discutir ideias com outros.",
    24: "Me sinto confortavel sendo o porta-voz de um grupo em situacoes formais.",
    25: "Depois de um dia social intenso, preciso de tempo sozinho para recarregar.",
    26: "Busco ativamente conhecer pessoas novas em ambientes sociais.",
    27: "Prefiro me comunicar por escrito a falar ao vivo quando tenho algo importante a dizer.",
    28: "Me sinto bem em ambientes barulhentos e movimentados.",
    29: "Em conversas em grupo, frequentemente fico mais ouvindo do que falando.",
    30: "Quando tenho uma opiniao, nao tenho dificuldade de exprimi-la mesmo que outros discordem.",
    # AMABILIDADE
    31: "Quando alguem esta passando por algo dificil, meu primeiro instinto e ajudar.",
    32: "Tenho facilidade para identificar como o outro esta se sentindo, mesmo sem ele dizer.",
    33: "Em desacordos, prefiro ceder do que prolongar o conflito.",
    34: "Me importo mais com o resultado certo do que com o que as pessoas vao pensar de mim.",
    35: "Fico desconfortavel quando percebo que decepcionei alguem.",
    36: "Consigo discordar de alguem sem que isso afete a relacao.",
    37: "Evito dar feedback negativo para nao criar tensao.",
    38: "Confio nas pessoas ate que me provem o contrario.",
    39: "Quando preciso dizer algo dificil, costumo adiar mais do que deveria.",
    40: "Me preocupo genuinamente com o bem-estar das pessoas ao meu redor, nao so das proximas.",
    41: "Frequentemente coloco as necessidades dos outros a frente das minhas, mesmo quando isso me custa.",
    # NEUROTICISMO
    42: "Quando algo da errado, fico remoendo o que aconteceu por horas ou dias.",
    43: "Me recupero emocionalmente rapido depois de situacoes dificeis.",
    44: "Frequentemente me preocupo com coisas que ainda nao aconteceram.",
    45: "Consigo manter a calma em situacoes de pressao alta.",
    46: "Pequenos contratempos do dia me afetam mais do que deveriam.",
    47: "Quando estou sob estresse, minha capacidade de tomar decisoes piora visivelmente.",
    48: "Me sinto estavel emocionalmente na maior parte do tempo.",
    49: "Fico ansioso quando nao sei o que esperar de uma situacao.",
    50: "Criticas, mesmo construtivas, me afetam emocionalmente por um tempo.",
    51: "Consigo separar o que sinto do que preciso fazer, mesmo em momentos dificeis.",
    52: "Quando cometo um erro, fico muito mais tempo me cobrando do que a situacao justificaria.",
    # SEGURANCA
    53: "Me sinto mais confortavel quando sei exatamente o que esperar de uma situacao.",
    54: "Consigo agir com confianca mesmo quando nao tenho todas as informacoes.",
    55: "Mudancas inesperadas nos meus planos me deixam mais incomodado do que a maioria.",
    56: "Prefiro uma oportunidade menor mas garantida a uma maior mas incerta.",
    57: "Me sinto bem entrando em situacoes onde nao sei exatamente o que vai acontecer.",
    58: "Demoro para confiar em pessoas ou ambientes novos.",
    59: "Quando estou numa rotina que funciona, resisto a mudar mesmo que haja opcoes melhores.",
    60: "Consigo me comprometer com algo antes de ter certeza absoluta de que vai dar certo.",
    61: "Sinto desconforto real quando preciso tomar decisoes sem um plano claro.",
    62: "Me sinto seguro mesmo em fases de transicao ou incerteza na minha vida.",
    63: "Prefiro confirmar os detalhes antes de agir do que improvisar no momento.",
    # ABUNDANCIA
    64: "Quando vejo alguem bem-sucedido, meu primeiro pensamento e de inspiracao, nao de comparacao.",
    65: "Sinto que as oportunidades disponiveis para mim sao limitadas.",
    66: "Consigo gastar dinheiro em algo que vale a pena sem sentir culpa depois.",
    67: "Frequentemente sinto que estou ficando para tras em relacao a onde deveria estar.",
    68: "Acredito que ha espaco para todo mundo crescer - o sucesso dos outros nao diminui o meu.",
    69: "Pensar em dinheiro me gera mais ansiedade do que clareza.",
    70: "Quando surge uma oportunidade nova, meu primeiro instinto e ver o que posso ganhar.",
    71: "Tenho dificuldade de investir em mim mesmo quando nao vejo retorno garantido.",
    72: "Me sinto a vontade para pedir o que acredito que meu trabalho vale.",
    73: "Sinto que, independente do que faco, nunca e suficiente.",
    74: "A possibilidade de perder o que ja tenho me preocupa mais do que a possibilidade de ganhar algo novo.",
}

# Versao com acentuacao completa para exibicao na tela
questions_display = {
    # ABERTURA
    1:  "Fico genuinamente curioso quando encontro uma ideia que contradiz o que eu penso.",
    2:  "Prefiro soluções já testadas a experimentar abordagens novas.",
    3:  "Busco conhecimento em assuntos novos por prazer, não por obrigação.",
    4:  "Me incomoda quando conversas ficam muito abstratas ou filosóficas.",
    5:  "Consigo encontrar conexões entre assuntos que parecem não ter nada a ver.",
    6:  "Prefiro que as coisas sejam diretas e práticas, sem muita especulação.",
    7:  "Já mudei uma opinião importante por causa de um argumento bem fundamentado.",
    8:  "Me atrai explorar áreas onde ainda não tenho domínio.",
    9:  "Acho desgastante quando alguém fica questionando como as coisas sempre foram feitas.",
    10: "Tenho imaginação ativa — frequentemente visualizo cenários, histórias ou possibilidades.",
    # CONSCIENCIOSIDADE
    11: "Quando assumo um compromisso, cumpro — mesmo quando não tenho mais vontade.",
    12: "Começo tarefas importantes só quando estou com disposição para isso.",
    13: "Tenho um sistema claro para organizar minhas prioridades do dia.",
    14: "Deixo para decidir na hora em vez de planejar com antecedência.",
    15: "Quando começo algo, tenho dificuldade de parar antes de terminar.",
    16: "Frequentemente percebo que deixei algo importante para a última hora.",
    17: "Reviso meu trabalho antes de entregar, mesmo quando estou confiante.",
    18: "Tenho clareza sobre o que precisa ser feito hoje para chegar onde quero em um ano.",
    19: "Me distraio com facilidade quando deveria estar focado em algo importante.",
    20: "Mantenho meus compromissos mesmo quando surgem opções mais atraentes.",
    # EXTROVERSAO
    21: "Me sinto com mais energia depois de passar tempo com pessoas do que antes.",
    22: "Em grupos, costumo tomar a iniciativa de falar primeiro.",
    23: "Prefiro pensar sozinho antes de discutir ideias com outros.",
    24: "Me sinto confortável sendo o porta-voz de um grupo em situações formais.",
    25: "Depois de um dia social intenso, preciso de tempo sozinho para recarregar.",
    26: "Busco ativamente conhecer pessoas novas em ambientes sociais.",
    27: "Prefiro me comunicar por escrito a falar ao vivo quando tenho algo importante a dizer.",
    28: "Me sinto bem em ambientes barulhentos e movimentados.",
    29: "Em conversas em grupo, frequentemente fico mais ouvindo do que falando.",
    30: "Quando tenho uma opinião, não tenho dificuldade de exprimi-la mesmo que outros discordem.",
    # AMABILIDADE
    31: "Quando alguém está passando por algo difícil, meu primeiro instinto é ajudar.",
    32: "Tenho facilidade para identificar como o outro está se sentindo, mesmo sem ele dizer.",
    33: "Em desacordos, prefiro ceder do que prolongar o conflito.",
    34: "Me importo mais com o resultado certo do que com o que as pessoas vão pensar de mim.",
    35: "Fico desconfortável quando percebo que decepcionei alguém.",
    36: "Consigo discordar de alguém sem que isso afete a relação.",
    37: "Evito dar feedback negativo para não criar tensão.",
    38: "Confio nas pessoas até que me provem o contrário.",
    39: "Quando preciso dizer algo difícil, costumo adiar mais do que deveria.",
    40: "Me preocupo genuinamente com o bem-estar das pessoas ao meu redor, não só das próximas.",
    41: "Frequentemente coloco as necessidades dos outros à frente das minhas, mesmo quando isso me custa.",
    # NEUROTICISMO
    42: "Quando algo dá errado, fico remoendo o que aconteceu por horas ou dias.",
    43: "Me recupero emocionalmente rápido depois de situações difíceis.",
    44: "Frequentemente me preocupo com coisas que ainda não aconteceram.",
    45: "Consigo manter a calma em situações de pressão alta.",
    46: "Pequenos contratempos do dia me afetam mais do que deveriam.",
    47: "Quando estou sob estresse, minha capacidade de tomar decisões piora visivelmente.",
    48: "Me sinto estável emocionalmente na maior parte do tempo.",
    49: "Fico ansioso quando não sei o que esperar de uma situação.",
    50: "Críticas, mesmo construtivas, me afetam emocionalmente por um tempo.",
    51: "Consigo separar o que sinto do que preciso fazer, mesmo em momentos difíceis.",
    52: "Quando cometo um erro, fico muito mais tempo me cobrando do que a situação justificaria.",
    # SEGURANCA
    53: "Me sinto mais confortável quando sei exatamente o que esperar de uma situação.",
    54: "Consigo agir com confiança mesmo quando não tenho todas as informações.",
    55: "Mudanças inesperadas nos meus planos me deixam mais incomodado do que a maioria.",
    56: "Prefiro uma oportunidade menor mas garantida a uma maior mas incerta.",
    57: "Me sinto bem entrando em situações onde não sei exatamente o que vai acontecer.",
    58: "Demoro para confiar em pessoas ou ambientes novos.",
    59: "Quando estou numa rotina que funciona, resisto a mudar mesmo que haja opções melhores.",
    60: "Consigo me comprometer com algo antes de ter certeza absoluta de que vai dar certo.",
    61: "Sinto desconforto real quando preciso tomar decisões sem um plano claro.",
    62: "Me sinto seguro mesmo em fases de transição ou incerteza na minha vida.",
    63: "Prefiro confirmar os detalhes antes de agir do que improvisar no momento.",
    # ABUNDANCIA
    64: "Quando vejo alguém bem-sucedido, meu primeiro pensamento é de inspiração, não de comparação.",
    65: "Sinto que as oportunidades disponíveis para mim são limitadas.",
    66: "Consigo gastar dinheiro em algo que vale a pena sem sentir culpa depois.",
    67: "Frequentemente sinto que estou ficando para trás em relação a onde deveria estar.",
    68: "Acredito que há espaço para todo mundo crescer — o sucesso dos outros não diminui o meu.",
    69: "Pensar em dinheiro me gera mais ansiedade do que clareza.",
    70: "Quando surge uma oportunidade nova, meu primeiro instinto é ver o que posso ganhar.",
    71: "Tenho dificuldade de investir em mim mesmo quando não vejo retorno garantido.",
    72: "Me sinto à vontade para pedir o que acredito que meu trabalho vale.",
    73: "Sinto que, independente do que faço, nunca é suficiente.",
    74: "A possibilidade de perder o que já tenho me preocupa mais do que a possibilidade de ganhar algo novo.",
}

scale = [
    "1 - Discordo totalmente",
    "2 - Discordo",
    "3 - Neutro",
    "4 - Concordo",
    "5 - Concordo totalmente",
]

# =============================================================
# INVERSAO DE PONTUACAO
# Perguntas onde concordar = traco BAIXO
# score_invertido = 6 - score_original
# Exemplo: resposta 5 vira 1 / resposta 4 vira 2
# =============================================================

PERGUNTAS_INVERTIDAS = {
    2, 4, 6, 9,
    12, 14, 16, 19,
    23, 25, 27, 29,
    33, 34, 37, 39,
    43, 45, 48, 51,
    54, 57, 60, 62, 63,
    65, 67, 69, 71, 73, 74
}

def aplicar_inversao(q, score):
    if q in PERGUNTAS_INVERTIDAS:
        return 6 - score
    return score

# =============================================================
# ENGINE DE CALCULO DO PERFIL
# =============================================================

def gerar_perfil(respostas):
    respostas_ajustadas = {
        q: aplicar_inversao(q, s)
        for q, s in respostas.items()
    }

    df = pd.DataFrame(
        list(respostas_ajustadas.items()),
        columns=["Q", "Score"]
    )

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

    eixo_mais_alto  = max(medias, key=medias.get)
    eixo_mais_baixo = min(medias, key=medias.get)

    # Calcular TODOS os 21 contrastes possiveis entre os 7 eixos
    eixos_lista = list(medias.keys())
    diferencas = {}
    for i in range(len(eixos_lista)):
        for j in range(i + 1, len(eixos_lista)):
            e1, e2 = eixos_lista[i], eixos_lista[j]
            diferencas[e1 + "_vs_" + e2] = round(medias[e1] - medias[e2], 2)

    media_geral   = round(df["Score"].mean(), 2)
    desvio_padrao = round(float(df["Score"].std(ddof=0)), 3)
    amplitude     = int(df["Score"].max() - df["Score"].min())

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

    flags = []
    if medias["Seguranca"] > medias["Abundancia"]:
        flags.append("mais orientacao a seguranca do que a expansao")
    if medias["Amabilidade"] > medias["Extroversao"]:
        flags.append("mais adaptacao relacional do que impulso de exposicao")
    if medias["Abundancia"] < 3:
        flags.append("baixa percepcao de abundancia")
    if medias["Neuroticismo"] >= 3.5:
        flags.append("reatividade emocional elevada")
    elif medias["Neuroticismo"] >= 3.0:
        flags.append("sensibilidade emocional presente")
    if medias["Seguranca"] >= 3.5:
        flags.append("forte orientacao a estabilidade e previsibilidade")
    if medias["Conscienciosidade"] >= 3.5:
        flags.append("alto senso de responsabilidade e disciplina")
    if medias["Abertura"] >= 3.5:
        flags.append("abertura intelectual e curiosidade acima da media")
    if medias["Extroversao"] < 3:
        flags.append("introversao predominante - energia social mais contida")
    if medias["Amabilidade"] >= 4.0:
        flags.append("amabilidade muito alta - possivel custo em assertividade")

    hipotese_tecnica = []
    if medias["Seguranca"] > medias["Abundancia"]:
        hipotese_tecnica.append("tendencia a preservar estabilidade antes de explorar oportunidade")
    if medias["Amabilidade"] >= 3.5:
        hipotese_tecnica.append("forte tendencia a manter harmonia relacional - possivel custo em assertividade e limites")
    if medias["Extroversao"] < 3:
        hipotese_tecnica.append("introversao predominante - processa internamente antes de externalizar")
    if medias["Abundancia"] < 3:
        hipotese_tecnica.append("possivel restricao na relacao com expansao, valor ou oportunidade - mentalidade de escassez")
    if medias["Neuroticismo"] >= 3.5:
        hipotese_tecnica.append("reatividade emocional elevada - pode impactar decisoes sob pressao e sob critica")
    if medias["Conscienciosidade"] >= 3.5:
        hipotese_tecnica.append("alto padrao de entrega e responsabilidade - possivel rigidez ou autocritica excessiva")
    if medias["Abertura"] >= 3.5 and medias["Conscienciosidade"] < 3:
        hipotese_tecnica.append("gerador de ideias com dificuldade de execucao sistematica")
    if medias["Abertura"] < 3 and medias["Conscienciosidade"] >= 3.5:
        hipotese_tecnica.append("executor confiavel com resistencia a mudanca de rota ou metodo")
    if medias["Abertura"] >= 3.5 and medias["Extroversao"] < 3.5:
        diff_ab_ex = round(medias["Abertura"] - medias["Extroversao"], 2)
        hipotese_tecnica.append(
            "curiosidade intelectual intensa (Abertura %.2f) processada internamente - "
            "Extroversao %.2f indica que explora sozinho, nao em grupo. "
            "Contraste Abertura_vs_Extroversao = %+.2f" % (
                medias["Abertura"], medias["Extroversao"], diff_ab_ex
            )
        )

    def intensidade(valor):
        if valor >= 4.3:
            return "muito alto - traco dominante"
        elif valor >= 3.5:
            return "alto - padrao consistente"
        elif valor >= 3.0:
            return "moderado - contextual"
        elif valor >= 2.1:
            return "abaixo da media - tendencia limitante"
        else:
            return "muito baixo - ausencia marcante"

    intensidades = {k: intensidade(v) for k, v in medias.items()}

    # Ranking de eixos do mais alto ao mais baixo
    ranking_eixos = sorted(medias.items(), key=lambda x: -x[1])

    # Maior contraste absoluto entre TODOS os 21 pares
    maior_contraste_key = max(diferencas, key=lambda k: abs(diferencas[k]))
    maior_contraste_val = diferencas[maior_contraste_key]

    # Aviso de amplitude comprimida
    all_adj_vals = list(respostas_ajustadas.values())
    pct_3_4 = sum(1 for v in all_adj_vals if v in (3, 4)) / len(all_adj_vals) * 100
    alerta_amplitude = pct_3_4 > 60

    # Eixos abaixo de 3.0 (limitantes)
    eixos_baixos = {k: v for k, v in medias.items() if v < 3.0}

    # Eixos moderados (3.0-3.4) - nao devem ser tratados como problematicos
    eixos_moderados = {k: v for k, v in medias.items() if 3.0 <= v < 3.5}

    # Scores diagnosticos por eixo (questoes mais reveladoras)
    adj = respostas_ajustadas
    scores_diagnosticos = {
        "Conscienciosidade": {
            "cumpre_compromissos_Q11":      adj.get(11, 3),
            "revisa_antes_entregar_Q17":    adj.get(17, 3),
            "mantem_compromissos_Q20":      adj.get(20, 3),
            "tem_sistema_prioridades_Q13":  adj.get(13, 3),
            "clareza_metas_longo_prazo_Q18": adj.get(18, 3),
            "se_distrai_facilmente_Q19":    adj.get(19, 3),
        },
        "Seguranca": {
            "prefere_saber_o_que_esperar_Q53":  adj.get(53, 3),
            "mudancas_incomodam_Q55":           adj.get(55, 3),
            "prefere_menor_garantido_Q56":      adj.get(56, 3),
            "resiste_mudar_rotina_Q59":         adj.get(59, 3),
            "age_sem_informacoes_Q54":          adj.get(54, 3),
            "confirma_antes_de_agir_Q63":       adj.get(63, 3),
        },
        "Extroversao": {
            "energia_com_pessoas_Q21":      adj.get(21, 3),
            "toma_iniciativa_grupo_Q22":    adj.get(22, 3),
            "busca_pessoas_novas_Q26":      adj.get(26, 3),
            "prefere_pensar_sozinho_Q23":   adj.get(23, 3),
        },
        "Amabilidade": {
            "ajuda_instintivamente_Q31":    adj.get(31, 3),
            "le_emocoes_dos_outros_Q32":    adj.get(32, 3),
            "fica_mal_ao_decepcionar_Q35":  adj.get(35, 3),
            "coloca_outros_na_frente_Q41": adj.get(41, 3),
        },
        "Neuroticismo": {
            "preocupa_com_futuro_Q44":      adj.get(44, 3),
            "ansioso_sem_previsibilidade_Q49": adj.get(49, 3),
            "rumina_erros_Q52":             adj.get(52, 3),
        },
    }

    return {
        "medias":              medias,
        "intensidades":        intensidades,
        "eixo_mais_alto":      eixo_mais_alto,
        "eixo_mais_baixo":     eixo_mais_baixo,
        "diferencas":          diferencas,
        "media_geral":         media_geral,
        "desvio_padrao":       desvio_padrao,
        "amplitude":           amplitude,
        "tipo_resposta":       tipo_resposta,
        "confiabilidade":      confiabilidade,
        "flags":               flags,
        "hipotese_tecnica":    hipotese_tecnica,
        "respostas_brutas":    dict(sorted(respostas.items())),
        "respostas_ajustadas": dict(sorted(respostas_ajustadas.items())),
        "ranking_eixos":       ranking_eixos,
        "maior_contraste_key": maior_contraste_key,
        "maior_contraste_val": maior_contraste_val,
        "eixos_baixos":        eixos_baixos,
        "eixos_moderados":       eixos_moderados,
        "alerta_amplitude":      alerta_amplitude,
        "pct_3_4":               round(pct_3_4, 1),
        "scores_diagnosticos":   scores_diagnosticos,
    }

# =============================================================
# GERACAO DO RELATORIO (PROMPT CALIBRADO V5.4)
# =============================================================

def gerar_relatorio(perfil):
    client = get_openai_client()
    if client is None:
        return "Erro: OPENAI_API_KEY nao encontrada em Secrets."

    medias               = perfil["medias"]
    intensidades         = perfil["intensidades"]
    eixo_alto            = perfil["eixo_mais_alto"]
    eixo_baixo           = perfil["eixo_mais_baixo"]
    ranking_eixos        = perfil["ranking_eixos"]
    maior_contraste_key  = perfil["maior_contraste_key"]
    maior_contraste_val  = perfil["maior_contraste_val"]
    eixos_baixos         = perfil["eixos_baixos"]
    hipotese             = perfil["hipotese_tecnica"]
    diag                 = perfil["scores_diagnosticos"]

    # Linhas do ranking
    linhas_ranking = "\n".join([
        "  %d. %s: %.2f  [%s]" % (i + 1, k, v, intensidades[k])
        for i, (k, v) in enumerate(ranking_eixos)
    ])

    # Linhas de medias
    linhas_medias = "\n".join([
        "- %s: %.2f  -> %s" % (k, v, intensidades[k])
        for k, v in medias.items()
    ])

    # Scores diagnosticos formatados
    def fmt_diag(eixo):
        items = diag.get(eixo, {})
        return "\n".join(["    %s = %d" % (k, v) for k, v in items.items()])

    # Eixos abaixo de 3.0
    eixos_baixos_str = ", ".join([
        "%s %.2f" % (k, v) for k, v in eixos_baixos.items()
    ]) if eixos_baixos else "nenhum"

    linhas_hipotese = "\n".join(["- " + h for h in hipotese])

    prompt = (
        "Voce e um especialista em comportamento humano que escreve relatorios de perfil.\n"
        "Seu objetivo e fazer a pessoa ler o relatorio e pensar: 'isso sou eu de verdade'.\n"
        "O relatorio deve ser humano, direto, especifico e motivador.\n"
        "Ele deve ajudar a pessoa a entender onde ela brilha, onde ela trava, e o que ela pode fazer a respeito.\n\n"

        "DADOS DO PERFIL:\n"
        "Escala: 1.0 (muito baixo) a 5.0 (muito alto). Media 3.0 = neutro.\n\n"

        "RANKING DOS EIXOS (do mais alto ao mais baixo):\n"
        + linhas_ranking + "\n\n"

        "MEDIAS POR EIXO:\n"
        + linhas_medias + "\n\n"

        "MAIOR CONTRASTE DO PERFIL: " + maior_contraste_key
        + " = %+.2f\n" % maior_contraste_val
        + "(Este e o padrao mais revelador desta pessoa - DEVE aparecer no relatorio)\n\n"

        "SCORES DIAGNOSTICOS DE CONSCIENCIOSIDADE:\n"
        + fmt_diag("Conscienciosidade") + "\n"
        + "ATENCAO: cumpre_compromissos=" + str(diag.get("Conscienciosidade", {}).get("cumpre_compromissos_Q11", 3))
        + " e revisa_antes_entregar=" + str(diag.get("Conscienciosidade", {}).get("revisa_antes_entregar_Q17", 3))
        + " sao altos, mas tem_sistema_prioridades=" + str(diag.get("Conscienciosidade", {}).get("tem_sistema_prioridades_Q13", 3))
        + " e clareza_metas_longo_prazo=" + str(diag.get("Conscienciosidade", {}).get("clareza_metas_longo_prazo_Q18", 3))
        + " sao moderados. NAO diga que a pessoa 'planeja minuciosamente' ou 'tem visao estrategica de longo prazo'.\n"
        + "DIGA que ela e confiavel, entrega com qualidade, cumpre o que promete.\n\n"

        "SCORES DIAGNOSTICOS DE SEGURANCA:\n"
        + fmt_diag("Seguranca") + "\n"
        + "ATENCAO: prefere_saber_o_que_esperar=" + str(diag.get("Seguranca", {}).get("prefere_saber_o_que_esperar_Q53", 3))
        + " e mudancas_incomodam=" + str(diag.get("Seguranca", {}).get("mudancas_incomodam_Q55", 3))
        + " e prefere_menor_garantido=" + str(diag.get("Seguranca", {}).get("prefere_menor_garantido_Q56", 3))
        + " sao altos. Isso indica preferencia real por previsibilidade. Use isso concretamente.\n\n"

        "SCORES DIAGNOSTICOS DE EXTROVERSAO:\n"
        + fmt_diag("Extroversao") + "\n\n"

        "SCORES DIAGNOSTICOS DE AMABILIDADE:\n"
        + fmt_diag("Amabilidade") + "\n\n"

        "SCORES DIAGNOSTICOS DE NEUROTICISMO:\n"
        + fmt_diag("Neuroticismo") + "\n\n"

        "HIPOTESE TECNICA (base para o relatorio):\n"
        + linhas_hipotese + "\n\n"

        "DEFINICAO DOS EIXOS (para sua referencia interna - NAO cite esses nomes no relatorio):\n"
        "- Abertura: curiosidade intelectual, apreciacao por novidade, imaginacao, flexibilidade mental\n"
        "- Conscienciosidade: responsabilidade, disciplina, qualidade de entrega, confiabilidade\n"
        "- Extroversao: energia social, assertividade, sociabilidade, busca por estimulo externo\n"
        "- Amabilidade: empatia, cooperacao, cuidado com os outros, generosidade\n"
        "- Neuroticismo: ansiedade, sensibilidade emocional, ruminacao, reatividade a estresse\n"
        "- Seguranca: necessidade de previsibilidade, aversao a risco, preferencia por rotina\n"
        "- Abundancia: mentalidade de escassez vs. fartura, relacao com recursos e oportunidades\n\n"

        "COMBINACOES IMPORTANTES PARA ESTE PERFIL:\n"
        "- Abertura alta + Extroversao moderada = curiosidade intensa exercida de forma mais interna e seletiva\n"
        "- Conscienciosidade alta = entrega com qualidade, mas pode ser autocritico\n"
        "- Seguranca moderada-alta = prefere certeza antes de agir, pode perder oportunidades por excesso de cautela\n"
        "- Amabilidade alta + Extroversao moderada = muito presente nas relacoes proximas, mas nao busca exposicao ampla\n\n"

        "REGRAS ABSOLUTAS:\n"
        "1. Escreva sempre em 'voce' - nunca em terceira pessoa\n"
        "2. NUNCA use os nomes dos eixos (Abertura, Conscienciosidade, etc.) no texto\n"
        "3. NUNCA use termos tecnicos como 'introversao', 'neuroticismo', 'extroversao'\n"
        "4. NUNCA escreva frases que servem para qualquer pessoa ('voce e uma pessoa curiosa')\n"
        "5. NUNCA diga 'planeja minuciosamente', 'foco excepcional' ou 'visao estrategica' - os dados nao sustentam\n"
        "6. NUNCA diga que a pessoa 'toma iniciativa em grupo' ou 'e a primeira a agir publicamente' - Extroversao = "
        + "%.2f\n" % medias["Extroversao"]
        + "7. Cada afirmacao deve ser verificavel nos dados - se voce nao consegue apontar qual score sustenta, nao escreva\n"
        + "8. O relatorio deve ser especifico o suficiente para que a pessoa pense 'como voce sabia disso?'\n\n"

        "ESTRUTURA OBRIGATORIA DO RELATORIO:\n\n"

        "1. COMO VOCE FUNCIONA DE VERDADE\n"
        "Baseado nos dois eixos mais altos. Descreva como essa pessoa entra em situacoes novas, "
        "como reage sob pressao, como se posiciona. Use situacoes do dia a dia. "
        "Seja especifico: o que ela faz que outras pessoas nao fazem?\n\n"

        "2. COMO VOCE TOMA DECISOES\n"
        "Baseado em Conscienciosidade, Seguranca e Abertura. "
        "Mostre o processo de decisao real: onde ela e forte, onde ela trava, o que ela prioriza. "
        "Use os scores diagnosticos para ser preciso.\n\n"

        "3. COMO VOCE SE RELACIONA\n"
        "Baseado em Amabilidade, Extroversao e Neuroticismo. "
        "Mostre como ela cria conexoes, como ela se comporta em grupos vs. um a um, "
        "onde ela da mais do que deveria e onde isso cobra um preco.\n\n"

        "4. O QUE ACONTECE DENTRO DE VOCE\n"
        "Use o maior contraste do perfil ("
        + maior_contraste_key + " = %+.2f) como eixo central. " % maior_contraste_val
        + "Descreva o dialogo interno que esse contraste cria. "
        "O que essa pessoa sente mas raramente diz? O que acontece na cabeca dela que os outros nao veem?\n\n"

        "5. ONDE VOCE PODE BRILHAR\n"
        "Este e o ponto mais importante do relatorio. "
        "Com base no perfil completo, identifique 3 a 4 contextos, funcoes ou situacoes onde essa pessoa "
        "teria desempenho excepcional usando suas forcas naturais. "
        "Inclua exemplos de areas profissionais, tipos de lideranca, projetos ou papeis onde ela se destacaria. "
        "Seja concreto: nao diga 'voce seria bom em trabalhos criativos', diga qual tipo de trabalho e por que esse perfil especifico brilha nele.\n\n"

        "6. SUAS FORCAS REAIS\n"
        "Maximo 5. Formato obrigatorio: 'Voce [verbo concreto e especifico] quando [situacao especifica]'. "
        "Cada forca deve ser sustentada por um score >= 3.5. Nada generico.\n\n"

        "7. ONDE VOCE TRAVA\n"
        "Maximo 4. Formato obrigatorio: 'Porque voce tende a [padrao especifico], "
        "o que acontece na pratica e [consequencia concreta e real]'. "
        "Seja direto. Nao suavize. Mostre o custo real desse padrao na vida profissional e pessoal.\n\n"

        "8. O QUE VALE DESENVOLVER\n"
        "Identifique 2 a 3 areas de desenvolvimento que, se trabalhadas, teriam o maior impacto "
        "no crescimento pessoal, profissional ou financeiro desta pessoa. "
        "Nao e sobre 'fraquezas' - e sobre o que, se desenvolvido, abriria novas possibilidades. "
        "Seja especifico sobre o que desenvolver e qual seria o impacto concreto.\n\n"

        "9. PROXIMOS PASSOS\n"
        "4 acoes concretas e executaveis na proxima semana. "
        "Cada acao deve derivar diretamente de um padrao especifico deste perfil. "
        "Formato: acao especifica + por que faz sentido para este perfil + o que muda se ela fizer isso. "
        "Nada generico. Nada que qualquer pessoa poderia fazer.\n\n"

        "TOM E ESTILO:\n"
        "- Escreva como um mentor que conhece a pessoa de verdade, nao como um relatorio de RH\n"
        "- Seja direto e humano ao mesmo tempo\n"
        "- Mostre que voce entende o que e ser essa pessoa especifica\n"
        "- O objetivo e que a pessoa leia e sinta vontade de agir - nao apenas de concordar\n"
        "- Evite listas de adjetivos. Prefira frases que descrevem comportamentos reais\n"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Voce e um analista de comportamento humano. "
                        "Sua funcao e traduzir dados de perfil em leituras precisas, humanas e especificas. "
                        "Voce nunca generaliza. Voce nunca inventa. "
                        "Voce so escreve o que os dados sustentam."
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
        return "Erro ao gerar relatorio:\n\n" + str(e)

# =============================================================
# DEBUG RENDER
# =============================================================

def render_debug(perfil):
    st.markdown("---")
    st.header("Debug - Transparencia Total do Perfil")
    st.caption(
        "Este painel mostra todos os dados, calculos e logica usados para gerar o relatorio. "
        "Para desativar: mude DEBUG_MODE = False no topo do arquivo."
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

    st.subheader("1. Respostas Brutas")
    st.caption("Score original sem transformacao. Verifique se o app registrou corretamente cada resposta.")
    brutas = perfil["respostas_brutas"]
    df_brutas = pd.DataFrame([
        {
            "Q": q,
            "Pergunta": questions_display.get(q, "-"),
            "Score Bruto": s,
            "Invertida?": "sim" if q in PERGUNTAS_INVERTIDAS else "-"
        }
        for q, s in brutas.items()
    ])
    st.dataframe(df_brutas, use_container_width=True)

    st.subheader("2. Respostas Apos Inversao")
    st.caption("Score apos inversao. Este e o dado que entra nos calculos de media.")
    ajustadas = perfil["respostas_ajustadas"]
    df_aj = pd.DataFrame([
        {
            "Q": q,
            "Pergunta": questions_display.get(q, "-"),
            "Score Bruto": brutas[q],
            "Score Ajustado": ajustadas[q],
            "Diferenca": ajustadas[q] - brutas[q]
        }
        for q in brutas
    ])
    st.dataframe(df_aj, use_container_width=True)

    st.subheader("3. Medias por Eixo")
    st.caption("Media dos scores ajustados. Este e o numero central do perfil.")
    medias = perfil["medias"]
    intensidades = perfil["intensidades"]
    for eixo, (q_ini, q_fim) in blocos_info.items():
        media = medias[eixo]
        pct = (media - 1) / 4
        bar_filled = int(pct * 30)
        bar = "#" * bar_filled + "." * (30 - bar_filled)
        st.markdown(
            "**" + eixo + "** (Q" + str(q_ini) + "-Q" + str(q_fim) + ")  \n"
            "`" + bar + "` **" + str(media) + "** - " + intensidades[eixo]
        )

    st.subheader("4. Ranking dos Eixos")
    for i, (k, v) in enumerate(perfil["ranking_eixos"]):
        st.write("%d. **%s**: %.2f  [%s]" % (i + 1, k, v, intensidades[k]))

    st.subheader("5. Maior Contraste do Perfil")
    st.info(
        "**%s** = %+.2f" % (perfil["maior_contraste_key"], perfil["maior_contraste_val"])
        + "  (este contraste e obrigatorio no relatorio)"
    )

    st.subheader("6. Eixos Extremos")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Eixo Mais Alto", perfil["eixo_mais_alto"], str(medias[perfil["eixo_mais_alto"]]))
    with col2:
        st.metric("Eixo Mais Baixo", perfil["eixo_mais_baixo"], str(medias[perfil["eixo_mais_baixo"]]))

    st.subheader("7. Contrastes Entre Eixos (todos os 21 pares)")
    st.caption("Diferenca entre todos os pares de eixos. Contrastes altos revelam tensoes comportamentais.")
    for par, valor in sorted(perfil["diferencas"].items(), key=lambda x: -abs(x[1])):
        direcao = "alto" if valor > 0 else ("baixo" if valor < 0 else "igual")
        marker = " <- MAIOR CONTRASTE" if par == perfil["maior_contraste_key"] else ""
        st.write("**" + par + "**: " + str(valor) + " (" + direcao + ")" + marker)

    if perfil.get("alerta_amplitude"):
        st.warning(
            "AVISO: %.1f%% das respostas sao 3 ou 4. "
            "Amplitude comprimida pode reduzir a precisao do relatorio. "
            "Considere responder com mais 1 e 5 quando sentir certeza." % perfil["pct_3_4"]
        )

    st.subheader("8. Qualidade Estatistica")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Media Geral",    str(perfil["media_geral"]))
    col2.metric("Desvio Padrao",  str(perfil["desvio_padrao"]))
    col3.metric("Amplitude",      str(perfil["amplitude"]))
    col4.metric("Tipo Resposta",  perfil["tipo_resposta"])
    col5.metric("Confiabilidade", perfil["confiabilidade"])

    st.subheader("9. Flags Automaticas")
    for flag in perfil["flags"]:
        st.write(">> " + flag)

    st.subheader("10. Hipotese Tecnica")
    st.caption("E o que o AI recebe como base. Se estiver errado aqui, o relatorio estara errado.")
    for h in perfil["hipotese_tecnica"]:
        st.write("-> " + h)

    st.subheader("11. Configuracao do Modelo")
    st.json({
        "model": "gpt-4o",
        "temperature": 0.5,
        "perguntas_invertidas": len(PERGUNTAS_INVERTIDAS),
        "total_perguntas": len(questions),
        "eixos": list(blocos_info.keys()),
        "total_contrastes_calculados": len(perfil["diferencas"]),
        "versao_prompt": "V5.3 - calibrado por Manus AI",
    })

# =============================================================
# INTERFACE PRINCIPAL
# =============================================================

st.title("Mind Insight AI")
st.markdown(
    '<div class="manus-badge">V5.3 | Criado com Claude (Anthropic) | '
    'Aperfeicoado por Manus AI | Debug ativo</div>',
    unsafe_allow_html=True
)

TOTAL = len(questions)

# ------------------------------------------------------------------
# TELA 0 - Selecao de modo (antes da pergunta 1)
# ------------------------------------------------------------------
if not st.session_state.modo_selecionado:
    st.markdown("---")
    st.subheader("Como voce quer comecar?")
    st.caption(
        "Opcao de reutilizacao disponivel apenas durante a fase de calibracao. "
        "Sera removida na versao final."
    )

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Usar respostas do ultimo teste**")
        st.caption(
            "Carrega automaticamente as 74 respostas ja registradas. "
            "Gera o relatorio em segundos sem precisar responder novamente."
        )
        if st.button("Usar ultimo teste", key="btn_ultimo"):
            st.session_state.responses = dict(ULTIMO_TESTE)
            st.session_state.current_question = TOTAL + 1
            st.session_state.modo_selecionado = True
            st.rerun()

    with col_b:
        st.markdown("**Responder o questionario novamente**")
        st.caption(
            "Responde todas as 74 perguntas do zero. "
            "Use quando quiser registrar um novo conjunto de respostas."
        )
        if st.button("Responder questionario", key="btn_novo"):
            st.session_state.responses = {}
            st.session_state.current_question = 1
            st.session_state.modo_selecionado = True
            st.rerun()

# ------------------------------------------------------------------
# TELA 1 - Questionario
# ------------------------------------------------------------------
elif st.session_state.current_question <= TOTAL:
    q_num = st.session_state.current_question
    progresso = (q_num - 1) / TOTAL

    st.progress(progresso)
    st.caption("Pergunta " + str(q_num) + " de " + str(TOTAL))
    st.markdown("### " + questions_display[q_num])

    resposta = st.radio(
        "Sua resposta:",
        scale,
        index=None,
        key="q_" + str(q_num),
    )

    if st.button("Proxima"):
        if resposta is not None:
            valor = int(resposta.split(" - ")[0])
            st.session_state.responses[q_num] = valor
            st.session_state.current_question += 1
            st.rerun()
        else:
            st.warning("Por favor, selecione uma resposta antes de continuar.")

# ------------------------------------------------------------------
# TELA 2 - Relatorio
# ------------------------------------------------------------------
else:
    st.title("Seu Relatorio de Perfil")

    perfil = gerar_perfil(st.session_state.responses)

    with st.spinner("Gerando sua analise..."):
        relatorio = gerar_relatorio(perfil)

    st.markdown(relatorio)

    if DEBUG_MODE:
        render_debug(perfil)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Refazer o teste"):
            st.session_state.responses = {}
            st.session_state.current_question = 1
            st.session_state.modo_selecionado = False
            st.rerun()
    with col2:
        if st.button("Voltar ao inicio"):
            st.session_state.responses = {}
            st.session_state.current_question = 0
            st.session_state.modo_selecionado = False
            st.rerun()
