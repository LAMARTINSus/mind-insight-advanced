# -*- coding: utf-8 -*-

# =============================================================
# MIND INSIGHT ADVANCED AI
# Version: V5.2
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
    63: "Minha sensacao de estabilidade depende mais do que eu penso sobre mim do que do que os outros pensam.",
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
    63: "Minha sensação de estabilidade depende mais do que eu penso sobre mim do que do que os outros pensam.",
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

    diferencas = {
        "Seguranca_vs_Abundancia":       round(medias["Seguranca"] - medias["Abundancia"], 2),
        "Conscienciosidade_vs_Abertura": round(medias["Conscienciosidade"] - medias["Abertura"], 2),
        "Neuroticismo_vs_Extroversao":   round(medias["Neuroticismo"] - medias["Extroversao"], 2),
        "Neuroticismo_vs_Seguranca":     round(medias["Neuroticismo"] - medias["Seguranca"], 2),
    }

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

    # Maior contraste absoluto entre pares de eixos
    maior_contraste_key = max(diferencas, key=lambda k: abs(diferencas[k]))
    maior_contraste_val = diferencas[maior_contraste_key]

    # Eixos abaixo de 3.0 (limitantes)
    eixos_baixos = {k: v for k, v in medias.items() if v < 3.0}

    # Eixos moderados (3.0-3.4) - nao devem ser tratados como problematicos
    eixos_moderados = {k: v for k, v in medias.items() if 3.0 <= v < 3.5}

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
        "eixos_moderados":     eixos_moderados,
    }

# =============================================================
# GERACAO DO RELATORIO (PROMPT CALIBRADO V5.2)
# =============================================================

def gerar_relatorio(perfil):
    client = get_openai_client()
    if client is None:
        return "Erro: OPENAI_API_KEY nao encontrada em Secrets."

    medias               = perfil["medias"]
    intensidades         = perfil["intensidades"]
    eixo_alto            = perfil["eixo_mais_alto"]
    eixo_baixo           = perfil["eixo_mais_baixo"]
    diferencas           = perfil["diferencas"]
    flags                = perfil["flags"]
    hipotese             = perfil["hipotese_tecnica"]
    ranking_eixos        = perfil["ranking_eixos"]
    maior_contraste_key  = perfil["maior_contraste_key"]
    maior_contraste_val  = perfil["maior_contraste_val"]
    eixos_baixos         = perfil["eixos_baixos"]
    eixos_moderados      = perfil["eixos_moderados"]

    linhas_ranking = "\n".join([
        "  %d. %s: %.2f  [%s]" % (i + 1, k, v, intensidades[k])
        for i, (k, v) in enumerate(ranking_eixos)
    ])

    linhas_medias = "\n".join([
        "- %s: %.2f  -> %s" % (k, v, intensidades[k])
        for k, v in medias.items()
    ])

    linhas_diferencas = "\n".join([
        "- %s: %+.2f%s" % (k, v, " <- MAIOR CONTRASTE DO PERFIL" if k == maior_contraste_key else "")
        for k, v in sorted(diferencas.items(), key=lambda x: -abs(x[1]))
    ])

    linhas_flags    = "\n".join(["- " + f for f in flags])
    linhas_hipotese = "\n".join(["- " + h for h in hipotese])

    if eixos_baixos:
        linhas_eixos_baixos = "\n".join([
            "- %s: %.2f (abaixo de 3.0 - traco limitante real)" % (k, v)
            for k, v in eixos_baixos.items()
        ])
    else:
        linhas_eixos_baixos = "- Nenhum eixo abaixo de 3.0"

    if eixos_moderados:
        linhas_eixos_moderados = "\n".join([
            "- %s: %.2f (moderado - nao e ponto critico)" % (k, v)
            for k, v in eixos_moderados.items()
        ])
    else:
        linhas_eixos_moderados = "- Nenhum eixo moderado"

    eixos_baixos_str = ", ".join([
        "%s %.2f" % (k, v) for k, v in eixos_baixos.items()
    ]) if eixos_baixos else "nenhum"

    prompt = (
        "Voce esta analisando uma pessoa real com base em dados precisos de perfil comportamental.\n"
        "Seu trabalho e ser fiel aos numeros. Nada do que voce escrever pode contradizer os dados abaixo.\n\n"

        "RANKING DOS EIXOS (do mais alto ao mais baixo):\n"
        + linhas_ranking + "\n\n"

        "MEDIAS POR EIXO (escala 1.0 a 5.0):\n"
        + linhas_medias + "\n\n"

        "EIXO MAIS ALTO: " + eixo_alto + "\n"
        "EIXO MAIS BAIXO: " + eixo_baixo + "\n\n"

        "CONTRASTES ENTRE EIXOS (ordenados por magnitude):\n"
        + linhas_diferencas + "\n\n"

        "EIXOS ABAIXO DE 3.0 - TRACOS LIMITANTES REAIS:\n"
        + linhas_eixos_baixos + "\n\n"

        "EIXOS MODERADOS (3.0-3.4) - NAO SAO PROBLEMAS CRITICOS:\n"
        + linhas_eixos_moderados + "\n\n"

        "FLAGS IDENTIFICADAS:\n" + linhas_flags + "\n\n"
        "HIPOTESE TECNICA:\n" + linhas_hipotese + "\n\n"

        "ESCALA DE INTENSIDADE:\n"
        "- 1.0 a 2.0: traco muito baixo - ausencia marcante\n"
        "- 2.1 a 2.9: traco abaixo da media - tendencia limitante\n"
        "- 3.0 a 3.4: traco moderado - contextual\n"
        "- 3.5 a 4.2: traco alto - padrao consistente\n"
        "- 4.3 a 5.0: traco muito alto - dominante\n\n"

        "DEFINICAO DOS EIXOS:\n"
        "- Abertura: curiosidade intelectual, apreciacao por novidade, imaginacao, flexibilidade mental\n"
        "- Conscienciosidade: organizacao, disciplina, planejamento, responsabilidade, foco\n"
        "- Extroversao: energia social, assertividade, sociabilidade, busca por estimulo externo\n"
        "- Amabilidade: empatia, cooperacao, evitar conflito, confianca nos outros, generosidade\n"
        "- Neuroticismo: ansiedade, instabilidade emocional, ruminacao, reatividade a estresse\n"
        "- Seguranca: orientacao para estabilidade, necessidade de previsibilidade, aversao a risco\n"
        "- Abundancia: mentalidade de escassez vs. fartura, relacao emocional com recursos e oportunidades\n\n"

        "COMBINACOES IMPORTANTES:\n"
        "- Seguranca alta + Abundancia baixa = protege o que tem, dificuldade de expandir\n"
        "- Amabilidade alta + Extroversao baixa = cuida dos outros mas evita exposicao social\n"
        "- Amabilidade alta + Neuroticismo alto = sensivel as relacoes, ansioso com conflitos\n"
        "- Conscienciosidade alta + Abertura baixa = executa bem, resiste a mudanca de rota\n"
        "- Neuroticismo alto + Seguranca alta = ansioso internamente, busca controle externo como alivio\n"
        "- Neuroticismo alto + Extroversao baixa = processa internamente, rumina sozinho, nao externaliza\n\n"

        "REGRAS FUNDAMENTAIS:\n"
        "- Fale sempre em 'voce'\n"
        "- Nao use linguagem tecnica nem nomeie os eixos diretamente\n"
        "- Nao use frases genericas que servem para qualquer pessoa\n"
        "- Nao romantize nem suavize pontos dificeis que os dados mostram\n"
        "- Cada traco deve mostrar onde funciona bem E onde cobra um preco\n"
        "- Mostre comportamentos concretos em situacoes reais do dia a dia\n\n"

        "REGRAS DE VALIDACAO CRUZADA - OBRIGATORIAS:\n"
        "REGRA 1 - ANTI-CONTRADICAO: Antes de escrever qualquer forca, verifique o eixo correspondente. "
        "Se o eixo estiver abaixo de 3.0, esse traco NAO pode aparecer como forca. "
        "Exemplo proibido: escrever 'voce planeja meticulosamente' se Conscienciosidade < 3.0. "
        "Exemplo proibido: escrever 'voce se adapta rapidamente a mudancas' se Seguranca >= 3.5.\n"
        "REGRA 2 - ANTI-AMPLIFICACAO: Eixos moderados (3.0 a 3.4) nao sao problemas criticos. "
        "Nao trate eixo moderado como se fosse baixo ou problematico. "
        "Exemplo proibido: tratar Abundancia 3.18 como 'mentalidade de escassez severa'.\n"
        "REGRA 3 - MAIOR CONTRASTE OBRIGATORIO: O maior contraste do perfil e '"
        + maior_contraste_key
        + " = %+.2f'. " % maior_contraste_val
        + "Este padrao DEVE aparecer explicitamente na secao 'O que acontece dentro de voce'. "
        "Nao e opcional.\n"
        "REGRA 4 - EIXOS BAIXOS SAO DESAFIOS REAIS: Cada eixo abaixo de 3.0 deve aparecer "
        "nas secoes de desafio com impacto concreto no comportamento. Nao pode ser ignorado.\n"
        "REGRA 5 - DIRECAO PRATICA DERIVADA DOS DADOS: Cada orientacao da secao 9 deve derivar "
        "diretamente dos eixos mais baixos ou do maior contraste deste perfil especifico. "
        "Orientacoes genericas como 'experimente uma nova rota para o trabalho' ou "
        "'saia da zona de conforto' sao proibidas.\n\n"

        "ESTRUTURA OBRIGATORIA:\n\n"
        "1. COMO VOCE FUNCIONA DE VERDADE\n"
        "Use os dois eixos mais altos do ranking. Mostre como a pessoa entra em ambientes, reage sob pressao, se posiciona.\n\n"
        "2. COMO VOCE TOMA DECISOES\n"
        "Use Conscienciosidade, Seguranca e Abertura com seus valores reais. Mostre onde decide bem, onde trava, onde cede.\n\n"
        "3. COMO VOCE SE RELACIONA\n"
        "Use Amabilidade, Extroversao e Neuroticismo. Mostre como cria conexao e onde vai alem do que deveria.\n\n"
        "4. O QUE ACONTECE DENTRO DE VOCE\n"
        "Use o maior contraste do perfil ("
        + maior_contraste_key
        + " = %+.2f) como eixo central. " % maior_contraste_val
        + "Descreva o padrao de pensamento interno que esse contraste cria.\n\n"
        "5. SEU PADRAO MAIS FORTE\n"
        "Pegue o eixo mais alto ("
        + eixo_alto
        + ": %.2f). " % medias[eixo_alto]
        + "Mostre em 3 situacoes do cotidiano. Trunfo e problema concretos.\n\n"
        "6. SUAS FORCAS REAIS\n"
        "Maximo 5. Formato: 'Voce [verbo concreto] quando [situacao especifica]'. "
        "VALIDACAO OBRIGATORIA: cada forca deve ser sustentada por um eixo >= 3.0.\n\n"
        "7. SUAS AREAS DE DESAFIO\n"
        "Maximo 5. Formato: 'Porque voce tende a [padrao], o que acontece na pratica e [consequencia concreta]'. "
        "OBRIGATORIO: incluir os eixos abaixo de 3.0 (" + eixos_baixos_str + ").\n\n"
        "8. O PONTO QUE MAIS MERECE ATENCAO\n"
        "Um ponto. Aprofunde: como aparece, o que protege, o que custa, o sinal de que esta acontecendo.\n\n"
        "9. DIRECAO PRATICA\n"
        "4 a 5 orientacoes concretas executaveis na proxima semana. "
        "Cada orientacao deve derivar de um eixo especifico deste perfil. "
        "Cite o comportamento real que a orientacao visa mudar.\n\n"
        "CRITERIO FINAL: a pessoa deve ler e pensar 'como voce sabia disso?' - nao 'faz sentido para muita gente'."
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

    st.subheader("7. Contrastes Entre Eixos")
    st.caption("Diferenca entre pares de eixos. Contrastes altos revelam tensoes comportamentais.")
    for par, valor in sorted(perfil["diferencas"].items(), key=lambda x: -abs(x[1])):
        direcao = "alto" if valor > 0 else ("baixo" if valor < 0 else "igual")
        marker = " <- MAIOR CONTRASTE" if par == perfil["maior_contraste_key"] else ""
        st.write("**" + par + "**: " + str(valor) + " (" + direcao + ")" + marker)

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
        "versao_prompt": "V5.2 - calibrado por Manus AI",
    })

# =============================================================
# INTERFACE PRINCIPAL
# =============================================================

st.title("Mind Insight AI")
st.markdown(
    '<div class="manus-badge">V5.2 | Criado com Claude (Anthropic) | '
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
