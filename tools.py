def calcola_ral_da_netto(netto_mensile_paga) -> int:
    """
    Calcola la RAL (Retribuzione Annua Lorda) a partire dalla retribuzione netta mensile.
    Assume 13 mensilità e considera gli scaglioni IRPEF vigenti in Italia.

    :param netto_mensile_paga: Retribuzione netta mensile (in euro).
    :return: RAL (Retribuzione Annua Lorda, in euro).
    """
    # Scaglioni IRPEF (tassazione vigente in Italia, 2023)
    scaglioni = [
        (15000, 0.23),        # Fino a 15.000 €: 23%
        (28000, 0.25),        # Da 15.001 a 28.000 €: 25%
        (50000, 0.35),        # Da 28.001 a 50.000 €: 35%
        (float('inf'), 0.43)  # Oltre 50.000 €: 43%
    ]

    # Funzione per calcolare l'IRPEF lorda
    def calcola_irpef_lorda(reddito_lordo_annuo):
        imposta = 0
        reddito_residuo = reddito_lordo_annuo

        for limite, aliquota in scaglioni:
            if reddito_residuo > limite:
                imposta += limite * aliquota
                reddito_residuo -= limite
            else:
                imposta += reddito_residuo * aliquota
                break

        return imposta

    # Iterazione per trovare il lordo corrispondente al netto
    netto_annuo = netto_mensile_paga * 13
    lordo_prova = 0
    lordo_min = netto_annuo  # Ipotesi minima (nessuna tassa)
    lordo_max = netto_annuo * 2  # Stima iniziale alta per il lordo

    while lordo_max - lordo_min > 1:
        lordo_prova = (lordo_min + lordo_max) / 2
        irpef_lorda = calcola_irpef_lorda(lordo_prova)
        netto_calcolato = lordo_prova - irpef_lorda

        if netto_calcolato < netto_annuo:
            lordo_min = lordo_prova
        else:
            lordo_max = lordo_prova

    return int(lordo_prova)
#
# # Esempio di utilizzo
# netto_mensile = 1500  # Inserire il netto mensile desiderato
# ral_calcolata = calcola_ral_da_netto(netto_mensile)
# print(f"Per un netto mensile di {netto_mensile} €, la RAL stimata è di {ral_calcolata} €.")
