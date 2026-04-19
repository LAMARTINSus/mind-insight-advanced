# patterns.py

def evaluate_patterns(perfil):
    """
    Extrai padrões comportamentais principais.
    NÃO altera lógica, apenas organiza.
    """

    patterns = []

    # Exemplo (substitua com sua lógica real existente)
    if perfil.get("impulso_expansao", 0) > 0.7:
        patterns.append("Alta tendência à expansão")

    if perfil.get("evita_conflito", 0) > 0.7:
        patterns.append("Evita conflitos")

    return patterns


def evaluate_tensions(perfil):
    """
    Identifica tensões internas (um dos seus diferenciais).
    """

    tensions = []

    # Exemplo (substitua com sua lógica real existente)
    if perfil.get("impulso_expansao", 0) > 0.7 and perfil.get("necessidade_previsibilidade", 0) > 0.7:
        tensions.append("Conflito entre crescer e manter segurança")

    return tensions