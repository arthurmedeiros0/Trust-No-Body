def diagnosticar(sintomas, noticias_lidas):
    padrao1 = (
        "boletim_07" in noticias_lidas
        and sintomas.get("manchas_maos") is True
        and sintomas.get("dentes_deteriorados") is True
        and sintomas.get("olhos_alterados") is False
    )

    padrao2 = (
        "boletim_14" in noticias_lidas
        and sintomas.get("veias_escurecidas") is True
        and sintomas.get("palidez_anormal") is True
        and sintomas.get("tremores_involuntarios") is False
    )

    padrao3 = (
        "boletim_17" in noticias_lidas
        and sintomas.get("olhos_alterados") is True
        and sintomas.get("tremores_involuntarios") is True
        and sintomas.get("manchas_maos") is False
    )

    if padrao1 or padrao2 or padrao3:
        return "infectado"

    sinais = {
        "manchas_maos",
        "dentes_deteriorados",
        "olhos_alterados",
        "veias_escurecidas",
        "palidez_anormal",
        "tremores_involuntarios"
    }

    protocolo_completo = {
        "boletim_07",
        "boletim_14",
        "boletim_17"
    }.issubset(noticias_lidas)

    todos_examinados = sinais.issubset(sintomas)

    if protocolo_completo and todos_examinados:
        return "saudavel"

    return "inconclusivo"