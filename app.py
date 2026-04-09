# -*- coding: utf-8 -*-

# =============================================================
# MIND INSIGHT ADVANCED AI
# Version: V5.16
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
                "data_hora", "nome", "idade", "genero", "email",
                "Abertura", "Conscienciosidade", "Extroversao",
                "Amabilidade", "Neuroticismo", "Seguranca", "Abundancia",
                "maior_contraste", "amplitude_pct", "padroes_ativos",
                "ajustes_calibracao", "relatorio"
            ] + ["Q" + str(i) for i in range(1, 75)]
            ws.append_row(cabecalho)
        linha = [
            dados.get("data_hora", ""),
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
        msg["Subject"] = "Seu Relatorio Mind Insight"
        msg["From"] = "Mind Insight <" + gmail_user + ">"
        msg["To"] = destinatario

        texto_plain = (
            "Ola " + nome + ",\n\n"
            "Aqui esta o seu relatorio completo de perfil comportamental gerado pelo Mind Insight.\n\n"
            + relatorio_texto
            + "\n\n---\nMind Insight | Análise comportamental potencializada por psicologia científica e inteligência artificial avançada"
        )

        html_body = (
            "<html><body style='font-family:Arial,sans-serif;max-width:700px;margin:auto;padding:20px'>"
            "<h2 style='color:#1a1a1a'>Seu Relatorio Mind Insight</h2>"
            "<p>Ola <strong>" + nome + "</strong>,</p>"
            "<p>Aqui esta o seu relatorio completo de perfil comportamental.</p>"
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

        "1. COMO VOCE FUNCIONA DE VERDADE\n"
        "Descreva o padrao de funcionamento desta pessoa usando o conhecimento sobre como os dois tracos mais altos "
        "se manifestam em comportamentos observaveis. Como ela entra em situacoes novas? "
        "Como ela reage quando algo nao sai como esperado? O que ela faz automaticamente que outras pessoas nao fazem? "
        "Use exemplos de situacoes reais do dia a dia - reuniao, projeto novo, conversa dificil, decisao sob pressao.\n\n"

        "2. COMO VOCE TOMA DECISOES\n"
        "Descreva o processo de decisao real desta pessoa com base nos tracos de responsabilidade, "
        "orientacao a certeza e curiosidade intelectual. "
        "Qual e o padrao tipico de pessoas com esses scores ao tomar decisoes importantes? "
        "Onde elas decidem bem? Onde elas travam? O que elas precisam sentir antes de se comprometer com algo? "
        "Se Conscienciosidade < 3.0, descreva o padrao de entrega sob pressao sem sistema.\n\n"

        "3. COMO VOCE SE RELACIONA\n"
        "Descreva o padrao relacional tipico de pessoas com esses scores de empatia, energia social e sensibilidade emocional. "
        "Como ela se comporta em grupos vs. em relacoes um a um? "
        "O que ela faz pelos outros que nao percebe que faz? Onde isso cobra um preco dela? "
        "Se o padrao de evitacao de conflito estiver ativo, DEVE ser descrito aqui com impacto real.\n\n"

        "4. O QUE ACONTECE DENTRO DE VOCE\n"
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

        + "5. ONDE VOCE PODE BRILHAR\n"
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

        "7. ONDE VOCE TRAVA\n"
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

        "9. PROXIMOS PASSOS\n"
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
LOGO_B64 = "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"

col_logo, col_title = st.columns([1, 5])
with col_logo:
    import io as _io, base64 as _b64
    _logo_bytes = _b64.b64decode(LOGO_B64)
    st.image(_io.BytesIO(_logo_bytes), width=120)
with col_title:
    st.title("Mind Insight")
    if MODO_TESTE:
        st.markdown(
            '<div class="manus-badge">V5.16 | Criado com Claude (Anthropic) | '
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
        st.subheader("[MODO TESTE] Como voce quer comecar?")
        st.caption(
            "Opcao de reutilizacao disponivel apenas no modo teste (?modo=teste na URL). "
            "Usuarios normais vao direto para as perguntas."
        )

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**Usar respostas do ultimo teste**")
            _json_existe = os.path.exists(ULTIMO_TESTE_JSON)
            if _json_existe:
                st.caption(
                    "Serao usadas as respostas da sua **ultima sessao calibrada** (salvas automaticamente). "
                    "Gera o relatorio em segundos sem precisar responder novamente."
                )
            else:
                st.caption(
                    "Serao usadas as respostas de referencia (nenhuma calibracao salva ainda). "
                    "Gera o relatorio em segundos sem precisar responder novamente."
                )
            if st.button("Usar ultimo teste", key="btn_ultimo"):
                st.session_state.responses = carregar_ultimo_teste()
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

    else:
        # --- MODO PRODUCAO: coleta de dados do usuario ---
        if not st.session_state.user_info_completo:
            st.markdown("---")
            st.subheader("Antes de comecar")
            st.markdown(
                "Preencha os dados abaixo para personalizar seu relatorio. "
                "Ao final, voce tambem recebera uma copia por email."
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
                        ["Prefiro nao informar", "Feminino", "Masculino", "Nao-binario", "Outro"]
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

    st.title("Verificacao Rapida do Perfil")
    st.markdown(
        "Antes de gerar seu relatorio completo, preciso confirmar se as afirmacoes abaixo "
        "descrevem voce com precisao. **Isso leva menos de 2 minutos** e garante que o "
        "relatorio final seja fiel a quem voce realmente e."
    )
    st.markdown("---")

    opcoes_validacao = [
        "Sim, isso me descreve bem",
        "Sim, mas com menos intensidade do que a realidade",
        "Sim, mas com mais intensidade do que a realidade",
        "Nao me descreve"
    ]

    todas_respondidas = True
    ajustes_acumulados = {}

    for stmt in statements:
        sid = stmt["id"]
        st.markdown("**Afirmacao " + str(sid) + " — " + stmt["eixo"] + ":**")
        st.info(stmt["texto"])

        resposta_stmt = st.radio(
            "Esta afirmacao te descreve?",
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
                    followup_label = "Para entender melhor o que e verdadeiro para voce:"
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
        if st.button("Gerar meu relatorio completo", type="primary"):
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
    st.title("Seu Relatorio de Perfil")

    if st.session_state.perfil_cache is not None:
        perfil = st.session_state.perfil_cache
    else:
        perfil = gerar_perfil(st.session_state.responses)

    if st.session_state.calibracao_ajustes:
        n_ajustes = len(st.session_state.calibracao_ajustes)
        st.success(
            "Relatorio calibrado com base nas suas respostas de validacao. "
            + str(n_ajustes) + " ajuste(s) aplicado(s) para maior precisao."
        )

    with st.spinner("Gerando sua analise..."):
        relatorio = gerar_relatorio(perfil)

    st.markdown(relatorio)

    if MODO_TESTE:
        render_debug(perfil)

    # ------------------------------------------------------------------
    # Registro no Google Sheets e envio de email (modo producao)
    # ------------------------------------------------------------------
    if not MODO_TESTE and not st.session_state.dados_registrados:
        user_info = st.session_state.get("user_info", {})
        medias_perfil = perfil.get("medias", {})
        respostas_finais = st.session_state.responses
        if st.session_state.calibracao_ajustes:
            respostas_finais = aplicar_ajustes_calibracao(
                st.session_state.responses, st.session_state.calibracao_ajustes
            )
        dados_registro = {
            "data_hora": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nome": user_info.get("nome", ""),
            "idade": user_info.get("idade", ""),
            "genero": user_info.get("genero", ""),
            "email": user_info.get("email", ""),
            "Abertura": medias_perfil.get("Abertura", ""),
            "Conscienciosidade": medias_perfil.get("Conscienciosidade", ""),
            "Extroversao": medias_perfil.get("Extroversao", ""),
            "Amabilidade": medias_perfil.get("Amabilidade", ""),
            "Neuroticismo": medias_perfil.get("Neuroticismo", ""),
            "Seguranca": medias_perfil.get("Seguranca", ""),
            "Abundancia": medias_perfil.get("Abundancia", ""),
            "maior_contraste": perfil.get("maior_contraste_key", "") + " = " + str(perfil.get("maior_contraste_val", "")),
            "amplitude_pct": str(perfil.get("pct_3_4", "")),
            "padroes_ativos": "; ".join(perfil.get("flags", [])),
            "ajustes_calibracao": str(len(st.session_state.get("calibracao_ajustes", {}))),
            "relatorio": relatorio,
            "respostas": respostas_finais,
        }
        ok_sheets, msg_sheets = registrar_no_sheets(dados_registro)
        nome_usuario = user_info.get("nome", "")
        email_usuario = user_info.get("email", "")
        if email_usuario:
            ok_email, msg_email = enviar_email(email_usuario, nome_usuario, relatorio)
            if ok_email:
                st.success(
                    "Uma copia do seu relatorio foi enviada para **" + email_usuario + "**. "
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
