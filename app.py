# -*- coding: utf-8 -*-

# =============================================================
# MIND INSIGHT ADVANCED AI
# Version: V5.17
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
#        - Prompt: relatorio deve fazer a pessoa se identificar e querer agir
# V5.14 - Fix NameError: q26 nao declarada em gerar_relatorio
#       - Afirmação 2 (Extroversão) reescrita para eliminar ambiguidade
# V5.15 - Acentuação gráfica completa em português nos textos fixos
#       - Subtítulo atualizado: 'Análise comportamental potencializada por
#         psicologia científica e inteligência artificial avançada'
# V5.16 - Logo Mind Insight adicionado ao cabeçalho
# V5.17 - Google Sheets: grava em modo teste e producao; mostra erro no debug; coluna modo_teste adicionada
#       - Pergunta de calibração de Segurança separada em duas afirmações
#         independentes (Q55: reatividade emocional / Q59: preferência por rotina)
# =============================================================
import streamlit as st
import json
import os
import pandas as pd
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_OK = True
except ImportError:
    GSPREAD_OK = False

# =============================================================
# MODO DE OPERACAO
# Producao (padrao): sem debug, sem reutilizacao de respostas
# Teste: acesse a URL com ?modo=teste para ativar o modo de desenvolvimento
# =============================================================

def detectar_modo():
    try:
        params = st.query_params
        return params.get("modo", "producao") == "teste"
    except Exception:
        return False

DEBUG_MODE = detectar_modo()
MODO_TESTE = DEBUG_MODE

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
    page_title="Mind Insight",
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
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
if "user_info_completo" not in st.session_state:
    st.session_state.user_info_completo = False
if "relatorio_gerado" not in st.session_state:
    st.session_state.relatorio_gerado = ""
if "dados_registrados" not in st.session_state:
    st.session_state.dados_registrados = False
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "modo_selecionado" not in st.session_state:
    st.session_state.modo_selecionado = False
if "calibracao_completa" not in st.session_state:
    st.session_state.calibracao_completa = False
if "calibracao_statements" not in st.session_state:
    st.session_state.calibracao_statements = []
if "calibracao_respostas" not in st.session_state:
    st.session_state.calibracao_respostas = {}
if "calibracao_followup" not in st.session_state:
    st.session_state.calibracao_followup = {}
if "calibracao_ajustes" not in st.session_state:
    st.session_state.calibracao_ajustes = {}
if "perfil_cache" not in st.session_state:
    st.session_state.perfil_cache = None
if "calibracao_completa" not in st.session_state:
    st.session_state.calibracao_completa = False
if "calibracao_statements" not in st.session_state:
    st.session_state.calibracao_statements = []
if "calibracao_respostas" not in st.session_state:
    st.session_state.calibracao_respostas = {}
if "calibracao_followup" not in st.session_state:
    st.session_state.calibracao_followup = {}
if "calibracao_ajustes" not in st.session_state:
    st.session_state.calibracao_ajustes = {}
if "perfil_cache" not in st.session_state:
    st.session_state.perfil_cache = None

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
# PERSISTENCIA DE RESPOSTAS CALIBRADAS
# =============================================================

ULTIMO_TESTE_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ultimo_teste.json")

def salvar_ultimo_teste(respostas):
    """Salva as respostas calibradas em JSON para reutilizacao futura."""
    try:
        # Converte chaves para string para compatibilidade JSON
        data = {str(k): v for k, v in respostas.items()}
        with open(ULTIMO_TESTE_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return False

def carregar_ultimo_teste():
    """
    Carrega as respostas do ultimo teste.
    Prioridade: arquivo JSON (respostas calibradas) > ULTIMO_TESTE hardcoded.
    """
    if os.path.exists(ULTIMO_TESTE_JSON):
        try:
            with open(ULTIMO_TESTE_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Converte chaves de volta para int
            return {int(k): v for k, v in data.items()}
        except Exception:
            pass
    # Fallback para hardcoded
    return dict(ULTIMO_TESTE)

# =============================================================
# GOOGLE SHEETS LOGGING
# =============================================================

def registrar_no_sheets(dados):
    """Envia uma linha de dados para o Google Sheets configurado em st.secrets."""
    if not GSPREAD_OK:
        return False, "gspread nao instalado"
    try:
        creds_dict = dict(st.secrets.get("gcp_service_account", {}))
        if not creds_dict:
            return False, "gcp_service_account nao configurado em secrets"
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(creds)
        sheet_url = st.secrets.get("GOOGLE_SHEET_URL", "")
        if not sheet_url:
            return False, "GOOGLE_SHEET_URL nao configurado em secrets"
        sh = gc.open_by_url(sheet_url)
        ws = sh.sheet1
        # Cabecalho se planilha vazia
        if ws.row_count == 0 or ws.cell(1, 1).value != "data_hora":
            cabecalho = [
                "data_hora", "modo_teste", "nome", "idade", "genero", "email",
                "Abertura", "Conscienciosidade", "Extroversao",
                "Amabilidade", "Neuroticismo", "Seguranca", "Abundancia",
                "maior_contraste", "amplitude_pct", "padroes_ativos",
                "ajustes_calibracao", "relatorio"
            ] + ["Q" + str(i) for i in range(1, 75)]
            ws.append_row(cabecalho)
        linha = [
            dados.get("data_hora", ""),
            dados.get("modo_teste", "NAO"),
            dados.get("nome", ""),
            dados.get("idade", ""),
            dados.get("genero", ""),
            dados.get("email", ""),
            dados.get("Abertura", ""),
            dados.get("Conscienciosidade", ""),
            dados.get("Extroversao", ""),
            dados.get("Amabilidade", ""),
            dados.get("Neuroticismo", ""),
            dados.get("Seguranca", ""),
            dados.get("Abundancia", ""),
            dados.get("maior_contraste", ""),
            dados.get("amplitude_pct", ""),
            dados.get("padroes_ativos", ""),
            dados.get("ajustes_calibracao", ""),
            dados.get("relatorio", "")[:5000],  # limitar tamanho
        ] + [dados.get("respostas", {}).get(i, "") for i in range(1, 75)]
        ws.append_row(linha)
        return True, "ok"
    except Exception as e:
        return False, str(e)


def enviar_email(destinatario, nome, relatorio_texto):
    """Envia o relatorio por email via Gmail configurado em st.secrets."""
    try:
        gmail_user = st.secrets.get("GMAIL_USER", "")
        gmail_pass = st.secrets.get("GMAIL_APP_PASSWORD", "")
        if not gmail_user or not gmail_pass:
            return False, "GMAIL_USER ou GMAIL_APP_PASSWORD nao configurados em secrets"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Seu Relatório Mind Insight"
        msg["From"] = "Mind Insight <" + gmail_user + ">"
        msg["To"] = destinatario

        texto_plain = (
            "Olá " + nome + ",\n\n"
            "Aqui está o seu relatório completo de perfil comportamental gerado pelo Mind Insight.\n\n"
            + relatorio_texto
            + "\n\n---\nMind Insight | Análise comportamental potencializada por psicologia científica e inteligência artificial avançada"
        )

        html_body = (
            "<html><body style='font-family:Arial,sans-serif;max-width:700px;margin:auto;padding:20px'>"
            "<h2 style='color:#1a1a1a'>Seu Relatório Mind Insight</h2>"
            "<p>Olá <strong>" + nome + "</strong>,</p>"
            "<p>Aqui está o seu relatório completo de perfil comportamental.</p>"
            "<hr>"
            + relatorio_texto.replace("\n", "<br>")
            + "<hr><p style='color:#888;font-size:0.85em'>Mind Insight | Análise comportamental potencializada por psicologia científica e inteligência artificial avançada</p>"
            "</body></html>"
        )

        msg.attach(MIMEText(texto_plain, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, destinatario, msg.as_string())
        return True, "ok"
    except Exception as e:
        return False, str(e)


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
    # Detectar extroversao bimodal: reservado socialmente mas assertivo em contextos formais/tecnicos
    _q22 = respostas_ajustadas.get(22, 3)
    _q24 = respostas_ajustadas.get(24, 3)
    _q30 = respostas_ajustadas.get(30, 3)
    _q21 = respostas_ajustadas.get(21, 3)
    _q26 = respostas_ajustadas.get(26, 3)
    _q28 = respostas_ajustadas.get(28, 3)
    _media_formal   = (_q22 + _q24 + _q30) / 3
    _media_informal = (_q21 + _q26 + _q28) / 3
    if _media_formal >= 3.5 and _media_informal < 3.0:
        flags.append("extroversao bimodal: assertivo em contextos formais/tecnicos, reservado socialmente")
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
# GERACAO DO RELATORIO (PROMPT CALIBRADO V5.6)
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

    # --- Scores ajustados por questao para combinacoes ---
    q_adj = perfil.get("respostas_ajustadas", {})

    # Evitacao de conflito (Amabilidade)
    q33 = q_adj.get(33, 3)   # prefere ceder em desacordos (invertida: 5->1)
    q35 = q_adj.get(35, 3)   # desconfortavel ao decepcionar
    q37 = q_adj.get(37, 3)   # evita feedback negativo (invertida: 5->1)
    q39 = q_adj.get(39, 3)   # adia dizer coisas dificeis (invertida: 5->1)

    # Conscienciosidade
    q11 = q_adj.get(11, 3)   # cumpre compromissos
    q12 = q_adj.get(12, 3)   # so comeca com disposicao (invertida)
    q13 = q_adj.get(13, 3)   # sistema de prioridades
    q14 = q_adj.get(14, 3)   # deixa para decidir na hora (invertida)
    q16 = q_adj.get(16, 3)   # deixa para ultima hora (invertida)
    q17 = q_adj.get(17, 3)   # revisa antes de entregar
    q18 = q_adj.get(18, 3)   # clareza metas longo prazo
    q20 = q_adj.get(20, 3)   # mantem compromissos

    # Extroversao
    q21 = q_adj.get(21, 3)   # energia com pessoas
    q22 = q_adj.get(22, 3)   # toma iniciativa em grupo
    q24 = q_adj.get(24, 3)   # porta-voz de grupo
    q26 = q_adj.get(26, 3)   # busca novas pessoas
    q27 = q_adj.get(27, 3)   # prefere escrever a falar (invertida)
    q29 = q_adj.get(29, 3)   # fica ouvindo em grupo (invertida)
    q30 = q_adj.get(30, 3)   # exprime opiniao quando discordam

    # Abertura
    q3  = q_adj.get(3, 3)    # busca conhecimento por prazer
    q4  = q_adj.get(4, 3)    # incomoda conversas abstratas (invertida)
    q6  = q_adj.get(6, 3)    # prefere direto e pratico (invertida)
    q7  = q_adj.get(7, 3)    # muda opiniao por argumento

    # Abundancia
    q65 = q_adj.get(65, 3)   # oportunidades limitadas (invertida: 1->5)
    q67 = q_adj.get(67, 3)   # espaco para todos (invertida: 5->1)
    q70 = q_adj.get(70, 3)   # instinto de ganhar
    q71 = q_adj.get(71, 3)   # dificuldade de investir sem garantia (invertida: 5->1)

    # Seguranca
    q53 = q_adj.get(53, 3)   # prefere saber o que esperar
    q55 = q_adj.get(55, 3)   # mudancas incomodam
    q56 = q_adj.get(56, 3)   # prefere menor garantido

    # Neuroticismo
    q44 = q_adj.get(44, 3)   # preocupa com futuro
    q49 = q_adj.get(49, 3)   # ansioso sem previsibilidade
    q52 = q_adj.get(52, 3)   # rumina erros

    ab  = medias["Abertura"]
    co  = medias["Conscienciosidade"]
    ex  = medias["Extroversao"]
    am  = medias["Amabilidade"]
    ne  = medias["Neuroticismo"]
    se  = medias["Seguranca"]
    abu = medias["Abundancia"]

    # --- Construir combinacoes ativas ---
    combinacoes_ativas = []

    # 1. Abertura
    if ab >= 3.5 and ex < 3.5:
        combinacoes_ativas.append(
            "CURIOSIDADE INTERNA (Abertura %.2f + Extroversao %.2f): "
            "Esta pessoa tem vida intelectual rica e intensa, mas processa isso internamente. "
            "Ela explora ideias sozinha, nao em grupo. Ela nao e 'a primeira a falar' - "
            "e a que ja pensou mais fundo antes de qualquer um abrir a boca. "
            "Em reunioes, parece quieta mas ja chegou com a analise pronta. "
            "Tem opinioes fortes que raramente externaliza sem ser provocada. "
            "Pode ser subestimada por quem confunde silencio com falta de ideias." % (ab, ex)
        )
    elif 3.0 <= ab < 3.5 and q4 <= 2 and q6 <= 2 and (q3 >= 4 or q7 >= 4):
        combinacoes_ativas.append(
            "CURIOSIDADE PRATICA (Abertura %.2f, busca_conhecimento=%d, muda_opiniao_por_argumento=%d, "
            "incomoda_abstracionismo=%d, prefere_pratico=%d): "
            "Esta pessoa e curiosa, mas com foco pratico. Ela busca conhecimento que pode usar, "
            "muda de opiniao quando o argumento e solido, mas se incomoda com abstracionismo excessivo. "
            "Ela nao e teorica - e uma pessoa que aprende para aplicar." % (ab, q3, q7, q4, q6)
        )

    # 2. Conscienciosidade
    if co >= 3.5:
        if q11 >= 4 and q17 >= 4 and q13 <= 3:
            combinacoes_ativas.append(
                "CONFIABILIDADE SEM RIGIDEZ (Conscienciosidade %.2f, cumpre_compromissos=%d, "
                "revisa=%d, sistema_prioridades=%d): "
                "Esta pessoa e altamente confiavel - quando assume algo, entrega. Mas nao e um planejador rigido. "
                "Ela nao precisa de um sistema perfeito para comecar, mas nao descansa enquanto nao termina com qualidade. "
                "O padrao dela e: assume, executa, entrega bem. O risco e assumir mais do que consegue absorver "
                "porque dificilmente diz nao quando se compromete." % (co, q11, q17, q13)
            )
        elif q11 >= 4 and q18 >= 4:
            combinacoes_ativas.append(
                "EXECUCAO ORIENTADA A RESULTADO (Conscienciosidade %.2f): "
                "Esta pessoa combina responsabilidade alta com clareza de onde quer chegar. "
                "Ela nao apenas entrega - ela entrega no caminho certo. "
                "O risco e perfeccionismo: pode demorar mais do que o necessario "
                "por nao aceitar resultado 'bom o suficiente'." % co
            )
    elif co < 3.0 and q11 >= 4 and q17 >= 4 and (q13 <= 2 or q16 <= 2):
        combinacoes_ativas.append(
            "ENTREGA SOB PRESSAO SEM SISTEMA (Conscienciosidade %.2f, "
            "cumpre_compromissos=%d, revisa=%d, sistema_prioridades=%d, deixa_ultima_hora=%d): "
            "Esta e uma das contradicoes mais importantes do perfil. "
            "Esta pessoa entrega (cumpre_compromissos=%d, revisa=%d) mas sem sistema de organizacao (sistema=%d). "
            "O padrao tipico: procrastina, acumula, entra em modo de urgencia e entrega sob alta pressao. "
            "Ela cumpre o que promete, mas o custo pessoal e alto - estresse, noites longas, "
            "sensacao de estar sempre atrasada. "
            "Nao e 'organizada e confiavel' - e 'confiavel apesar da desorganizacao'. "
            "Esta distincao e crucial para entender o desgaste que ela sente." % (
                co, q11, q17, q13, q16, q11, q17, q13)
        )

    # 3. Seguranca
    if se >= 3.5:
        combinacoes_ativas.append(
            "ORIENTACAO A CERTEZA (Seguranca %.2f, prefere_previsibilidade=%d, "
            "mudancas_incomodam=%d, prefere_menor_garantido=%d): "
            "Esta pessoa funciona melhor quando sabe o que esperar. Nao e medo - "
            "e preferencia por operar com informacao suficiente. "
            "Ela tende a escolher a opcao menor mas certa em vez da maior mas incerta. "
            "Em ambientes de alta mudanca ou ambiguidade, ela gasta energia extra "
            "so para se estabilizar antes de agir. "
            "Isso pode fazer ela perder janelas de oportunidade que exigem acao rapida sem garantia." % (
                se, q53, q55, q56)
        )
    elif 3.0 <= se < 3.5:
        combinacoes_ativas.append(
            "CAUTELA SELETIVA (Seguranca %.2f): "
            "Esta pessoa tem preferencia moderada por previsibilidade. Consegue agir em incerteza quando necessario, "
            "mas prefere ter informacao suficiente antes de se comprometer. "
            "Nao e avessa a risco - e criteriosamente cautelosa." % se
        )

    # 4. Evitacao de conflito (padrao independente de Amabilidade)
    evita_conflito = (q33 <= 3 or q37 <= 3 or q39 <= 3) and q35 >= 3
    if evita_conflito:
        combinacoes_ativas.append(
            "EVITACAO DE CONFLITO SISTEMATICA "
            "(cede_desacordos=%d, desconfortavel_decepcionar=%d, "
            "evita_feedback_negativo=%d, adia_conversas_dificeis=%d): "
            "ESTE E PROVAVELMENTE O PADRAO COM MAIOR IMPACTO NA CARREIRA E NAS RELACOES DESTA PESSOA. "
            "Ela cede em desacordos (score=%d), fica muito desconfortavel ao decepcionar alguem (score=%d), "
            "evita dar feedback negativo (score=%d) e adia conversas dificeis (score=%d). "
            "Na pratica: ela concorda quando nao concorda, nao diz o que pensa quando sabe que vai gerar tensao, "
            "e carrega o peso de situacoes nao resolvidas por muito tempo. "
            "Profissionalmente: pode ser vista como 'facil de trabalhar' mas nao e promovida porque nao se impos. "
            "Relacionalmente: acumula ressentimento silencioso e pode se afastar abruptamente "
            "depois de muito tempo cedendo. "
            "Este padrao DEVE ser descrito com clareza e honestidade no relatorio." % (
                q33, q35, q37, q39, q33, q35, q37, q39)
        )

    # 5. Amabilidade
    if am >= 3.5 and ex < 3.5:
        combinacoes_ativas.append(
            "CUIDADO SELETIVO (Amabilidade %.2f + Extroversao %.2f): "
            "Esta pessoa e muito presente e generosa nas relacoes proximas, mas nao busca exposicao social ampla. "
            "Ela nao cuida de todo mundo - cuida profundamente de quem esta perto. "
            "Em grupos grandes, pode parecer distante ou reservada, "
            "mas em relacoes um a um e extremamente atenta e confiavel. "
            "O risco: coloca as necessidades dos outros na frente das proprias com tanta frequencia que "
            "pode acumular ressentimento silencioso quando nao e correspondida." % (am, ex)
        )
    elif am >= 3.0 and evita_conflito:
        combinacoes_ativas.append(
            "GENEROSIDADE COM CUSTO OCULTO (Amabilidade %.2f): "
            "Esta pessoa e genuinamente empatica e cuida das pessoas ao redor. "
            "Mas combinada com a evitacao de conflito, isso cria um padrao onde ela da mais do que deveria "
            "e raramente recupera o que investiu. "
            "Ela nao pede ajuda facilmente, nao estabelece limites com clareza, "
            "e pode se sentir esgotada sem conseguir identificar por que." % am
        )

    # 6. Neuroticismo
    if ne >= 3.0 and (q44 >= 4 or q49 >= 4):
        combinacoes_ativas.append(
            "ANTECIPACAO ANSIOSA (Neuroticismo %.2f, preocupa_futuro=%d, "
            "ansioso_sem_previsibilidade=%d, rumina_erros=%d): "
            "Esta pessoa processa riscos e cenarios negativos antes que acontecam. "
            "Isso a torna excelente em identificar problemas que outros nao veem - mas cobra um preco: "
            "ela gasta energia antecipando o que pode dar errado mesmo quando a situacao e segura. "
            "Em momentos de transicao ou incerteza, a cabeca dela trabalha mais do que o necessario." % (
                ne, q44, q49, q52)
        )

    # 7. Abundancia
    if abu < 3.0:
        combinacoes_ativas.append(
            "RELACAO RESTRITIVA COM OPORTUNIDADE (Abundancia %.2f): "
            "Esta pessoa tende a ver os recursos e oportunidades disponiveis para ela como limitados. "
            "Isso pode fazer ela subvalorizar o proprio trabalho, hesitar em pedir o que merece, "
            "ou evitar investir em si mesma quando o retorno nao e garantido. "
            "O impacto financeiro e real: ela pode estar deixando dinheiro na mesa "
            "por nao se posicionar com confianca." % abu
        )
    elif 3.0 <= abu < 3.5:
        if q70 >= 4 and q71 <= 2:
            combinacoes_ativas.append(
                "ABUNDANCIA MISTA (Abundancia %.2f, instinto_de_ganhar=%d, "
                "dificuldade_investir_sem_garantia=%d): "
                "Este e um padrao sofisticado: esta pessoa tem mentalidade de abundancia nas relacoes "
                "(nao compara, nao inveja, acredita que ha espaco para todos), "
                "mas e restritiva quando se trata de investir em si mesma. "
                "Ela ve oportunidade nos outros mas hesita em apostar em si propria sem garantia de retorno. "
                "Na pratica: pode recomendar oportunidades para outros mas nao se candidatar, "
                "pode negociar bem para clientes mas nao para si mesma, "
                "pode investir em outros mas hesitar em pagar por desenvolvimento proprio. "
                "Este padrao tem impacto direto no crescimento financeiro e profissional." % (abu, q70, q71)
            )
        else:
            combinacoes_ativas.append(
                "ABUNDANCIA MODERADA (Abundancia %.2f): "
                "Esta pessoa tem uma relacao neutra com oportunidade e recursos. "
                "Em momentos de decisao financeira ou de carreira, "
                "pode oscilar entre confiar no proprio valor e duvidar dele." % abu
            )

    # 8. Perfil de especialista profundo
    if ab >= 3.5 and co >= 3.5 and ex < 3.5:
        combinacoes_ativas.append(
            "PERFIL DE ESPECIALISTA PROFUNDO (Abertura %.2f + Conscienciosidade %.2f + Extroversao %.2f): "
            "Esta combinacao e classica em pessoas que se tornam referencia silenciosa em suas areas. "
            "Exploram com profundidade, entregam com qualidade, mas nao buscam holofote. "
            "Sao as pessoas que os outros consultam quando o assunto e serio. "
            "O risco: podem ser preteridas em promocoes ou oportunidades de lideranca "
            "porque nao se vendem bem, mesmo sendo as mais capazes na sala." % (ab, co, ex)
        )

    # 8b. Extroversao bimodal
    _media_formal_ex   = (q22 + q24 + q30) / 3
    _media_informal_ex = (q21 + q26 + q_adj.get(28, 3)) / 3
    if _media_formal_ex >= 3.5 and _media_informal_ex < 3.0:
        combinacoes_ativas.append(
            "EXTROVERSAO BIMODAL (formal=%.2f, informal=%.2f): "
            "Esta pessoa tem dois modos de extroversao completamente diferentes. "
            "Em contextos formais, tecnicos ou onde tem autoridade no assunto "
            "(toma_iniciativa_grupo=%d, porta_voz=%d, exprime_opiniao=%d), ela e assertiva e presente. "
            "Em contextos sociais informais (energia_com_pessoas=%d, busca_novas_pessoas=%d), "
            "ela e reservada e nao busca estimulo. "
            "Isso significa que ela NAO e introvertida no sentido classico - "
            "ela e seletiva: se expoe quando tem algo concreto a contribuir, "
            "nao por prazer social. "
            "Pode ser vista como 'diferente' dependendo do contexto - "
            "quieta na festa, mas a que lidera a reuniao tecnica." % (
                _media_formal_ex, _media_informal_ex,
                q22, q24, q30, q21, q26)
        )

    # 9. Extroversao baixa a muito baixa
    if ex < 3.0:
        combinacoes_ativas.append(
            "PADRAO DE BAIXO IMPULSO SOCIAL (Extroversao %.2f): "
            "Este e um dos eixos mais extremos do perfil e precisa ser descrito com seriedade. "
            "Scores: toma_iniciativa_grupo=%d, porta_voz=%d, prefere_escrever_a_falar=%d, "
            "fica_ouvindo_grupo=%d, exprime_opiniao_quando_discordam=%d. "
            "Esta pessoa NAO busca estimulo em grupos, NAO toma iniciativa em situacoes sociais, "
            "NAO se sente confortavel como porta-voz, e PREFERE comunicacao escrita a oral. "
            "Isso nao e timidez - e uma preferencia genuina e consistente por baixa exposicao social. "
            "O impacto profissional e imenso: ela pode ter ideias excelentes que nao chegam a ser ouvidas, "
            "pode ser preterida em oportunidades que exigem visibilidade, "
            "e pode ser subestimada por gestores que confundem silencio com falta de contribuicao. "
            "Funcoes que exigem apresentacoes frequentes, vendas ou exposicao constante sao de alto custo. "
            "Funcoes que permitem contribuicao por escrito, analise profunda e trabalho autonomo "
            "sao onde ela brilha." % (ex, q22, q24, q27, q29, q30)
        )

    linhas_combinacoes = "\n\n".join(combinacoes_ativas) if combinacoes_ativas else "Nenhuma combinacao critica identificada."

    # --- CALIBRACAO 2: Ancoras concretas para secao interna ---
    # Pre-calcula frases especificas baseadas nos dados reais para guiar o AI
    ancoras_internas = []
    if maior_contraste_val >= 0.8:
        partes = maior_contraste_key.split("_vs_")
        if len(partes) == 2:
            eixo_a, eixo_b = partes[0], partes[1]
            ancoras_internas.append(
                "ANCORA OBRIGATORIA para secao 4: O contraste %s (%.2f) vs %s (%.2f) = %+.2f "
                "significa que esta pessoa tem um nivel de %s que nao combina com o nivel de %s. "
                "Na pratica concreta: ela pode estar pensando em algo com profundidade de nivel %.1f "
                "mas expressando com intensidade de nivel %.1f. "
                "Isso cria uma lacuna entre o que ela processa internamente e o que os outros percebem dela. "
                "Descreva ESTA lacuna especifica - nao uma descricao abstrata dos dois tracos." % (
                    eixo_a, medias.get(eixo_a, 3.0),
                    eixo_b, medias.get(eixo_b, 3.0),
                    maior_contraste_val,
                    eixo_a, eixo_b,
                    medias.get(eixo_a, 3.0),
                    medias.get(eixo_b, 3.0)
                )
            )
    if q44 >= 4 or q49 >= 4:
        ancoras_internas.append(
            "ANCORA para secao 4: Esta pessoa antecipa problemas antes que acontecam "
            "(preocupa_futuro=%d, ansioso_sem_previsibilidade=%d). "
            "Descreva o que acontece na cabeca dela ANTES de uma reuniao importante, "
            "ANTES de uma decisao grande, ou ANTES de uma mudanca. "
            "Ela nao esta com medo - ela esta processando cenarios. "
            "O custo e que ela gasta energia em problemas que nunca acontecem." % (q44, q49)
        )
    if evita_conflito:
        ancoras_internas.append(
            "ANCORA para secao 4: Esta pessoa sabe o que pensa mas frequentemente nao diz "
            "(evita_conflito ativo: q33=%d, q35=%d, q37=%d, q39=%d). "
            "Ha um dialogo interno onde ela formula a resposta honesta, decide nao dar, "
            "e depois carrega o peso do que nao disse. "
            "Descreva esse momento especifico - nao a evitacao em geral." % (q33, q35, q37, q39)
        )
    linhas_ancoras = "\n".join(ancoras_internas) if ancoras_internas else ""

    # --- CALIBRACAO 3: Pre-gerar candidatos de proximos passos ---
    passos_candidatos = []
    if evita_conflito:
        passos_candidatos.append(
            "PASSO DERIVADO DE EVITACAO DE CONFLITO: "
            "Identifique UMA situacao especifica esta semana onde voce sabe o que pensa mas nao disse. "
            "Diga. Nao precisa ser dramatico - pode ser um e-mail, uma mensagem, uma conversa de 5 minutos. "
            "Resultado esperado: voce vai perceber que a tensao que antecipou era menor do que o peso de nao ter dito."
        )
    if ab >= 3.5 and ex < 3.5:
        passos_candidatos.append(
            "PASSO DERIVADO DE CURIOSIDADE INTERNA: "
            "Voce ja pensou sobre algo com profundidade que nao compartilhou. "
            "Esta semana, escreva essa analise - pode ser um e-mail, uma mensagem no grupo, um documento. "
            "Nao espere ser perguntado. Compartilhe antes. "
            "Resultado esperado: as pessoas vao reagir com surpresa positiva ao ver o que voce ja sabia."
        )
    if se >= 3.0 and (q55 >= 4 or q56 >= 4):
        passos_candidatos.append(
            "PASSO DERIVADO DE CAUTELA: "
            "Identifique uma decisao ou oportunidade que voce adiou porque nao tinha informacao suficiente. "
            "Defina qual seria o minimo de informacao aceitavel para decidir - e decida com o que ja tem. "
            "Resultado esperado: voce vai descobrir que a decisao era mais simples do que parecia."
        )
    if ab >= 3.5 and co >= 3.5:
        passos_candidatos.append(
            "PASSO DERIVADO DE ESPECIALISTA PROFUNDO: "
            "Voce tem conhecimento profundo em algo que as pessoas ao seu redor precisam. "
            "Esta semana, ofeca essa analise ou conhecimento proativamente - sem esperar ser chamado. "
            "Pode ser uma recomendacao, uma analise, uma perspectiva que voce guardou para si. "
            "Resultado esperado: maior visibilidade do seu valor sem precisar se autopromover."
        )
    if ne >= 3.0 and (q44 >= 4 or q49 >= 4):
        passos_candidatos.append(
            "PASSO DERIVADO DE ANTECIPACAO ANSIOSA: "
            "Na proxima vez que perceber que esta antecipando um problema que ainda nao aconteceu, "
            "escreva os 3 cenarios possiveis e a probabilidade real de cada um. "
            "Resultado esperado: voce vai perceber que o cenario que mais preocupa raramente e o mais provavel."
        )
    if not passos_candidatos:
        passos_candidatos.append(
            "PASSO GERAL: Use as forcas identificadas no perfil para criar visibilidade do seu trabalho esta semana."
        )
    linhas_passos_candidatos = "\n\n".join(passos_candidatos[:4])

    # --- Estilo de lideranca ---
    if ab >= 3.5 and co >= 3.5 and ex < 3.5:
        estilo_lideranca = (
            "ESTILO DE LIDERANCA PROVAVEL: Lideranca por competencia e confiabilidade, nao por carisma. "
            "Esta pessoa lidera sendo a referencia tecnica ou estrategica do grupo. "
            "As pessoas a seguem porque confiam no julgamento dela, nao porque ela se impos. "
            "E mais eficaz em lideranca de pequenos times ou projetos do que em lideranca de palco. "
            "Pode ter dificuldade de se promover e de dar visibilidade ao proprio trabalho."
        )
    elif ex >= 3.5 and am >= 3.5:
        estilo_lideranca = (
            "ESTILO DE LIDERANCA PROVAVEL: Lideranca relacional e inspiradora. "
            "Esta pessoa energiza grupos, cria conexao e faz as pessoas se sentirem vistas. "
            "E mais forte em lideranca de pessoas do que em lideranca de processos."
        )
    elif co >= 3.5 and se >= 3.5:
        estilo_lideranca = (
            "ESTILO DE LIDERANCA PROVAVEL: Lideranca por estrutura e previsibilidade. "
            "Esta pessoa cria ambientes organizados e confiaveis. "
            "Times sob sua lideranca sabem o que esperar. "
            "Pode ter dificuldade em liderar em contextos de alta ambiguidade."
        )
    elif ex < 3.0:
        estilo_lideranca = (
            "ESTILO DE LIDERANCA PROVAVEL: Lideranca por influencia silenciosa e profundidade. "
            "Esta pessoa nao lidera pelo palco - lidera pela qualidade do que produz e pela confianca que inspira. "
            "E consultada, nao imposta. Influencia por escrito, por analise, por consistencia. "
            "Nao e o tipo que se candidata a liderar - e o tipo que as pessoas escolhem quando precisam "
            "de alguem em quem confiar de verdade."
        )
    else:
        estilo_lideranca = (
            "ESTILO DE LIDERANCA: situacional - adapta o estilo ao contexto. "
            "Mais eficaz em ambientes onde pode usar as forcas especificas identificadas no perfil."
        )

    # --- Scores extremos para regras do prompt ---
    scores_extremos_linhas = ""
    if q22 <= 1:
        scores_extremos_linhas += "   - toma_iniciativa_grupo=%d (MUITO BAIXO - nao toma iniciativa em grupos)\n" % q22
    if q24 <= 1:
        scores_extremos_linhas += "   - porta_voz=%d (MUITO BAIXO - nao e porta-voz)\n" % q24
    if q33 <= 2:
        scores_extremos_linhas += "   - cede_desacordos=%d (MUITO BAIXO - cede sistematicamente)\n" % q33
    if q37 <= 2:
        scores_extremos_linhas += "   - evita_feedback_negativo=%d (MUITO BAIXO - nunca da feedback negativo)\n" % q37
    if q39 <= 2:
        scores_extremos_linhas += "   - adia_conversas_dificeis=%d (MUITO BAIXO - sempre adia)\n" % q39
    if q13 <= 1:
        scores_extremos_linhas += "   - sistema_prioridades=%d (MUITO BAIXO - sem sistema de organizacao)\n" % q13
    if q16 <= 1:
        scores_extremos_linhas += "   - deixa_ultima_hora=%d (MUITO BAIXO - frequentemente deixa para ultima hora)\n" % q16
    if q27 <= 1:
        scores_extremos_linhas += "   - prefere_escrever_a_falar=%d (MUITO BAIXO - prefere escrita a fala)\n" % q27
    if q29 <= 1:
        scores_extremos_linhas += "   - fica_ouvindo_grupo=%d (MUITO BAIXO - fica ouvindo em grupos)\n" % q29
    # Adicionar scores moderados relevantes quando amplitude e comprimida
    if q33 == 3 and q35 >= 3 and q37 == 3 and q39 == 3:
        scores_extremos_linhas += "   - padrao_evitacao_conflito_moderado: q33=%d, q35=%d, q37=%d, q39=%d (moderado mas consistente)\n" % (q33, q35, q37, q39)
    if q27 == 3 and q29 == 3 and ex < 3.5:
        scores_extremos_linhas += "   - preferencia_por_escuta_e_escrita: q27=%d, q29=%d (moderado mas consistente com Extroversao %.2f)\n" % (q27, q29, ex)
    if not scores_extremos_linhas:
        scores_extremos_linhas = "   Nenhum score extremo identificado.\n"

    prompt = (
        "Voce e um especialista em psicologia comportamental com profundo conhecimento em Big Five, "
        "padroes de comportamento humano e desenvolvimento de carreira. "
        "Voce vai escrever um relatorio de perfil comportamental para uma pessoa real.\n\n"

        "SUA MISSAO:\n"
        "Usar os dados do perfil abaixo para identificar e descrever os PADROES DE COMPORTAMENTO "
        "que pessoas com este perfil especifico exibem - no trabalho, nas relacoes, sob pressao, ao tomar decisoes. "
        "Voce NAO esta apenas reformulando as respostas do questionario. "
        "Voce esta usando seu conhecimento sobre como esses tracos se manifestam na vida real "
        "para revelar coisas que a pessoa reconhece como verdadeiras mas talvez nunca tenha articulado.\n\n"

        "DADOS DO PERFIL (escala 1.0 a 5.0, media 3.0 = neutro):\n\n"
        "RANKING DOS EIXOS:\n"
        + linhas_ranking + "\n\n"

        "MEDIAS POR EIXO:\n"
        + linhas_medias + "\n\n"

        "MAIOR CONTRASTE DO PERFIL: " + maior_contraste_key
        + " = %+.2f" % maior_contraste_val
        + " (o padrao mais revelador - OBRIGATORIO aparecer no relatorio)\n\n"

        "SCORES DIAGNOSTICOS (questoes mais reveladoras por eixo):\n"
        "Conscienciosidade:\n" + fmt_diag("Conscienciosidade") + "\n"
        "Seguranca:\n" + fmt_diag("Seguranca") + "\n"
        "Extroversao:\n" + fmt_diag("Extroversao") + "\n"
        "Amabilidade:\n" + fmt_diag("Amabilidade") + "\n"
        "Neuroticismo:\n" + fmt_diag("Neuroticismo") + "\n\n"

        "ANALISE DAS COMBINACOES ATIVAS NESTE PERFIL:\n"
        "(Use estas combinacoes como base para identificar os padroes comportamentais reais)\n\n"
        + linhas_combinacoes + "\n\n"

        + estilo_lideranca + "\n\n"

        "REGRAS ABSOLUTAS - VIOLACAO INVALIDA O RELATORIO:\n"
        "1. Escreva sempre em 'voce' - nunca em terceira pessoa\n"
        "2. NUNCA use os nomes dos eixos no texto (Abertura, Conscienciosidade, Extroversao, etc.)\n"
        "3. NUNCA use termos tecnicos como 'introversao', 'neuroticismo', 'Big Five'\n"
        "4. NUNCA escreva frases que servem para qualquer pessoa - cada frase deve ser especifica deste perfil\n"
        "5. NUNCA invente tracos que os dados nao sustentam - cada afirmacao deve ter respaldo nos scores\n"
        "6. Conscienciosidade "
        + "%.2f" % co
        + ": cumpre_compromissos=" + str(q11)
        + ", sistema_prioridades=" + str(q13)
        + ", deixa_ultima_hora=" + str(q16)
        + " -> SE Conscienciosidade < 3.0: PROIBIDO dizer 'planeja minuciosamente', "
        "'gerenciamento de projetos', 'compliance' ou qualquer coisa que implique alta organizacao\n"
        "7. Extroversao "
        + "%.2f" % ex
        + ": toma_iniciativa_grupo=" + str(q22)
        + ", porta_voz=" + str(q24)
        + " -> PROIBIDO dizer que toma iniciativa em grupo, e porta-voz, "
        "brilha em atendimento ao cliente, RH ou qualquer funcao de alta exposicao social\n"
        "8. PROIBIDO suavizar scores extremos: quando um score e 1 ou 5, "
        "isso e um padrao FORTE e consistente, nao uma 'tendencia' ou 'preferencia leve'\n"
        "9. Scores extremos encontrados neste perfil que DEVEM ser tratados como padroes fortes:\n"
        + scores_extremos_linhas
        + "10. O relatorio deve fazer a pessoa pensar 'como voce sabia disso?' - "
        "nao 'faz sentido para muita gente'\n\n"

        "ESTRUTURA OBRIGATORIA:\n\n"

        "1. COMO VOCÊ FUNCIONA DE VERDADE\n"
        "Descreva o padrao de funcionamento desta pessoa usando o conhecimento sobre como os dois tracos mais altos "
        "se manifestam em comportamentos observaveis. Como ela entra em situacoes novas? "
        "Como ela reage quando algo nao sai como esperado? O que ela faz automaticamente que outras pessoas nao fazem? "
        "Use exemplos de situacoes reais do dia a dia - reuniao, projeto novo, conversa dificil, decisao sob pressao.\n\n"

        "2. COMO VOCÊ TOMA DECISÕES\n"
        "Descreva o processo de decisao real desta pessoa com base nos tracos de responsabilidade, "
        "orientacao a certeza e curiosidade intelectual. "
        "Qual e o padrao tipico de pessoas com esses scores ao tomar decisoes importantes? "
        "Onde elas decidem bem? Onde elas travam? O que elas precisam sentir antes de se comprometer com algo? "
        "Se Conscienciosidade < 3.0, descreva o padrao de entrega sob pressao sem sistema.\n\n"

        "3. COMO VOCÊ SE RELACIONA\n"
        "Descreva o padrao relacional tipico de pessoas com esses scores de empatia, energia social e sensibilidade emocional. "
        "Como ela se comporta em grupos vs. em relacoes um a um? "
        "O que ela faz pelos outros que nao percebe que faz? Onde isso cobra um preco dela? "
        "Se o padrao de evitacao de conflito estiver ativo, DEVE ser descrito aqui com impacto real.\n\n"

        "4. O QUE ACONTECE DENTRO DE VOCÊ\n"
        "Use o maior contraste do perfil ("
        + maior_contraste_key + " = %+.2f) para descrever " % maior_contraste_val
        + "o dialogo interno tipico de pessoas com essa combinacao especifica de tracos. "
        "O que essa pessoa sente mas raramente externaliza? "
        "Qual e o padrao de pensamento que acontece na cabeca dela que os outros nao veem? "
        "IMPORTANTE: seja cirurgico. Nao descreva o contraste de forma abstrata. "
        "Descreva o que acontece concretamente: em que momentos do dia ela sente isso? "
        "Em que tipo de situacao esse contraste aparece? O que ela pensa mas nao diz? "
        "Exemplo de profundidade esperada: se o contraste e Abertura alta vs Extroversao moderada, "
        "nao diga 'voce tem vida intelectual rica' - diga 'voce chega a uma reuniao ja tendo "
        "pensado mais profundamente sobre o assunto do que qualquer pessoa na sala, "
        "mas raramente externaliza isso a menos que seja diretamente solicitado - "
        "e quando externaliza, frequentemente surpreende quem nao esperava essa profundidade'.\n"
        + ("ANCORAS ESPECIFICAS PARA ESTA SECAO (use como base, nao ignore):\n" + linhas_ancoras + "\n\n" if linhas_ancoras else "\n")

        + "5. ONDE VOCÊ PODE BRILHAR\n"
        "Com base no perfil completo e no estilo de lideranca identificado, descreva 3 a 4 contextos especificos "
        "onde esta pessoa teria desempenho excepcional. "
        "Nao seja generico. Diga: qual tipo de funcao, qual tipo de ambiente, qual tipo de projeto, "
        "qual papel em um time. Por que esse perfil especifico brilha nesse contexto e nao em outro? "
        "Inclua pelo menos um contexto de lideranca ou influencia. "
        "ATENCAO: Extroversao "
        + "%.2f" % ex
        + " - PROIBIDO sugerir funcoes de alta exposicao social como atendimento, vendas, RH ou apresentacoes frequentes.\n\n"

        "6. SUAS FORÇAS REAIS\n"
        "Maximo 5 forcas. Formato obrigatorio: 'Voce [verbo de acao concreto] quando [situacao especifica]'. "
        "Cada forca deve descrever um comportamento observavel, nao um adjetivo. "
        "Nao escreva 'voce e curioso' - escreva o que ela faz por causa dessa curiosidade. "
        "Cada forca deve ser sustentada por score >= 3.5 nos dados.\n\n"

        "7. ONDE VOCÊ TRAVA\n"
        "Maximo 4 pontos. Formato obrigatorio: 'Porque voce tende a [padrao comportamental especifico], "
        "o que acontece na pratica e [consequencia concreta na vida real]'. "
        "Seja direto. Mostre o custo real - financeiro, profissional, relacional. "
        "Nao suavize. Pessoas com esse perfil reconhecem esses padroes quando sao descritos com precisao. "
        "Se o padrao de evitacao de conflito estiver ativo, DEVE aparecer aqui. "
        "REGRA CRITICA PARA CONSCIENCIOSIDADE: se cumpre_compromissos >= 4 E sistema_prioridades <= 3, "
        "o padrao correto NAO e 'se compromete facilmente' - e 'entrega mesmo sem um sistema claro, "
        "o que gera custo oculto: a entrega acontece mas com esforco desproporcional, "
        "acumulo de pressao de ultima hora, e sensacao de que poderia ter feito melhor se tivesse se organizado antes'. "
        "Descreva o custo real da entrega sem sistema, nao o excesso de compromissos. "
        "REGRA PARA SEGURANCA: mudancas_incomodam_Q55="
        + str(q_adj.get(55, 3))
        + ", resiste_mudar_rotina_Q59="
        + str(q_adj.get(59, 3))
        + ". Se Q55 >= 4 OU Q59 >= 4, DEVE aparecer como trava: "
        "'Quando uma oportunidade exige mudar de rotina ou de plano, voce tende a resistir mesmo quando a mudanca vale a pena. "
        "O custo: pode recusar oportunidades de crescimento por desconforto com a transicao, "
        "nao por falta de capacidade.'\n\n"

        "8. O QUE VALE DESENVOLVER\n"
        "2 a 3 areas de desenvolvimento de alto impacto para este perfil especifico. "
        "Nao e sobre corrigir fraquezas - e sobre o que, se desenvolvido, multiplicaria os resultados "
        "que essa pessoa ja consegue. Seja especifico: o que desenvolver, como isso se conecta ao perfil, "
        "e qual seria o impacto concreto na carreira, nas relacoes ou nas financas. "
        "ABUNDANCIA: Abundancia="
        + "%.2f" % abu
        + ", oportunidades_limitadas_Q65="
        + str(q_adj.get(65, 3))
        + ", dificuldade_investir_sem_garantia_Q71="
        + str(q_adj.get(71, 3))
        + ". Se Q65 >= 4 OU Q71 >= 4, DEVE aparecer como area de desenvolvimento: "
        "'Aprender a investir em si mesmo sem exigir retorno garantido antes de comecar - "
        "porque o crescimento mais importante frequentemente exige apostar antes de ter certeza.'\n\n"

        "9. PRÓXIMOS PASSOS\n"
        "INSTRUCAO CRITICA: Os passos abaixo foram pre-gerados com base nos padroes especificos deste perfil. "
        "Use-os como base obrigatoria. Voce pode refinar a linguagem para soar mais natural e humana, "
        "mas NAO pode substituir por passos genericos que servem para qualquer pessoa. "
        "REMOVA os prefixos 'PASSO DERIVADO DE...' do texto final - eles sao instrucoes internas, nao devem aparecer para o usuario. "
        "Cada passo deve comecar diretamente com a acao, sem rotulo. "
        "PASSOS CANDIDATOS DERIVADOS DOS PADROES DESTE PERFIL:\n"
        + linhas_passos_candidatos
        + "\n\nFormate cada passo com: numero + acao especifica + por que faz sentido para este perfil + resultado esperado.\n\n"

        "TOM E ESTILO:\n"
        "- Escreva como um mentor que conhece profundamente esse tipo de pessoa\n"
        "- Seja direto, especifico e humano\n"
        "- Evite listas de adjetivos - prefira descricoes de comportamentos reais\n"
        "- O criterio final: a pessoa deve ler e pensar 'isso sou eu de verdade, como voce sabia?'\n"
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
                        "Voce so escreve o que os dados sustentam. "
                        "Scores extremos (1 ou 5) indicam padroes fortes que devem ser descritos com clareza, "
                        "nao suavizados como 'tendencias'."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
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
        "temperature": 0.4,
        "perguntas_invertidas": len(PERGUNTAS_INVERTIDAS),
        "total_perguntas": len(questions),
        "eixos": list(blocos_info.keys()),
        "total_contrastes_calculados": len(perfil["diferencas"]),
        "versao_prompt": "V5.15 - calibrado por Manus AI",
    })


# =============================================================
# CALIBRACAO GUIADA
# =============================================================

def gerar_statements_calibracao(perfil):
    medias = perfil["medias"]
    adj = perfil["respostas_ajustadas"]
    ab  = medias["Abertura"]
    co  = medias["Conscienciosidade"]
    ex  = medias["Extroversao"]
    am  = medias["Amabilidade"]
    ne  = medias["Neuroticismo"]
    se  = medias["Seguranca"]
    abu = medias["Abundancia"]
    q11 = adj.get(11, 3); q17 = adj.get(17, 3); q20 = adj.get(20, 3)
    q22 = adj.get(22, 3); q24 = adj.get(24, 3); q26 = adj.get(26, 3)
    q33 = adj.get(33, 3); q35 = adj.get(35, 3); q37 = adj.get(37, 3); q39 = adj.get(39, 3)
    q44 = adj.get(44, 3); q49 = adj.get(49, 3)
    q55 = adj.get(55, 3); q56 = adj.get(56, 3); q61 = adj.get(61, 3)
    evita_conflito = (q33 <= 3 or q37 <= 3 or q39 <= 3) and q35 >= 3
    statements = []
    sid = 1

    if ab >= 3.5:
        statements.append({
            "id": sid, "eixo": "Abertura",
            "texto": (
                "Voce tem uma curiosidade intelectual acima da media. "
                "Quando encontra um problema ou tema novo, tende a ir fundo: "
                "pesquisa, conecta ideias, e frequentemente sabe mais sobre o assunto "
                "do que a maioria das pessoas ao seu redor."
            ),
            "followup_verdadeiro": (
                "Isso acontece em qualquer assunto, ou so em areas que voce ja tem interesse? "
                "(1 = so em areas especificas / 5 = em praticamente qualquer assunto novo)"
            ),
            "followup_falso": (
                "Voce prefere aplicar o que ja sabe em vez de explorar areas novas? "
                "Ou voce tem curiosidade, mas ela e mais seletiva do que o descrito? "
                "(1 = prefiro muito o que ja sei / 5 = tenho curiosidade mas so em temas especificos)"
            ),
            "root_questions": [1, 3, 5, 7, 8, 10],
            "ajuste_mais_forte": {1: 1, 3: 1, 8: 1},
            "ajuste_mais_fraco": {1: -1, 3: -1, 8: -1},
        })
        sid += 1

    if q11 >= 3 and q17 >= 3 and q20 >= 3:
        statements.append({
            "id": sid, "eixo": "Conscienciosidade",
            "texto": (
                "Quando voce assume um compromisso, cumpre - mesmo quando nao esta com vontade, "
                "mesmo quando o prazo aperta. "
                "As pessoas que dependem de voce sabem que podem contar com o que voce prometeu."
            ),
            "followup_verdadeiro": (
                "Voce cumpre porque tem um sistema de organizacao claro, "
                "ou porque se sente responsavel mesmo sem sistema? "
                "(1 = tenho sistema claro / 5 = cumpro mesmo sem sistema, no esforco)"
            ),
            "followup_falso": (
                "Voce cumpre compromissos em algumas areas mas nao em outras? "
                "Ou a descricao foi exagerada? "
                "(1 = sou bem menos confiavel do que descrito / "
                "5 = sou confiavel mas so em certas areas)"
            ),
            "root_questions": [11, 17, 20],
            "ajuste_mais_forte": {11: 1, 17: 1, 20: 1},
            "ajuste_mais_fraco": {11: -1, 17: -1, 20: -1},
        })
        sid += 1

    if ex <= 3.2:
        statements.append({
            "id": sid, "eixo": "Extroversao",
            "texto": (
                "Em grupos, voce prefere observar e ouvir na maior parte do tempo, "
                "escolhendo falar apenas quando tem algo importante a acrescentar."
            ),
            "followup_verdadeiro": (
                "Isso e uma preferencia ou grupos grandes te deixam genuinamente desconfortavel? "
                "(1 = e apenas preferencia, me adapto bem / "
                "5 = grupos grandes me custam energia real)"
            ),
            "followup_falso": (
                "Voce se ve como alguem que toma iniciativa em grupos com frequencia? "
                "Ou voce tem lideranca, mas ela e por competencia, nao por volume de fala? "
                "(1 = tomo iniciativa com frequencia, sou vocal / "
                "5 = tenho lideranca mas ela e silenciosa)"
            ),
            "root_questions": [22, 24, 26, 29, 30],
            "ajuste_mais_forte": {22: -1, 24: -1, 26: -1},
            "ajuste_mais_fraco": {22: 1, 24: 1, 26: 1},
        })
        sid += 1

    if evita_conflito:
        statements.append({
            "id": sid, "eixo": "Amabilidade",
            "texto": (
                "Quando ha tensao ou desacordo, voce tende a ceder ou guardar o que pensa "
                "em vez de confrontar diretamente. "
                "Voce raramente da feedback negativo, adia conversas dificeis, "
                "e frequentemente sai de situacoes sem ter dito o que realmente pensava."
            ),
            "followup_verdadeiro": (
                "Isso acontece em todas as relacoes ou so com pessoas especificas? "
                "(1 = so com pessoas de autoridade / "
                "5 = acontece em praticamente todas as relacoes)"
            ),
            "followup_falso": (
                "Voce consegue confrontar quando necessario, mas prefere nao fazer desnecessariamente? "
                "Ou a descricao exagerou - voce e direto e nao tem dificuldade com conflito? "
                "(1 = sou direto, conflito nao me incomoda / "
                "5 = consigo confrontar mas prefiro evitar)"
            ),
            "root_questions": [33, 35, 37, 39],
            "ajuste_mais_forte": {33: -1, 37: -1, 39: -1},
            "ajuste_mais_fraco": {33: 1, 37: 1, 39: 1},
        })
        sid += 1

    if q44 >= 3 or q49 >= 3:
        statements.append({
            "id": sid, "eixo": "Neuroticismo",
            "texto": (
                "Voce tende a antecipar problemas antes que eles acontecam. "
                "Antes de uma reuniao importante, de uma decisao grande ou de uma mudanca, "
                "sua mente ja esta processando os possiveis cenarios - inclusive os negativos. "
                "Isso te torna bom em prever riscos, mas tambem gasta energia "
                "em preocupacoes que muitas vezes nao se concretizam."
            ),
            "followup_verdadeiro": (
                "Essa antecipacao te paralisa ou te prepara? "
                "(1 = me paralisa com frequencia / "
                "5 = me prepara - raramente me paralisa)"
            ),
            "followup_falso": (
                "Voce e mais calmo do que descrito - lida bem com incerteza sem antecipar muito? "
                "Ou a antecipacao existe mas e leve, nao um padrao forte? "
                "(1 = sou muito calmo, raramente antecipo / "
                "5 = antecipo mas de forma leve - a descricao foi exagerada)"
            ),
            "root_questions": [44, 49, 42, 46],
            "ajuste_mais_forte": {44: 1, 49: 1},
            "ajuste_mais_fraco": {44: -1, 49: -1},
        })
        sid += 1

    # Afirmacao 6a: Aversao a risco (cautela antes de decidir)
    # Perguntas diretas: Q56 (garantia vs incerteza), Q61 (desconforto sem plano), Q63 (confirmar antes de agir)
    # Perguntas invertidas: Q54, Q57, Q60, Q62 (agir com confianca sem info completa)
    q56 = adj.get(56, 3); q61 = adj.get(61, 3); q63 = adj.get(63, 3)
    if q56 >= 3 or q61 >= 3 or q63 >= 3:
        statements.append({
            "id": sid, "eixo": "Cautela e Risco",
            "texto": (
                "Quando precisa tomar uma decisao importante, voce prefere esperar ter "
                "informacao suficiente antes de se comprometer. "
                "Prefere uma oportunidade menor mas garantida a uma maior mas incerta. "
                "Nao e que voce fuja do risco - e que voce precisa entender o risco antes de aceita-lo."
            ),
            "followup_verdadeiro": (
                "Essa cautela ja te fez perder oportunidades que valiam o risco? "
                "(1 = raramente perco oportunidades por cautela / "
                "5 = ja perdi oportunidades claras por nao agir a tempo)"
            ),
            "followup_falso": (
                "Voce age com mais facilidade mesmo sem todas as informacoes? "
                "Ou a descricao estava certa mas a intensidade foi exagerada? "
                "(1 = ajo rapido, incerteza nao me paralisa / "
                "5 = a descricao estava certa mas foi um pouco exagerada)"
            ),
            "root_questions": [56, 61, 63],
            "ajuste_mais_forte": {56: 1, 61: 1, 63: 1},
            "ajuste_mais_fraco": {56: -1, 61: -1, 63: -1},
        })
        sid += 1

    # Afirmacao 6b: Tolerancia a mudancas de planos (imprevisibilidade)
    # Q55 (mudancas inesperadas incomodam), Q59 (resiste a mudar rotina que funciona)
    # Q57 invertida (se sente bem em situacoes imprevisíveis), Q62 invertida (seguro em transicoes)
    q55 = adj.get(55, 3); q59 = adj.get(59, 3)
    if q55 >= 3:
        statements.append({
            "id": sid, "eixo": "Reatividade a Mudanças",
            "texto": (
                "Quando seus planos mudam de forma inesperada, você tende a se incomodar "
                "mais do que a maioria das pessoas — mesmo quando a mudança é pequena."
            ),
            "followup_verdadeiro": (
                "Isso acontece em qualquer mudança ou só em mudanças que afetam áreas importantes para você? "
                "(1 = só me incomoda quando afeta áreas muito importantes / "
                "5 = qualquer mudança inesperada me tira do eixo)"
            ),
            "followup_falso": (
                "Você lida bem com mudanças de planos — elas não te afetam mais do que a média? "
                "Ou a descrição estava certa mas exagerada na intensidade? "
                "(1 = lido bem com mudanças, me adapto facilmente / "
                "5 = a descrição estava certa mas foi um pouco exagerada)"
            ),
            "root_questions": [55],
            "ajuste_mais_forte": {55: 1},
            "ajuste_mais_fraco": {55: -1},
        })
        sid += 1

    if q59 >= 3:
        statements.append({
            "id": sid, "eixo": "Preferência por Rotina",
            "texto": (
                "Quando você encontra uma rotina que funciona, tende a mantê-la — "
                "mesmo quando há opções melhores disponíveis. "
                "Não é resistência à mudança por medo: é uma preferência genuína pelo que já foi testado e funciona."
            ),
            "followup_verdadeiro": (
                "Essa preferência por rotina se aplica a todas as áreas da sua vida ou só a algumas? "
                "(1 = só em certas áreas específicas / "
                "5 = em praticamente todas as áreas — prefiro o que já funciona)"
            ),
            "followup_falso": (
                "Você muda de rotina com facilidade quando vê uma opção melhor? "
                "Ou a descrição estava certa mas a intensidade foi exagerada? "
                "(1 = mudo facilmente, não tenho apego a rotinas / "
                "5 = a descrição estava certa mas foi um pouco exagerada)"
            ),
            "root_questions": [59],
            "ajuste_mais_forte": {59: 1},
            "ajuste_mais_fraco": {59: -1},
        })
        sid += 1

    if ab >= 3.5 and co >= 3.5:
        statements.append({
            "id": sid, "eixo": "Lideranca",
            "texto": (
                "Voce tem tracos de lideranca - mas do tipo silencioso. "
                "Nao e o tipo que se impos ou buscou o cargo. "
                "E o tipo que as pessoas consultam quando o assunto e serio, "
                "que entrega quando os outros nao entregam, "
                "e que influencia por competencia e confiabilidade, nao por carisma ou volume."
            ),
            "followup_verdadeiro": (
                "Voce ja esteve em posicao de lideranca formal? "
                "Ou voce lidera informalmente - sem o titulo, mas as pessoas te seguem? "
                "(1 = nunca liderei, nao me vejo como lider / "
                "5 = lidero informalmente - as pessoas me seguem mesmo sem eu ter o cargo)"
            ),
            "followup_falso": (
                "Voce diria que nao tem tracos de lideranca - prefere seguir do que liderar? "
                "Ou que tem lideranca mas ela e mais direta e visivel do que o descrito? "
                "(1 = nao tenho tracos de lideranca, prefiro seguir / "
                "5 = tenho lideranca mas ela e mais direta e visivel)"
            ),
            "root_questions": [11, 17, 20, 22, 24, 30],
            "ajuste_mais_forte": {22: 1, 24: 1, 30: 1},
            "ajuste_mais_fraco": {22: -1, 24: -1, 30: -1},
        })
        sid += 1

    return statements


def aplicar_ajustes_calibracao(respostas_originais, ajustes):
    novas = dict(respostas_originais)
    for q_num, delta in ajustes.items():
        if q_num in novas:
            novo_val = max(1, min(5, novas[q_num] + delta))
            novas[q_num] = novo_val
    return novas


# =============================================================
# INTERFACE PRINCIPAL
# =============================================================

# Logo + título (embutido como base64 para evitar dependência de arquivo estático)
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("logo_mindinsight.png", width=220)
with col_title:
    st.markdown("<h1 style='margin-bottom:0'>Mind Insight™</h1>", unsafe_allow_html=True)
    if MODO_TESTE:
        st.markdown(
            '<div class="manus-badge">V5.17 | Criado com Claude (Anthropic) | '
            'Aperfeiçoado por Manus AI | MODO TESTE ATIVO</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="manus-badge">Análise comportamental potencializada por psicologia científica e inteligência artificial avançada</div>',
            unsafe_allow_html=True
        )

TOTAL = len(questions)

# ------------------------------------------------------------------
# TELA 0 - Coleta de dados do usuario (producao) ou selecao de modo (teste)
# ------------------------------------------------------------------
if not st.session_state.modo_selecionado:
    if MODO_TESTE:
        # --- MODO TESTE: opcoes de reutilizacao ---
        st.markdown("---")
        st.subheader("[MODO TESTE] Como você quer começar?")
        st.caption(
            "Opção de reutilização disponível apenas no modo teste (?modo=teste na URL). "
            "Usuários normais vão direto para as perguntas."
        )

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**Usar respostas do último teste**")
            _json_existe = os.path.exists(ULTIMO_TESTE_JSON)
            if _json_existe:
                st.caption(
                    "Serão usadas as respostas da sua **última sessão calibrada** (salvas automaticamente). "
                    "Gera o relatório em segundos sem precisar responder novamente."
                )
            else:
                st.caption(
                    "Serão usadas as respostas de referência (nenhuma calibração salva ainda). "
                    "Gera o relatório em segundos sem precisar responder novamente."
                )
            if st.button("Usar último teste", key="btn_ultimo"):
                st.session_state.responses = carregar_ultimo_teste()
                st.session_state.current_question = TOTAL + 1
                st.session_state.modo_selecionado = True
                st.rerun()

        with col_b:
            st.markdown("**Responder o questionário novamente**")
            st.caption(
                "Responde todas as 74 perguntas do zero. "
                "Use quando quiser registrar um novo conjunto de respostas."
            )
            if st.button("Responder questionário", key="btn_novo"):
                st.session_state.responses = {}
                st.session_state.current_question = 1
                st.session_state.modo_selecionado = True
                st.rerun()

    else:
        # --- MODO PRODUCAO: coleta de dados do usuario ---
        if not st.session_state.user_info_completo:
            st.markdown("---")
            st.subheader("Antes de começar")
            st.markdown(
                "Preencha os dados abaixo para personalizar seu relatório. Ao final, você também receberá uma cópia por email."
            )
            st.markdown("---")

            with st.form("form_dados_usuario"):
                nome_input = st.text_input("Seu nome *", placeholder="Como prefere ser chamado(a)")
                col_idade, col_genero = st.columns(2)
                with col_idade:
                    idade_input = st.number_input("Idade *", min_value=16, max_value=99, value=30, step=1)
                with col_genero:
                    genero_input = st.selectbox(
                        "Genero *",
                        ["Prefiro não informar", "Feminino", "Masculino", "Nao-binario", "Outro"]
                    )
                email_input = st.text_input("Email *", placeholder="seu@email.com")
                st.caption("Seu email sera usado apenas para enviar uma copia do seu relatorio.")

                submitted = st.form_submit_button("Comecar o teste", type="primary")
                if submitted:
                    if not nome_input.strip():
                        st.error("Por favor, informe seu nome.")
                    elif not email_input.strip() or "@" not in email_input:
                        st.error("Por favor, informe um email valido.")
                    else:
                        st.session_state.user_info = {
                            "nome": nome_input.strip(),
                            "idade": int(idade_input),
                            "genero": genero_input,
                            "email": email_input.strip().lower(),
                        }
                        st.session_state.user_info_completo = True
                        st.session_state.responses = {}
                        st.session_state.current_question = 1
                        st.session_state.modo_selecionado = True
                        st.rerun()
        else:
            # user_info ja preenchido, ir para questionario
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
# TELA 1.5 - Calibracao Guiada
# ------------------------------------------------------------------
elif not st.session_state.calibracao_completa:
    if st.session_state.perfil_cache is None:
        st.session_state.perfil_cache = gerar_perfil(st.session_state.responses)
    if not st.session_state.calibracao_statements:
        st.session_state.calibracao_statements = gerar_statements_calibracao(st.session_state.perfil_cache)

    statements = st.session_state.calibracao_statements

    st.title("Verificação Rápida do Perfil")
    st.markdown(
        "Antes de gerar seu relatório completo, preciso confirmar se as afirmações abaixo "
        "descrevem você com precisão. **Isso leva menos de 2 minutos** e garante que o "
        "relatório final seja fiel a quem você realmente é."
    )
    st.markdown("---")

    opcoes_validacao = [
        "Sim, isso me descreve bem",
        "Sim, mas com menos intensidade do que a realidade",
        "Sim, mas com mais intensidade do que a realidade",
        "Não me descreve"
    ]

    todas_respondidas = True
    ajustes_acumulados = {}

    for stmt in statements:
        sid = stmt["id"]
        st.markdown("**Afirmação " + str(sid) + " — " + stmt["eixo"] + ":**")
        st.info(stmt["texto"])

        resposta_stmt = st.radio(
            "Esta afirmação te descreve?",
            opcoes_validacao,
            index=None,
            key="calib_stmt_" + str(sid)
        )

        if resposta_stmt is None:
            todas_respondidas = False
        else:
            st.session_state.calibracao_respostas[sid] = resposta_stmt

            if resposta_stmt != opcoes_validacao[0]:
                if resposta_stmt == opcoes_validacao[3]:
                    followup_txt = stmt["followup_falso"]
                    followup_label = "Para entender melhor o que é verdadeiro para você:"
                else:
                    followup_txt = stmt["followup_verdadeiro"]
                    followup_label = "Ajude-nos a calibrar a intensidade correta:"

                st.markdown("*" + followup_label + "*")
                st.caption(followup_txt)

                followup_val = st.slider(
                    "Sua resposta (1 a 5):",
                    min_value=1, max_value=5, value=3,
                    key="calib_followup_" + str(sid)
                )
                st.session_state.calibracao_followup[sid] = followup_val

                intensidade = max(1, followup_val - 2)
                if resposta_stmt == opcoes_validacao[1]:
                    for q_num, delta in stmt["ajuste_mais_forte"].items():
                        ajustes_acumulados[q_num] = ajustes_acumulados.get(q_num, 0) + int(round(delta * intensidade))
                elif resposta_stmt == opcoes_validacao[2]:
                    for q_num, delta in stmt["ajuste_mais_fraco"].items():
                        ajustes_acumulados[q_num] = ajustes_acumulados.get(q_num, 0) + int(round(delta * intensidade))
                else:
                    for q_num, delta in stmt["ajuste_mais_fraco"].items():
                        ajustes_acumulados[q_num] = ajustes_acumulados.get(q_num, 0) + int(round(delta * 2))

        st.markdown("---")

    if todas_respondidas:
        st.session_state.calibracao_ajustes = ajustes_acumulados
        if st.button("Gerar meu relatório completo", type="primary"):
            if ajustes_acumulados:
                novas_respostas = aplicar_ajustes_calibracao(
                    st.session_state.responses, ajustes_acumulados
                )
                st.session_state.perfil_cache = gerar_perfil(novas_respostas)
            # Salva as respostas calibradas para reutilizacao futura
            respostas_para_salvar = aplicar_ajustes_calibracao(
                st.session_state.responses, ajustes_acumulados
            ) if ajustes_acumulados else dict(st.session_state.responses)
            salvar_ultimo_teste(respostas_para_salvar)
            st.session_state.calibracao_completa = True
            st.rerun()
    else:
        st.warning("Por favor, responda todas as afirmacoes acima para continuar.")

# ------------------------------------------------------------------
# TELA 2 - Relatorio
# ------------------------------------------------------------------
else:
    st.title("Seu Relatório de Perfil")

    if st.session_state.perfil_cache is not None:
        perfil = st.session_state.perfil_cache
    else:
        perfil = gerar_perfil(st.session_state.responses)

    if st.session_state.calibracao_ajustes:
        n_ajustes = len(st.session_state.calibracao_ajustes)
        st.success(
            "Relatório calibrado com base nas suas respostas de validação. "
            + str(n_ajustes) + " ajuste(s) aplicado(s) para maior precisão."
        )

    with st.spinner("Gerando sua análise..."):
        relatorio = gerar_relatorio(perfil)

    st.markdown(relatorio)

    if MODO_TESTE:
        render_debug(perfil)

    # ------------------------------------------------------------------
    # Registro no Google Sheets e envio de email (modo producao)
    # ------------------------------------------------------------------
    if not st.session_state.dados_registrados:
        user_info = st.session_state.get("user_info", {})
        medias_perfil = perfil.get("medias", {})
        respostas_finais = st.session_state.responses
        if st.session_state.calibracao_ajustes:
            respostas_finais = aplicar_ajustes_calibracao(
                st.session_state.responses, st.session_state.calibracao_ajustes
            )
        dados_registro = {
            "data_hora": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modo_teste": "SIM" if MODO_TESTE else "NAO",
            "nome": user_info.get("nome", ""),
            "idade": user_info.get("idade", ""),
            "genero": user_info.get("genero", ""),
            "email": user_info.get("email", ""),
            "Abertura": round(medias_perfil.get("Abertura", 0), 2),
            "Conscienciosidade": round(medias_perfil.get("Conscienciosidade", 0), 2),
            "Extroversao": round(medias_perfil.get("Extroversao", 0), 2),
            "Amabilidade": round(medias_perfil.get("Amabilidade", 0), 2),
            "Neuroticismo": round(medias_perfil.get("Neuroticismo", 0), 2),
            "Seguranca": round(medias_perfil.get("Seguranca", 0), 2),
            "Abundancia": round(medias_perfil.get("Abundancia", 0), 2),
            "maior_contraste": perfil.get("maior_contraste_key", "") + " = " + str(perfil.get("maior_contraste_val", "")),
            "amplitude_pct": str(perfil.get("pct_3_4", "")),
            "padroes_ativos": "; ".join(perfil.get("flags", [])),
            "ajustes_calibracao": str(len(st.session_state.get("calibracao_ajustes", {}))),
            "relatorio": relatorio,
            "respostas": respostas_finais,
        }
        ok_sheets, msg_sheets = registrar_no_sheets(dados_registro)
        if MODO_TESTE:
            if ok_sheets:
                st.info("[DEBUG] Registro no Google Sheets: OK")
            else:
                st.error("[DEBUG] Erro no Google Sheets: " + str(msg_sheets))
        # Email apenas em modo producao
        if not MODO_TESTE:
            nome_usuario = user_info.get("nome", "")
            email_usuario = user_info.get("email", "")
            if email_usuario:
                ok_email, msg_email = enviar_email(email_usuario, nome_usuario, relatorio)
                if ok_email:
                    st.success(
                        "Uma cópia do seu relatório foi enviada para **" + email_usuario + "**. "
                        "Verifique sua caixa de entrada (ou spam)."
                    )
        st.session_state.dados_registrados = True

    st.markdown("---")

    # ------------------------------------------------------------------
    # Botao de download das respostas calibradas (apenas modo teste)
    # ------------------------------------------------------------------
    if MODO_TESTE:
        respostas_para_download = st.session_state.responses
        if st.session_state.perfil_cache is not None and st.session_state.calibracao_ajustes:
            respostas_para_download = aplicar_ajustes_calibracao(
                st.session_state.responses, st.session_state.calibracao_ajustes
            )
        _json_bytes = json.dumps(
            {str(k): v for k, v in respostas_para_download.items()},
            ensure_ascii=False, indent=2
        ).encode('utf-8')
        st.download_button(
            label="[TESTE] Baixar respostas calibradas (ultimo_teste.json)",
            data=_json_bytes,
            file_name="ultimo_teste.json",
            mime="application/json",
            help=(
                "Baixe este arquivo e adicione ao seu repositorio GitHub junto com o app.py. "
                "Assim as respostas calibradas serao preservadas em futuros deploys."
            )
        )
        st.caption(
            "Dica: coloque o arquivo baixado na mesma pasta do app.py no seu repositorio "
            "para que as respostas calibradas sejam usadas automaticamente nos proximos deploys."
        )

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Refazer o teste"):
            for key in ["responses", "calibracao_completa", "calibracao_statements",
                        "calibracao_respostas", "calibracao_followup",
                        "calibracao_ajustes", "perfil_cache",
                        "relatorio_gerado", "dados_registrados",
                        "user_info", "user_info_completo"]:
                if key in ("responses", "user_info"):
                    st.session_state[key] = {}
                elif key in ("calibracao_statements",):
                    st.session_state[key] = []
                elif key in ("calibracao_respostas", "calibracao_followup", "calibracao_ajustes"):
                    st.session_state[key] = {}
                elif key == "perfil_cache":
                    st.session_state[key] = None
                elif key == "relatorio_gerado":
                    st.session_state[key] = ""
                else:
                    st.session_state[key] = False
            st.session_state.current_question = 1
            st.session_state.modo_selecionado = False
            st.rerun()
    with col2:
        if st.button("Voltar ao inicio"):
            for key in ["responses", "calibracao_completa", "calibracao_statements",
                        "calibracao_respostas", "calibracao_followup",
                        "calibracao_ajustes", "perfil_cache",
                        "relatorio_gerado", "dados_registrados",
                        "user_info", "user_info_completo"]:
                if key in ("responses", "user_info"):
                    st.session_state[key] = {}
                elif key in ("calibracao_statements",):
                    st.session_state[key] = []
                elif key in ("calibracao_respostas", "calibracao_followup", "calibracao_ajustes"):
                    st.session_state[key] = {}
                elif key == "perfil_cache":
                    st.session_state[key] = None
                elif key == "relatorio_gerado":
                    st.session_state[key] = ""
                else:
                    st.session_state[key] = False
            st.session_state.current_question = 0
            st.session_state.modo_selecionado = False
            st.rerun()
