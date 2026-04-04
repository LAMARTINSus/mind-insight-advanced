import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mind Insight Advanced", page_icon="🧠", layout="wide")

# =========================================================
# STYLE
# =========================================================
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 950px;
}
.question-card {
    border-radius: 18px;
    padding: 24px;
    margin-top: 10px;
    margin-bottom: 20px;
    border: 1px solid #ddd;
}
.card-a {
    background: #faf5ff;
}
.card-b {
    background: #f5f3ff;
}
.question-badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    background: #7c3aed;
    color: white;
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 14px;
}
.question-title {
    font-size: 1.35rem;
    font-weight: 700;
    line-height: 1.5;
    margin-bottom: 6px;
}
.question-sub {
    color: #666;
    margin-bottom: 14px;
}
.section-title {
    margin-top: 26px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# QUESTIONS
# =========================================================
questions = {
    1: "Gosto de experimentar novas ideias e atividades.",
    2: "Sou organizado e planejo minhas tarefas com antecedência.",
    3: "Me sinto energizado em grupos grandes de pessoas.",
    4: "Sou compassivo e priorizo as necessidades dos outros.",
    5: "Fico ansioso em situações de incerteza.",
    6: "Prefiro rotinas previsíveis a mudanças inesperadas.",
    7: "Tenho facilidade para me concentrar em uma tarefa por horas.",
    8: "Evito conflitos para manter a harmonia.",
    9: "Sou criativo e penso fora da caixa.",
    10: "Me irrito facilmente com erros alheios.",
    11: "Gosto de ser o centro das atenções.",
    12: "Sou disciplinado com prazos e compromissos.",
    13: "Me preocupo excessivamente com o futuro.",
    14: "Valorizo a lealdade acima de tudo nas relações.",
    15: "Busco conhecimento por prazer, não por obrigação.",
    16: "Tomo decisões rápidas baseadas em intuição.",
    17: "Analiso todos os detalhes antes de agir.",
    18: "Sou direto e falo o que penso, mesmo que incomode.",
    19: "Prefiro trabalhar sozinho a em equipe.",
    20: "Adapto meu comportamento conforme o ambiente.",
    21: "Sou persistente mesmo diante de fracassos.",
    22: "Evito riscos desnecessários.",
    23: "Expresso emoções abertamente.",
    24: "Planejo conversas importantes com antecedência.",
    25: "Sou flexível com mudanças de planos.",
    26: "Priorizo eficiência acima de relações.",
    27: "Aprendo mais observando do que fazendo.",
    28: "Em crises, mantenho a calma e foco na solução.",
    29: "Fico paralisado quando algo dá errado.",
    30: "Sob estresse, busco apoio de outros.",
    31: "Reajo com raiva quando provocado.",
    32: "Transformo pressão em motivação.",
    33: "Evito confrontos diretos em tensões.",
    34: "Recupero equilíbrio emocional rapidamente.",
    35: "Culpo os outros por meus erros.",
    36: "Aumento a produtividade sob prazos apertados.",
    37: "Fico ansioso com críticas.",
    38: "Tenho facilidade para aprender novas habilidades técnicas.",
    39: "Sou bom em liderar grupos para resultados.",
    40: "Resolvo problemas matemáticos ou lógicos intuitivamente.",
    41: "Crio conteúdo persuasivo (escrita, vídeo).",
    42: "Organizo espaços e rotinas de forma eficiente.",
    43: "Negocio bem preços e acordos.",
    44: "Sou criativo em soluções cotidianas.",
    45: "Gerencio múltiplas tarefas sem perder o foco.",
    46: "Inspiro confiança em negociações.",
    47: "Identifico oportunidades de negócio rapidamente.",
    48: "Ensino ou explico conceitos complexos com clareza.",
    49: "Melhoro processos existentes de forma inovadora.",
    50: "Meu valor depende da aprovação dos outros.",
    51: "Me sinto confortável em papéis de liderança.",
    52: "Priorizo família acima de carreira.",
    53: "Construo redes de contatos facilmente.",
    54: "Sou influenciado por normas do meu grupo social.",
    55: "Defendo minhas opiniões em debates públicos.",
    56: "Valorizo tradições culturais da minha família.",
    57: "Me adapto bem a culturas diferentes.",
    58: "Sou generoso com tempo e recursos.",
    59: "Competição me motiva mais que colaboração.",
    60: "Meu papel social ideal é de cuidador.",
    61: "Questiono normas sociais estabelecidas.",
    62: "Estou satisfeito com minha vida atual.",
    63: "Sei exatamente o que quero mudar nos próximos 6 meses.",
    64: "Minhas ações diárias me aproximam dos meus objetivos.",
    65: "Sinto que desperdiço potencial.",
    66: "Tenho clareza sobre minha identidade principal.",
    67: "Me comparo frequentemente com outros.",
    68: "Estou em uma fase de crescimento.",
    69: "Visualizo meu 'eu ideal' com detalhes.",
    70: "Falta de recursos me impede de avançar.",
    71: "Sou proativo em buscar mudanças.",
    72: "Dinheiro é fonte de segurança emocional para mim.",
    73: "Gosto de exibir bens para impressionar.",
    74: "Planejo finanças com 5+ anos de visão.",
    75: "Perdas financeiras me afetam por semanas.",
    76: "Sou generoso e dou sem esperar retorno.",
    77: "Prefiro guardar para emergências que investir.",
    78: "Meu trabalho é valorizado financeiramente.",
    79: "Dinheiro 'circula' naturalmente na minha vida.",
    80: "Gastei impulsivamente nos últimos 6 meses."
}

scale_options = [
    "1 - Discordo totalmente",
    "2 - Discordo",
    "3 - Neutro",
    "4 - Concordo",
    "5 - Concordo totalmente",
]

# =========================================================
# SESSION STATE
# =========================================================
if "responses" not in st.session_state:
    st.session_state.responses = {}

if "current_question" not in st.session_state:
    st.session_state.current_question = 1

# =========================================================
# ENGINE V2
# =========================================================
def engine_v2(respostas):
    df = pd.DataFrame(list(respostas.items()), columns=["Q", "Score"])

    blocos = {
        "Abertura": (1, 15),
        "Consciencioso": (16, 27),
        "Extroversao": (28, 37),
        "Amavel": (38, 49),
        "Neuroticismo": (50, 61),
        "Seguranca": (62, 71),
        "Abundancia": (72, 80),
    }

    medias = {
        k: round(df[(df["Q"] >= i) & (df["Q"] <= f)]["Score"].mean(), 2)
        for k, (i, f) in blocos.items()
    }

    def nivel(score):
        if score >= 4:
            return "alto"
        elif score >= 3:
            return "medio"
        return "baixo"

    niveis = {k: nivel(v) for k, v in medias.items()}

    padroes = []
    conflitos = []

    def add_padrao(nome, peso):
        padroes.append({"nome": nome, "peso": round(peso, 2)})

    def add_conflito(nome, peso):
        conflitos.append({"nome": nome, "peso": round(peso, 2)})

    # PADRÕES
    if niveis["Extroversao"] == "baixo" and niveis["Abertura"] == "alto":
        peso = max(0.1, (medias["Abertura"] - medias["Extroversao"]) / 5)
        add_padrao("expressao_seletiva", peso)

    if niveis["Amavel"] == "alto" and niveis["Extroversao"] in ["baixo", "medio"]:
        add_padrao("orientacao_outro", medias["Amavel"] / 5)

    if niveis["Abertura"] == "alto" and niveis["Consciencioso"] == "baixo":
        add_padrao("ideias_execucao_gap", 1.0)

    if niveis["Consciencioso"] == "alto" and niveis["Extroversao"] == "baixo":
        add_padrao("consistencia_silenciosa", medias["Consciencioso"] / 5)

    if medias["Neuroticismo"] < 2.5:
        add_padrao("presenca_calma", (5 - medias["Neuroticismo"]) / 5)

    if medias["Neuroticismo"] > 4:
        add_padrao("tensao_interna", medias["Neuroticismo"] / 5)

    if niveis["Seguranca"] == "alto" and niveis["Abertura"] in ["baixo", "medio"]:
        add_padrao("decisao_prudente", medias["Seguranca"] / 5)

    if niveis["Abundancia"] == "alto" and niveis["Abertura"] == "alto":
        add_padrao("impulso_crescimento", medias["Abundancia"] / 5)

    if niveis["Amavel"] == "alto" and niveis["Consciencioso"] in ["medio", "alto"]:
        add_padrao("conexao_autentica", medias["Amavel"] / 5)

    if niveis["Consciencioso"] == "alto" and niveis["Neuroticismo"] == "medio":
        add_padrao("controle_interno", medias["Consciencioso"] / 5)

    if niveis["Neuroticismo"] == "baixo" and niveis["Consciencioso"] in ["medio", "alto"]:
        add_padrao("clareza_interna", (medias["Consciencioso"] + (5 - medias["Neuroticismo"])) / 10)

    if niveis["Abertura"] == "alto" and niveis["Neuroticismo"] == "medio":
        add_padrao("autoconsciencia_elevada", (medias["Abertura"] + medias["Neuroticismo"]) / 10)

    if niveis["Extroversao"] == "alto" and niveis["Consciencioso"] in ["baixo", "medio"]:
        add_padrao("acao_imediata", (medias["Extroversao"] + (6 - medias["Consciencioso"])) / 10)

    if niveis["Amavel"] == "alto" and niveis["Neuroticismo"] in ["medio", "alto"]:
        add_padrao("empatia_profunda", (medias["Amavel"] + medias["Neuroticismo"]) / 10)

    if niveis["Abertura"] == "alto" and niveis["Amavel"] in ["medio", "alto"]:
        add_padrao("busca_significado", (medias["Abertura"] + medias["Amavel"]) / 10)

    if niveis["Seguranca"] == "alto" and niveis["Neuroticismo"] in ["medio", "alto"]:
        add_padrao("relacao_emocional_dinheiro", (medias["Seguranca"] + medias["Neuroticismo"]) / 10)

    if niveis["Amavel"] == "alto" and niveis["Extroversao"] == "medio":
        add_padrao("adaptacao_social", (medias["Amavel"] + medias["Extroversao"]) / 10)

    if niveis["Consciencioso"] in ["medio", "alto"] and niveis["Abertura"] in ["medio", "alto"]:
        add_padrao("movimento_com_direcao", (medias["Consciencioso"] + medias["Abertura"]) / 10)

    # CONFLITOS
    if niveis["Abundancia"] == "alto" and niveis["Seguranca"] == "alto":
        add_conflito("expansao_vs_seguranca", 1.0)

    if niveis["Abertura"] == "alto" and niveis["Consciencioso"] == "baixo":
        add_conflito("ideia_vs_execucao", 1.0)

    if niveis["Amavel"] == "alto" and niveis["Extroversao"] == "baixo":
        add_conflito("posicionamento_vs_aceitacao", 0.9)

    padroes = sorted(padroes, key=lambda x: x["peso"], reverse=True)
    conflitos = sorted(conflitos, key=lambda x: x["peso"], reverse=True)

    return {
        "medias": medias,
        "niveis": niveis,
        "padroes": padroes[:4],
        "conflitos": conflitos[:3],
    }

# =========================================================
# TEXT LIBRARY
# =========================================================
def get_texto(nome):
    textos = {
        "expressao_seletiva": """
Você não é do tipo que entra em qualquer ambiente querendo aparecer.

Primeiro, você observa. Sente o clima. Entende o contexto. E só depois decide se vale a pena se posicionar.

Isso faz com que, em alguns lugares, você pareça mais reservado. Em outros, quando existe sentido, alinhamento ou domínio do assunto, você se mostra com clareza, firmeza e até influência.

Isso não é inconsistência. É seletividade.

Você não desperdiça energia onde não vê valor. O ponto de atenção é não sair cedo demais de situações que poderiam se abrir para você com um pouco mais de tempo.
""",

        "orientacao_outro": """
Você percebe as pessoas com facilidade.

Antes de falar, você sente. Antes de agir, considera. Isso faz de você alguém que cria conexão com naturalidade.

Mas essa mesma sensibilidade pode te levar a se adaptar mais do que gostaria. Em alguns momentos, você pode priorizar a harmonia e deixar sua própria voz em segundo plano.

O crescimento aqui não está em deixar de ser sensível. Está em se incluir na relação com a mesma importância que você dá ao outro.
""",

        "ideias_execucao_gap": """
Sua mente é forte. Você cria, imagina e conecta ideias com facilidade.

O desafio aparece quando existe distância entre visão e execução. Você pode começar com entusiasmo, mas nem sempre sustentar no mesmo ritmo.

Isso não aponta falta de talento. Aponta necessidade de estrutura.

Quando você cria uma forma mínima de sustentar suas ideias, deixa de ser alguém com grande potencial… e passa a gerar resultado real.
""",

        "consistencia_silenciosa": """
Você faz o que precisa ser feito mesmo sem plateia.

Existe em você uma força de constância, responsabilidade e entrega que não depende tanto de validação externa.

Isso te torna confiável. O risco é que, por não se expor tanto, sua competência fique menos visível do que merece.

Seu ajuste não é virar outra pessoa. É permitir que o valor do que você faz apareça mais.
""",

        "presenca_calma": """
Você tende a reagir com mais calma do que a média.

Há um espaço entre o que acontece e a forma como você responde. Isso te dá estabilidade e transmite segurança.

O ponto de atenção é não confundir estabilidade com silenciamento emocional. Às vezes, você pode seguir em frente sem realmente processar o que sentiu.
""",

        "tensao_interna": """
Existe um nível de alerta dentro de você.

Você pensa, revisa, antecipa, considera cenários. Isso te dá percepção, mas também pode te cansar.

Você não vive apenas os momentos. Muitas vezes continua vivendo eles por dentro, mesmo depois que passaram.

Seu desafio não é sentir menos. É não permanecer em estado de vigilância o tempo todo.
""",

        "decisao_prudente": """
Você pensa antes de agir.

Avalia risco, cenário, consequência. Isso te protege de impulsos que poderiam custar caro.

Mas essa mesma prudência, quando excessiva, pode atrasar movimento. Seu crescimento passa por agir sem exigir certeza total.
""",

        "impulso_crescimento": """
Existe em você um impulso claro de crescer.

Você se move por possibilidade, expansão e construção de algo maior. Isso é força.

O risco é tentar abraçar mais do que consegue sustentar ao mesmo tempo. Seu próximo nível está em alinhar ambição com direção.
""",

        "conexao_autentica": """
Você se envolve de verdade com as pessoas.

Não entra pela metade. Escuta com presença, entrega mais do que o mínimo e tende a construir relações com profundidade.

O ponto de atenção é investir energia onde não há reciprocidade. Seu crescimento está em selecionar melhor onde colocar o que você tem de mais valioso.
""",

        "controle_interno": """
Você gosta de manter as coisas sob controle.

Organiza, planeja, prevê, ajusta. Isso te dá segurança e consistência.

Mas nem tudo pode ser previsto. Às vezes, seu próximo passo não é controlar mais. É confiar mais no processo sem perder direção.
""",

        "clareza_interna": """
Existe em você uma linha interna relativamente firme.

Mesmo quando o ambiente oscila, você tende a conservar direção. Isso te dá autonomia e presença.

O risco é confiar tanto na sua leitura que deixe menos espaço para ajustes necessários. O equilíbrio está em manter convicção sem perder flexibilidade.
""",

        "autoconsciencia_elevada": """
Você percebe a si mesmo com profundidade.

Reflete sobre o que sente, analisa suas reações e tenta entender o que acontece dentro de você. Isso gera consciência.

Mas também pode produzir excesso de reflexão. Nem tudo precisa ser resolvido por análise antes de ser vivido.
""",

        "acao_imediata": """
Você tende a agir rápido.

Quando algo aparece, você se movimenta. Isso te coloca na frente de muita gente que fica presa pensando.

O risco é velocidade sem estrutura. Seu ajuste não é desacelerar por medo. É adicionar direção ao impulso.
""",

        "empatia_profunda": """
Você sente as pessoas de forma intensa.

Não apenas entende. Você capta o ambiente, percebe nuances e absorve mais do que aparenta.

Essa sensibilidade é uma força. Mas também pode te sobrecarregar. Seu crescimento está em diferenciar melhor o que é seu e o que é do outro.
""",

        "busca_significado": """
Você não se move só por resultado.

Precisa de sentido. Precisa sentir que aquilo importa, que conecta com algo real.

Isso te dá profundidade. O risco é rejeitar cedo demais caminhos que ainda não revelaram totalmente o valor que podem ter.
""",

        "relacao_emocional_dinheiro": """
Dinheiro, para você, não é apenas recurso.

Ele também representa segurança, estabilidade, controle ou alívio. Isso influencia mais decisões do que talvez pareça à primeira vista.

Seu crescimento passa por tornar essa relação mais consciente, para que proteção não se transforme em limitação.
""",

        "adaptacao_social": """
Você sabe se ajustar ao ambiente.

Lê pessoas, percebe contextos e adapta sua forma de se expressar. Isso te dá flexibilidade.

O ponto de atenção é não se adaptar tanto a ponto de perder clareza sobre a sua própria voz.
""",

        "movimento_com_direcao": """
Você reúne duas forças que nem sempre andam juntas: visão e execução.

Consegue pensar e fazer. Refletir e avançar. Isso te dá um potencial importante de evolução consistente.

O ponto de atenção é tentar fazer tudo ao mesmo tempo. Nem tudo precisa crescer junto para que você esteja avançando.
""",

        "expansao_vs_seguranca": """
Existe em você uma tensão real entre crescer e se proteger.

Uma parte quer avançar, expandir, explorar. Outra quer segurança, estabilidade e base sólida.

Nenhuma dessas forças está errada. O desafio é não deixar que uma bloqueie completamente a outra. Seu caminho está em crescer com estratégia.
""",

        "ideia_vs_execucao": """
Você pensa bem. Enxerga possibilidades. Cria caminhos.

Mas nem sempre executa no mesmo nível em que imagina. O desafio aqui não é ter mais ideias. É sustentar ação o suficiente para dar forma ao que você já vê.
""",

        "posicionamento_vs_aceitacao": """
Você tende a evitar confronto desnecessário e valoriza harmonia.

Mas isso pode fazer com que, em alguns momentos, você se silencie mais do que deveria.

Seu crescimento está em se posicionar sem sentir que precisa deixar de ser quem você é.
""",
    }
    return textos.get(nome, "")

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("🧠 Mind Insight Advanced")
progress = (st.session_state.current_question - 1) / 80 if st.session_state.current_question <= 80 else 1.0
st.sidebar.progress(progress)
if st.session_state.current_question <= 80:
    st.sidebar.metric("Pergunta", f"{st.session_state.current_question}/80")
else:
    st.sidebar.success("Teste concluído")

# =========================================================
# APP
# =========================================================
st.title("🧠 Mind Insight Advanced")
st.caption("Leitura comportamental aprofundada")

if st.session_state.current_question <= 80:
    q = st.session_state.current_question
    card_class = "card-a" if q % 2 == 1 else "card-b"

    st.markdown(
        f"""
        <div class="question-card {card_class}">
            <div class="question-badge">Pergunta {q} de 80</div>
            <div class="question-title">{questions[q]}</div>
            <div class="question-sub">Escolha a opção que mais combina com você.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    resposta = st.radio(
        "Resposta",
        scale_options,
        index=None,
        key=f"q_{q}",
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Anterior", use_container_width=True, disabled=(q == 1)):
            if resposta is not None:
                st.session_state.responses[q] = int(resposta.split(" - ")[0])
            st.session_state.current_question -= 1
            st.rerun()

    with col2:
        label = "✅ Finalizar" if q == 80 else "➡️ Próxima"
        if st.button(label, use_container_width=True):
            if resposta is None:
                st.warning("Selecione uma resposta antes de continuar.")
            else:
                st.session_state.responses[q] = int(resposta.split(" - ")[0])
                st.session_state.current_question += 1
                st.rerun()

else:
    resultado = engine_v2(st.session_state.responses)

    st.success("Seu relatório foi gerado.")
    st.subheader("🪞 Relatório Profundo de Personalidade")

    medias = resultado["medias"]
    padroes = resultado["padroes"]
    conflitos = resultado["conflitos"]

    st.markdown("---")
    st.header("🪞 Como você funciona")

    if padroes:
        st.markdown(get_texto(padroes[0]["nome"]))

    st.markdown("---")
    st.header("🧠 Sua forma de pensar")

    st.markdown(f"""
Você combina níveis de criatividade (**{medias['Abertura']}**) e estrutura (**{medias['Consciencioso']}**).

Isso influencia diretamente a forma como você transforma percepção em ação. Em você, o pensamento não é apenas intelectual. Ele afeta ritmo, direção e consistência.
""")

    st.markdown("---")
    st.header("🤝 Como você se relaciona")

    st.markdown(f"""
Sua forma de se relacionar mistura sensibilidade (**{medias['Amavel']}**) e expressão (**{medias['Extroversao']}**).

Isso ajuda a entender como você se conecta, se adapta, se posiciona e preserva sua energia nos ambientes.
""")

    st.markdown("---")
    st.header("⚡ Sua dinâmica interna")

    if medias["Neuroticismo"] < 3:
        st.markdown(get_texto("presenca_calma"))
    else:
        st.markdown(get_texto("tensao_interna"))

    st.markdown("---")
    st.header("⚖️ Conflitos internos")

    if conflitos:
        for c in conflitos:
            st.markdown(get_texto(c["nome"]))
    else:
        st.markdown("No momento, não surgiu um conflito interno dominante com força suficiente para entrar como destaque principal no relatório.")

    st.markdown("---")
    st.header("🚀 Padrões fortes em você")

    if padroes:
        for p in padroes:
            st.markdown(f"**• {p['nome'].replace('_', ' ').title()}**")
    else:
        st.markdown("Nenhum padrão dominante foi ativado com força alta nesta leitura inicial.")

    st.markdown("---")
    st.header("🧭 Direção de evolução")

    st.markdown("""
Seu crescimento não depende de mudar quem você é.

Depende de ajustar como você usa seus padrões.

O que hoje parece obstáculo, muitas vezes é apenas uma força mal calibrada. Pequenos ajustes conscientes podem produzir mudanças grandes na forma como você vive, decide, se posiciona e cresce.
""")

    st.markdown("---")
    st.header("📅 Plano de 90 dias")

    st.markdown("""
**Primeiras 2 semanas**  
Observe onde seus padrões mais fortes aparecem com mais clareza.

**30 dias**  
Escolha 1 comportamento-chave para ajustar com intenção.

**60 dias**  
Sustente a prática mesmo quando o ambiente não ajudar.

**90 dias**  
Consolide uma nova forma de agir que respeite quem você é, mas te leve além.
""")

    st.markdown("---")
    if st.button("🔄 Novo teste", use_container_width=True):
        st.session_state.responses = {}
        st.session_state.current_question = 1
        st.rerun()
