user_needs = {
    "ambiguity": "Prefiro quando o texto diz exatamente o que quer dizer, sem duplo sentido nem enrolação.",
    "simple_language": "Gosto quando o texto é fácil de ler. Palavras curtas e frases simples me ajudam muito."
}

def get_needs_values(personalized_needs):
    if len(personalized_needs) > 0:
        return [user_needs[chave] for chave in personalized_needs]
    
    return []