# -*- coding: utf-8 -*-

# =============================================================
# MIND INSIGHT ADVANCED AI
# Version: V5.33
# Criado com: Claude (Anthropic)
# Aperfeicoado por: Manus AI
#
# V5.33 - Correcoes psicometricas e de consistencia
#       - Q75-Q89 removidas de PERGUNTAS_INVERTIDAS
#       - Q84 movida para Conscienciosidade
#       - Q88 movida para Extroversao
#       - evita_conflito agora usa respostas brutas
#       - scores diagnosticos enviados ao prompt usam o sentido literal da pergunta
#       - calibracao de conflito corrigida
#       - Google Sheets registra todas as perguntas reais
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
# RESPOSTAS DO ULTIMO TESTE
# =============================================================

ULTIMO_TESTE = {
    # ABERTURA (Q1-Q8, sem Q6, Q9, Q10)
    1: 4, 2: 2, 3: 4, 4: 2, 5: 4, 7: 4, 8: 4,
    # CONSCIENCIOSIDADE (Q11-Q20, sem Q15, Q19)
    11: 4, 12: 2, 13: 3, 14: 2, 16: 3, 17: 4, 18: 3, 20: 4,
    # EXTROVERSAO (Q21-Q30, sem Q27, Q28)
    21: 3, 22: 3, 23: 3, 24: 3, 25: 3, 26: 3, 29: 3, 30: 3,
    # AMABILIDADE (Q31-Q41, sem Q34, Q40, Q41)
    31: 4, 32: 4, 33: 3, 35: 4, 36: 3, 37: 3, 38: 4, 39: 3,
    # NEUROTICISMO (Q42-Q52)
    42: 3, 43: 3, 44: 4, 45: 3, 46: 3, 47: 3, 48: 3, 49: 4, 50: 3, 51: 3, 52: 3,
    # SEGURANCA (Q53-Q63)
    53: 4, 54: 4, 55: 4, 56: 4, 57: 3, 58: 3, 59: 4, 60: 3, 61: 4, 62: 3, 63: 4,
    # ABUNDANCIA (Q64-Q74)
    64: 4, 65: 2, 66: 3, 67: 3, 68: 4, 69: 3, 70: 3, 71: 3, 72: 3, 73: 3, 74: 3,
    # NOVAS Q75-Q89
    75: 3, 76: 3, 77: 3, 78: 3, 79: 3, 80: 2, 81: 3, 82: 3, 83: 4, 84: 3,
    85: 3, 86: 3, 87: 3, 88: 3, 89: 2,
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

# =============================================================
# PERGUNTAS
# =============================================================

questions = {
    # ABERTURA
    1:  "Fico genuinamente curioso quando encontro uma ideia que contradiz o que eu penso.",
    2:  "Prefiro solucoes ja testadas a experimentar abordagens novas.",
    3:  "Busco conhecimento em assuntos novos por prazer, nao por obrigacao.",
    4:  "Me incomoda quando conversas ficam muito abstratas ou filosoficas.",
    5:  "Consigo encontrar conexoes entre assuntos que parecem nao ter nada a ver.",
    7:  "Ja mudei uma opiniao importante por causa de um argumento bem fundamentado.",
    8:  "Me atrai explorar areas onde ainda nao tenho dominio.",
    # CONSCIENCIOSIDADE
    11: "Quando assumo um compromisso, cumpro - mesmo quando nao tenho mais vontade.",
    12: "Comeco tarefas importantes so quando estou com disposicao para isso.",
    13: "Tenho um sistema claro para organizar minhas prioridades do dia.",
    14: "Deixo para decidir na hora em vez de planejar com antecedencia.",
    16: "Frequentemente percebo que deixei algo importante para a ultima hora.",
    17: "Reviso meu trabalho antes de entregar, mesmo quando estou confiante.",
    18: "Tenho clareza sobre o que precisa ser feito hoje para chegar onde quero em um ano.",
    20: "Mantenho meus compromissos mesmo quando surgem opcoes mais atraentes.",
    # EXTROVERSAO
    21: "Me sinto com mais energia depois de passar tempo com pessoas do que antes.",
    22: "Em grupos, costumo tomar a iniciativa de falar primeiro.",
    23: "Prefiro pensar sozinho antes de discutir ideias com outros.",
    24: "Me sinto confortavel sendo o porta-voz de um grupo em situacoes formais.",
    25: "Depois de um dia social intenso, preciso de tempo sozinho para recarregar.",
    26: "Busco ativamente conhecer pessoas novas em ambientes sociais.",
    29: "Em conversas em grupo, frequentemente fico mais ouvindo do que falando.",
    30: "Quando tenho uma opiniao, nao tenho dificuldade de exprimi-la mesmo que outros discordem.",
    # AMABILIDADE
    31: "Quando alguem esta passando por algo dificil, meu primeiro instinto e ajudar.",
    32: "Tenho facilidade para identificar como o outro esta se sentindo, mesmo sem ele dizer.",
    33: "Em desacordos, prefiro ceder do que prolongar o conflito.",
    35: "Fico desconfortavel quando percebo que decepcionei alguem.",
    36: "Consigo discordar de alguem sem que isso afete a relacao.",
    37: "Evito dar feedback negativo para nao criar tensao.",
    38: "Confio nas pessoas ate que me provem o contrario.",
    39: "Quando preciso dizer algo dificil, costumo adiar mais do que deveria.",
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
    # NOVAS Q75-Q89
    75: "Quando reconheco que errei com alguem, consigo pedir desculpas diretamente, sem rodeios.",
    76: "Consigo me sentir satisfeito com meu trabalho mesmo quando ninguem comenta ou reconhece o que fiz.",
    77: "Quando vejo algo que precisa ser feito e ninguem esta fazendo, costumo ser a pessoa que toma a frente.",
    78: "Consigo entregar uma tarefa importante para outra pessoa sem ficar verificando como ela esta sendo feita.",
    79: "Consigo descansar sem sentir que deveria estar fazendo algo produtivo.",
    80: "Quando alguem me elogia, consigo receber sem minimizar ou desviar o assunto.",
    81: "Consigo pedir ajuda quando estou sobrecarregado, sem sentir que isso me diminui.",
    82: "Quando comeco um projeto, consigo manter o interesse mesmo depois que a novidade passa.",
    83: "Quando alguem proximo tem uma conquista importante, minha reacao genuina e de alegria, nao de comparacao.",
    84: "Quando alguem me pergunta o que eu realmente quero para minha vida, consigo responder com clareza.",
    85: "Consigo ouvir o outro numa conversa sem ja estar formulando minha resposta enquanto ele fala.",
    86: "Consigo estar presente numa conversa sem que minha mente va para o que preciso fazer depois.",
    87: "Consigo dizer nao para pedidos que me sobrecarregariam, mesmo quando a pessoa vai ficar desapontada.",
    88: "Consigo dizer o que penso mesmo quando sei que vai gerar desconforto ou discordancia.",
    89: "Quando alguem me pergunta sobre algo que fiz bem, consigo falar sobre isso sem diminuir o que conquistei.",
}

questions_display = {
    q: text.replace("nao", "não").replace("solucoes", "soluções").replace("situacoes", "situações").replace("opiniao", "opinião").replace("voce", "você").replace("tambem", "também").replace("ja", "já").replace("facil", "fácil") if False else text
    for q, text in questions.items()
}
# Ajustes manuais de exibição com acentuação mais completa
questions_display.update({
    2: "Prefiro soluções já testadas a experimentar abordagens novas.",
    3: "Busco conhecimento em assuntos novos por prazer, não por obrigação.",
    4: "Me incomoda quando conversas ficam muito abstratas ou filosóficas.",
    5: "Consigo encontrar conexões entre assuntos que parecem não ter nada a ver.",
    7: "Já mudei uma opinião importante por causa de um argumento bem fundamentado.",
    8: "Me atrai explorar áreas onde ainda não tenho domínio.",
    11: "Quando assumo um compromisso, cumpro - mesmo quando não tenho mais vontade.",
    12: "Começo tarefas importantes só quando estou com disposição para isso.",
    14: "Deixo para decidir na hora em vez de planejar com antecedência.",
    16: "Frequentemente percebo que deixei algo importante para a última hora.",
    18: "Tenho clareza sobre o que precisa ser feito hoje para chegar onde quero em um ano.",
    20: "Mantenho meus compromissos mesmo quando surgem opções mais atraentes.",
    21: "Me sinto com mais energia depois de passar tempo com pessoas do que antes.",
    24: "Me sinto confortável sendo o porta-voz de um grupo em situações formais.",
    29: "Em conversas em grupo, frequentemente fico mais ouvindo do que falando.",
    31: "Quando alguém está passando por algo difícil, meu primeiro instinto é ajudar.",
    32: "Tenho facilidade para identificar como o outro está se sentindo, mesmo sem ele dizer.",
    33: "Em desacordos, prefiro ceder do que prolongar o conflito.",
    35: "Fico desconfortável quando percebo que decepcionei alguém.",
    36: "Consigo discordar de alguém sem que isso afete a relação.",
    37: "Evito dar feedback negativo para não criar tensão.",
    38: "Confio nas pessoas até que me provem o contrário.",
    39: "Quando preciso dizer algo difícil, costumo adiar mais do que deveria.",
    42: "Quando algo dá errado, fico remoendo o que aconteceu por horas ou dias.",
    43: "Me recupero emocionalmente rápido depois de situações difíceis.",
    44: "Frequentemente me preocupo com coisas que ainda não aconteceram.",
    45: "Consigo manter a calma em situações de pressão alta.",
    47: "Quando estou sob estresse, minha capacidade de tomar decisões piora visivelmente.",
    48: "Me sinto estável emocionalmente na maior parte do tempo.",
    49: "Fico ansioso quando não sei o que esperar de uma situação.",
    50: "Críticas, mesmo construtivas, me afetam emocionalmente por um tempo.",
    51: "Consigo separar o que sinto do que preciso fazer, mesmo em momentos difíceis.",
    52: "Quando cometo um erro, fico muito mais tempo me cobrando do que a situação justificaria.",
    53: "Me sinto mais confortável quando sei exatamente o que esperar de uma situação.",
    54: "Consigo agir com confiança mesmo quando não tenho todas as informações.",
    55: "Mudanças inesperadas nos meus planos me deixam mais incomodado do que a maioria.",
    57: "Me sinto bem entrando em situações onde não sei exatamente o que vai acontecer.",
    58: "Demoro para confiar em pessoas ou ambientes novos.",
    59: "Quando estou numa rotina que funciona, resisto a mudar mesmo que haja opções melhores.",
    60: "Consigo me comprometer com algo antes de ter certeza absoluta de que vai dar certo.",
    61: "Sinto desconforto real quando preciso tomar decisões sem um plano claro.",
    62: "Me sinto seguro mesmo em fases de transição ou incerteza na minha vida.",
    63: "Prefiro confirmar os detalhes antes de agir do que improvisar no momento.",
    64: "Quando vejo alguém bem-sucedido, meu primeiro pensamento é de inspiração, não de comparação.",
    65: "Sinto que as oportunidades disponíveis para mim são limitadas.",
    67: "Frequentemente sinto que estou ficando para trás em relação a onde deveria estar.",
    68: "Acredito que há espaço para todo mundo crescer - o sucesso dos outros não diminui o meu.",
    69: "Pensar em dinheiro me gera mais ansiedade do que clareza.",
    71: "Tenho dificuldade de investir em mim mesmo quando não vejo retorno garantido.",
    72: "Me sinto à vontade para pedir o que acredito que meu trabalho vale.",
    73: "Sinto que, independente do que faço, nunca é suficiente.",
    74: "A possibilidade de perder o que já tenho me preocupa mais do que a possibilidade de ganhar algo novo.",
    75: "Quando reconheço que errei com alguém, consigo pedir desculpas diretamente, sem rodeios.",
    76: "Consigo me sentir satisfeito com meu trabalho mesmo quando ninguém comenta ou reconhece o que fiz.",
    77: "Quando vejo algo que precisa ser feito e ninguém está fazendo, costumo ser a pessoa que toma a frente.",
    78: "Consigo entregar uma tarefa importante para outra pessoa sem ficar verificando como ela está sendo feita.",
    79: "Consigo descansar sem sentir que deveria estar fazendo algo produtivo.",
    80: "Quando alguém me elogia, consigo receber sem minimizar ou desviar o assunto.",
    81: "Consigo pedir ajuda quando estou sobrecarregado, sem sentir que isso me diminui.",
    82: "Quando começo um projeto, consigo manter o interesse mesmo depois que a novidade passa.",
    83: "Quando alguém próximo tem uma conquista importante, minha reação genuína é de alegria, não de comparação.",
    84: "Quando alguém me pergunta o que eu realmente quero para minha vida, consigo responder com clareza.",
    85: "Consigo ouvir o outro numa conversa sem já estar formulando minha resposta enquanto ele fala.",
    86: "Consigo estar presente numa conversa sem que minha mente vá para o que preciso fazer depois.",
    87: "Consigo dizer não para pedidos que me sobrecarregariam, mesmo quando a pessoa vai ficar desapontada.",
    88: "Consigo dizer o que penso mesmo quando sei que vai gerar desconforto ou discordância.",
    89: "Quando alguém me pergunta sobre algo que fiz bem, consigo falar sobre isso sem diminuir o que conquistei.",
})

scale = [
    "1 - Discordo totalmente",
    "2 - Discordo",
    "3 - Neutro",
    "4 - Concordo",
    "5 - Concordo totalmente",
]

QUESTION_KEYS = sorted(questions.keys())
TOTAL = len(questions)

# =============================================================
# INVERSAO DE PONTUACAO
# =============================================================

PERGUNTAS_INVERTIDAS = {
    2, 4,
    12, 14, 16,
    23, 25, 29,
    33, 37, 39,
    43, 45, 48, 51,
    54, 57, 60, 62,
    65, 67, 69, 71, 73, 74,
}

def aplicar_inversao(q, score):
    if q in PERGUNTAS_INVERTIDAS:
        return 6 - score
    return score

# =============================================================
# PERSISTENCIA
# =============================================================

ULTIMO_TESTE_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ultimo_teste.json")

def salvar_ultimo_teste(respostas):
    try:
        data = {str(k): v for k, v in respostas.items()}
        with open(ULTIMO_TESTE_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def carregar_ultimo_teste():
    if os.path.exists(ULTIMO_TESTE_JSON):
        try:
            with open(ULTIMO_TESTE_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {int(k): v for k, v in data.items()}
        except Exception:
            pass
    return dict(ULTIMO_TESTE)

# =============================================================
# GOOGLE SHEETS LOGGING
# =============================================================

def registrar_no_sheets(dados):
    if not GSPREAD_OK:
        return False, "gspread nao instalado"
    try:
        creds_dict = dict(st.secrets.get("gcp_service_account", {}))
        if not creds_dict:
            return False, "gcp_service_account nao configurado em secrets"

        if "private_key" in creds_dict:
            pk = creds_dict["private_key"]
            if "\\n" in pk and "\n" not in pk:
                creds_dict["private_key"] = pk.replace("\\n", "\n")

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(creds)
        sheet_url = st.secrets.get("GOOGLE_SHEET_URL", "")
        if not sheet_url:
            return False, "GOOGLE_SHEET_URL nao configurado em secrets"

        import re as _re
        _match = _re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", sheet_url)
        if not _match:
            return False, "GOOGLE_SHEET_URL invalida - nao foi possivel extrair o ID"

        sheet_id = _match.group(1)
        sh = gc.open_by_key(sheet_id)
        ws = sh.sheet1
        question_keys = sorted(questions.keys())

        if ws.row_count == 0 or ws.cell(1, 1).value != "data_hora":
            cabecalho = [
                "data_hora", "modo_teste", "nome", "idade", "genero", "email",
                "Abertura", "Conscienciosidade", "Extroversao",
                "Amabilidade", "Neuroticismo", "Seguranca", "Abundancia",
                "maior_contraste", "amplitude_pct", "padroes_ativos",
                "ajustes_calibracao", "relatorio"
            ] + ["Q" + str(i) for i in question_keys]
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
            dados.get("relatorio", "")[:5000],
        ] + [dados.get("respostas", {}).get(i, "") for i in question_keys]
        ws.append_row(linha)
        return True, "ok"
    except Exception as e:
        import traceback
        tb = traceback.format_exc().replace("\n", " | ")
        return False, str(e) + " | DETALHE: " + tb


def enviar_email(destinatario, nome, relatorio_texto):
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
        "Abertura":          [1, 2, 3, 4, 5, 7, 8],
        "Conscienciosidade": [11, 12, 13, 14, 16, 17, 18, 20, 77, 78, 82, 84],
        "Extroversao":       [21, 22, 23, 24, 25, 26, 29, 30, 81, 88],
        "Amabilidade":       [31, 32, 33, 35, 36, 37, 38, 39, 75, 85, 87],
        "Neuroticismo":      [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 79, 80, 86, 89],
        "Seguranca":         [53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63],
        "Abundancia":        [64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 76, 83],
    }

    medias = {
        k: round(df[df["Q"].isin(qs)]["Score"].mean(), 2)
        for k, qs in blocos.items()
    }

    eixo_mais_alto  = max(medias, key=medias.get)
    eixo_mais_baixo = min(medias, key=medias.get)

    eixos_lista = list(medias.keys())
    diferencas = {}
    for i in range(len(eixos_lista)):
        for j in range(i + 1, len(eixos_lista)):
            e1, e2 = eixos_lista[i], eixos_lista[j]
            diferencas[e1 + "_vs_" + e2] = round(medias[e1] - medias[e2], 2)

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

    _q22 = respostas_ajustadas.get(22, 3)
    _q24 = respostas_ajustadas.get(24, 3)
    _q30 = respostas_ajustadas.get(30, 3)
    _q21 = respostas_ajustadas.get(21, 3)
    _q26 = respostas_ajustadas.get(26, 3)
    _media_formal = (_q22 + _q24 + _q30) / 3
    _media_informal = (_q21 + _q26) / 2
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
    ranking_eixos = sorted(medias.items(), key=lambda x: -x[1])
    maior_contraste_key = max(diferencas, key=lambda k: abs(diferencas[k]))
    maior_contraste_val = diferencas[maior_contraste_key]

    all_adj_vals = list(respostas_ajustadas.values())
    pct_3_4 = sum(1 for v in all_adj_vals if v in (3, 4)) / len(all_adj_vals) * 100
    alerta_amplitude = pct_3_4 > 60

    eixos_baixos = {k: v for k, v in medias.items() if v < 3.0}
    eixos_moderados = {k: v for k, v in medias.items() if 3.0 <= v < 3.5}

    raw = respostas
    scores_diagnosticos = {
        "Conscienciosidade": {
            "cumpre_compromissos_Q11": raw.get(11, 3),
            "revisa_antes_entregar_Q17": raw.get(17, 3),
            "mantem_compromissos_Q20": raw.get(20, 3),
            "tem_sistema_prioridades_Q13": raw.get(13, 3),
            "clareza_metas_longo_prazo_Q18": raw.get(18, 3),
            "toma_iniciativa_espontanea_Q77": raw.get(77, 3),
            "delega_sem_microgerenciar_Q78": raw.get(78, 3),
            "mantem_interesse_longo_prazo_Q82": raw.get(82, 3),
            "clareza_sobre_o_que_quer_Q84": raw.get(84, 3),
        },
        "Seguranca": {
            "prefere_saber_o_que_esperar_Q53": raw.get(53, 3),
            "mudancas_incomodam_Q55": raw.get(55, 3),
            "prefere_menor_garantido_Q56": raw.get(56, 3),
            "resiste_mudar_rotina_Q59": raw.get(59, 3),
            "age_sem_todas_as_informacoes_Q54": raw.get(54, 3),
            "confirma_antes_de_agir_Q63": raw.get(63, 3),
        },
        "Extroversao": {
            "energia_com_pessoas_Q21": raw.get(21, 3),
            "toma_iniciativa_grupo_Q22": raw.get(22, 3),
            "busca_pessoas_novas_Q26": raw.get(26, 3),
            "prefere_pensar_sozinho_Q23": raw.get(23, 3),
            "pede_ajuda_sem_se_diminuir_Q81": raw.get(81, 3),
            "diz_o_que_pensa_mesmo_incomodo_Q88": raw.get(88, 3),
        },
        "Amabilidade": {
            "ajuda_instintivamente_Q31": raw.get(31, 3),
            "le_emocoes_dos_outros_Q32": raw.get(32, 3),
            "fica_mal_ao_decepcionar_Q35": raw.get(35, 3),
            "pede_desculpas_Q75": raw.get(75, 3),
            "ouve_sem_formular_Q85": raw.get(85, 3),
            "consegue_dizer_nao_Q87": raw.get(87, 3),
            "cede_em_desacordos_Q33": raw.get(33, 3),
            "evita_feedback_negativo_Q37": raw.get(37, 3),
            "adia_conversas_dificeis_Q39": raw.get(39, 3),
        },
        "Neuroticismo": {
            "preocupa_com_futuro_Q44": raw.get(44, 3),
            "ansioso_sem_previsibilidade_Q49": raw.get(49, 3),
            "rumina_erros_Q52": raw.get(52, 3),
            "consegue_descansar_sem_culpa_Q79": raw.get(79, 3),
            "recebe_elogio_sem_minimizar_Q80": raw.get(80, 3),
            "presente_nas_conversas_Q86": raw.get(86, 3),
            "fala_conquistas_sem_diminuir_Q89": raw.get(89, 3),
        },
        "Abundancia": {
            "satisfeito_sem_reconhecimento_Q76": raw.get(76, 3),
            "alegria_com_conquistas_alheias_Q83": raw.get(83, 3),
            "oportunidades_limitadas_Q65": raw.get(65, 3),
            "dificuldade_investir_sem_garantia_Q71": raw.get(71, 3),
        },
    }

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
        "ranking_eixos": ranking_eixos,
        "maior_contraste_key": maior_contraste_key,
        "maior_contraste_val": maior_contraste_val,
        "eixos_baixos": eixos_baixos,
        "eixos_moderados": eixos_moderados,
        "alerta_amplitude": alerta_amplitude,
        "pct_3_4": round(pct_3_4, 1),
        "scores_diagnosticos": scores_diagnosticos,
    }

# =============================================================
# GERACAO DO RELATORIO
# =============================================================

def gerar_relatorio(perfil):
    client = get_openai_client()
    if client is None:
        return "Erro: OPENAI_API_KEY nao encontrada em Secrets.", [], []

    medias = perfil["medias"]
    intensidades = perfil["intensidades"]
    ranking_eixos = perfil["ranking_eixos"]
    maior_contraste_key = perfil["maior_contraste_key"]
    maior_contraste_val = perfil["maior_contraste_val"]
    eixos_baixos = perfil["eixos_baixos"]
    hipotese = perfil["hipotese_tecnica"]
    diag = perfil["scores_diagnosticos"]

    linhas_ranking = "\n".join([
        "  %d. %s: %.2f  [%s]" % (i + 1, k, v, intensidades[k])
        for i, (k, v) in enumerate(ranking_eixos)
    ])

    linhas_medias = "\n".join([
        "- %s: %.2f  -> %s" % (k, v, intensidades[k])
        for k, v in medias.items()
    ])

    def fmt_diag(eixo):
        items = diag.get(eixo, {})
        return "\n".join(["    %s = %d" % (k, v) for k, v in items.items()])

    eixos_baixos_str = ", ".join([
        "%s %.2f" % (k, v) for k, v in eixos_baixos.items()
    ]) if eixos_baixos else "nenhum"

    linhas_hipotese = "\n".join(["- " + h for h in hipotese])

    q_adj = perfil.get("respostas_ajustadas", {})
    q_raw = perfil.get("respostas_brutas", {})

    q33 = q_raw.get(33, 3)
    q35 = q_raw.get(35, 3)
    q37 = q_raw.get(37, 3)
    q39 = q_raw.get(39, 3)

    q11 = q_adj.get(11, 3)
    q13 = q_adj.get(13, 3)
    q16 = q_adj.get(16, 3)
    q17 = q_adj.get(17, 3)
    q18 = q_adj.get(18, 3)
    q20 = q_adj.get(20, 3)

    q21 = q_adj.get(21, 3)
    q22 = q_adj.get(22, 3)
    q24 = q_adj.get(24, 3)
    q26 = q_adj.get(26, 3)
    q29 = q_adj.get(29, 3)
    q30 = q_adj.get(30, 3)

    q3 = q_adj.get(3, 3)
    q4 = q_adj.get(4, 3)
    q7 = q_adj.get(7, 3)

    q75 = q_raw.get(75, 3)
    q76 = q_raw.get(76, 3)
    q77 = q_raw.get(77, 3)
    q78 = q_raw.get(78, 3)
    q79 = q_raw.get(79, 3)
    q80 = q_raw.get(80, 3)
    q81 = q_raw.get(81, 3)
    q82 = q_raw.get(82, 3)
    q83 = q_raw.get(83, 3)
    q84 = q_raw.get(84, 3)
    q85 = q_raw.get(85, 3)
    q86 = q_raw.get(86, 3)
    q87 = q_raw.get(87, 3)
    q88 = q_raw.get(88, 3)
    q89 = q_raw.get(89, 3)

    q65 = q_adj.get(65, 3)
    q70 = q_adj.get(70, 3)
    q71 = q_adj.get(71, 3)

    q53 = q_adj.get(53, 3)
    q55 = q_adj.get(55, 3)
    q56 = q_adj.get(56, 3)

    q44 = q_adj.get(44, 3)
    q49 = q_adj.get(49, 3)
    q52 = q_adj.get(52, 3)

    ab  = medias["Abertura"]
    co  = medias["Conscienciosidade"]
    ex  = medias["Extroversao"]
    am  = medias["Amabilidade"]
    ne  = medias["Neuroticismo"]
    se  = medias["Seguranca"]
    abu = medias["Abundancia"]

    evita_conflito = (q33 >= 4 or q37 >= 4 or q39 >= 4) and q35 >= 3

    combinacoes_ativas = []
    if ab >= 3.5 and ex < 3.5:
        combinacoes_ativas.append(
            "CURIOSIDADE INTERNA (Abertura %.2f + Extroversao %.2f): "
            "Esta pessoa tem vida intelectual rica e intensa, mas processa isso internamente. "
            "Ela explora ideias sozinha, nao em grupo. Em reunioes, parece quieta mas ja chegou com a analise pronta."
            % (ab, ex)
        )
    elif 3.0 <= ab < 3.5 and q4 <= 2 and (q3 >= 4 or q7 >= 4):
        combinacoes_ativas.append(
            "CURIOSIDADE PRATICA (Abertura %.2f): aprende para aplicar, nao por abstracao pura." % ab
        )

    if co >= 3.5 and q11 >= 4 and q17 >= 4 and q13 <= 3:
        combinacoes_ativas.append(
            "CONFIABILIDADE SEM RIGIDEZ (Conscienciosidade %.2f): entrega com qualidade mesmo sem um sistema perfeito." % co
        )
    elif co < 3.0 and q11 >= 4 and q17 >= 4 and (q13 <= 2 or q16 <= 2):
        combinacoes_ativas.append(
            "ENTREGA SOB PRESSAO SEM SISTEMA (Conscienciosidade %.2f): confiavel apesar da desorganizacao." % co
        )

    if se >= 3.5:
        combinacoes_ativas.append(
            "ORIENTACAO A CERTEZA (Seguranca %.2f): prefere operar com informacao suficiente antes de se comprometer." % se
        )
    elif 3.0 <= se < 3.5:
        combinacoes_ativas.append(
            "CAUTELA SELETIVA (Seguranca %.2f): consegue agir em incerteza, mas prefere informacao suficiente." % se
        )

    if evita_conflito:
        combinacoes_ativas.append(
            "EVITACAO DE CONFLITO SISTEMATICA: cede, adia conversas dificeis e evita feedback negativo para nao gerar tensao."
        )

    if am >= 3.5 and ex < 3.5:
        combinacoes_ativas.append(
            "CUIDADO SELETIVO (Amabilidade %.2f + Extroversao %.2f): cuida profundamente de quem esta perto, sem buscar exposicao ampla." % (am, ex)
        )
    elif am >= 3.0 and evita_conflito:
        combinacoes_ativas.append(
            "GENEROSIDADE COM CUSTO OCULTO (Amabilidade %.2f): da mais do que deveria e nem sempre estabelece limites com clareza." % am
        )

    if ne >= 3.0 and (q44 >= 4 or q49 >= 4):
        combinacoes_ativas.append(
            "ANTECIPACAO ANSIOSA (Neuroticismo %.2f): processa cenarios negativos antes que acontecam." % ne
        )

    if abu < 3.0:
        combinacoes_ativas.append(
            "RELACAO RESTRITIVA COM OPORTUNIDADE (Abundancia %.2f): hesita em pedir o que merece ou investir em si mesma sem garantia." % abu
        )
    elif 3.0 <= abu < 3.5:
        combinacoes_ativas.append(
            "ABUNDANCIA MODERADA (Abundancia %.2f): oscila entre confiar no proprio valor e duvidar dele." % abu
        )

    if ab >= 3.5 and co >= 3.5 and ex < 3.5:
        combinacoes_ativas.append(
            "PERFIL DE ESPECIALISTA PROFUNDO: explora com profundidade, entrega com qualidade e nao busca holofote."
        )

    _media_formal_ex   = (q22 + q24 + q30) / 3
    _media_informal_ex = (q21 + q26 + q_adj.get(29, 3)) / 3
    if _media_formal_ex >= 3.5 and _media_informal_ex < 3.0:
        combinacoes_ativas.append(
            "EXTROVERSAO BIMODAL: assertivo em contextos formais, reservado em contextos sociais informais."
        )

    if ex < 3.0:
        combinacoes_ativas.append(
            "PADRAO DE BAIXO IMPULSO SOCIAL: prefere baixa exposicao social e pode ser subestimada por falar menos."
        )

    linhas_combinacoes = "\n\n".join(combinacoes_ativas) if combinacoes_ativas else "Nenhuma combinacao critica identificada."

    tracos_desafios = []
    tracos_forcas = []

    _autoexigencia = sum([
        1 if q79 <= 2 else 0,
        1 if q80 <= 2 else 0,
        1 if q86 <= 2 else 0,
        1 if q89 <= 2 else 0,
    ])
    if _autoexigencia >= 3:
        tracos_desafios.append(
            "Voce exibe um padrao de autoexigencia cronica que nao desliga."
        )

    _presenca_baixa = sum([
        1 if q85 <= 2 else 0,
        1 if q86 <= 2 else 0,
    ])
    _presenca_alta = sum([
        1 if q85 >= 4 else 0,
        1 if q86 >= 4 else 0,
        1 if q75 >= 4 else 0,
    ])
    if _presenca_baixa >= 2:
        tracos_desafios.append(
            "Voce exibe um padrao de presenca relacional comprometida."
        )
    if _presenca_alta >= 2 and am >= 3.5:
        tracos_forcas.append(
            "Voce exibe um padrao de presenca relacional genuina."
        )

    _autoestima_contingente = sum([
        1 if q76 <= 2 else 0,
        1 if q83 <= 2 else 0,
        1 if q89 <= 2 else 0,
        1 if q80 <= 2 else 0,
    ])
    if _autoestima_contingente >= 3:
        tracos_desafios.append(
            "Voce exibe um padrao de autoestima contingente."
        )
    _autoestima_solida = sum([
        1 if q76 >= 4 else 0,
        1 if q83 >= 4 else 0,
        1 if q89 >= 4 else 0,
    ])
    if _autoestima_solida >= 3 and abu >= 3.0:
        tracos_forcas.append(
            "Voce exibe um padrao de autoestima solida e independente."
        )

    if q87 <= 2 and q35 >= 3:
        tracos_desafios.append(
            "Voce exibe tracos de quem tem dificuldade de dizer nao."
        )
    if q88 <= 2 and evita_conflito:
        tracos_desafios.append(
            "Voce exibe tracos de quem filtra o que pensa antes de falar."
        )
    if q88 >= 4 and not evita_conflito:
        tracos_forcas.append(
            "Voce exibe um traco incomum: diz o que pensa mesmo quando sabe que vai gerar desconforto."
        )
    if q87 >= 4 and q88 >= 4 and not evita_conflito:
        tracos_forcas.append(
            "Voce exibe um padrao de assertividade funcional completa."
        )

    _execucao_forte = sum([
        1 if q77 >= 4 else 0,
        1 if q82 >= 4 else 0,
        1 if q78 >= 4 else 0,
    ])
    _execucao_fraca = sum([
        1 if q77 <= 2 else 0,
        1 if q82 <= 2 else 0,
    ])
    if _execucao_forte >= 2 and co >= 3.0:
        tracos_forcas.append(
            "Voce exibe um padrao de iniciativa e execucao sustentada."
        )
    elif q77 >= 4 and q82 < 4 and co >= 3.0:
        tracos_forcas.append(
            "Voce exibe um traco de iniciativa espontanea."
        )
    if _execucao_fraca >= 2 and co < 3.5:
        tracos_desafios.append(
            "Voce exibe um padrao de dificuldade com iniciativa e continuidade."
        )
    if q78 <= 2 and co >= 3.5:
        tracos_desafios.append(
            "Voce exibe tracos de quem tem dificuldade de soltar o controle."
        )
    if q81 <= 2:
        tracos_desafios.append(
            "Voce exibe tracos de quem prefere se virar sozinho a pedir ajuda."
        )

    if q84 <= 2 and q18 <= 2 and ne >= 3.0:
        tracos_desafios.append(
            "Voce exibe um padrao de falta de clareza sobre o que quer."
        )
    if q84 >= 4 and q18 >= 4 and co >= 3.0:
        tracos_forcas.append(
            "Voce exibe um padrao de clareza de proposito incomum."
        )

    linhas_desafios = "\n\n".join(tracos_desafios) if tracos_desafios else ""
    linhas_forcas = "\n\n".join(tracos_forcas) if tracos_forcas else ""

    partes_tracos = []
    if tracos_forcas:
        partes_tracos.append("FORCAS COMPORTAMENTAIS IDENTIFICADAS:\n" + linhas_forcas)
    if tracos_desafios:
        partes_tracos.append("DESAFIOS COMPORTAMENTAIS IDENTIFICADOS:\n" + linhas_desafios)

    bloco_tracos = (
        "TRACOS COMPORTAMENTAIS DE ALTA CONFIANCA:\n"
        + "\n\n".join(partes_tracos)
    ) if (tracos_forcas or tracos_desafios) else ""

    ancoras_internas = []
    if maior_contraste_val >= 0.8:
        partes = maior_contraste_key.split("_vs_")
        if len(partes) == 2:
            eixo_a, eixo_b = partes[0], partes[1]
            ancoras_internas.append(
                "ANCORA OBRIGATORIA para secao 4: o contraste %s vs %s = %+.2f cria uma lacuna entre o que esta pessoa processa internamente e o que os outros percebem." % (
                    eixo_a, eixo_b, maior_contraste_val
                )
            )
    if q44 >= 4 or q49 >= 4:
        ancoras_internas.append(
            "ANCORA para secao 4: esta pessoa antecipa problemas antes que acontecam."
        )
    if evita_conflito:
        ancoras_internas.append(
            "ANCORA para secao 4: esta pessoa sabe o que pensa mas frequentemente nao diz."
        )
    linhas_ancoras = "\n".join(ancoras_internas) if ancoras_internas else ""

    passos_candidatos = []
    if evita_conflito:
        passos_candidatos.append(
            "PASSO DERIVADO DE EVITACAO DE CONFLITO: Identifique UMA situacao especifica esta semana onde voce sabe o que pensa mas nao disse. Diga."
        )
    if ab >= 3.5 and ex < 3.5:
        passos_candidatos.append(
            "PASSO DERIVADO DE CURIOSIDADE INTERNA: compartilhe uma analise que voce costuma guardar para si."
        )
    if se >= 3.0 and (q55 >= 4 or q56 >= 4):
        passos_candidatos.append(
            "PASSO DERIVADO DE CAUTELA: defina o minimo de informacao aceitavel para decidir - e decida com o que ja tem."
        )
    if ab >= 3.5 and co >= 3.5:
        passos_candidatos.append(
            "PASSO DERIVADO DE ESPECIALISTA PROFUNDO: ofereca proativamente uma analise ou recomendacao que voce ja formulou."
        )
    if ne >= 3.0 and (q44 >= 4 or q49 >= 4):
        passos_candidatos.append(
            "PASSO DERIVADO DE ANTECIPACAO ANSIOSA: escreva os 3 cenarios possiveis e a probabilidade real de cada um."
        )
    if not passos_candidatos:
        passos_candidatos.append("PASSO GERAL: use as forcas identificadas no perfil para criar visibilidade do seu trabalho esta semana.")
    linhas_passos_candidatos = "\n\n".join(passos_candidatos[:4])

    if ab >= 3.5 and co >= 3.5 and ex < 3.5:
        estilo_lideranca = (
            "ESTILO DE LIDERANCA PROVAVEL: lideranca por competencia e confiabilidade, nao por carisma."
        )
    elif ex >= 3.5 and am >= 3.5:
        estilo_lideranca = (
            "ESTILO DE LIDERANCA PROVAVEL: lideranca relacional e inspiradora."
        )
    elif co >= 3.5 and se >= 3.5:
        estilo_lideranca = (
            "ESTILO DE LIDERANCA PROVAVEL: lideranca por estrutura e previsibilidade."
        )
    elif ex < 3.0:
        estilo_lideranca = (
            "ESTILO DE LIDERANCA PROVAVEL: lideranca por influencia silenciosa e profundidade."
        )
    else:
        estilo_lideranca = (
            "ESTILO DE LIDERANCA: situacional - adapta o estilo ao contexto."
        )

    scores_extremos_linhas = ""
    if q22 <= 1:
        scores_extremos_linhas += "   - toma_iniciativa_grupo=%d (MUITO BAIXO)\n" % q22
    if q24 <= 1:
        scores_extremos_linhas += "   - porta_voz=%d (MUITO BAIXO)\n" % q24
    if q33 >= 5:
        scores_extremos_linhas += "   - cede_desacordos=%d (MUITO ALTO)\n" % q33
    if q37 >= 5:
        scores_extremos_linhas += "   - evita_feedback_negativo=%d (MUITO ALTO)\n" % q37
    if q39 >= 5:
        scores_extremos_linhas += "   - adia_conversas_dificeis=%d (MUITO ALTO)\n" % q39
    if q13 <= 1:
        scores_extremos_linhas += "   - sistema_prioridades=%d (MUITO BAIXO)\n" % q13
    if q16 <= 1:
        scores_extremos_linhas += "   - deixa_ultima_hora=%d (MUITO BAIXO)\n" % q16
    if q29 <= 1:
        scores_extremos_linhas += "   - fica_ouvindo_grupo=%d (MUITO BAIXO)\n" % q29
    if not scores_extremos_linhas:
        scores_extremos_linhas = "   Nenhum score extremo identificado.\n"

    prompt = (
        "Voce e um especialista em psicologia comportamental com profundo conhecimento em Big Five, "
        "padroes de comportamento humano e desenvolvimento de carreira. "
        "Voce vai escrever um relatorio de perfil comportamental para uma pessoa real.\n\n"

        "SUA MISSAO:\n"
        "Usar os dados do perfil abaixo para identificar e descrever padroes de comportamento "
        "que pessoas com este perfil especifico exibem.\n\n"

        "DADOS DO PERFIL (escala 1.0 a 5.0, media 3.0 = neutro):\n\n"
        "RANKING DOS EIXOS:\n"
        + linhas_ranking + "\n\n"

        "MEDIAS POR EIXO:\n"
        + linhas_medias + "\n\n"

        "MAIOR CONTRASTE DO PERFIL: " + maior_contraste_key
        + " = %+.2f" % maior_contraste_val
        + "\n\n"

        "SCORES DIAGNOSTICOS (questoes mais reveladoras por eixo - scores BRUTOS no sentido literal da pergunta):\n"
        "Conscienciosidade:\n" + fmt_diag("Conscienciosidade") + "\n"
        "Seguranca:\n" + fmt_diag("Seguranca") + "\n"
        "Extroversao:\n" + fmt_diag("Extroversao") + "\n"
        "Amabilidade:\n" + fmt_diag("Amabilidade") + "\n"
        "Neuroticismo:\n" + fmt_diag("Neuroticismo") + "\n"
        "Abundancia:\n" + fmt_diag("Abundancia") + "\n\n"

        "PERGUNTAS DE PRECISAO (Q75-Q89 - scores BRUTOS; 1=nunca/dificilmente, 5=sempre/facilmente):\n"
        "    pede_desculpas_diretamente_Q75=" + str(q75) + "\n"
        "    satisfeito_sem_reconhecimento_externo_Q76=" + str(q76) + "\n"
        "    toma_iniciativa_espontanea_Q77=" + str(q77) + "\n"
        "    delega_sem_microgerenciar_Q78=" + str(q78) + "\n"
        "    descansa_sem_culpa_Q79=" + str(q79) + "\n"
        "    recebe_elogio_sem_minimizar_Q80=" + str(q80) + "\n"
        "    pede_ajuda_sem_se_diminuir_Q81=" + str(q81) + "\n"
        "    mantem_interesse_projetos_longos_Q82=" + str(q82) + "\n"
        "    alegria_genuina_com_conquistas_alheias_Q83=" + str(q83) + "\n"
        "    clareza_sobre_o_que_quer_Q84=" + str(q84) + "\n"
        "    ouve_sem_formular_resposta_Q85=" + str(q85) + "\n"
        "    presente_nas_conversas_Q86=" + str(q86) + "\n"
        "    consegue_dizer_nao_Q87=" + str(q87) + "\n"
        "    diz_o_que_pensa_mesmo_gerando_incomodo_Q88=" + str(q88) + "\n"
        "    fala_de_conquistas_sem_diminuir_Q89=" + str(q89) + "\n\n"

        "ANALISE DAS COMBINACOES ATIVAS NESTE PERFIL:\n"
        + linhas_combinacoes + "\n\n"

        + (bloco_tracos + "\n\n" if bloco_tracos else "")
        + estilo_lideranca + "\n\n"

        "REGRAS ABSOLUTAS:\n"
        "1. Escreva sempre em 'voce'\n"
        "2. NUNCA use os nomes dos eixos no texto\n"
        "3. NUNCA use termos tecnicos como 'introversao', 'neuroticismo', 'Big Five'\n"
        "4. NUNCA invente tracos que os dados nao sustentam\n"
        "5. O texto deve soar especifico e preciso, nao generico\n\n"

        "ESTRUTURA OBRIGATORIA:\n\n"
        "1. COMO VOCÊ FUNCIONA DE VERDADE\n"
        "2. COMO VOCÊ TOMA DECISÕES\n"
        "3. COMO VOCÊ SE RELACIONA\n"
        "4. O QUE ACONTECE DENTRO DE VOCÊ\n"
        + ("ANCORAS ESPECIFICAS PARA ESTA SECAO:\n" + linhas_ancoras + "\n\n" if linhas_ancoras else "")
        + "5. ONDE VOCÊ PODE BRILHAR\n"
        "6. SUAS FORÇAS REAIS\n"
        "7. ONDE VOCÊ TRAVA\n"
        "8. O QUE VALE DESENVOLVER\n"
        "11. PRÓXIMOS PASSOS\n"
        "PASSOS CANDIDATOS DERIVADOS DOS PADROES DESTE PERFIL:\n"
        + linhas_passos_candidatos
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Voce e um analista de comportamento humano. "
                        "Voce traduz dados de perfil em leituras precisas, humanas e especificas. "
                        "Voce nao generaliza. Voce nao inventa. "
                        "Voce so escreve o que os dados sustentam."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
        )
        return response.choices[0].message.content, tracos_forcas, tracos_desafios
    except Exception as e:
        return "Erro ao gerar relatorio:\n\n" + str(e), [], []

# =============================================================
# DEBUG
# =============================================================

def render_debug(perfil):
    st.markdown("---")
    st.markdown("**Versão: V5.33**", unsafe_allow_html=False)
    st.header("Debug - Transparência Total do Perfil")
    st.caption(
        "Este painel mostra todos os dados, calculos e logica usados para gerar o relatorio."
    )

    blocos_info = {
        "Abertura":          (1, 8),
        "Conscienciosidade": (11, 84),
        "Extroversao":       (21, 88),
        "Amabilidade":       (31, 87),
        "Neuroticismo":      (42, 89),
        "Seguranca":         (53, 63),
        "Abundancia":        (64, 83),
    }

    st.subheader("1. Respostas Brutas")
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
    for par, valor in sorted(perfil["diferencas"].items(), key=lambda x: -abs(x[1])):
        direcao = "alto" if valor > 0 else ("baixo" if valor < 0 else "igual")
        marker = " <- MAIOR CONTRASTE" if par == perfil["maior_contraste_key"] else ""
        st.write("**" + par + "**: " + str(valor) + " (" + direcao + ")" + marker)

    if perfil.get("alerta_amplitude"):
        st.warning(
            "AVISO: %.1f%% das respostas sao 3 ou 4. "
            "Amplitude comprimida pode reduzir a precisao do relatorio." % perfil["pct_3_4"]
        )

    st.subheader("8. Qualidade Estatistica")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Media Geral", str(perfil["media_geral"]))
    col2.metric("Desvio Padrao", str(perfil["desvio_padrao"]))
    col3.metric("Amplitude", str(perfil["amplitude"]))
    col4.metric("Tipo Resposta", perfil["tipo_resposta"])
    col5.metric("Confiabilidade", perfil["confiabilidade"])

    st.subheader("9. Flags Automaticas")
    for flag in perfil["flags"]:
        st.write(">> " + flag)

    st.subheader("10. Hipotese Tecnica")
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
        "versao_prompt": "V5.33 - recalibrado",
    })

# =============================================================
# CALIBRACAO GUIADA
# =============================================================

def gerar_statements_calibracao(perfil):
    medias = perfil["medias"]
    adj = perfil["respostas_ajustadas"]
    raw = perfil["respostas_brutas"]

    ab  = medias["Abertura"]
    co  = medias["Conscienciosidade"]
    ex  = medias["Extroversao"]

    q11 = adj.get(11, 3)
    q17 = adj.get(17, 3)
    q20 = adj.get(20, 3)
    q22 = adj.get(22, 3)
    q24 = adj.get(24, 3)
    q26 = adj.get(26, 3)
    q33 = raw.get(33, 3)
    q35 = raw.get(35, 3)
    q37 = raw.get(37, 3)
    q39 = raw.get(39, 3)
    q44 = adj.get(44, 3)
    q49 = adj.get(49, 3)
    q55 = adj.get(55, 3)
    q56 = adj.get(56, 3)
    q61 = adj.get(61, 3)
    q63 = adj.get(63, 3)
    q59 = adj.get(59, 3)

    evita_conflito = (q33 >= 4 or q37 >= 4 or q39 >= 4) and q35 >= 3
    statements = []
    sid = 1

    if ab >= 3.5:
        statements.append({
            "id": sid, "eixo": "Abertura",
            "texto": (
                "Voce tem uma curiosidade intelectual acima da media. "
                "Quando encontra um problema ou tema novo, tende a ir fundo: pesquisa, conecta ideias, "
                "e frequentemente sabe mais sobre o assunto do que a maioria das pessoas ao seu redor."
            ),
            "followup_verdadeiro": (
                "Isso acontece em qualquer assunto, ou so em areas que voce ja tem interesse? "
                "(1 = so em areas especificas / 5 = em praticamente qualquer assunto novo)"
            ),
            "followup_falso": (
                "Voce prefere aplicar o que ja sabe em vez de explorar areas novas? "
                "(1 = prefiro muito o que ja sei / 5 = tenho curiosidade mas so em temas especificos)"
            ),
            "ajuste_mais_forte": {1: 1, 3: 1, 8: 1},
            "ajuste_mais_fraco": {1: -1, 3: -1, 8: -1},
        })
        sid += 1

    if q11 >= 3 and q17 >= 3 and q20 >= 3:
        statements.append({
            "id": sid, "eixo": "Conscienciosidade",
            "texto": (
                "Quando voce assume um compromisso, cumpre - mesmo quando nao esta com vontade, "
                "mesmo quando o prazo aperta."
            ),
            "followup_verdadeiro": (
                "Voce cumpre porque tem um sistema claro ou porque se sente responsavel mesmo sem sistema? "
                "(1 = tenho sistema claro / 5 = cumpro mesmo sem sistema, no esforco)"
            ),
            "followup_falso": (
                "Voce cumpre compromissos em algumas areas mas nao em outras? "
                "(1 = sou bem menos confiavel / 5 = sou confiavel mas so em certas areas)"
            ),
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
                "Isso e uma preferencia ou grupos grandes te custam energia real? "
                "(1 = apenas preferencia / 5 = custa energia real)"
            ),
            "followup_falso": (
                "Voce toma iniciativa em grupos com frequencia? "
                "(1 = tomo iniciativa com frequencia / 5 = tenho lideranca mas ela e silenciosa)"
            ),
            "ajuste_mais_forte": {22: -1, 24: -1, 26: -1},
            "ajuste_mais_fraco": {22: 1, 24: 1, 26: 1},
        })
        sid += 1

    if evita_conflito:
        statements.append({
            "id": sid, "eixo": "Amabilidade",
            "texto": (
                "Quando ha tensao ou desacordo, voce tende a ceder ou guardar o que pensa "
                "em vez de confrontar diretamente."
            ),
            "followup_verdadeiro": (
                "Isso acontece em todas as relacoes ou so com pessoas especificas? "
                "(1 = so com pessoas de autoridade / 5 = em praticamente todas as relacoes)"
            ),
            "followup_falso": (
                "Voce consegue confrontar quando necessario? "
                "(1 = sou direto / 5 = consigo confrontar mas prefiro evitar)"
            ),
            "ajuste_mais_forte": {33: 1, 37: 1, 39: 1},
            "ajuste_mais_fraco": {33: -1, 37: -1, 39: -1},
        })
        sid += 1

    if q44 >= 3 or q49 >= 3:
        statements.append({
            "id": sid, "eixo": "Neuroticismo",
            "texto": (
                "Voce tende a antecipar problemas antes que eles acontecam."
            ),
            "followup_verdadeiro": (
                "Essa antecipacao te paralisa ou te prepara? (1 = paralisa / 5 = prepara)"
            ),
            "followup_falso": (
                "Voce e mais calmo do que descrito? (1 = muito mais calmo / 5 = a descricao so exagerou)"
            ),
            "ajuste_mais_forte": {44: 1, 49: 1},
            "ajuste_mais_fraco": {44: -1, 49: -1},
        })
        sid += 1

    if q56 >= 3 or q61 >= 3 or q63 >= 3:
        statements.append({
            "id": sid, "eixo": "Cautela e Risco",
            "texto": (
                "Quando precisa tomar uma decisao importante, voce prefere esperar ter informacao suficiente antes de se comprometer."
            ),
            "followup_verdadeiro": (
                "Essa cautela ja te fez perder oportunidades? (1 = raramente / 5 = ja perdi oportunidades claras)"
            ),
            "followup_falso": (
                "Voce age com mais facilidade mesmo sem todas as informacoes? (1 = ajo rapido / 5 = a descricao so exagerou)"
            ),
            "ajuste_mais_forte": {56: 1, 61: 1, 63: 1},
            "ajuste_mais_fraco": {56: -1, 61: -1, 63: -1},
        })
        sid += 1

    if q55 >= 3:
        statements.append({
            "id": sid, "eixo": "Reatividade a Mudancas",
            "texto": (
                "Quando seus planos mudam de forma inesperada, voce tende a se incomodar mais do que a maioria."
            ),
            "followup_verdadeiro": (
                "Isso acontece em qualquer mudanca ou so em areas importantes? (1 = so em areas importantes / 5 = quase sempre)"
            ),
            "followup_falso": (
                "Voce lida bem com mudancas? (1 = me adapto facilmente / 5 = a descricao so exagerou)"
            ),
            "ajuste_mais_forte": {55: 1},
            "ajuste_mais_fraco": {55: -1},
        })
        sid += 1

    if q59 >= 3:
        statements.append({
            "id": sid, "eixo": "Preferencia por Rotina",
            "texto": (
                "Quando voce encontra uma rotina que funciona, tende a mante-la - mesmo quando ha opcoes melhores."
            ),
            "followup_verdadeiro": (
                "Essa preferencia se aplica a todas as areas? (1 = so algumas / 5 = quase todas)"
            ),
            "followup_falso": (
                "Voce muda de rotina com facilidade quando ve algo melhor? (1 = mudo facilmente / 5 = a descricao so exagerou)"
            ),
            "ajuste_mais_forte": {59: 1},
            "ajuste_mais_fraco": {59: -1},
        })
        sid += 1

    if ab >= 3.5 and co >= 3.5:
        statements.append({
            "id": sid, "eixo": "Lideranca",
            "texto": (
                "Voce tem tracos de lideranca - mas do tipo silencioso, por competencia e confiabilidade."
            ),
            "followup_verdadeiro": (
                "Voce ja liderou informalmente sem o titulo? (1 = nunca / 5 = frequentemente)"
            ),
            "followup_falso": (
                "Voce se ve mais como seguidor do que lider? (1 = claramente sim / 5 = nao, so descreveu errado)"
            ),
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

col_logo, col_title = st.columns([1, 5])
with col_logo:
    try:
        st.image("logo_mindinsight.png", width=220)
    except Exception:
        st.write("")
with col_title:
    st.markdown("<h1 style='margin-bottom:0'>Mind Insight™</h1>", unsafe_allow_html=True)
    if MODO_TESTE:
        st.markdown(
            '<div class="manus-badge">V5.33 | Criado com Claude (Anthropic) | Aperfeiçoado por Manus AI | MODO TESTE ATIVO</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="manus-badge">Análise comportamental potencializada por psicologia científica e inteligência artificial avançada</div>',
            unsafe_allow_html=True
        )

if not st.session_state.modo_selecionado:
    if MODO_TESTE:
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
                    "Serão usadas as respostas da sua última sessão calibrada."
                )
            else:
                st.caption(
                    "Serão usadas as respostas de referência."
                )
            if st.button("Usar último teste", key="btn_ultimo"):
                st.session_state.responses = carregar_ultimo_teste()
                st.session_state.current_question = TOTAL + 1
                st.session_state.modo_selecionado = True
                st.rerun()

        with col_b:
            st.markdown("**Responder o questionário novamente**")
            st.caption(
                "Responde todas as " + str(TOTAL) + " perguntas do zero."
            )
            if st.button("Responder questionário", key="btn_novo"):
                st.session_state.responses = {}
                st.session_state.current_question = 1
                st.session_state.modo_selecionado = True
                st.rerun()

    else:
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
            st.session_state.responses = {}
            st.session_state.current_question = 1
            st.session_state.modo_selecionado = True
            st.rerun()

elif st.session_state.current_question <= TOTAL:
    idx = st.session_state.current_question - 1
    q_num = QUESTION_KEYS[idx]
    progresso = (st.session_state.current_question - 1) / TOTAL
    st.progress(progresso)
    st.caption("Pergunta " + str(st.session_state.current_question) + " de " + str(TOTAL) + "  |  Q" + str(q_num))
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

elif not st.session_state.calibracao_completa:
    if st.session_state.perfil_cache is None:
        st.session_state.perfil_cache = gerar_perfil(st.session_state.responses)
    if not st.session_state.calibracao_statements:
        st.session_state.calibracao_statements = gerar_statements_calibracao(st.session_state.perfil_cache)

    statements = st.session_state.calibracao_statements

    st.title("Verificação Rápida do Perfil")
    st.markdown(
        "Antes de gerar seu relatório completo, preciso confirmar se as afirmações abaixo "
        "descrevem você com precisão. Isso ajuda a tornar o relatório final mais fiel a quem você realmente é."
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
            respostas_para_salvar = aplicar_ajustes_calibracao(
                st.session_state.responses, ajustes_acumulados
            ) if ajustes_acumulados else dict(st.session_state.responses)
            salvar_ultimo_teste(respostas_para_salvar)
            st.session_state.calibracao_completa = True
            st.rerun()
    else:
        st.warning("Por favor, responda todas as afirmacoes acima para continuar.")

else:
    st.title("Seu Relatório de Perfil")
    if MODO_TESTE:
        st.caption("Versão: V5.33 | MODO TESTE ATIVO")

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
        relatorio_ai, tracos_forcas_exib, tracos_desafios_exib = gerar_relatorio(perfil)

    secao10_partes = []
    if tracos_forcas_exib:
        linhas_f = []
        for t in tracos_forcas_exib:
            linhas = t.split("\n", 1)
            titulo = linhas[0].strip()
            descricao = linhas[1].strip() if len(linhas) > 1 else ""
            linhas_f.append("**" + titulo + "**  \n" + descricao)
        secao10_partes.append("### O QUE TE FORTALECE\n\n" + "\n\n".join(linhas_f))
    if tracos_desafios_exib:
        linhas_d = []
        for t in tracos_desafios_exib:
            linhas = t.split("\n", 1)
            titulo = linhas[0].strip()
            descricao = linhas[1].strip() if len(linhas) > 1 else ""
            linhas_d.append("**" + titulo + "**  \n" + descricao)
        secao10_partes.append("### O QUE TE DESAFIA\n\n" + "\n\n".join(linhas_d))

    if secao10_partes:
        secao10_bloco = "\n\n## 10. TRAÇOS COMPORTAMENTAIS IDENTIFICADOS\n\n" + "\n\n".join(secao10_partes)
        if "11." in relatorio_ai or "PRÓXIMOS PASSOS" in relatorio_ai.upper():
            import re
            relatorio = re.sub(
                r'(##?\s*1[01]\.\s*PR[OÓ]XIMOS PASSOS)',
                secao10_bloco + "\n\n" + r'\1',
                relatorio_ai,
                count=1,
                flags=re.IGNORECASE
            )
            if relatorio == relatorio_ai:
                relatorio = relatorio_ai + secao10_bloco
        else:
            relatorio = relatorio_ai + secao10_bloco
    else:
        relatorio = relatorio_ai

    st.markdown(relatorio)

    if MODO_TESTE:
        render_debug(perfil)

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
                st.info("[DEBUG] Registro no Google Sheets: OK — VERSAO V5.33 ATIVA")
            else:
                st.error("[DEBUG] Erro no Google Sheets: " + str(msg_sheets) + " — VERSAO V5.33 ATIVA")
        if not MODO_TESTE:
            nome_usuario = user_info.get("nome", "")
            email_usuario = user_info.get("email", "")
            if email_usuario:
                ok_email, _ = enviar_email(email_usuario, nome_usuario, relatorio)
                if ok_email:
                    st.success(
                        "Uma cópia do seu relatório foi enviada para **" + email_usuario + "**. "
                        "Verifique sua caixa de entrada (ou spam)."
                    )
        st.session_state.dados_registrados = True

    st.markdown("---")

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
            help="Baixe este arquivo e adicione ao seu repositorio GitHub junto com o app.py."
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
