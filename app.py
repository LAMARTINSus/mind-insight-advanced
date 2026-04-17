
# -*- coding: utf-8 -*-

# =============================================================
# MIND INSIGHT ADVANCED AI
# Version: V8.4
# Data: 2026-04-16
# Criado com: Claude (Anthropic)
# Aperfeiçoado por: Manus AI
# Reestruturado para inferência comportamental profunda com impacto psicológico e amplitude por facetas
#
# V7 - Integração de profundidade + amplitude + impacto psicológico
# V7.2 - Distribuição de profundidade por facetas com anti-repetição temática
#      - Mantém toda a estrutura do app intacta
#      - OpenAI corrigido via st.secrets / variável de ambiente
#      - Padrões com peso e prioridade narrativa
#      - Tensões internas com peso e contexto
#      - Camada separada de comportamentos dominantes
#      - Follow-ups usados como desempate real de interpretação
#      - Compressão de respostas modula o tom do relatório
#      - Relatório multidimensional: profundidade sem reducionismo
# V7.3A - Engines extras separadas para aprofundar presença social e mundo interno
#      - Corrige bugs de retorno em Google Sheets e email
#      - Adiciona engine_presenca_social
#      - Adiciona engine_mundo_interno
#      - Integra engines no perfil, relatório e debug
# V7.4 - Engines extras completas por faceta
#      - Mantém toda a V7.3A intacta
#      - Adiciona engine_execucao_decisao
#      - Adiciona engine_relacoes_limites
#      - Adiciona engine_valor_oportunidade
#      - Integra as 3 novas engines no perfil, relatório e debug
# V7.5 - Controle de redundância + distribuição de foco
#      - Impede repetição semântica entre seções
#      - Distribui causa principal e ângulo narrativo por seção
#      - Prioriza fonte exclusiva de dados em cada parte do relatório
#      - Reforça checklist final de não repetição antes de gerar
# V7.8 - Separação causal real + linguagem humana + anti-colapso narrativo
#      - Data: 2026-04-16
#      - Bloqueia reuso de causa principal entre seções
#      - Força lente exclusiva e fonte principal concreta por seção
#      - Adiciona protocolo interno de pré-escrita e testes anti-colapso
#      - Reforça linguagem natural, humana e sem tom de ferramenta
# V7.9 - Exclusividade causal forçada + travas laterais + anti-re-resumo terminal
#      - Data: 2026-04-16
#      - Exige 6 causas principais realmente diferentes, uma por seção
#      - Bloqueia reaproveitamento da mesma tese-mãe em presença, valor e fechamento
#      - Torna mandatória a fonte dominante correta em cada seção
#      - Impede que o bloco final recompacte o relatório em frases redundantes
#      - Reforça testes finais bloqueantes e mantém linguagem humana
# V8.0 - Linguagem direta + maior cobertura temática + calibração mais limpa
#      - Data: 2026-04-16
#      - Proíbe construção por negação comparativa e contraste artificial no texto final
#      - Mantém separação causal, mas impede vazamento da etapa interna para o relatório
#      - Exige novidade real por seção e maior cobertura de áreas pouco salientadas do perfil
#      - Reforça potenciais positivos, autonomia silenciosa, abertura cognitiva e escuta fina
#      - Simplifica a afirmação de reconhecimento na calibração guiada
# V8.1 - Subfacetas + evidências por seção + validação final de linguagem
#      - Data: 2026-04-16
#      - Amplia a preservação de sinais antes do prompt com subfacetas temáticas
#      - Injeta evidências itemizadas por seção com score bruto, ajustado e transparência de inversão
#      - Reforça a proibição de voz conversacional na seção 9
#      - Adiciona validação e uma segunda passada automática quando surgem contrastes artificiais
# V8.1F - Correção isolada do fechamento para base comparativa funcional
#      - Data: 2026-04-16
#      - Sanea o texto final quando ainda vazam comandos, ofertas de ajuda ou voz de assistente
#      - Limpa o bloco 9 e substitui fechamento contaminado por próximos passos concretos
#      - Preserva a arquitetura atual para comparação posterior com a versão nova
# V8.2 - Ampliação de derivadas, evidências e cobertura causal por seção
#      - Data: 2026-04-16
#      - Expande a camada intermediária com novas derivadas para Abertura, Neuroticismo, Segurança e Abundância
#      - Aumenta a riqueza das evidências itemizadas por seção e sua priorização interpretativa
#      - Reforça especialmente as seções de mundo interno, execução e valor/oportunidade
#      - Mantém a base funcional saneada para comparação com a versão anterior
# V8.3 - Linguagem do povo, mensagem direta e frase que cala na alma
#      - Data: 2026-04-16
#      - Reescreve o padrão de prompt para linguagem simples, concreta e memorável
#      - Exige que cada seção nomeie padrão, força, custo e efeito prático com clareza
#      - Bloqueia formulação bonita demais, abstração vazia e elegância sem mensagem
#      - Mantém a estrutura técnica da V8.2, mas muda profundamente a voz do relatório
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
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI, AuthenticationError

APP_VERSION = "V8.4"
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

SUBFACET_LIBRARY_V81 = {
    "abertura_curiosidade": {"label": "curiosidade e exploração intelectual", "bloco": "Abertura", "itens": [1, 3, 8]},
    "abertura_flexibilidade": {"label": "flexibilidade de crença", "bloco": "Abertura", "itens": [2, 7]},
    "abertura_abstracao": {"label": "abstração e conexão mental", "bloco": "Abertura", "itens": [4, 5]},
    "abertura_revisao_crenca": {"label": "revisão de crença com abertura real", "bloco": "Abertura", "itens": [2, 5, 7]},
    "abertura_exploracao_ativa": {"label": "exploração ativa de novidade", "bloco": "Abertura", "itens": [1, 3, 8]},
    "consc_planejamento": {"label": "planejamento e antecipação", "bloco": "Conscienciosidade", "itens": [13, 14, 18, 84]},
    "consc_constancia": {"label": "constância e sustentação", "bloco": "Conscienciosidade", "itens": [11, 20, 82]},
    "consc_revisao": {"label": "revisão e controle de qualidade", "bloco": "Conscienciosidade", "itens": [17, 78]},
    "consc_autonomia": {"label": "autonomia de execução", "bloco": "Conscienciosidade", "itens": [12, 16, 77]},
    "consc_clareza_direcao": {"label": "clareza de direção e meta", "bloco": "Conscienciosidade", "itens": [18, 84]},
    "ext_energia_social": {"label": "energia social", "bloco": "Extroversao", "itens": [21, 25]},
    "ext_iniciativa_expressiva": {"label": "iniciativa de fala e exposição", "bloco": "Extroversao", "itens": [22, 24, 30]},
    "ext_busca_social": {"label": "busca ativa de contato", "bloco": "Extroversao", "itens": [26, 81]},
    "ext_modulacao_presenca": {"label": "modulação entre escuta e protagonismo", "bloco": "Extroversao", "itens": [23, 29, 88]},
    "amab_empatia": {"label": "empatia e leitura do outro", "bloco": "Amabilidade", "itens": [31, 32, 38]},
    "amab_limites": {"label": "limites com firmeza", "bloco": "Amabilidade", "itens": [33, 36, 87]},
    "amab_atrito": {"label": "custo relacional do atrito", "bloco": "Amabilidade", "itens": [35, 37, 39]},
    "amab_reparacao_presenca": {"label": "reparação e presença com o outro", "bloco": "Amabilidade", "itens": [75, 85, 86]},
    "neuro_antecipacao": {"label": "antecipação e necessidade de previsibilidade", "bloco": "Neuroticismo", "itens": [44, 49]},
    "neuro_estabilidade_pressao": {"label": "estabilidade sob pressão", "bloco": "Neuroticismo", "itens": [43, 45, 47, 48]},
    "neuro_ruminacao": {"label": "ruminação e impacto pós-evento", "bloco": "Neuroticismo", "itens": [42, 46, 50, 52]},
    "neuro_merito_descanso": {"label": "descanso, mérito e autoaceitação", "bloco": "Neuroticismo", "itens": [79, 80, 89]},
    "neuro_sensibilidade_critica": {"label": "sensibilidade à crítica e autoimpacto", "bloco": "Neuroticismo", "itens": [44, 46, 50, 80]},
    "neuro_recuperacao": {"label": "recuperação depois da pressão", "bloco": "Neuroticismo", "itens": [47, 48, 79]},
    "seg_previsibilidade": {"label": "necessidade de previsibilidade", "bloco": "Seguranca", "itens": [53, 55, 61, 63]},
    "seg_transicao": {"label": "conforto em transição", "bloco": "Seguranca", "itens": [58, 62]},
    "seg_risco_acao": {"label": "ação sem garantia total", "bloco": "Seguranca", "itens": [54, 57, 60]},
    "seg_apego_estavel": {"label": "apego ao que já funciona", "bloco": "Seguranca", "itens": [56, 59]},
    "abund_expansao": {"label": "expansão e visão de ganho", "bloco": "Abundancia", "itens": [64, 68, 70, 83]},
    "abund_escassez": {"label": "escassez, comparação e insuficiência", "bloco": "Abundancia", "itens": [65, 67, 73]},
    "abund_investimento_proprio": {"label": "investimento em si e retorno esperado", "bloco": "Abundancia", "itens": [66, 71]},
    "abund_pedido_valor": {"label": "pedido e cobrança de valor", "bloco": "Abundancia", "itens": [72]},
    "abund_perda_prudencia": {"label": "perda, prudência e mérito silencioso", "bloco": "Abundancia", "itens": [69, 74, 76]},
    "abund_merecimento": {"label": "merecimento econômico e autorização para receber", "bloco": "Abundancia", "itens": [72, 76, 80]},
    "abund_comparacao": {"label": "comparação e contração por insuficiência", "bloco": "Abundancia", "itens": [65, 67, 73]},
    "abund_protecao_perda": {"label": "proteção contra perda e recuo de expansão", "bloco": "Abundancia", "itens": [69, 74]},
}

SECTION_SUBFACETS_V81 = {
    "central": ["abertura_curiosidade", "abertura_revisao_crenca", "consc_constancia", "neuro_merito_descanso", "seg_previsibilidade", "abund_escassez"],
    "execucao_decisao": ["consc_planejamento", "consc_constancia", "consc_autonomia", "consc_clareza_direcao", "seg_risco_acao", "seg_apego_estavel"],
    "presenca_expressao": ["ext_energia_social", "ext_iniciativa_expressiva", "ext_busca_social", "ext_modulacao_presenca"],
    "mundo_interno": ["abertura_curiosidade", "abertura_abstracao", "abertura_revisao_crenca", "neuro_antecipacao", "neuro_ruminacao", "neuro_sensibilidade_critica", "neuro_recuperacao", "neuro_merito_descanso"],
    "relacoes_conflito": ["amab_empatia", "amab_limites", "amab_atrito", "amab_reparacao_presenca"],
    "valor_oportunidade": ["abund_expansao", "abund_escassez", "abund_investimento_proprio", "abund_pedido_valor", "abund_perda_prudencia", "abund_merecimento", "abund_comparacao", "abund_protecao_perda"],
}

SECTION_ITEM_IDS_V81 = {
    "central": [1, 5, 11, 17, 44, 54, 65, 72, 76, 79, 80, 89],
    "execucao_decisao": [11, 13, 14, 17, 18, 20, 54, 57, 60, 61, 63, 77, 78, 82, 84],
    "presenca_expressao": [21, 22, 23, 24, 26, 29, 30, 81, 88],
    "mundo_interno": [1, 2, 3, 4, 5, 7, 8, 42, 44, 46, 49, 50, 52, 79, 80, 89],
    "relacoes_conflito": [31, 32, 33, 35, 36, 37, 38, 39, 75, 85, 86, 87],
    "valor_oportunidade": [64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 76, 80, 83],
}


def classificar_intensidade_curta(valor):
    if valor >= 4.2:
        return "muito saliente"
    if valor >= 3.5:
        return "saliente"
    if valor >= 2.8:
        return "contextual"
    if valor >= 2.2:
        return "contido"
    return "muito contido"


def compute_subfacets(raw, adjusted):
    subfacetas = {}
    for nome, meta in SUBFACET_LIBRARY_V81.items():
        itens = meta["itens"]
        valores = [adjusted.get(q, 3) for q in itens]
        score = round(sum(valores) / len(valores), 2) if valores else 3.0
        subfacetas[nome] = {
            "nome": nome,
            "label": meta["label"],
            "bloco": meta["bloco"],
            "itens": itens,
            "score": score,
            "intensidade": classificar_intensidade_curta(score),
        }
    return subfacetas


def get_top_subfacets_for_section(subfacetas, section_name, limit=4):
    nomes = SECTION_SUBFACETS_V81.get(section_name, [])
    candidatos = [subfacetas[n] for n in nomes if n in subfacetas]
    candidatos = sorted(candidatos, key=lambda x: abs(x["score"] - 3), reverse=True)
    return candidatos[:limit]


def score_evidencia_v82(bruto, ajustado, invertida):
    distancia = abs(ajustado - 3)
    bonus_inversao = 0.15 if invertida and bruto != ajustado else 0.0
    bonus_extremo = 0.2 if ajustado >= 4.3 or ajustado <= 1.7 else 0.0
    bonus_contraste = 0.1 if abs(bruto - ajustado) >= 1 else 0.0
    return round(distancia + bonus_inversao + bonus_extremo + bonus_contraste, 3)


def build_section_evidence_v81(raw, adjusted, section_name, limit=6):
    evidencias = []
    for q in SECTION_ITEM_IDS_V81.get(section_name, []):
        bruto = raw.get(q, 3)
        ajustado = adjusted.get(q, 3)
        invertida = q in PERGUNTAS_INVERTIDAS
        texto = questions_display.get(q, "-")
        if ajustado >= 4.2:
            leitura = "o sinal aparece com força e merece peso real na leitura"
        elif ajustado >= 3.5:
            leitura = "o sinal aparece de forma consistente"
        elif ajustado <= 1.8:
            leitura = "o sinal aparece muito pouco e funciona como ausência relevante"
        elif ajustado <= 2.5:
            leitura = "o sinal aparece com reserva e ajuda a limitar conclusões exageradas"
        else:
            leitura = "o sinal é contextual e pede leitura sem absolutismo"
        if invertida and bruto != ajustado:
            leitura += "; a interpretação final depende do score ajustado após inversão"
        evidencias.append({
            "q": q,
            "texto": texto,
            "bruto": bruto,
            "ajustado": ajustado,
            "invertida": invertida,
            "forca": abs(ajustado - 3),
            "score_evidencia": score_evidencia_v82(bruto, ajustado, invertida),
            "leitura": leitura,
        })
    evidencias = sorted(evidencias, key=lambda x: (x["score_evidencia"], x["forca"], x["invertida"]), reverse=True)
    return evidencias[:limit]


def build_all_section_evidences_v81(raw, adjusted):
    return {
        nome: build_section_evidence_v81(raw, adjusted, nome)
        for nome in SECTION_ITEM_IDS_V81.keys()
    }


def compute_derived_variables(medias, raw, adjusted, followup_answers=None):
    followup_answers = followup_answers or {}

    def avg(*values):
        return round(sum(values) / len(values), 2)

    # Base comportamental preservada
    auto_reconhecimento = avg(raw.get(80, 3), raw.get(89, 3), raw.get(76, 3))
    assertividade = avg(raw.get(87, 3), raw.get(88, 3), adjusted.get(36, 3), adjusted.get(30, 3))
    tolerancia_risco = avg(adjusted.get(54, 3), adjusted.get(57, 3), adjusted.get(60, 3), adjusted.get(62, 3))
    presenca_relacional = avg(raw.get(85, 3), raw.get(86, 3), raw.get(75, 3))
    impulso_social = avg(adjusted.get(21, 3), adjusted.get(22, 3), adjusted.get(24, 3), adjusted.get(26, 3))
    autoexigencia = avg((6 - raw.get(79, 3)), (6 - raw.get(80, 3)), (6 - raw.get(89, 3)))
    visibilidade_pessoal = avg(adjusted.get(30, 3), raw.get(88, 3), raw.get(89, 3))
    evita_conflito = avg(raw.get(33, 3), raw.get(37, 3), raw.get(39, 3))
    autonomia_execucao = avg(raw.get(77, 3), raw.get(82, 3), adjusted.get(11, 3), adjusted.get(17, 3))

    # Novas derivadas para ampliar cobertura
    flexibilidade_cognitiva = avg(adjusted.get(2, 3), adjusted.get(5, 3), adjusted.get(7, 3))
    conforto_abstracao = avg(adjusted.get(4, 3), adjusted.get(5, 3), adjusted.get(8, 3))
    planejamento_antecipado = avg(adjusted.get(13, 3), adjusted.get(14, 3), adjusted.get(18, 3), adjusted.get(84, 3))
    sensibilidade_pressao = avg(adjusted.get(43, 3), adjusted.get(45, 3), adjusted.get(47, 3), adjusted.get(48, 3))
    ruminacao_pos_evento = avg(adjusted.get(42, 3), adjusted.get(46, 3), adjusted.get(50, 3), adjusted.get(52, 3))
    necessidade_previsibilidade = avg(adjusted.get(53, 3), adjusted.get(55, 3), adjusted.get(61, 3), adjusted.get(63, 3))
    merecimento_economico = avg(raw.get(72, 3), raw.get(76, 3), raw.get(80, 3))
    impulso_expansao = avg(adjusted.get(64, 3), adjusted.get(68, 3), adjusted.get(70, 3), adjusted.get(83, 3))
    comparacao_escassez = avg(adjusted.get(65, 3), adjusted.get(67, 3), adjusted.get(73, 3))

    # Ajustes pelos follow-ups
    if followup_answers.get("posicionamento_social") == "Falo de forma direta e tranquila":
        assertividade = min(5.0, round(assertividade + 0.35, 2))
        visibilidade_pessoal = min(5.0, round(visibilidade_pessoal + 0.20, 2))
    elif followup_answers.get("posicionamento_social") == "Adio ou evito para não criar tensão":
        assertividade = max(1.0, round(assertividade - 0.40, 2))
        evita_conflito = min(5.0, round(evita_conflito + 0.35, 2))

    if followup_answers.get("natureza_conflito") == "Desconforto real com tensão ou desaprovação":
        evita_conflito = min(5.0, round(evita_conflito + 0.40, 2))
        sensibilidade_pressao = min(5.0, round(sensibilidade_pressao + 0.15, 2))
    elif followup_answers.get("natureza_conflito") == "Estratégia - acho desnecessário em muitos casos":
        evita_conflito = max(1.0, round(evita_conflito - 0.20, 2))

    if followup_answers.get("reconhecimento") == "Fico desconfortável e tento mudar de assunto":
        auto_reconhecimento = max(1.0, round(auto_reconhecimento - 0.45, 2))
        visibilidade_pessoal = max(1.0, round(visibilidade_pessoal - 0.25, 2))
        merecimento_economico = max(1.0, round(merecimento_economico - 0.25, 2))
    elif followup_answers.get("reconhecimento") == "Agradeço, mas minimizo por hábito":
        auto_reconhecimento = max(1.0, round(auto_reconhecimento - 0.20, 2))
        merecimento_economico = max(1.0, round(merecimento_economico - 0.15, 2))
    elif followup_answers.get("reconhecimento") == "Recebo bem e sigo em frente":
        auto_reconhecimento = min(5.0, round(auto_reconhecimento + 0.20, 2))
        merecimento_economico = min(5.0, round(merecimento_economico + 0.15, 2))

    if followup_answers.get("risco_expansao") == "Permanecer no que já funciona":
        tolerancia_risco = max(1.0, round(tolerancia_risco - 0.30, 2))
        impulso_expansao = max(1.0, round(impulso_expansao - 0.20, 2))
    elif followup_answers.get("risco_expansao") == "Agir se o upside parecer claro":
        tolerancia_risco = min(5.0, round(tolerancia_risco + 0.20, 2))
        impulso_expansao = min(5.0, round(impulso_expansao + 0.15, 2))

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
        "flexibilidade_cognitiva": flexibilidade_cognitiva,
        "conforto_abstracao": conforto_abstracao,
        "planejamento_antecipado": planejamento_antecipado,
        "sensibilidade_pressao": sensibilidade_pressao,
        "ruminacao_pos_evento": ruminacao_pos_evento,
        "necessidade_previsibilidade": necessidade_previsibilidade,
        "merecimento_economico": merecimento_economico,
        "impulso_expansao": impulso_expansao,
        "comparacao_escassez": comparacao_escassez,
    }


# =============================================================
# ENGINES EXTRAS V7.3A
# =============================================================

def engine_presenca_social(medias, derived, raw, followup_answers=None):
    followup_answers = followup_answers or {}

    leitura = []
    riscos = []
    forcas = []
    ajustes = []

    vis = derived["visibilidade_pessoal"]
    ass = derived["assertividade"]
    ext = medias["Extroversao"]
    impulso_social = derived.get("impulso_social", 3)
    pos = followup_answers.get("posicionamento_social", "")

    if pos == "Depende muito da pessoa e do contexto":
        leitura.append("aquecimento_social_contextual")
        ajustes.append("Sua presença não entra igual em todo lugar. Você lê o ambiente primeiro e só ocupa mais espaço quando sente abertura real.")

    if 3.0 <= ext <= 3.4 and 3.0 <= impulso_social <= 3.2:
        leitura.append("presenca_de_arranque_lento")
        riscos.append("Em ambientes novos, você pode demorar um pouco para mostrar a parte mais viva do seu repertório.")

    if vis >= 3.4 and ass >= 3.4:
        forcas.append("ocupacao_clara_quando_ha_abertura")

    if vis <= 3.1 and ass <= 3.1:
        leitura.append("legibilidade_social_variavel")
        riscos.append("Quem vê só o seu começo pode subestimar presença, clareza ou firmeza que aparecem depois.")

    if ass <= 3.0:
        leitura.append("ocupacao_medida_do_espaco")
        riscos.append("Sua entrada costuma ser mais medida do que imediata, e isso pode reduzir impacto inicial em contextos mais competitivos.")
    elif ass >= 3.7:
        forcas.append("posicionamento_claro")

    if ext >= 3.6:
        forcas.append("presenca_espontaneamente_ativa")
    elif ext <= 3.0 and pos != "Adio ou evito para não criar tensão":
        leitura.append("presenca_sem_pressa_de_aparecer")

    if pos == "Falo de forma direta e tranquila":
        forcas.append("fala_direta_sem_teatralidade")
    elif pos == "Adio ou evito para não criar tensão":
        leitura.append("entrada_social_contida_pelo_clima")
        riscos.append("Quando o ambiente parece áspero, você pode segurar demais a própria emissão para não piorar o clima.")

    return {
        "leitura": leitura,
        "riscos": riscos,
        "forcas": forcas,
        "ajustes": ajustes,
    }


def engine_mundo_interno(medias, derived, raw, followup_answers=None):
    followup_answers = followup_answers or {}

    leitura = []
    riscos = []
    forcas = []
    ajustes = []

    auto_rec = derived["auto_reconhecimento"]
    autoex = derived["autoexigencia"]
    aber = medias["Abertura"]
    neuro = medias["Neuroticismo"]
    flex = derived.get("flexibilidade_cognitiva", 3)
    pressao = derived.get("sensibilidade_pressao", 3)
    rum = derived.get("ruminacao_pos_evento", 3)
    rec = followup_answers.get("reconhecimento", "")

    if aber >= 3.7 and flex >= 3.7:
        leitura.append("mente_associativa_viva")
        forcas.append("revisao_inteligente_de_perspectiva")
        ajustes.append("Sua mente costuma ligar pontos rápido, revisar ideia boa sem muito apego e aprender por interesse real.")

    if aber >= 3.7 and rum <= 3.1:
        forcas.append("curiosidade_sem_excesso_de_ruido")

    if autoex >= 3.8:
        leitura.append("autoavaliacao_em_aberto")
        riscos.append("Sua cabeça pode seguir revisando o que fez mesmo quando já existe base suficiente para encerrar o julgamento.")

    if pressao >= 3.6 or rum >= 3.6:
        leitura.append("mente_puxa_assunto_depois_do_fato")
        riscos.append("Depois de situações marcantes, sua mente pode continuar trabalhando nelas mais tempo do que seria útil.")

    if neuro <= 2.9:
        forcas.append("estabilidade_funcional")
        ajustes.append("Seu desgaste interno nem sempre aparece como drama. Muitas vezes ele vem em forma de revisão silenciosa e cobrança limpa.")

    if auto_rec <= 2.9:
        leitura.append("merito_demora_a_assentar")
        riscos.append("Você pode entender bastante, produzir bastante e ainda assim demorar para sentir por dentro o peso real do que já construiu.")

    if rec == "Recebo bem e sigo em frente":
        leitura.append("reconhecimento_passa_sem_fixar")
        riscos.append("Você pode receber validação, mas não deixar isso assentar de verdade dentro de você.")
    elif rec == "Agradeço, mas minimizo por hábito":
        leitura.append("minimizacao_do_proprio_tamanho")
        riscos.append("Sua tendência pode ser baixar o volume interno das próprias conquistas quase por reflexo.")
    elif rec == "Fico desconfortável e tento mudar de assunto":
        leitura.append("desconforto_com_reconhecimento")
        riscos.append("Quando o reconhecimento chega, ele pode tocar mais em exposição do que em descanso interno.")

    return {
        "leitura": leitura,
        "riscos": riscos,
        "forcas": forcas,
        "ajustes": ajustes,
    }


def engine_execucao_decisao(medias, derived, raw, followup_answers=None):
    followup_answers = followup_answers or {}

    leitura = []
    riscos = []
    forcas = []
    ajustes = []

    consc = medias["Conscienciosidade"]
    seg = medias["Seguranca"]
    risco = derived["tolerancia_risco"]
    auto_exec = derived["autonomia_execucao"]
    previs = derived.get("necessidade_previsibilidade", 3)
    planejamento = derived.get("planejamento_antecipado", 3)
    risco_exp = followup_answers.get("risco_expansao", "")

    if consc >= 3.5:
        leitura.append("execucao_estavel")
        forcas.append("consistencia_sem_muito_clima")

    if auto_exec >= 3.8:
        leitura.append("autonomia_para_executar")
        forcas.append("funciona_melhor_com_liberdade_do_que_com_supervisao")

    if planejamento >= 3.2 and previs >= 3.6:
        leitura.append("preparacao_antes_da_virada")

    if seg >= 3.4 and risco <= 3.0:
        leitura.append("entrada_com_base_suficiente")
        riscos.append("Você pode esperar maturidade demais do cenário antes do movimento estratégico.")

    if risco_exp == "Esperar informação suficiente antes de agir":
        leitura.append("timing_dependente_de_clareza")
        riscos.append("Pode perder vantagem de posição por exigir clareza acima do que o contexto entrega.")
    elif risco_exp == "Permanecer no que já funciona":
        leitura.append("continuidade_antes_de_expansao")
        riscos.append("Pode proteger demais o que já funciona e adiar movimentos que dependem mais de decisão do que de prova nova.")
    elif risco_exp == "Agir se o upside parecer claro":
        forcas.append("acao_condicionada_a_logica_de_ganho")

    if consc >= 3.5 and risco <= 2.9:
        ajustes.append("Seu risco não é falta de execução. É entrar tarde em oportunidades que premiam movimento antes da certeza total.")

    return {
        "leitura": leitura,
        "riscos": riscos,
        "forcas": forcas,
        "ajustes": ajustes,
    }


def engine_relacoes_limites(medias, derived, raw, followup_answers=None):
    followup_answers = followup_answers or {}

    leitura = []
    riscos = []
    forcas = []
    ajustes = []

    amab = medias["Amabilidade"]
    evita = derived["evita_conflito"]
    ass = derived["assertividade"]
    pres = derived["presenca_relacional"]
    pos = followup_answers.get("posicionamento_social", "")
    nat = followup_answers.get("natureza_conflito", "")

    if amab >= 3.3:
        leitura.append("adaptacao_relacional")
        forcas.append("convivencia_sem_teatralidade")

    if pres >= 3.5:
        forcas.append("presenca_relacional_estavel")

    if evita >= 3.2 and ass <= 3.1:
        leitura.append("limite_tardio")
        riscos.append("Os outros podem interpretar sua contenção como concordância ou disponibilidade.")

    if pos == "Depende muito da pessoa e do contexto":
        leitura.append("ajuste_relacional_antes_do_posicionamento")
        ajustes.append("Sua forma de se posicionar muda bastante conforme o vínculo e a leitura de abertura do outro.")

    if nat == "Desconforto real com tensão ou desaprovação":
        leitura.append("atrito_caro_demais")
        riscos.append("Você pode adiar conversas necessárias não por falta de clareza, mas pelo desgaste emocional antecipado.")
    elif nat == "Estratégia - acho desnecessário em muitos casos":
        leitura.append("seletividade_no_conflito")
        forcas.append("nao_compra_toda_fricao")
    elif nat == "Medo de prejudicar a relação":
        leitura.append("preserva_vinculo_antes_do_limite")
        riscos.append("Pode sacrificar clareza demais para preservar o vínculo.")
    elif nat == "Não sei - só percebo que evito":
        leitura.append("cede_antes_de_nomear")
        riscos.append("Você pode ceder espaço relacional antes mesmo de perceber que está cedendo.")

    if amab >= 3.3 and evita >= 3.2:
        ajustes.append("Sua nuance é força em relações maduras, mas pode virar terreno cedido em relações oportunistas.")

    return {
        "leitura": leitura,
        "riscos": riscos,
        "forcas": forcas,
        "ajustes": ajustes,
    }


def engine_valor_oportunidade(medias, derived, raw, followup_answers=None):
    followup_answers = followup_answers or {}

    leitura = []
    riscos = []
    forcas = []
    ajustes = []

    abund = medias["Abundancia"]
    auto_rec = derived["auto_reconhecimento"]
    risco = derived["tolerancia_risco"]
    autoex = derived["autoexigencia"]
    merecimento = derived.get("merecimento_economico", 3)
    impulso_expansao = derived.get("impulso_expansao", 3)
    comparacao_escassez = derived.get("comparacao_escassez", 3)
    rec = followup_answers.get("reconhecimento", "")
    risco_exp = followup_answers.get("risco_expansao", "")

    if abund <= 3.3:
        leitura.append("valor_ainda_nao_virou_avanco")
        riscos.append("Seu crescimento pode ficar abaixo do que sua capacidade já sustenta.")

    if merecimento <= 2.9:
        leitura.append("pedido_e_cobranca_pedem_autorizacao_alta")
        riscos.append("Pode existir competência real sem autorização interna proporcional para pedir, cobrar ou receber melhor.")

    if risco <= 3.0:
        leitura.append("ocupacao_de_espaco_passa_por_filtro_de_segurança")
        riscos.append("Você pode exigir garantias demais antes de pedir, propor, cobrar ou ocupar espaço.")

    if impulso_expansao <= 3.0:
        leitura.append("avanco_precisa_de_justificativa_forte")
        riscos.append("Seu movimento de crescimento pode depender de prova demais antes de se tornar ação concreta.")

    if comparacao_escassez >= 3.6:
        leitura.append("comparacao_encolhe_negociacao")
        riscos.append("Quando a referência vira insuficiência, parte da energia que poderia virar movimento vai para proteção e comparação.")

    if auto_rec <= 2.9 and merecimento <= 3.0:
        leitura.append("capacidade_sem_conversao_em_pedido")
        riscos.append("Você pode construir valor real sem convertê-lo em autorização prática para pedir, propor ou ocupar mais espaço.")

    if autoex >= 4.0:
        leitura.append("regua_sobe_antes_do_ganho_assentar")
        riscos.append("Sua régua sobe rápido demais e faz conquistas reais parecerem apenas obrigação básica.")

    if rec == "Agradeço, mas minimizo por hábito":
        leitura.append("merecimento_rebaixado_por_habito")
        riscos.append("Você pode reduzir internamente sinais legítimos de valor e manter o merecimento abaixo da evidência.")
    elif rec == "Fico desconfortável e tento mudar de assunto":
        leitura.append("desconforto_com_expansao_do_proprio_valor")
        riscos.append("Reconhecimento pode tocar mais em exposição do que em patrimônio interno.")
    elif rec == "Recebo bem e sigo em frente":
        ajustes.append("Você recebe o reconhecimento, mas nem sempre transforma isso em autorização prática para pedir mais, cobrar melhor ou avançar logo.")

    if risco_exp == "Esperar informação suficiente antes de agir":
        leitura.append("autorizacao_tardia_para_avanco")
        riscos.append("Você pode tratar expansão como algo que precisa estar completamente sustentado antes de ser ocupado.")
    elif risco_exp == "Permanecer no que já funciona":
        leitura.append("valor_fica_preso_no_que_ja_provou")
        riscos.append("Parte da abundância potencial pode ficar presa atrás de prudência excessiva.")
    elif risco_exp == "Agir se o upside parecer claro":
        forcas.append("movimento_quando_o_ganho_faz_sentido")

    if abund >= 3.4 and merecimento >= 3.1:
        forcas.append("potencial_de_expansao_mais_saudavel")

    if impulso_expansao >= 3.5 and comparacao_escassez <= 3.0:
        forcas.append("expansao_com_menos_contracao_defensiva")

    ajustes.append("Seu gargalo pode não estar em gerar valor, e sim em transformar capacidade em pedido, proposta, negociação e avanço concreto.")
    ajustes.append("Nesta versão, a leitura de valor precisa nascer de ocupação, merecimento, negociação e autorização para avançar — não só de prudência geral.")

    return {
        "leitura": leitura,
        "riscos": riscos,
        "forcas": forcas,
        "ajustes": ajustes,
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
    "entrada_tardia_por_criterio": {
        "peso": 8,
        "tipo": "decisao",
        "insight": "Você sabe tocar, mas às vezes entra tarde demais.",
        "descricao": "Seu gargalo não costuma ser manter o movimento; costuma ser decidir a hora de começar.",
        "custo": "Timing, posição e janela de oportunidade podem escapar antes da sua entrada."
    },
    "aquecimento_social_contextual": {
        "peso": 8,
        "tipo": "social",
        "insight": "Você não chega igual em todo lugar.",
        "descricao": "Sua presença aquece conforme a leitura de abertura, afinidade e qualidade do ambiente.",
        "custo": "Quem vê só o começo pode errar feio a leitura do seu tamanho social."
    },
    "mente_associativa_viva": {
        "peso": 8,
        "tipo": "interno",
        "insight": "Sua cabeça liga pontos o tempo todo.",
        "descricao": "Você aprende por conexão, revisa ideia boa sem apego e costuma enxergar relação entre assuntos com rapidez.",
        "custo": "Sem fechamento interno suficiente, a mente pode continuar aberta demais mesmo depois de já haver base."
    },
    "limite_tardio_por_preservacao": {
        "peso": 8,
        "tipo": "relacional",
        "insight": "Você costuma segurar o limite para preservar a relação.",
        "descricao": "Antes de endurecer, você tenta manter vínculo, clima e convivência minimamente intactos.",
        "custo": "Isso pode fazer o limite chegar tarde, já com acúmulo desnecessário."
    },
    "valor_sem_conversao_em_pedido": {
        "peso": 8,
        "tipo": "valor",
        "insight": "Você pode ter valor real e ainda assim pedir menos do que poderia.",
        "descricao": "Existe capacidade, mas a conversão disso em proposta, cobrança, negociação ou ocupação de espaço pode atrasar.",
        "custo": "Ganho, avanço e posicionamento ficam aquém do que o valor já sustentaria."
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
    "timing_vs_execucao": {
        "peso": 8,
        "texto": "Sua capacidade de executar pode ser maior do que a velocidade com que você se autoriza a começar."
    },
    "leitura_do_ambiente_vs_impacto_inicial": {
        "peso": 8,
        "texto": "Sua leitura fina do ambiente pode atrasar o impacto inicial da sua presença."
    },
    "mente_viva_vs_fechamento_interno": {
        "peso": 8,
        "texto": "Sua mente abre caminhos com facilidade, mas nem sempre fecha rápido o que já entendeu ou construiu."
    },
    "preservacao_do_vinculo_vs_limite_no_tempo_certo": {
        "peso": 8,
        "texto": "Sua vontade de preservar a relação pode atrasar o limite que protegeria você no tempo certo."
    },
    "capacidade_vs_conversao_em_avanco": {
        "peso": 9,
        "texto": "Sua capacidade pode estar pronta antes da sua autorização para pedir, negociar e ocupar espaço."
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
        padroes.append({"nome": "entrada_tardia_por_criterio", "peso": 8})

    if medias["Conscienciosidade"] >= 3.5:
        padroes.append({"nome": "execucao_consistente", "peso": 7})

    if pct_3_4 >= 75:
        padroes.append({"nome": "economia_de_extremos", "peso": 7})

    pos = followup_answers.get("posicionamento_social")
    if pos == "Depende muito da pessoa e do contexto":
        padroes.append({"nome": "exposicao_seletiva", "peso": 8})
        padroes.append({"nome": "aquecimento_social_contextual", "peso": 8})
    elif pos == "Adio ou evito para não criar tensão":
        padroes.append({"nome": "evita_atrito_contextual", "peso": 7})

    if derived["auto_reconhecimento"] <= 2.9:
        padroes.append({"nome": "competencia_nao_internalizada", "peso": 8})

    if medias["Abertura"] >= 3.7 and derived.get("flexibilidade_cognitiva", 3) >= 3.7:
        padroes.append({"nome": "mente_associativa_viva", "peso": 8})

    if derived["presenca_relacional"] >= 3.8 and raw.get(85, 3) >= 4 and raw.get(86, 3) >= 4:
        padroes.append({"nome": "presenca_relacional_rara", "peso": 6})

    if derived["visibilidade_pessoal"] <= 2.9 and raw.get(89, 3) <= 3:
        padroes.append({"nome": "autoexpressao_reduzida", "peso": 7})

    if derived["evita_conflito"] >= 3.2 and derived["assertividade"] <= 3.1:
        padroes.append({"nome": "limite_tardio_por_preservacao", "peso": 8})

    if derived.get("merecimento_economico", 3) <= 3.0 and derived.get("impulso_expansao", 3) >= 3.3:
        padroes.append({"nome": "valor_sem_conversao_em_pedido", "peso": 8})

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
        tensoes.append({"nome": "timing_vs_execucao", "peso": 8})

    if medias["Abertura"] > medias["Extroversao"]:
        tensoes.append({"nome": "complexidade_interna_vs_expressao_externa", "peso": 8})

    if medias["Abertura"] >= 3.7 and derived.get("flexibilidade_cognitiva", 3) >= 3.7:
        tensoes.append({"nome": "mente_viva_vs_fechamento_interno", "peso": 8})

    if derived["assertividade"] <= 3.0 and derived["evita_conflito"] >= 3.2:
        tensoes.append({"nome": "adaptacao_social_vs_clareza_de_posicao", "peso": 7})
        tensoes.append({"nome": "preservacao_do_vinculo_vs_limite_no_tempo_certo", "peso": 8})

    if medias["Neuroticismo"] <= 2.9 and derived["auto_reconhecimento"] <= 2.9:
        tensoes.append({"nome": "solidez_externa_vs_merito_interno", "peso": 8})

    if 2.8 <= medias["Extroversao"] <= 3.2 and derived["impulso_social"] <= 3.1:
        tensoes.append({"nome": "funcionalidade_social_vs_busca_de_palco", "peso": 6})
        tensoes.append({"nome": "leitura_do_ambiente_vs_impacto_inicial", "peso": 8})

    if derived.get("merecimento_economico", 3) <= 3.0 and derived.get("impulso_expansao", 3) >= 3.3:
        tensoes.append({"nome": "capacidade_vs_conversao_em_avanco", "peso": 9})

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
    subfacetas = compute_subfacets(respostas, respostas_ajustadas)
    evidencias_por_secao = build_all_section_evidences_v81(respostas, respostas_ajustadas)

    engine_presenca = engine_presenca_social(medias, derived, respostas, followup_answers)
    engine_interno = engine_mundo_interno(medias, derived, respostas, followup_answers)
    engine_execucao = engine_execucao_decisao(medias, derived, respostas, followup_answers)
    engine_relacoes = engine_relacoes_limites(medias, derived, respostas, followup_answers)
    engine_valor = engine_valor_oportunidade(medias, derived, respostas, followup_answers)

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
        "subfacetas": subfacetas,
        "evidencias_por_secao": evidencias_por_secao,
        "padroes": padroes,
        "tensoes": tensoes,
        "padroes_v62": padroes_v62,
        "tensoes_v62": tensoes_v62,
        "comportamentos_v62": comportamentos_v62,
        "engine_presenca": engine_presenca,
        "engine_mundo_interno": engine_interno,
        "engine_execucao_decisao": engine_execucao,
        "engine_relacoes_limites": engine_relacoes,
        "engine_valor_oportunidade": engine_valor,
        "followup_answers": followup_answers or {},
    }


# =============================================================
# RELATORIO
# =============================================================



PATTERN_DOMAINS_V71 = {
    "execucao": {"execucao_consistente", "prudencia_funcional", "economia_de_extremos", "entrada_tardia_por_criterio"},
    "presenca": {"merito_subcomunicado", "exposicao_seletiva", "autoexpressao_reduzida", "aquecimento_social_contextual"},
    "interno": {"clareza_interna_maior_que_presenca", "competencia_nao_internalizada", "mente_associativa_viva"},
    "relacional": {"evita_atrito_contextual", "presenca_relacional_rara", "limite_tardio_por_preservacao"},
    "valor": {"valor_sem_conversao_em_pedido"},
}

TENSION_DOMAINS_V71 = {
    "valor_real_vs_presenca_percebida": "presenca",
    "seguranca_vs_expansao": "execucao",
    "timing_vs_execucao": "execucao",
    "complexidade_interna_vs_expressao_externa": "interno",
    "mente_viva_vs_fechamento_interno": "interno",
    "adaptacao_social_vs_clareza_de_posicao": "relacional",
    "preservacao_do_vinculo_vs_limite_no_tempo_certo": "relacional",
    "solidez_externa_vs_merito_interno": "interno",
    "funcionalidade_social_vs_busca_de_palco": "presenca",
    "leitura_do_ambiente_vs_impacto_inicial": "presenca",
    "capacidade_vs_conversao_em_avanco": "valor",
}


def _pick_items_v71(items, used_tags, limit=2):
    selected = []
    for item in items:
        tag = item.get("tag")
        if tag and tag in used_tags:
            continue
        selected.append(item)
        if tag:
            used_tags.add(tag)
        if len(selected) >= limit:
            break
    return selected


def build_section_map_v71(perfil):
    medias = perfil["medias"]
    derived = perfil["derived"]
    followups = perfil.get("followup_answers", {})
    padroes = perfil.get("padroes_v62", [])
    tensoes = perfil.get("tensoes_v62", [])
    comportamentos = perfil.get("comportamentos_v62", [])
    subfacetas = perfil.get("subfacetas", {})
    evidencias_por_secao = perfil.get("evidencias_por_secao", {})

    annotated_patterns = []
    for p in padroes:
        nome = p["nome"]
        matched = False
        for dominio, nomes in PATTERN_DOMAINS_V71.items():
            if nome in nomes:
                annotated_patterns.append({**p, "dominio": dominio, "tag": dominio})
                matched = True
                break
        if not matched:
            annotated_patterns.append({**p, "dominio": "geral", "tag": "geral"})

    annotated_tensions = []
    for t in tensoes:
        nome = t["nome"]
        dominio = TENSION_DOMAINS_V71.get(nome, "geral")
        annotated_tensions.append({**t, "dominio": dominio, "tag": f"ten_{dominio}"})

    used = set()
    return {
        "central": {
            "patterns": annotated_patterns[:3],
            "tensions": annotated_tensions[:1],
            "subfacets": get_top_subfacets_for_section(subfacetas, "central"),
            "evidencias": evidencias_por_secao.get("central", []),
        },
        "execucao_decisao": {
            "patterns": _pick_items_v71([p for p in annotated_patterns if p["dominio"] == "execucao"], used, limit=2),
            "tensions": _pick_items_v71([t for t in annotated_tensions if t["dominio"] == "execucao"], used, limit=1),
            "subfacets": get_top_subfacets_for_section(subfacetas, "execucao_decisao"),
            "evidencias": evidencias_por_secao.get("execucao_decisao", []),
            "facts": {
                "Conscienciosidade": medias["Conscienciosidade"],
                "Seguranca": medias["Seguranca"],
                "autonomia_execucao": derived["autonomia_execucao"],
                "tolerancia_risco": derived["tolerancia_risco"],
                "planejamento_antecipado": derived.get("planejamento_antecipado", 3),
                "necessidade_previsibilidade": derived.get("necessidade_previsibilidade", 3),
            },
        },
        "presenca_expressao": {
            "patterns": _pick_items_v71([p for p in annotated_patterns if p["dominio"] == "presenca"], used, limit=2),
            "tensions": _pick_items_v71([t for t in annotated_tensions if t["dominio"] == "presenca"], used, limit=1),
            "subfacets": get_top_subfacets_for_section(subfacetas, "presenca_expressao"),
            "evidencias": evidencias_por_secao.get("presenca_expressao", []),
            "facts": {
                "Extroversao": medias["Extroversao"],
                "visibilidade_pessoal": derived["visibilidade_pessoal"],
                "assertividade": derived["assertividade"],
                "posicionamento_social": followups.get("posicionamento_social", ""),
            },
        },
        "mundo_interno": {
            "patterns": _pick_items_v71([p for p in annotated_patterns if p["dominio"] == "interno"], used, limit=2),
            "tensions": _pick_items_v71([t for t in annotated_tensions if t["dominio"] == "interno"], used, limit=1),
            "subfacets": get_top_subfacets_for_section(subfacetas, "mundo_interno"),
            "evidencias": evidencias_por_secao.get("mundo_interno", []),
            "facts": {
                "Abertura": medias["Abertura"],
                "Neuroticismo": medias["Neuroticismo"],
                "auto_reconhecimento": derived["auto_reconhecimento"],
                "autoexigencia": derived["autoexigencia"],
                "flexibilidade_cognitiva": derived.get("flexibilidade_cognitiva", 3),
                "conforto_abstracao": derived.get("conforto_abstracao", 3),
                "sensibilidade_pressao": derived.get("sensibilidade_pressao", 3),
                "ruminacao_pos_evento": derived.get("ruminacao_pos_evento", 3),
                "reconhecimento": followups.get("reconhecimento", ""),
            },
        },
        "relacoes_conflito": {
            "patterns": _pick_items_v71([p for p in annotated_patterns if p["dominio"] == "relacional"], used, limit=2),
            "tensions": _pick_items_v71([t for t in annotated_tensions if t["dominio"] == "relacional"], used, limit=1),
            "subfacets": get_top_subfacets_for_section(subfacetas, "relacoes_conflito"),
            "evidencias": evidencias_por_secao.get("relacoes_conflito", []),
            "facts": {
                "Amabilidade": medias["Amabilidade"],
                "presenca_relacional": derived["presenca_relacional"],
                "evita_conflito": derived["evita_conflito"],
                "assertividade": derived["assertividade"],
            },
        },
        "valor_oportunidade": {
            "patterns": _pick_items_v71([p for p in annotated_patterns if p["dominio"] == "valor"], used, limit=2),
            "tensions": _pick_items_v71([t for t in annotated_tensions if t["dominio"] == "valor"], used, limit=1),
            "subfacets": get_top_subfacets_for_section(subfacetas, "valor_oportunidade"),
            "evidencias": evidencias_por_secao.get("valor_oportunidade", []),
            "facts": [
                {"tipo": "media", "nome": "Abundancia", "valor": medias["Abundancia"]},
                {"tipo": "derived", "nome": "auto_reconhecimento", "valor": derived["auto_reconhecimento"]},
                {"tipo": "derived", "nome": "tolerancia_risco", "valor": derived["tolerancia_risco"]},
                {"tipo": "derived", "nome": "merecimento_economico", "valor": derived.get("merecimento_economico", 3)},
                {"tipo": "derived", "nome": "impulso_expansao", "valor": derived.get("impulso_expansao", 3)},
                {"tipo": "derived", "nome": "comparacao_escassez", "valor": derived.get("comparacao_escassez", 3)},
                {"tipo": "followup", "nome": "reconhecimento", "valor": followups.get("reconhecimento", "")},
                {"tipo": "followup", "nome": "risco_expansao", "valor": followups.get("risco_expansao", "")},
            ]
        },
        "comportamentos": comportamentos,
    }


def format_section_inputs_v71(section):
    lines = []
    for sf in section.get("subfacets", []):
        lines.append(f"- subfaceta: {sf['label']} = {sf['score']:.2f} [{sf['intensidade']}] | itens {sf['itens']}")
    for ev in section.get("evidencias", []):
        inv = "sim" if ev["invertida"] else "nao"
        lines.append(f"- evidencia: Q{ev['q']} | bruto={ev['bruto']} | ajustado={ev['ajustado']} | invertida={inv} | {ev['texto']} | leitura: {ev['leitura']}")
    for p in section.get("patterns", []):
        info = PATTERN_LIBRARY.get(p["nome"], {})
        lines.append(f"- padrão ({p['peso']}): {info.get('insight','')} | {info.get('descricao','')}")
    for t in section.get("tensions", []):
        info = TENSION_LIBRARY.get(t["nome"], {})
        lines.append(f"- tensão ({t['peso']}): {info.get('texto','')}")
    facts = section.get("facts", {})
    if isinstance(facts, dict):
        for k, v in facts.items():
            lines.append(f"- dado: {k} = {v}")
    elif isinstance(facts, list):
        for item in facts:
            lines.append(f"- {item['tipo']}: {item['nome']} = {item['valor']}")
    return "\n".join(lines) if lines else "- sem insumos específicos"


def gerar_resumo_base(perfil):
    padroes_v62 = perfil.get("padroes_v62", [])
    tensoes_v62 = perfil.get("tensoes_v62", [])
    comportamentos_v62 = perfil.get("comportamentos_v62", [])
    derived = perfil["derived"]
    subfacetas = perfil.get("subfacetas", {})

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

    if subfacetas:
        partes.append("Subfacetas com maior evidência:")
        top_subfacetas = sorted(subfacetas.values(), key=lambda x: abs(x["score"] - 3), reverse=True)[:8]
        for sf in top_subfacetas:
            partes.append(f"- {sf['label']}: {sf['score']:.2f} [{sf['intensidade']}] | itens {sf['itens']}")

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


def validate_generated_report_v81(texto):
    problemas = []
    verificacoes = [
        (r"se quiser", "voz conversacional proibida"),
        (r"eu posso", "voz de assistente proibida"),
        (r"posso transformar", "oferta de serviço proibida"),
        (r"nao por .*?, mas por", "contraste artificial do tipo nao X, mas Y"),
        (r"não por .*?, mas por", "contraste artificial do tipo não X, mas Y"),
        (r"não é .*?é ", "construção por negação comparativa"),
        (r"nao e .*?e ", "construção por negação comparativa"),
        (r"causas principais definidas", "vazamento de raciocínio interno"),
        (r"integração entre", "abertura abstrata demais"),
        (r"amplitude de pensamento", "linguagem abstrata demais"),
        (r"trajetória mais estável", "formulação genérica demais"),
        (r"esse encontro produz", "frase bonita demais e pouco direta"),
        (r"há curiosidade genuína", "abertura descritiva genérica"),
        (r"o ponto mais sensível do processo", "entrada elegante demais para crítica prática"),
    ]
    texto_limpo = texto.lower()
    for padrao, descricao in verificacoes:
        if re.search(padrao, texto_limpo, flags=re.IGNORECASE | re.DOTALL):
            problemas.append(descricao)

    if "1. eixo central" in texto_limpo and "você" not in texto_limpo:
        problemas.append("texto distante demais; falta tratamento direto da pessoa")

    if len(re.findall(r"\bcapacidade de\b", texto_limpo)) >= 3:
        problemas.append("repetição de formulação abstrata")

    return list(dict.fromkeys(problemas))


def sanitize_report_output_v81(texto):
    if not texto:
        return texto

    texto = texto.replace("\r\n", "\n")

    padroes_linha_proibida = [
        r"^\s*se quiser.*$",
        r"^\s*se desejar.*$",
        r"^\s*caso queira.*$",
        r"^\s*eu posso.*$",
        r"^\s*posso transformar.*$",
        r"^\s*posso adaptar.*$",
        r"^\s*posso converter.*$",
        r"^\s*posso te ajudar.*$",
        r"^\s*se preferir.*$",
    ]

    linhas = []
    for linha in texto.split("\n"):
        linha_limpa = linha.strip().lower()
        if any(re.search(p, linha_limpa, flags=re.IGNORECASE) for p in padroes_linha_proibida):
            continue
        if "causas principais definidas" in linha_limpa:
            continue
        linhas.append(linha)

    texto = "\n".join(linhas)

    match_secao_9 = re.search(r"(^|\n)(9\.[^\n]*próximos passos[^\n]*\n)(.*)$", texto, flags=re.IGNORECASE | re.DOTALL)
    if match_secao_9:
        cabecalho = match_secao_9.group(2)
        corpo = match_secao_9.group(3)
        linhas_validas = []
        for linha in corpo.split("\n"):
            linha_limpa = linha.strip()
            if not linha_limpa:
                continue
            baixa = linha_limpa.lower()
            if any(expr in baixa for expr in ["se quiser", "eu posso", "posso transformar", "caso queira", "se desejar", "posso adaptar", "posso converter"]):
                continue
            linhas_validas.append(linha_limpa)

        if not linhas_validas:
            linhas_validas = [
                "1. Escolha uma situação concreta desta semana para se posicionar com mais clareza, sem adiar a conversa necessária.",
                "2. Registre por escrito uma entrega recente de valor e o resultado objetivo que ela gerou, para consolidar mérito com evidência.",
                "3. Defina um movimento pequeno de expansão com prazo curto, mesmo sem esperar sensação de certeza total.",
            ]

        texto = texto[:match_secao_9.start()] + ("\n" if not texto[:match_secao_9.start()].endswith("\n") else "") + cabecalho + "\n".join(linhas_validas)

    texto = re.sub(r"\n{3,}", "\n\n", texto).strip()
    return texto


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
    section_map = build_section_map_v71(perfil)
    subfacetas = perfil.get("subfacetas", {})
    engine_presenca = perfil.get("engine_presenca", {})
    engine_mundo_interno = perfil.get("engine_mundo_interno", {})
    engine_execucao = perfil.get("engine_execucao_decisao", {})
    engine_relacoes = perfil.get("engine_relacoes_limites", {})
    engine_valor = perfil.get("engine_valor_oportunidade", {})

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
        "O perfil tem compressão alta de respostas. Preserve nuance e precisão, mas não use isso como desculpa para repetir o mesmo eixo central em todas as seções."
        if compressao_alta else
        "O perfil tem contraste suficiente para afirmações mais nítidas e concretas."
    )

    bloco_engine_presenca = "\n".join(
        [f"- leitura: {x}" for x in engine_presenca.get("leitura", [])] +
        [f"- força: {x}" for x in engine_presenca.get("forcas", [])] +
        [f"- risco: {x}" for x in engine_presenca.get("riscos", [])] +
        [f"- ajuste: {x}" for x in engine_presenca.get("ajustes", [])]
    ) if engine_presenca else "- sem dados extras"

    bloco_engine_interno = "\n".join(
        [f"- leitura: {x}" for x in engine_mundo_interno.get("leitura", [])] +
        [f"- força: {x}" for x in engine_mundo_interno.get("forcas", [])] +
        [f"- risco: {x}" for x in engine_mundo_interno.get("riscos", [])] +
        [f"- ajuste: {x}" for x in engine_mundo_interno.get("ajustes", [])]
    ) if engine_mundo_interno else "- sem dados extras"

    bloco_engine_execucao = "\n".join(
        [f"- leitura: {x}" for x in engine_execucao.get("leitura", [])] +
        [f"- força: {x}" for x in engine_execucao.get("forcas", [])] +
        [f"- risco: {x}" for x in engine_execucao.get("riscos", [])] +
        [f"- ajuste: {x}" for x in engine_execucao.get("ajustes", [])]
    ) if engine_execucao else "- sem dados extras"

    bloco_engine_relacoes = "\n".join(
        [f"- leitura: {x}" for x in engine_relacoes.get("leitura", [])] +
        [f"- força: {x}" for x in engine_relacoes.get("forcas", [])] +
        [f"- risco: {x}" for x in engine_relacoes.get("riscos", [])] +
        [f"- ajuste: {x}" for x in engine_relacoes.get("ajustes", [])]
    ) if engine_relacoes else "- sem dados extras"

    bloco_engine_valor = "\n".join(
        [f"- leitura: {x}" for x in engine_valor.get("leitura", [])] +
        [f"- força: {x}" for x in engine_valor.get("forcas", [])] +
        [f"- risco: {x}" for x in engine_valor.get("riscos", [])] +
        [f"- ajuste: {x}" for x in engine_valor.get("ajustes", [])]
    ) if engine_valor else "- sem dados extras"

    linhas_subfacetas = "\n".join([
        f"- {sf['label']}: {sf['score']:.2f} [{sf['intensidade']}] | bloco={sf['bloco']} | itens={sf['itens']}"
        for sf in sorted(subfacetas.values(), key=lambda x: abs(x["score"] - 3), reverse=True)[:12]
    ]) if subfacetas else "- sem subfacetas adicionais"

    prompt = f"""
Você é um analista de comportamento humano altamente preciso.
Seu trabalho é produzir um relatório fiel, profundo, multidimensional e psicologicamente impactante.

OBJETIVO DA VERSÃO {APP_VERSION}:
Gerar um relatório comportamental com linguagem direta, profundidade real, cobertura mais ampla do perfil e separação causal consistente entre seções. O texto final deve soar humano, claro e preciso, sem repetir a mesma lógica com vocabulário diferente e sem usar contrastes artificiais para parecer sofisticado.

REGRA CENTRAL:
Cada seção deve ter obrigatoriamente uma pergunta principal própria, uma lente explicativa própria, uma fonte principal de dados própria e uma causa principal própria.
Não basta mudar o nome da causa. Se duas seções derivarem da mesma tese-mãe, da mesma família causal, do mesmo gargalo estrutural ou da mesma explicação-base com roupas diferentes, o relatório está errado.

REGRA DE EXCLUSIVIDADE CAUSAL FORÇADA:
Antes de escrever o relatório, defina silenciosamente 6 causas principais diferentes, uma para cada seção.
Essas causas são internas e não podem aparecer no texto final como lista, introdução metodológica ou explicação de bastidor.
Nenhuma delas pode ser variação semântica, aplicação lateral, consequência expandida ou tradução contextual de outra.
Exemplos de causas diferentes: necessidade de base antes de agir; leitura contextual do ambiente; dificuldade de consolidar mérito interno; preservação do vínculo antes do atrito; filtro alto de merecimento; processamento interno profundo.
Exemplos de famílias causais proibidas em mais de uma seção: baixa visibilidade; pouca projeção; valor não percebido; presença menor que capacidade; você faz mais do que mostra.

PERGUNTA ÚNICA POR SEÇÃO:
- EIXO CENTRAL responde: qual é o padrão dominante do seu funcionamento?
- EXECUÇÃO responde: como você decide, processa variáveis e entra em ação?
- PRESENÇA responde: como você se comporta socialmente em diferentes contextos?
- MUNDO INTERNO responde: como você se organiza por dentro?
- RELAÇÕES responde: como você lida com limite, convivência e conflito?
- VALOR responde: como você transforma capacidade em avanço real?
Se uma seção responder à pergunta central da outra, o relatório está errado.

LENTE EXCLUSIVA POR SEÇÃO:
- EIXO CENTRAL = padrão organizador global
- EXECUÇÃO = processo de decisão
- PRESENÇA = comportamento social contextual
- MUNDO INTERNO = processamento interno e autoimagem
- RELAÇÕES = negociação de espaço e limite
- VALOR = conversão de capacidade em oportunidade
Se duas seções usarem a mesma lente, o relatório está errado.

FONTE PRINCIPAL MANDATÓRIA POR SEÇÃO:
A fonte principal da seção não é apenas preferencial; ela é mandatória e deve comandar a explicação causal daquela parte.
- EIXO CENTRAL deve ser construído principalmente com PADROES PRIORIZADOS + TENSOES PRIORIZADAS
- EXECUÇÃO deve ser construída principalmente com ENGINE EXTRA - EXECUÇÃO/DECISÃO + insumos da seção 2
- PRESENÇA deve ser construída principalmente com ENGINE EXTRA - PRESENÇA SOCIAL + insumos da seção 3
- MUNDO INTERNO deve ser construída principalmente com ENGINE EXTRA - MUNDO INTERNO + insumos da seção 4
- RELAÇÕES deve ser construída principalmente com ENGINE EXTRA - RELAÇÕES/LIMITES + insumos da seção 5
- VALOR deve ser construída principalmente com ENGINE EXTRA - VALOR/OPORTUNIDADE + insumos da seção 6
As demais fontes só podem entrar como apoio secundário.
Se a interpretação global do perfil estiver comandando uma seção no lugar da sua fonte local, o relatório está errado.

REGRAS CRÍTICAS:
1. PROIBIÇÃO DE REUSO DE CAUSA: uma causa usada como principal em uma seção não pode reaparecer em outra nem com outro nome, nem como versão social, nem como versão relacional, nem como versão de valor, nem como consequência expandida da mesma tese-base.
2. PROIBIÇÃO DE REPETIÇÃO SEMÂNTICA: é proibido repetir a mesma ideia com palavras diferentes.
3. Considere como repetição semântica também qualquer conjunto de frases que compartilhe a mesma tese-mãe.
4. Exemplo de família de tese proibida de se espalhar: "você entrega mais do que projeta", "seu valor aparece menos do que deveria", "sua presença não acompanha sua capacidade" e "você faz mais do que mostra" contam como a mesma família explicativa.
5. DIVERSIDADE REAL: cada seção deve conter pelo menos um mecanismo central, um custo específico e um potencial específico que não tenham sido usados como eixo em outra seção.
6. NOVIDADE REAL POR PARÁGRAFO: cada parágrafo deve acrescentar uma camada nova de compreensão. Não reescreva a mesma lógica com palavras mais bonitas.
7. COBERTURA AMPLIADA: aproveite, quando houver evidência nos dados, áreas que costumam ficar subexploradas, como abertura cognitiva, modo de aprender, repertório mental, autonomia silenciosa, qualidade de escuta, constância sem teatralidade, assertividade contextual e diferença entre sociabilidade e protagonismo social.
8. NÃO reduza a pessoa a um único padrão.
9. NÃO parafraseie perguntas do teste.
10. Use follow-ups como desempate real de interpretação.
11. Se houver compressão de respostas, trate isso como modulador do tom, não como desculpa para superficialidade.
12. A seção de direção prática precisa trazer 3 movimentos em áreas realmente diferentes.
13. A seção 9 é estritamente prática e impessoal: não use primeira pessoa, não ofereça ajuda, não diga "se quiser", não diga "eu posso" e não fale como assistente.

PROTOCOLO INTERNO OBRIGATÓRIO ANTES DE ESCREVER CADA SEÇÃO:
Antes de escrever cada seção, faça silenciosamente uma ficha interna com estes campos:
- pergunta central da seção
- causa principal da seção
- família causal proibida
- fonte dominante da seção
- área nova do perfil que pode ser salientada ali
- frase-resumo proibida
Se a família causal proibida reaparecer como eixo, custo central, fechamento central ou frase-resumo de outra seção, reescreva antes de seguir.

MODULADOR DE COMPRESSÃO:
{modulador_tom}

DADOS GERAIS DO PERFIL:
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
- flexibilidade_cognitiva: {derived.get('flexibilidade_cognitiva', 3):.2f}
- conforto_abstracao: {derived.get('conforto_abstracao', 3):.2f}
- planejamento_antecipado: {derived.get('planejamento_antecipado', 3):.2f}
- sensibilidade_pressao: {derived.get('sensibilidade_pressao', 3):.2f}
- ruminacao_pos_evento: {derived.get('ruminacao_pos_evento', 3):.2f}
- necessidade_previsibilidade: {derived.get('necessidade_previsibilidade', 3):.2f}
- merecimento_economico: {derived.get('merecimento_economico', 3):.2f}
- impulso_expansao: {derived.get('impulso_expansao', 3):.2f}
- comparacao_escassez: {derived.get('comparacao_escassez', 3):.2f}

PADROES PRIORIZADOS:
{linhas_padroes}

TENSOES PRIORIZADAS:
{linhas_tensoes}

COMPORTAMENTOS DOMINANTES:
{linhas_comportamentos}

FOLLOW-UPS:
{linhas_followups}

RESUMO BASE:
{resumo_base}

SUBFACETAS DE MAIOR EVIDÊNCIA:
{linhas_subfacetas}

ENGINE EXTRA - PRESENÇA SOCIAL:
{bloco_engine_presenca}

ENGINE EXTRA - MUNDO INTERNO:
{bloco_engine_interno}

ENGINE EXTRA - EXECUÇÃO/DECISÃO:
{bloco_engine_execucao}

ENGINE EXTRA - RELAÇÕES/LIMITES:
{bloco_engine_relacoes}

ENGINE EXTRA - VALOR/OPORTUNIDADE:
{bloco_engine_valor}

INSUMOS POR SEÇÃO:
1. EIXO CENTRAL DO SEU FUNCIONAMENTO
{format_section_inputs_v71(section_map['central'])}

2. EXECUÇÃO E TOMADA DE DECISÃO
{format_section_inputs_v71(section_map['execucao_decisao'])}

3. PRESENÇA SOCIAL E EXPRESSÃO EXTERNA
{format_section_inputs_v71(section_map['presenca_expressao'])}

4. MUNDO INTERNO E AUTOIMAGEM
{format_section_inputs_v71(section_map['mundo_interno'])}

5. RELAÇÕES, LIMITES E CONFLITO
{format_section_inputs_v71(section_map['relacoes_conflito'])}

6. VALOR, OPORTUNIDADE E MERECIMENTO
{format_section_inputs_v71(section_map['valor_oportunidade'])}

ESTRUTURA OBRIGATORIA:
1. EIXO CENTRAL DO SEU FUNCIONAMENTO
2. EXECUÇÃO E TOMADA DE DECISÃO
3. PRESENÇA SOCIAL E EXPRESSÃO EXTERNA
4. MUNDO INTERNO E AUTOIMAGEM
5. RELAÇÕES, LIMITES E CONFLITO
6. VALOR, OPORTUNIDADE E MERECIMENTO
7. DIREÇÃO PRÁTICA
8. FRASE FINAL DE IMPACTO
9. PRÓXIMOS PASSOS

INSTRUÇÕES ESPECÍFICAS POR SEÇÃO:
- BLOCO 1: diga logo, em português simples, qual é o jeito principal de a pessoa funcionar. Nomeie a força e o custo. Esta seção deve conter pelo menos uma frase que poderia ser repetida para resumir a pessoa sem perder a essência.
- EXECUÇÃO: diga com clareza como a pessoa decide, onde ela trava, o que faz ela entrar em ação e qual é o custo prático disso. Troque formulações elegantes por algo que a pessoa reconheça na vida real.
- PRESENÇA: diga como a pessoa aparece nos ambientes, quando ela se solta, quando ela se segura e o que isso produz nos outros. Não usar invisibilidade ou reconhecimento como explicação principal.
- MUNDO INTERNO: diga como a pessoa pensa, se cobra, se reconhece e se desgasta por dentro. Troque abstrações como "densidade" e "elaboração" por leitura concreta de vida mental.
- RELAÇÕES: diga como a pessoa cuida do vínculo, onde ela cede demais, onde ela segura demais e o preço emocional disso. Diferencie relação de presença social.
- VALOR: diga de forma concreta como a pessoa lida com pedir, cobrar, negociar, ocupar espaço e transformar capacidade em avanço. Esta seção precisa soar prática, não conceitual.
- DIREÇÃO PRÁTICA: cada ação deve atacar um mecanismo diferente e ser escrita como orientação simples, executável e sem linguagem de consultoria.
- FRASE FINAL: deve ser curta, forte e memorável. Precisa soar como verdade direta, não como frase bonita.
- PRÓXIMOS PASSOS: escreva ações concretas, observáveis e executáveis pela própria pessoa. É proibido usar voz conversacional, convite, oferta de ajuda, primeira pessoa do assistente ou qualquer formulação do tipo "se quiser", "eu posso" ou "posso transformar".
- QUALQUER BLOCO FINAL DE RESUMO, TRAÇOS, FORTALEZAS OU DESAFIOS: se existir, ele não pode repetir literalmente nem por equivalência as teses centrais já usadas nas seções anteriores. Ele deve acrescentar informação complementar, e não recompactar o relatório em frases curtas.

REGRA DE HUMANIZAÇÃO:
O texto final precisa falar a língua do povo sem perder precisão.
Escreva como quem traduz uma verdade psicológica complexa para algo que a pessoa entende na hora.
Cada seção precisa nomear com clareza: o padrão principal, a força disso, o custo disso e como isso aparece na vida real.
Prefira frases curtas, concretas e memoráveis.
Evite abstrações elegantes que soem inteligentes mas não transmitam mensagem.
Se puder dizer "você demora para começar porque quer clareza antes de agir", não escreva "seu movimento costuma ser precedido por entendimento".
Se puder dizer "você faz bem, mas nem sempre sente que já pode ocupar o espaço que merece", não escreva formulações abstratas sobre crédito interno.
Não introduza uma característica dizendo primeiro o que a pessoa não é.
Evite construções como "não é X, nem Y; é Z", "não porque..., mas porque..." e outros contrastes negativos usados apenas para criar efeito de profundidade.
Cada seção deve ter pelo menos uma frase que poderia ser lembrada depois de horas.
Não use no texto final palavras como "engine", "modelo", "sistema" ou "eixo".
Não use linguagem solene demais, acadêmica demais ou elegante demais.

TESTES FINAIS BLOQUEANTES:
1. Se a pessoa puder ler uma seção e dizer "falou bonito mas não disse nada", o relatório está errado.
2. Se uma seção não puder ser resumida em uma frase simples e forte, o relatório está errado.
3. Se duas seções puderem ser resumidas pela mesma tese-mãe, o relatório está errado.
4. Se duas seções tiverem a mesma causa principal, o relatório está errado.
5. Se presença e valor falarem de percepção, visibilidade, reconhecimento ou subestimação como eixo, o relatório está errado.
6. Se uma seção estiver usando como motor causal principal uma fonte que não seja a dela, o relatório está errado.
7. Se um bloco final de resumo, traços, fortalezas ou desafios recompuser em frases curtas o que o corpo do relatório já disse, o relatório está errado.
8. Se a frase final resumir a tese do bloco 1, o relatório está errado.
9. Se aparecer no texto final qualquer lista de causas internas, preparação metodológica ou bastidor do raciocínio, o relatório está errado.
10. Se o texto depender de contrastes negativos artificiais para descrever a pessoa, o relatório está errado.
11. Se áreas claramente presentes nos dados continuarem sem ser salientadas porque a mesma tese ocupou espaço demais, o relatório está errado.
12. Se o texto parecer técnico, frio, ornamental ou com cara de ferramenta, o relatório está errado.
13. Se a leitura parecer servir para quase qualquer pessoa, o relatório está errado.
Se qualquer teste falhar, reescreva antes de finalizar.
"""


    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um analista de comportamento humano que escreve de forma simples, certeira, humana e memorável. "
                        "Seu trabalho é transformar padrões de resposta em frases que a pessoa entende na hora e reconhece como verdade da própria vida. "
                        "Você não escreve para impressionar. Você escreve para acertar. "
                        "Você não parafraseia perguntas. Você nomeia mecanismo, força, custo e efeito prático. "
                        "Você deve aplicar exclusividade causal forçada: cada seção precisa nascer de uma causa principal realmente diferente, e não de variações elegantes da mesma tese-mãe. "
                        "Você não deve externalizar o seu planejamento interno, nem usar contrastes negativos artificiais para parecer profundo. "
                        "Cada seção precisa responder a uma pergunta diferente, usar sua fonte principal correta, salientar uma área real do perfil que ainda não tenha sido explorada e soar como alguém dizendo uma verdade importante de forma clara, e não como saída de ferramenta."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.28,
        )
        texto_final = response.choices[0].message.content
        problemas = validate_generated_report_v81(texto_final)
        if problemas:
            lista_problemas = "- " + "\n- ".join(problemas)
            prompt_revisao = f"""Reescreva integralmente o relatório abaixo mantendo a mesma estrutura numerada de 1 a 9.

Problemas detectados na primeira versão:
{lista_problemas}

Regras inegociáveis:
- Não usar contrastes do tipo “não X, mas Y”.
- Não usar voz conversacional do assistente.
- A seção 9 deve conter apenas próximos passos concretos, impessoais e acionáveis.
- Não mostrar bastidores, causas internas ou planejamento oculto.
- Trocar linguagem bonita demais por linguagem simples, direta e memorável.
- Cada seção deve dizer claramente o que a pessoa faz, qual é a força disso, qual é o custo disso e como isso aparece na prática.
- Se uma frase puder ser dita de forma mais simples e mais forte, reescreva.
- Preserve profundidade e exclusividade causal, mas fale como gente.

Texto a reescrever:
{texto_final}
"""
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você revisa relatórios comportamentais já escritos para remover artificialidade, abstração vazia, voz de assistente e vazamentos metodológicos sem empobrecer o conteúdo. "
                            "Você mantém a estrutura numerada, aprofunda o que for preciso e troca formulações bonitas demais por frases simples, fortes, humanas e memoráveis."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt_revisao
                    }
                ],
                temperature=0.2,
            )
            texto_final = response.choices[0].message.content
        texto_final = sanitize_report_output_v81(texto_final)
        return texto_final, bloco_forcas, bloco_desafios
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

    st.subheader("9.1 Engine Extra - Presença Social")
    st.json(perfil.get("engine_presenca", {}))

    st.subheader("9.2 Engine Extra - Mundo Interno")
    st.json(perfil.get("engine_mundo_interno", {}))

    st.subheader("9.3 Engine Extra - Execução/Decisão")
    st.json(perfil.get("engine_execucao_decisao", {}))

    st.subheader("9.4 Engine Extra - Relações/Limites")
    st.json(perfil.get("engine_relacoes_limites", {}))

    st.subheader("9.5 Engine Extra - Valor/Oportunidade")
    st.json(perfil.get("engine_valor_oportunidade", {}))

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
                "Quando você faz algo bem, nem sempre dá a si mesmo o devido mérito."
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

    # V7.9: o relatório principal não recebe mais um bloco automático de traços no final,
    # para evitar re-resumo redundante e reintrodução da mesma tese em formato comprimido.
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
