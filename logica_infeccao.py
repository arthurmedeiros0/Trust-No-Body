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

    if padrao1 or padrao2:
        return "infectado"

    return "inconclusivo"