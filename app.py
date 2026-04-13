
# -*- coding: utf-8 -*-

# =============================================================
# MIND INSIGHT ADVANCED AI
# Version: V7
# Criado com: Claude (Anthropic)
# Aperfeiçoado por: Manus AI
# Reestruturado para inferência comportamental profunda com impacto psicológico
#
# V7 - Integração de profundidade + amplitude + impacto psicológico
#      - Mantém toda a estrutura do app intacta
#      - OpenAI corrigido via st.secrets / variável de ambiente
#      - Padrões com peso e prioridade narrativa
#      - Tensões internas com peso e contexto
#      - Camada separada de comportamentos dominantes
#      - Follow-ups usados como desempate real de interpretação
#      - Compressão de respostas modula o tom do relatório
#      - Relatório multidimensional: profundidade sem reducionismo
#
# V6.0 - Nova engine de inferência comportamental
#      - Mantém Google Sheets, email, modo teste e debug
#      - Q75-Q89 permanecem NÃO invertidas
#      - Q84 em Conscienciosidade
#      - Q88 em Extroversao / Assertividade
#      - Camada nova de variáveis derivadas
#      - Camada nova de padrões comportamentais
#      - Camada nova de tensões internas
#      - Follow-up adaptativo de até 3 perguntas
#      - Prompt da IA passa a receber inferências, não apenas eixos
# =============================================================

import streamlit as st
import json
import os
import pandas as pd
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI, AuthenticationError

APP_VERSION = "V7"
MODEL_NAME = "gpt-5.4"

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
    1: 4, 2: 2, 3: 4, 4: 2, 5: 4, 7: 4, 8: 4,
    11: 4, 12: 2, 13: 3, 14: 2, 16: 3, 17: 4, 18: 3, 20: 4,
    21: 3, 22: 3, 23: 3, 24: 3, 25: 3, 26: 3, 29: 3, 30: 3,
    31: 4, 32: 4, 33: 3, 35: 4, 36: 3, 37: 3, 38: 4, 39: 3,
    42: 3, 43: 3, 44: 4, 45: 3, 46: 3, 47: 3, 48: 3, 49: 4, 50: 3, 51: 3, 52: 3,
    53: 4, 54: 4, 55: 4, 56: 4, 57: 3, 58: 3, 59: 4, 60: 3, 61: 4, 62: 3, 63: 4,
    64: 4, 65: 2, 66: 3, 67: 3, 68: 4, 69: 3, 70: 3, 71: 3, 72: 3, 73: 3, 74: 3,
    75: 3, 76: 3, 77: 3, 78: 3, 79: 3, 80: 2, 81: 3, 82: 3, 83: 4, 84: 3,
    85: 3, 86: 3, 87: 3, 88: 3, 89: 2,
}


# =============================================================
# CONFIG
# =============================================================

st.set_page_config(
    page_title="Mind Insight",
    page_icon="🧠",
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
.small-note {
    font-size: 0.85rem;
    color: #666;
}
</style>
""", unsafe_allow_html=True)


# =============================================================
# OPENAI CLIENT
# =============================================================

def get_openai_client():
    api_key = st.secrets.get("OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    api_key = api_key.strip() if isinstance(api_key, str) else ""
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


# =============================================================
# SESSION STATE
# =============================================================

DEFAULTS = {
    "responses": {},
    "user_info": {},
    "user_info_completo": False,
    "relatorio_gerado": "",
    "dados_registrados": False,
    "current_question": 0,
    "modo_selecionado": False,
    "calibracao_completa": False,
    "calibracao_statements": [],
    "calibracao_respostas": {},
    "calibracao_followup": {},
    "calibracao_ajustes": {},
    "perfil_cache": None,
    "followup_questions": [],
    "followup_answers": {},
    "followup_completo": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


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
    q: txt.replace("solucoes", "soluções").replace("nao", "não").replace("filosoficas", "filosóficas").replace("conexoes", "conexões").replace("opiniao", "opinião").replace("areas", "áreas").replace("dominio", "domínio").replace("Comeco", "Começo")
    for q, txt in questions.items()
}
# ajustes finos manuais
questions_display[11] = "Quando assumo um compromisso, cumpro - mesmo quando não tenho mais vontade."
questions_display[12] = "Começo tarefas importantes só quando estou com disposição para isso."
questions_display[13] = "Tenho um sistema claro para organizar minhas prioridades do dia."
questions_display[14] = "Deixo para decidir na hora em vez de planejar com antecedência."
questions_display[16] = "Frequentemente percebo que deixei algo importante para a última hora."
questions_display[17] = "Reviso meu trabalho antes de entregar, mesmo quando estou confiante."
questions_display[18] = "Tenho clareza sobre o que precisa ser feito hoje para chegar onde quero em um ano."
questions_display[20] = "Mantenho meus compromissos mesmo quando surgem opções mais atraentes."
questions_display[21] = "Me sinto com mais energia depois de passar tempo com pessoas do que antes."
questions_display[24] = "Me sinto confortável sendo o porta-voz de um grupo em situações formais."
questions_display[31] = "Quando alguém está passando por algo difícil, meu primeiro instinto é ajudar."
questions_display[32] = "Tenho facilidade para identificar como o outro está se sentindo, mesmo sem ele dizer."
questions_display[35] = "Fico desconfortável quando percebo que decepcionei alguém."
questions_display[36] = "Consigo discordar de alguém sem que isso afete a relação."
questions_display[38] = "Confio nas pessoas até que me provem o contrário."
questions_display[42] = "Quando algo dá errado, fico remoendo o que aconteceu por horas ou dias."
questions_display[43] = "Me recupero emocionalmente rápido depois de situações difíceis."
questions_display[44] = "Frequentemente me preocupo com coisas que ainda não aconteceram."
questions_display[45] = "Consigo manter a calma em situações de pressão alta."
questions_display[46] = "Pequenos contratempos do dia me afetam mais do que deveriam."
questions_display[47] = "Quando estou sob estresse, minha capacidade de tomar decisões piora visivelmente."
questions_display[48] = "Me sinto estável emocionalmente na maior parte do tempo."
questions_display[49] = "Fico ansioso quando não sei o que esperar de uma situação."
questions_display[50] = "Críticas, mesmo construtivas, me afetam emocionalmente por um tempo."
questions_display[51] = "Consigo separar o que sinto do que preciso fazer, mesmo em momentos difíceis."
questions_display[52] = "Quando cometo um erro, fico muito mais tempo me cobrando do que a situação justificaria."
questions_display[53] = "Me sinto mais confortável quando sei exatamente o que esperar de uma situação."
questions_display[54] = "Consigo agir com confiança mesmo quando não tenho todas as informações."
questions_display[55] = "Mudanças inesperadas nos meus planos me deixam mais incomodado do que a maioria."
questions_display[57] = "Me sinto bem entrando em situações onde não sei exatamente o que vai acontecer."
questions_display[58] = "Demoro para confiar em pessoas ou ambientes novos."
questions_display[59] = "Quando estou numa rotina que funciona, resisto a mudar mesmo que haja opções melhores."
questions_display[60] = "Consigo me comprometer com algo antes de ter certeza absoluta de que vai dar certo."
questions_display[61] = "Sinto desconforto real quando preciso tomar decisões sem um plano claro."
questions_display[62] = "Me sinto seguro mesmo em fases de transição ou incerteza na minha vida."
questions_display[63] = "Prefiro confirmar os detalhes antes de agir do que improvisar no momento."
questions_display[64] = "Quando vejo alguém bem-sucedido, meu primeiro pensamento é de inspiração, não de comparação."
questions_display[65] = "Sinto que as oportunidades disponíveis para mim são limitadas."
questions_display[66] = "Consigo gastar dinheiro em algo que vale a pena sem sentir culpa depois."
questions_display[67] = "Frequentemente sinto que estou ficando para trás em relação a onde deveria estar."
questions_display[68] = "Acredito que há espaço para todo mundo crescer - o sucesso dos outros não diminui o meu."
questions_display[69] = "Pensar em dinheiro me gera mais ansiedade do que clareza."
questions_display[71] = "Tenho dificuldade de investir em mim mesmo quando não vejo retorno garantido."
questions_display[72] = "Me sinto à vontade para pedir o que acredito que meu trabalho vale."
questions_display[73] = "Sinto que, independente do que faço, nunca é suficiente."
questions_display[74] = "A possibilidade de perder o que já tenho me preocupa mais do que a possibilidade de ganhar algo novo."
questions_display[75] = "Quando reconheço que errei com alguém, consigo pedir desculpas diretamente, sem rodeios."
questions_display[76] = "Consigo me sentir satisfeito com meu trabalho mesmo quando ninguém comenta ou reconhece o que fiz."
questions_display[77] = "Quando vejo algo que precisa ser feito e ninguém está fazendo, costumo ser a pessoa que toma a frente."
questions_display[78] = "Consigo entregar uma tarefa importante para outra pessoa sem ficar verificando como ela está sendo feita."
questions_display[79] = "Consigo descansar sem sentir que deveria estar fazendo algo produtivo."
questions_display[80] = "Quando alguém me elogia, consigo receber sem minimizar ou desviar o assunto."
questions_display[81] = "Consigo pedir ajuda quando estou sobrecarregado, sem sentir que isso me diminui."
questions_display[82] = "Quando começo um projeto, consigo manter o interesse mesmo depois que a novidade passa."
questions_display[83] = "Quando alguém próximo tem uma conquista importante, minha reação genuína é de alegria, não de comparação."
questions_display[84] = "Quando alguém me pergunta o que eu realmente quero para minha vida, consigo responder com clareza."
questions_display[85] = "Consigo ouvir o outro numa conversa sem já estar formulando minha resposta enquanto ele fala."
questions_display[86] = "Consigo estar presente numa conversa sem que minha mente vá para o que preciso fazer depois."
questions_display[87] = "Consigo dizer não para pedidos que me sobrecarregariam, mesmo quando a pessoa vai ficar desapontada."
questions_display[88] = "Consigo dizer o que penso mesmo quando sei que vai gerar desconforto ou discordância."
questions_display[89] = "Quando alguém me pergunta sobre algo que fiz bem, consigo falar sobre isso sem diminuir o que conquistei."

QUESTION_KEYS = sorted(questions.keys())
TOTAL = len(QUESTION_KEYS)

scale = [
    "1 - Discordo totalmente",
    "2 - Discordo",
    "3 - Neutro",
    "4 - Concordo",
    "5 - Concordo totalmente",
]


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
    return 6 - score if q in PERGUNTAS_INVERTIDAS else score


# =============================================================
# PERSISTENCIA
# =============================================================

ULTIMO_TESTE_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ultimo_teste.json")

def salvar_ultimo_teste(respostas):
    try:
        data = {str(k): v for k, v in respostas.items()}
        with open(ULTIMO_TESTE_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def carregar_ultimo_teste():
    if os.path.exists(ULTIMO_TESTE_JSON):
        try:
            with open(ULTIMO_TESTE_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {int(k): v for k, v in data.items()}
        except Exception:
            pass
    return dict(ULTIMO_TESTE)


# =============================================================
# GOOGLE SHEETS
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

        if ws.row_count == 0 or ws.cell(1, 1).value != "data_hora":
            cabecalho = [
                "data_hora", "modo_teste", "nome", "idade", "genero", "email",
                "Abertura", "Conscienciosidade", "Extroversao",
                "Amabilidade", "Neuroticismo", "Seguranca", "Abundancia",
                "maior_contraste", "amplitude_pct", "padroes_ativos",
                "tensoes_ativas", "followups", "ajustes_calibracao", "relatorio"
            ] + ["Q" + str(i) for i in QUESTION_KEYS]
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
            dados.get("tensoes_ativas", ""),
            dados.get("followups", ""),
            dados.get("ajustes_calibracao", ""),
            dados.get("relatorio", "")[:5000],
        ] + [dados.get("respostas", {}).get(i, "") for i in QUESTION_KEYS]

        ws.append_row(linha)
        return True, "ok"
    except Exception as e:
        return "Erro ao gerar relatorio:\n\n" + str(e), bloco_forcas, bloco_desafios
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
        return "Erro ao gerar relatorio:\n\n" + str(e), bloco_forcas, bloco_desafios
        return False, str(e)


# =============================================================
# FOLLOW-UPS ADAPTATIVOS
# =============================================================

def gerar_followups(perfil):
    medias = perfil["medias"]
    brutas = perfil["respostas_brutas"]
    perguntas = []

    ex = medias["Extroversao"]
    am = medias["Amabilidade"]
    se = medias["Seguranca"]
    abu = medias["Abundancia"]

    q33 = brutas.get(33, 3)
    q37 = brutas.get(37, 3)
    q39 = brutas.get(39, 3)
    q88 = brutas.get(88, 3)
    q80 = brutas.get(80, 3)
    q89 = brutas.get(89, 3)

    if 2.8 <= ex <= 3.2:
        perguntas.append({
            "id": "posicionamento_social",
            "pergunta": "Quando você discorda de alguém, o que acontece com mais frequência?",
            "opcoes": [
                "Falo de forma direta e tranquila",
                "Ajusto a forma para evitar atrito, mas digo",
                "Adio ou evito para não criar tensão",
                "Depende muito da pessoa e do contexto",
            ],
        })

    if (q33 >= 4 or q37 >= 4 or q39 >= 4) and q88 <= 3:
        perguntas.append({
            "id": "natureza_conflito",
            "pergunta": "Quando você evita confronto, isso acontece mais por:",
            "opcoes": [
                "Estratégia - acho desnecessário em muitos casos",
                "Desconforto real com tensão ou desaprovação",
                "Medo de prejudicar a relação",
                "Não sei - só percebo que evito",
            ],
        })

    if q80 <= 2 or q89 <= 2:
        perguntas.append({
            "id": "reconhecimento",
            "pergunta": "Quando alguém reconhece algo que você fez bem, sua reação mais natural é:",
            "opcoes": [
                "Recebo bem e sigo em frente",
                "Agradeço, mas minimizo por hábito",
                "Fico desconfortável e tento mudar de assunto",
                "Sinto que talvez a pessoa esteja exagerando",
            ],
        })

    if se >= 3.3 and abu <= 3.4:
        perguntas.append({
            "id": "risco_expansao",
            "pergunta": "Quando surge uma oportunidade boa, mas com incerteza, você tende a:",
            "opcoes": [
                "Agir se o upside parecer claro",
                "Esperar informação suficiente antes de agir",
                "Permanecer no que já funciona",
                "Oscilar bastante antes de decidir",
            ],
        })

    return perguntas[:3]


# =============================================================
# ENGINE DE CÁLCULO
# =============================================================

BLOCOS = {
    "Abertura":          [1, 2, 3, 4, 5, 7, 8],
    "Conscienciosidade": [11, 12, 13, 14, 16, 17, 18, 20, 77, 78, 82, 84],
    "Extroversao":       [21, 22, 23, 24, 25, 26, 29, 30, 81, 88],
    "Amabilidade":       [31, 32, 33, 35, 36, 37, 38, 39, 75, 85, 87],
    "Neuroticismo":      [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 79, 80, 86, 89],
    "Seguranca":         [53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63],
    "Abundancia":        [64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 76, 83],
}

def compute_derived_variables(medias, raw, adjusted, followup_answers=None):
    followup_answers = followup_answers or {}

    # Base comportamental
    auto_reconhecimento = round((raw.get(80, 3) + raw.get(89, 3) + raw.get(76, 3)) / 3, 2)
    assertividade = round((raw.get(87, 3) + raw.get(88, 3) + adjusted.get(36, 3) + adjusted.get(30, 3)) / 4, 2)
    tolerancia_risco = round((adjusted.get(54, 3) + adjusted.get(57, 3) + adjusted.get(60, 3) + adjusted.get(62, 3)) / 4, 2)
    presenca_relacional = round((raw.get(85, 3) + raw.get(86, 3) + raw.get(75, 3)) / 3, 2)
    impulso_social = round((adjusted.get(21, 3) + adjusted.get(22, 3) + adjusted.get(24, 3) + adjusted.get(26, 3)) / 4, 2)
    autoexigencia = round(((6 - raw.get(79, 3)) + (6 - raw.get(80, 3)) + (6 - raw.get(89, 3))) / 3, 2)
    visibilidade_pessoal = round((adjusted.get(30, 3) + raw.get(88, 3) + raw.get(89, 3)) / 3, 2)
    evita_conflito = round((raw.get(33, 3) + raw.get(37, 3) + raw.get(39, 3)) / 3, 2)
    autonomia_execucao = round((raw.get(77, 3) + raw.get(82, 3) + adjusted.get(11, 3) + adjusted.get(17, 3)) / 4, 2)

    # Ajustes pelos follow-ups
    if followup_answers.get("posicionamento_social") == "Falo de forma direta e tranquila":
        assertividade = min(5.0, round(assertividade + 0.35, 2))
        visibilidade_pessoal = min(5.0, round(visibilidade_pessoal + 0.20, 2))
    elif followup_answers.get("posicionamento_social") == "Adio ou evito para não criar tensão":
        assertividade = max(1.0, round(assertividade - 0.40, 2))
        evita_conflito = min(5.0, round(evita_conflito + 0.35, 2))

    if followup_answers.get("natureza_conflito") == "Desconforto real com tensão ou desaprovação":
        evita_conflito = min(5.0, round(evita_conflito + 0.40, 2))
    elif followup_answers.get("natureza_conflito") == "Estratégia - acho desnecessário em muitos casos":
        evita_conflito = max(1.0, round(evita_conflito - 0.20, 2))

    if followup_answers.get("reconhecimento") == "Fico desconfortável e tento mudar de assunto":
        auto_reconhecimento = max(1.0, round(auto_reconhecimento - 0.45, 2))
        visibilidade_pessoal = max(1.0, round(visibilidade_pessoal - 0.25, 2))
    elif followup_answers.get("reconhecimento") == "Agradeço, mas minimizo por hábito":
        auto_reconhecimento = max(1.0, round(auto_reconhecimento - 0.20, 2))
    elif followup_answers.get("reconhecimento") == "Recebo bem e sigo em frente":
        auto_reconhecimento = min(5.0, round(auto_reconhecimento + 0.20, 2))

    if followup_answers.get("risco_expansao") == "Permanecer no que já funciona":
        tolerancia_risco = max(1.0, round(tolerancia_risco - 0.30, 2))
    elif followup_answers.get("risco_expansao") == "Agir se o upside parecer claro":
        tolerancia_risco = min(5.0, round(tolerancia_risco + 0.20, 2))

    return {
        "auto_reconhecimento": auto_reconhecimento,
        "assertividade": assertividade,
        "tolerancia_risco": tolerancia_risco,
        "presenca_relacional": presenca_relacional,
        "impulso_social": impulso_social,
        "autoexigencia": autoexigencia,
        "visibilidade_pessoal": visibilidade_pessoal,
        "evita_conflito": evita_conflito,
        "autonomia_execucao": autonomia_execucao,
    }


PATTERN_LIBRARY = {
    "merito_subcomunicado": {
        "peso": 9,
        "tipo": "central",
        "insight": "Você entrega mais do que projeta.",
        "descricao": "Seu valor real aparece na qualidade e na constância, mas nem sempre vira presença percebida na mesma proporção.",
        "custo": "Reconhecimento, influência e timing de oportunidade podem ficar abaixo do seu mérito real."
    },
    "clareza_interna_maior_que_presenca": {
        "peso": 8,
        "tipo": "central",
        "insight": "Sua vida mental pode ser maior do que sua presença externa deixa transparecer.",
        "descricao": "Você processa, conecta e formula mais do que costuma externalizar com a mesma intensidade.",
        "custo": "Os outros podem perceber menos profundidade do que de fato existe."
    },
    "prudencia_funcional": {
        "peso": 8,
        "tipo": "decisao",
        "insight": "Você prefere consistência suficiente antes de expandir.",
        "descricao": "Seu sistema não gosta de se mover no vazio; ele busca um nível mínimo de clareza antes de avançar.",
        "custo": "Você pode chegar um pouco tarde em movimentos que exigem ação antes da certeza total."
    },
    "execucao_consistente": {
        "peso": 7,
        "tipo": "forca",
        "insight": "Você mantém padrão mesmo sem depender de clima ideal.",
        "descricao": "Seu funcionamento não precisa de empolgação alta para sustentar responsabilidade.",
        "custo": "Pode carregar mais do que deveria porque confia que vai dar conta."
    },
    "economia_de_extremos": {
        "peso": 7,
        "tipo": "modulador",
        "insight": "Você tende a responder e decidir com moderação e controle.",
        "descricao": "Seu perfil mostra baixa escolha de extremos, o que pode indicar equilíbrio, cautela ou economia de posicionamento.",
        "custo": "A leitura da sua identidade pode ficar menos nítida do que sua vida interna realmente é."
    },
    "exposicao_seletiva": {
        "peso": 8,
        "tipo": "social",
        "insight": "Sua exposição é contextual, não uniforme.",
        "descricao": "Você não aparece do mesmo jeito em todos os ambientes; sua presença depende de assunto, segurança relacional e contexto.",
        "custo": "Pode ser lido de forma inconsistente por quem vê apenas uma parte do seu comportamento."
    },
    "evita_atrito_contextual": {
        "peso": 7,
        "tipo": "relacional",
        "insight": "Você mede o custo do atrito antes de se posicionar.",
        "descricao": "Nem toda contenção é medo; em muitos contextos, você calcula se vale a pena abrir fricção.",
        "custo": "Quando exagerado, isso reduz clareza e atrasa conversas necessárias."
    },
    "competencia_nao_internalizada": {
        "peso": 8,
        "tipo": "interno",
        "insight": "Você faz bem, mas nem sempre transforma isso em senso interno de mérito.",
        "descricao": "Sua entrega pode crescer mais rápido do que a forma como você ocupa internamente suas próprias conquistas.",
        "custo": "Você pode depender de validação externa mesmo tendo base real para confiança."
    },
    "presenca_relacional_rara": {
        "peso": 6,
        "tipo": "forca",
        "insight": "Você consegue estar inteiro com o outro.",
        "descricao": "Sua escuta, presença e reparação relacional caminham juntas.",
        "custo": "Em excesso, pode dar mais espaço emocional ao outro do que a si mesmo."
    },
    "autoexpressao_reduzida": {
        "peso": 7,
        "tipo": "social",
        "insight": "Sua qualidade não vira linguagem com a mesma força.",
        "descricao": "Você pode ter boa substância interna, mas baixa ocupação verbal do próprio mérito.",
        "custo": "Seu valor fica claro para quem convive de perto, mas menos nítido para quem decide oportunidades."
    },
}

TENSION_LIBRARY = {
    "valor_real_vs_presenca_percebida": {
        "peso": 9,
        "texto": "Você constrói valor real com mais consistência do que o transforma em percepção externa proporcional."
    },
    "seguranca_vs_expansao": {
        "peso": 8,
        "texto": "Seu impulso por segurança compete com oportunidades que exigem movimento antes da certeza total."
    },
    "complexidade_interna_vs_expressao_externa": {
        "peso": 8,
        "texto": "Sua complexidade interna pode ser maior do que a sua expressão externa deixa visível."
    },
    "adaptacao_social_vs_clareza_de_posicao": {
        "peso": 7,
        "texto": "Sua habilidade de adaptar a forma pode, em alguns momentos, reduzir a nitidez da sua posição real."
    },
    "solidez_externa_vs_merito_interno": {
        "peso": 8,
        "texto": "Por fora você pode parecer sólido, mas por dentro tratar o próprio mérito com economia injusta."
    },
    "funcionalidade_social_vs_busca_de_palco": {
        "peso": 6,
        "texto": "Você pode funcionar bem socialmente sem buscar exposição como fonte de energia ou identidade."
    },
}

BEHAVIOR_LIBRARY = {
    "merito_subcomunicado": "Entrega valor consistente, mas comunica menos do que poderia.",
    "clareza_interna_maior_que_presenca": "Tem mais clareza interna do que presença externa visível.",
    "prudencia_funcional": "Prefere segurança e consistência antes de expandir.",
    "execucao_consistente": "Mantém padrão de execução mesmo sem motivação alta.",
    "economia_de_extremos": "Evita posições extremas e tende à moderação nas decisões e respostas.",
    "exposicao_seletiva": "Se expõe mais ou menos dependendo do ambiente, da pessoa e do tema.",
    "evita_atrito_contextual": "Ajusta o posicionamento quando percebe custo relacional alto.",
    "competencia_nao_internalizada": "Produz bem, mas internaliza o próprio mérito com atraso.",
    "presenca_relacional_rara": "Consegue estar presente com o outro sem competir com a própria mente.",
    "autoexpressao_reduzida": "Tem substância interna maior do que a ocupação verbal do próprio valor.",
}

def extract_patterns_v62(medias, derived, raw, pct_3_4, followup_answers=None):
    followup_answers = followup_answers or {}
    padroes = []

    if medias["Conscienciosidade"] >= 3.5 and (
        medias["Extroversao"] <= 3.2 or derived["visibilidade_pessoal"] <= 3.1
    ):
        padroes.append({"nome": "merito_subcomunicado", "peso": 9})

    if medias["Abertura"] - medias["Extroversao"] >= 0.7:
        padroes.append({"nome": "clareza_interna_maior_que_presenca", "peso": 8})

    if medias["Seguranca"] >= 3.4 and derived["tolerancia_risco"] <= 3.0:
        padroes.append({"nome": "prudencia_funcional", "peso": 8})

    if medias["Conscienciosidade"] >= 3.5:
        padroes.append({"nome": "execucao_consistente", "peso": 7})

    if pct_3_4 >= 75:
        padroes.append({"nome": "economia_de_extremos", "peso": 7})

    pos = followup_answers.get("posicionamento_social")
    if pos == "Depende muito da pessoa e do contexto":
        padroes.append({"nome": "exposicao_seletiva", "peso": 8})
    elif pos == "Adio ou evito para não criar tensão":
        padroes.append({"nome": "evita_atrito_contextual", "peso": 7})

    if derived["auto_reconhecimento"] <= 2.9:
        padroes.append({"nome": "competencia_nao_internalizada", "peso": 8})

    if derived["presenca_relacional"] >= 3.8 and raw.get(85, 3) >= 4 and raw.get(86, 3) >= 4:
        padroes.append({"nome": "presenca_relacional_rara", "peso": 6})

    if derived["visibilidade_pessoal"] <= 2.9 and raw.get(89, 3) <= 3:
        padroes.append({"nome": "autoexpressao_reduzida", "peso": 7})

    # remover duplicados preservando maior peso
    best = {}
    for p in padroes:
        n = p["nome"]
        if n not in best or p["peso"] > best[n]["peso"]:
            best[n] = p
    return sorted(best.values(), key=lambda x: x["peso"], reverse=True)

def extract_tensions_v62(medias, derived, followup_answers=None):
    followup_answers = followup_answers or {}
    tensoes = []

    if medias["Conscienciosidade"] >= 3.5 and derived["visibilidade_pessoal"] <= 3.1:
        tensoes.append({"nome": "valor_real_vs_presenca_percebida", "peso": 9})

    if medias["Seguranca"] >= 3.4 and derived["tolerancia_risco"] <= 3.0:
        tensoes.append({"nome": "seguranca_vs_expansao", "peso": 8})

    if medias["Abertura"] > medias["Extroversao"]:
        tensoes.append({"nome": "complexidade_interna_vs_expressao_externa", "peso": 8})

    if derived["assertividade"] <= 3.0 and derived["evita_conflito"] >= 3.2:
        tensoes.append({"nome": "adaptacao_social_vs_clareza_de_posicao", "peso": 7})

    if medias["Neuroticismo"] <= 2.9 and derived["auto_reconhecimento"] <= 2.9:
        tensoes.append({"nome": "solidez_externa_vs_merito_interno", "peso": 8})

    if 2.8 <= medias["Extroversao"] <= 3.2 and derived["impulso_social"] <= 3.1:
        tensoes.append({"nome": "funcionalidade_social_vs_busca_de_palco", "peso": 6})

    best = {}
    for t in tensoes:
        n = t["nome"]
        if n not in best or t["peso"] > best[n]["peso"]:
            best[n] = t
    return sorted(best.values(), key=lambda x: x["peso"], reverse=True)

def extract_behaviors_v62(padroes, tensoes, followup_answers=None):
    followup_answers = followup_answers or {}
    comportamentos = []

    for p in padroes:
        nome = p["nome"]
        if nome in BEHAVIOR_LIBRARY:
            comportamentos.append({
                "nome": nome,
                "descricao": BEHAVIOR_LIBRARY[nome],
                "peso": p["peso"],
                "fonte": "padrao",
            })

    # acrescentar comportamentos derivados de follow-up
    rec = followup_answers.get("reconhecimento")
    if rec == "Agradeço, mas minimizo por hábito":
        comportamentos.append({
            "nome": "minimiza_reconhecimento",
            "descricao": "Recebe reconhecimento, mas reduz internamente o peso dele quase por reflexo.",
            "peso": 7,
            "fonte": "followup",
        })
    elif rec == "Recebo bem e sigo em frente":
        comportamentos.append({
            "nome": "reconhecimento_funcional",
            "descricao": "Consegue receber reconhecimento sem transformá-lo em centro da identidade.",
            "peso": 5,
            "fonte": "followup",
        })

    risco = followup_answers.get("risco_expansao")
    if risco == "Esperar informação suficiente antes de agir":
        comportamentos.append({
            "nome": "timing_dependente_de_clareza",
            "descricao": "Anda melhor quando sente que a decisão já tem clareza suficiente para não parecer salto no escuro.",
            "peso": 7,
            "fonte": "followup",
        })
    elif risco == "Permanecer no que já funciona":
        comportamentos.append({
            "nome": "continuidade_antes_de_expansao",
            "descricao": "Prefere proteger continuidade funcional antes de explorar crescimento incerto.",
            "peso": 8,
            "fonte": "followup",
        })

    # evitar duplicados e ordenar
    best = {}
    for c in comportamentos:
        n = c["nome"]
        if n not in best or c["peso"] > best[n]["peso"]:
            best[n] = c
    return sorted(best.values(), key=lambda x: x["peso"], reverse=True)

def extract_patterns(medias, derived, raw, pct_3_4, followup_answers=None):
    return [p["nome"] for p in extract_patterns_v62(medias, derived, raw, pct_3_4, followup_answers)]

def detect_tensions(medias, derived, followup_answers=None):
    return [t["nome"] for t in extract_tensions_v62(medias, derived, followup_answers)]

def gerar_perfil(respostas, followup_answers=None):
    respostas_ajustadas = {q: aplicar_inversao(q, s) for q, s in respostas.items()}
    df = pd.DataFrame(list(respostas_ajustadas.items()), columns=["Q", "Score"])

    medias = {
        k: round(df[df["Q"].isin(qs)]["Score"].mean(), 2)
        for k, qs in BLOCOS.items()
    }

    eixo_mais_alto = max(medias, key=medias.get)
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

    all_adj_vals = list(respostas_ajustadas.values())
    pct_3_4 = sum(1 for v in all_adj_vals if v in (3, 4)) / len(all_adj_vals) * 100
    alerta_amplitude = pct_3_4 > 60

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

    eixos_baixos = {k: v for k, v in medias.items() if v < 3.0}
    eixos_moderados = {k: v for k, v in medias.items() if 3.0 <= v < 3.5}

    derived = compute_derived_variables(medias, respostas, respostas_ajustadas, followup_answers)
    padroes_v62 = extract_patterns_v62(medias, derived, respostas, pct_3_4, followup_answers)
    tensoes_v62 = extract_tensions_v62(medias, derived, followup_answers)
    comportamentos_v62 = extract_behaviors_v62(padroes_v62, tensoes_v62, followup_answers)
    padroes = [p["nome"] for p in padroes_v62]
    tensoes = [t["nome"] for t in tensoes_v62]

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
    if medias["Conscienciosidade"] >= 3.5:
        flags.append("alto senso de responsabilidade e disciplina")
    if medias["Abertura"] >= 3.5:
        flags.append("abertura intelectual e curiosidade acima da media")
    if medias["Extroversao"] < 3:
        flags.append("energia social mais contida")

    hipotese_tecnica = []
    for p in padroes:
        bloco = PATTERN_LIBRARY.get(p)
        if bloco:
            hipotese_tecnica.append(bloco["insight"])
    for t in tensoes:
        info = TENSION_LIBRARY.get(t, {})
        texto = info.get("texto", "")
        if texto:
            hipotese_tecnica.append("tensao: " + texto)

    scores_diagnosticos = {
        "Conscienciosidade": {
            "cumpre_compromissos_Q11": respostas.get(11, 3),
            "revisa_antes_entregar_Q17": respostas.get(17, 3),
            "mantem_compromissos_Q20": respostas.get(20, 3),
            "tem_sistema_prioridades_Q13": respostas.get(13, 3),
            "clareza_metas_longo_prazo_Q18": respostas.get(18, 3),
            "toma_iniciativa_espontanea_Q77": respostas.get(77, 3),
            "delega_sem_microgerenciar_Q78": respostas.get(78, 3),
            "mantem_interesse_longo_prazo_Q82": respostas.get(82, 3),
            "clareza_sobre_o_que_quer_Q84": respostas.get(84, 3),
        },
        "Extroversao": {
            "energia_com_pessoas_Q21": respostas.get(21, 3),
            "toma_iniciativa_grupo_Q22": respostas.get(22, 3),
            "busca_pessoas_novas_Q26": respostas.get(26, 3),
            "prefere_pensar_sozinho_Q23": respostas.get(23, 3),
            "pede_ajuda_sem_se_diminuir_Q81": respostas.get(81, 3),
            "diz_o_que_pensa_mesmo_incomodo_Q88": respostas.get(88, 3),
        },
        "Amabilidade": {
            "ajuda_instintivamente_Q31": respostas.get(31, 3),
            "le_emocoes_Q32": respostas.get(32, 3),
            "cede_desacordos_Q33": respostas.get(33, 3),
            "evita_feedback_Q37": respostas.get(37, 3),
            "adia_conversas_Q39": respostas.get(39, 3),
            "pede_desculpas_Q75": respostas.get(75, 3),
            "ouve_sem_formular_Q85": respostas.get(85, 3),
            "diz_nao_Q87": respostas.get(87, 3),
        },
        "Neuroticismo": {
            "preocupa_futuro_Q44": respostas.get(44, 3),
            "ansioso_sem_previsibilidade_Q49": respostas.get(49, 3),
            "rumina_erros_Q52": respostas.get(52, 3),
            "descansa_sem_culpa_Q79": respostas.get(79, 3),
            "recebe_elogio_Q80": respostas.get(80, 3),
            "presente_conversas_Q86": respostas.get(86, 3),
            "fala_conquistas_Q89": respostas.get(89, 3),
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
        "derived": derived,
        "padroes": padroes,
        "tensoes": tensoes,
        "padroes_v62": padroes_v62,
        "tensoes_v62": tensoes_v62,
        "comportamentos_v62": comportamentos_v62,
        "followup_answers": followup_answers or {},
    }


# =============================================================
# RELATORIO
# =============================================================


def gerar_resumo_base(perfil):
    padroes_v62 = perfil.get("padroes_v62", [])
    tensoes_v62 = perfil.get("tensoes_v62", [])
    comportamentos_v62 = perfil.get("comportamentos_v62", [])
    derived = perfil["derived"]

    partes = []

    if padroes_v62:
        partes.append("Padrões centrais priorizados:")
        for p in padroes_v62[:4]:
            bloco = PATTERN_LIBRARY.get(p["nome"], {})
            partes.append(
                f"- ({p['peso']}) {bloco.get('insight','')}: {bloco.get('descricao','')} Impacto: {bloco.get('custo','')}"
            )

    if tensoes_v62:
        partes.append("Tensões principais:")
        for t in tensoes_v62[:4]:
            info = TENSION_LIBRARY.get(t["nome"], {})
            partes.append(f"- ({t['peso']}) {info.get('texto','')}")

    if comportamentos_v62:
        partes.append("Comportamentos dominantes:")
        for c in comportamentos_v62[:5]:
            partes.append(f"- ({c['peso']}) {c['descricao']}")

    partes.append(
        "Variáveis derivadas: "
        f"auto_reconhecimento={derived['auto_reconhecimento']:.2f}, "
        f"assertividade={derived['assertividade']:.2f}, "
        f"tolerancia_risco={derived['tolerancia_risco']:.2f}, "
        f"visibilidade_pessoal={derived['visibilidade_pessoal']:.2f}, "
        f"presenca_relacional={derived['presenca_relacional']:.2f}, "
        f"evita_conflito={derived['evita_conflito']:.2f}, "
        f"autoexigencia={derived['autoexigencia']:.2f}."
    )

    return "\n".join(partes)

def gerar_relatorio(perfil):
    client = get_openai_client()
    if client is None:
        return "Erro: OPENAI_API_KEY nao encontrada em Secrets.", [], []

    medias = perfil["medias"]
    intensidades = perfil["intensidades"]
    ranking_eixos = perfil["ranking_eixos"]
    maior_contraste_key = perfil["maior_contraste_key"]
    maior_contraste_val = perfil["maior_contraste_val"]
    derived = perfil["derived"]
    padroes_v62 = perfil.get("padroes_v62", [])
    tensoes_v62 = perfil.get("tensoes_v62", [])
    comportamentos_v62 = perfil.get("comportamentos_v62", [])
    followup_answers = perfil.get("followup_answers", {})
    resumo_base = gerar_resumo_base(perfil)

    linhas_ranking = "\n".join([
        f"  {i + 1}. {k}: {v:.2f} [{intensidades[k]}]"
        for i, (k, v) in enumerate(ranking_eixos)
    ])
    linhas_medias = "\n".join([f"- {k}: {v:.2f} -> {intensidades[k]}" for k, v in medias.items()])
    linhas_padroes = "\n".join([
        f"- ({p['peso']}) {PATTERN_LIBRARY[p['nome']]['insight']}"
        for p in padroes_v62
    ]) if padroes_v62 else "- nenhum padrão forte identificado"
    linhas_tensoes = "\n".join([
        f"- ({t['peso']}) {TENSION_LIBRARY[t['nome']]['texto']}"
        for t in tensoes_v62
    ]) if tensoes_v62 else "- nenhuma tensão forte identificada"
    linhas_comportamentos = "\n".join([
        f"- ({c['peso']}) {c['descricao']}"
        for c in comportamentos_v62
    ]) if comportamentos_v62 else "- nenhum comportamento dominante identificado"
    linhas_followups = "\n".join([f"- {k}: {v}" for k, v in followup_answers.items()]) if followup_answers else "- nenhum follow-up aplicado"

    padrao_central = padroes_v62[0]["nome"] if padroes_v62 else None
    tensao_central = tensoes_v62[0]["nome"] if tensoes_v62 else None
    comportamento_central = comportamentos_v62[0]["descricao"] if comportamentos_v62 else ""

    bloco_forcas = []
    bloco_desafios = []
    for p in padroes_v62:
        info = PATTERN_LIBRARY.get(p["nome"], {})
        linha = f"**{info.get('insight','')}**  \n{info.get('descricao','')}"
        if info.get("tipo") in ["forca"] and len(bloco_forcas) < 4:
            bloco_forcas.append(linha)
        elif info.get("tipo") in ["central", "decisao", "social", "interno", "relacional", "modulador"] and len(bloco_desafios) < 6:
            bloco_desafios.append(linha)

    if not bloco_forcas and comportamentos_v62:
        for c in comportamentos_v62:
            if c["peso"] >= 7 and len(bloco_forcas) < 3:
                bloco_forcas.append(f"**Comportamento relevante**  \n{c['descricao']}")

    compressao_alta = perfil.get("pct_3_4", 0) >= 75
    modulador_tom = (
        "O perfil tem compressão alta de respostas. Isso NÃO deve levar a generalidade; "
        "deve levar a precisão com nuance, reconhecendo moderação, controle ou economia de posicionamento."
        if compressao_alta else
        "O perfil tem contraste suficiente para afirmações mais nítidas e concretas."
    )

    prompt = f"""
Você é um analista de comportamento humano altamente preciso.
Seu trabalho é produzir um relatório fiel, específico, multidimensional e psicologicamente impactante.

REGRAS CRÍTICAS:
1. NÃO reduza a pessoa a um único padrão.
2. Comece pelo padrão mais forte, mas expanda para um retrato completo.
3. NÃO parafraseie perguntas do teste.
4. NÃO use linguagem de eixo como "alta abertura" ou "baixa extroversão" no texto final.
5. Cada seção precisa revelar algo DIFERENTE.
6. Sempre descreva comportamento observável, custo invisível e contexto real.
7. O texto deve soar como descoberta, não como descrição genérica.
8. Gere identificação imediata e desconforto construtivo, sem dramatização barata.
8. Use follow-ups como desempate real de interpretação.
9. Se houver compressão de respostas, trate isso como modulador do tom, não como desculpa para superficialidade.

MODULADOR DE TOM:
{modulador_tom}

DADOS DO PERFIL:
RANKING DOS EIXOS:
{linhas_ranking}

MEDIAS POR EIXO:
{linhas_medias}

MAIOR CONTRASTE:
{maior_contraste_key} = {maior_contraste_val:+.2f}

VARIAVEIS DERIVADAS:
- auto_reconhecimento: {derived['auto_reconhecimento']:.2f}
- assertividade: {derived['assertividade']:.2f}
- tolerancia_risco: {derived['tolerancia_risco']:.2f}
- presenca_relacional: {derived['presenca_relacional']:.2f}
- impulso_social: {derived['impulso_social']:.2f}
- autoexigencia: {derived['autoexigencia']:.2f}
- visibilidade_pessoal: {derived['visibilidade_pessoal']:.2f}
- evita_conflito: {derived['evita_conflito']:.2f}
- autonomia_execucao: {derived['autonomia_execucao']:.2f}

PADROES PRIORIZADOS:
{linhas_padroes}

TENSOES PRIORIZADAS:
{linhas_tensoes}

COMPORTAMENTOS DOMINANTES:
{linhas_comportamentos}

FOLLOW-UPS:
{linhas_followups}

PADRAO CENTRAL:
{PATTERN_LIBRARY[padrao_central]['insight'] if padrao_central else 'nenhum'}

TENSAO CENTRAL:
{TENSION_LIBRARY[tensao_central]['texto'] if tensao_central else 'nenhuma'}

COMPORTAMENTO CENTRAL:
{comportamento_central}

RESUMO BASE:
{resumo_base}

ESTRUTURA OBRIGATORIA:
1. EIXO CENTRAL DO SEU FUNCIONAMENTO
   - comece pelo padrão mais forte, mas sem reduzir toda a pessoa a ele
2. COMO VOCÊ FUNCIONA NO DIA A DIA
   - execução, ritmo, decisões, timing
3. COMO VOCÊ APARECE PARA OS OUTROS
   - presença, comunicação, exposição, leitura social
4. O QUE ACONTECE DENTRO DE VOCÊ
   - diálogo interno, mérito, pressão, tensão principal
5. ONDE ESTÁ O PRINCIPAL BLOQUEIO
   - custo invisível mais importante
6. ONDE ESTÁ O MAIOR POTENCIAL NÃO EXPLORADO
   - o que já existe mas ainda não está sendo convertido em resultado
7. DIREÇÃO PRÁTICA
   - 3 próximos passos concretos, específicos e proporcionais ao perfil
8. FRASE FINAL DE IMPACTO
   - encerre com uma frase curta e memorável, sem exagero

FORMATO:
- escreva em português
- fale em "você"
- seja direto, humano e preciso
- evite jargão técnico
- cada seção deve ter foco próprio
- não repetir a mesma ideia com palavras diferentes
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um analista de comportamento humano especializado em transformar padrões de resposta em leitura reveladora. "
                        "Você não parafraseia perguntas. Você identifica mecanismos, custos, potencial escondido e contextos de alta performance. "
                        "Você não reduz a pessoa a um único traço; você integra profundidade e amplitude com fidelidade."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.32,
        )
        return response.choices[0].message.content, bloco_forcas, bloco_desafios
    except AuthenticationError:
        return (
            "Erro ao gerar relatorio:\n\n"
            "Falha de autenticação com a OpenAI. Verifique se a OPENAI_API_KEY em Secrets está correta e ativa.",
            bloco_forcas,
            bloco_desafios,
        )
    except Exception as e:
        return "Erro ao gerar relatorio:\n\n" + str(e), bloco_forcas, bloco_desafios


# =============================================================
# DEBUG
# =============================================================

def render_debug(perfil):
    st.markdown("---")
    st.markdown(f"**Versão: {APP_VERSION}**", unsafe_allow_html=False)
    st.header("Debug - Transparência Total do Perfil")
    st.caption("Este painel mostra todos os dados, cálculos e inferências usados para gerar o relatório.")

    brutas = perfil["respostas_brutas"]
    ajustadas = perfil["respostas_ajustadas"]

    st.subheader("1. Respostas Brutas")
    df_brutas = pd.DataFrame([
        {"Q": q, "Pergunta": questions_display.get(q, "-"), "Score Bruto": s, "Invertida?": "sim" if q in PERGUNTAS_INVERTIDAS else "-"}
        for q, s in brutas.items()
    ])
    st.dataframe(df_brutas, use_container_width=True)

    st.subheader("2. Respostas Após Inversão")
    df_aj = pd.DataFrame([
        {"Q": q, "Pergunta": questions_display.get(q, "-"), "Score Bruto": brutas[q], "Score Ajustado": ajustadas[q], "Diferença": ajustadas[q] - brutas[q]}
        for q in brutas
    ])
    st.dataframe(df_aj, use_container_width=True)

    st.subheader("3. Médias por Eixo")
    medias = perfil["medias"]
    intensidades = perfil["intensidades"]
    for eixo, media in medias.items():
        pct = (media - 1) / 4
        bar_filled = int(pct * 30)
        bar = "#" * bar_filled + "." * (30 - bar_filled)
        st.markdown(f"**{eixo}**  \n`{bar}` **{media}** - {intensidades[eixo]}")

    st.subheader("4. Ranking dos Eixos")
    for i, (k, v) in enumerate(perfil["ranking_eixos"]):
        st.write(f"{i+1}. **{k}**: {v:.2f} [{intensidades[k]}]")

    st.subheader("5. Maior Contraste")
    st.info(f"**{perfil['maior_contraste_key']}** = {perfil['maior_contraste_val']:+.2f}")

    if perfil.get("alerta_amplitude"):
        st.warning(
            f"AVISO: {perfil['pct_3_4']:.1f}% das respostas são 3 ou 4. "
            "Amplitude comprimida pode reduzir a precisão do relatório."
        )

    st.subheader("6. Variáveis Derivadas")
    st.json(perfil["derived"])

    st.subheader("7. Padrões Identificados")
    for p in perfil["padroes"]:
        st.write("→ " + PATTERN_LIBRARY[p]["insight"])

    st.subheader("8. Tensões Identificadas")
    for t in perfil["tensoes"]:
        nome = t.get("nome") if isinstance(t, dict) else t
        info = TENSION_LIBRARY.get(nome, {})
        texto = info.get("texto", str(nome))
        peso = info.get("peso", "-")
        st.write(f"→ {texto} [peso {peso}]")

    st.subheader("9. Follow-ups")
    if perfil.get("followup_answers"):
        st.json(perfil["followup_answers"])
    else:
        st.write("Nenhum follow-up aplicado.")

    st.subheader("10. Qualidade Estatística")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Media Geral", str(perfil["media_geral"]))
    c2.metric("Desvio Padrao", str(perfil["desvio_padrao"]))
    c3.metric("Amplitude", str(perfil["amplitude"]))
    c4.metric("Tipo Resposta", perfil["tipo_resposta"])
    c5.metric("Confiabilidade", perfil["confiabilidade"])


# =============================================================
# CALIBRACAO GUIADA
# =============================================================

def gerar_statements_calibracao(perfil):
    medias = perfil["medias"]
    raw = perfil["respostas_brutas"]
    adjusted = perfil["respostas_ajustadas"]
    derived = perfil["derived"]

    statements = []
    sid = 1

    if medias["Conscienciosidade"] >= 3.4:
        statements.append({
            "id": sid,
            "eixo": "Entrega",
            "texto": (
                "Quando você assume um compromisso, tende a levar até o fim. "
                "Mesmo sem um sistema perfeito, o que você promete costuma sair."
            ),
            "followup_verdadeiro": (
                "Isso acontece porque você é muito organizado ou porque sustenta na responsabilidade? "
                "(1 = muito sistema / 5 = muita responsabilidade mesmo sem sistema)"
            ),
            "followup_falso": (
                "A descrição exagerou sua consistência? "
                "(1 = exagerou muito / 5 = acerta parcialmente)"
            ),
            "ajuste_mais_forte": {11: 1, 17: 1, 20: 1},
            "ajuste_mais_fraco": {11: -1, 17: -1, 20: -1},
        })
        sid += 1

    if derived["visibilidade_pessoal"] <= 3.0 and medias["Conscienciosidade"] >= 3.4:
        statements.append({
            "id": sid,
            "eixo": "Visibilidade",
            "texto": (
                "Você parece produzir mais valor do que comunica. "
                "As pessoas que convivem de perto percebem sua qualidade, mas ela nem sempre aparece na mesma proporção para fora."
            ),
            "followup_verdadeiro": (
                "Isso te descreve de forma leve ou forte? "
                "(1 = leve / 5 = muito forte)"
            ),
            "followup_falso": (
                "Você sente que seu valor aparece sim, e essa leitura foi injusta? "
                "(1 = totalmente injusta / 5 = parcialmente injusta)"
            ),
            "ajuste_mais_forte": {88: 1, 89: 1},
            "ajuste_mais_fraco": {88: -1, 89: -1},
        })
        sid += 1

    if derived["evita_conflito"] >= 3.4:
        statements.append({
            "id": sid,
            "eixo": "Conflito",
            "texto": (
                "Quando percebe que uma conversa pode gerar tensão, você tende a medir o custo antes de falar. "
                "Em muitos casos, prefere preservar o ambiente em vez de se posicionar totalmente."
            ),
            "followup_verdadeiro": (
                "Isso acontece mais por estratégia ou por desconforto com tensão? "
                "(1 = estratégia / 5 = desconforto real)"
            ),
            "followup_falso": (
                "Você costuma se posicionar mais do que o texto sugere? "
                "(1 = muito mais / 5 = um pouco mais)"
            ),
            "ajuste_mais_forte": {33: 1, 37: 1, 39: 1},
            "ajuste_mais_fraco": {33: -1, 37: -1, 39: -1},
        })
        sid += 1

    if derived["auto_reconhecimento"] <= 2.9:
        statements.append({
            "id": sid,
            "eixo": "Reconhecimento",
            "texto": (
                "Existe uma diferença entre fazer bem e ocupar esse mérito. "
                "Você pode receber elogio ou reconhecimento com alguma economia, como se não incorporasse totalmente o que já fez."
            ),
            "followup_verdadeiro": (
                "Isso acontece pouco ou bastante? "
                "(1 = pouco / 5 = bastante)"
            ),
            "followup_falso": (
                "Você recebe reconhecimento com mais naturalidade do que o texto sugere? "
                "(1 = muito mais / 5 = um pouco mais)"
            ),
            "ajuste_mais_forte": {80: -1, 89: -1},
            "ajuste_mais_fraco": {80: 1, 89: 1},
        })
        sid += 1

    return statements[:4]

def aplicar_ajustes_calibracao(respostas_originais, ajustes):
    novas = dict(respostas_originais)
    for q_num, delta in ajustes.items():
        if q_num in novas:
            novo_val = max(1, min(5, novas[q_num] + delta))
            novas[q_num] = novo_val
    return novas


# =============================================================
# INTERFACE
# =============================================================

col_logo, col_title = st.columns([1, 5])
with col_logo:
    try:
        st.image("logo_mindinsight.png", width=220)
    except Exception:
        st.write("🧠")
with col_title:
    st.markdown("<h1 style='margin-bottom:0'>Mind Insight™</h1>", unsafe_allow_html=True)
    if MODO_TESTE:
        st.markdown(
            f'<div class="manus-badge">{APP_VERSION} | Inferência comportamental profunda | MODO TESTE ATIVO</div>',
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
        st.caption("Opção de reutilização disponível apenas no modo teste (?modo=teste na URL).")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Usar respostas do último teste**")
            if st.button("Usar último teste", key="btn_ultimo"):
                st.session_state.responses = carregar_ultimo_teste()
                st.session_state.current_question = TOTAL + 1
                st.session_state.modo_selecionado = True
                st.rerun()
        with col_b:
            st.markdown("**Responder o questionário novamente**")
            st.caption("Responde todas as " + str(TOTAL) + " perguntas do zero.")
            if st.button("Responder questionário", key="btn_novo"):
                st.session_state.responses = {}
                st.session_state.current_question = 1
                st.session_state.modo_selecionado = True
                st.rerun()
    else:
        if not st.session_state.user_info_completo:
            st.markdown("---")
            st.subheader("Antes de começar")
            st.markdown("Preencha os dados abaixo para personalizar seu relatório. Ao final, você também receberá uma cópia por email.")
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
                st.caption("Seu email será usado apenas para enviar uma cópia do seu relatório.")

                submitted = st.form_submit_button("Começar o teste", type="primary")
                if submitted:
                    if not nome_input.strip():
                        st.error("Por favor, informe seu nome.")
                    elif not email_input.strip() or "@" not in email_input:
                        st.error("Por favor, informe um email válido.")
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
    st.caption(f"Pergunta {st.session_state.current_question} de {TOTAL}  |  Q{q_num}")
    st.markdown("### " + questions_display[q_num])

    resposta = st.radio(
        "Sua resposta:",
        scale,
        index=None,
        key="q_" + str(q_num),
    )

    if st.button("Próxima"):
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
        "Antes do relatório final, preciso confirmar algumas leituras principais. "
        "Isso melhora a precisão quando o perfil está mais sutil ou comprimido."
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
        st.markdown(f"**Afirmação {sid} — {stmt['eixo']}:**")
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
        if st.button("Continuar para as perguntas adaptativas", type="primary"):
            respostas_calibradas = aplicar_ajustes_calibracao(
                st.session_state.responses, ajustes_acumulados
            ) if ajustes_acumulados else dict(st.session_state.responses)

            st.session_state.perfil_cache = gerar_perfil(respostas_calibradas)
            st.session_state.followup_questions = gerar_followups(st.session_state.perfil_cache)
            st.session_state.calibracao_completa = True
            st.rerun()
    else:
        st.warning("Por favor, responda todas as afirmações acima para continuar.")

elif not st.session_state.followup_completo:
    if st.session_state.perfil_cache is None:
        st.session_state.perfil_cache = gerar_perfil(st.session_state.responses)

    followups = st.session_state.followup_questions

    if not followups:
        st.session_state.followup_completo = True
        st.rerun()

    st.title("Perguntas Adaptativas")
    st.markdown(
        "Com base no seu perfil inicial, selecionei algumas perguntas extras para resolver ambiguidades específicas. "
        "Isso aprofunda a leitura sem transformar a experiência em outro teste."
    )
    st.markdown("---")

    completas = True
    for item in followups:
        resposta = st.radio(
            item["pergunta"],
            item["opcoes"],
            index=None,
            key="followup_" + item["id"]
        )
        if resposta is None:
            completas = False
        else:
            st.session_state.followup_answers[item["id"]] = resposta
        st.markdown("---")

    if completas:
        if st.button("Gerar meu relatório completo", type="primary"):
            respostas_finais = aplicar_ajustes_calibracao(
                st.session_state.responses, st.session_state.calibracao_ajustes
            ) if st.session_state.calibracao_ajustes else dict(st.session_state.responses)

            salvar_ultimo_teste(respostas_finais)
            st.session_state.perfil_cache = gerar_perfil(respostas_finais, st.session_state.followup_answers)
            st.session_state.followup_completo = True
            st.rerun()
    else:
        st.warning("Responda todas as perguntas adaptativas para continuar.")

else:
    st.title("Seu Relatório de Perfil")
    if MODO_TESTE:
        st.caption(f"Versão: {APP_VERSION} | MODO TESTE ATIVO")

    if st.session_state.perfil_cache is not None:
        perfil = st.session_state.perfil_cache
    else:
        respostas_finais = aplicar_ajustes_calibracao(
            st.session_state.responses, st.session_state.calibracao_ajustes
        ) if st.session_state.calibracao_ajustes else dict(st.session_state.responses)
        perfil = gerar_perfil(respostas_finais, st.session_state.followup_answers)

    if st.session_state.calibracao_ajustes:
        st.success(
            "Relatório calibrado com base nas suas respostas de validação. "
            + str(len(st.session_state.calibracao_ajustes)) + " ajuste(s) aplicados."
        )
    if st.session_state.followup_answers:
        st.success(
            "Perguntas adaptativas aplicadas para resolver ambiguidades específicas do perfil."
        )

    with st.spinner("Gerando sua análise profunda..."):
        relatorio_ai, tracos_forcas_exib, tracos_desafios_exib = gerar_relatorio(perfil)

    secao10_partes = []
    if tracos_forcas_exib:
        secao10_partes.append("### O QUE TE FORTALECE\n\n" + "\n\n".join(tracos_forcas_exib))
    if tracos_desafios_exib:
        secao10_partes.append("### O QUE TE DESAFIA\n\n" + "\n\n".join(tracos_desafios_exib))

    if secao10_partes:
        secao10_bloco = "\n\n## 10. TRAÇOS COMPORTAMENTAIS IDENTIFICADOS\n\n" + "\n\n".join(secao10_partes)
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
        relatorio = relatorio_ai

    st.markdown(relatorio)

    if MODO_TESTE:
        render_debug(perfil)

    if not st.session_state.dados_registrados:
        user_info = st.session_state.get("user_info", {})
        medias_perfil = perfil.get("medias", {})
        respostas_finais = aplicar_ajustes_calibracao(
            st.session_state.responses, st.session_state.calibracao_ajustes
        ) if st.session_state.calibracao_ajustes else dict(st.session_state.responses)

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
            "padroes_ativos": "; ".join(perfil.get("padroes", [])),
            "tensoes_ativas": "; ".join(perfil.get("tensoes", [])),
            "followups": json.dumps(st.session_state.followup_answers, ensure_ascii=False),
            "ajustes_calibracao": str(len(st.session_state.get("calibracao_ajustes", {}))),
            "relatorio": relatorio,
            "respostas": respostas_finais,
        }

        ok_sheets, msg_sheets = registrar_no_sheets(dados_registro)
        if MODO_TESTE:
            if ok_sheets:
                st.info(f"[DEBUG] Registro no Google Sheets: OK — VERSAO {APP_VERSION} ATIVA")
            else:
                st.error(f"[DEBUG] Erro no Google Sheets: {str(msg_sheets)} — VERSAO {APP_VERSION} ATIVA")

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
        respostas_para_download = aplicar_ajustes_calibracao(
            st.session_state.responses, st.session_state.calibracao_ajustes
        ) if st.session_state.calibracao_ajustes else dict(st.session_state.responses)
        _json_bytes = json.dumps(
            {str(k): v for k, v in respostas_para_download.items()},
            ensure_ascii=False, indent=2
        ).encode("utf-8")
        st.download_button(
            label="[TESTE] Baixar respostas calibradas (ultimo_teste.json)",
            data=_json_bytes,
            file_name="ultimo_teste.json",
            mime="application/json",
            help="Baixe este arquivo e adicione ao seu repositório GitHub junto com o app.py."
        )

    st.markdown("---")
    col1, col2 = st.columns(2)

    def reset_all(go_to=0):
        for key in DEFAULTS:
            if isinstance(DEFAULTS[key], dict):
                st.session_state[key] = {}
            elif isinstance(DEFAULTS[key], list):
                st.session_state[key] = []
            else:
                st.session_state[key] = DEFAULTS[key]
        st.session_state.current_question = go_to
        st.session_state.modo_selecionado = False

    with col1:
        if st.button("Refazer o teste"):
            reset_all(1)
            st.rerun()

    with col2:
        if st.button("Voltar ao início"):
            reset_all(0)
            st.rerun()
