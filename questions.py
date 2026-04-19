# questions.py

# Lista principal de perguntas
QUESTIONS = [
    # Cole aqui EXATAMENTE sua lista atual de perguntas (sem alterar ordem)
]

# Índices das perguntas invertidas (0-based)
INVERTED_QUESTIONS = {
    # Exemplo:
    # 2, 5, 10, ...
}

def get_questions():
    return QUESTIONS

def is_inverted(index):
    return index in INVERTED_QUESTIONS

def normalize_answer(value, index):
    """
    Normaliza resposta considerando inversão.
    Mantém exatamente a lógica atual do seu app.
    """
    if is_inverted(index):
        return 6 - value  # padrão Likert 1–5
    return value