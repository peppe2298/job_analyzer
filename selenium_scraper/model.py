# Dizionari per ogni categoria
LIVELLO_ESPERIENZA = {
    1: "Stage",
    2: "Esperienza minima",
    3: "Livello medio",
    4: "Livello medio-alto",
    5: "Direttore",
    6: "Executive"
}

TIPO_LAVORO = {
    1: "A tempo pieno",
    2: "Part-time",
    3: "Contratto",
    4: "Temporaneo",
    5: "Volontario",
    6: "Stage",
    7: "Altro"
}

DISTANZA = {
    1: "In sede",
    2: "Ibrido",
    3: "Da remoto"
}

SETTORE = {
    1: "Servizi IT e consulenza IT",
    2: "Vendita al dettaglio",
    3: "Consulenza e servizi aziendali",
    4: "Servizi risorse umane",
    5: "Settore alberghiero",
    6: "Sviluppo di software",
    7: "Pubblica amministrazione",
    8: "Fabbricazione di macchinari industriali",
    9: "Industria manifatturiera",
    10: "Servizi di marketing",
    11: "Servizi finanziari",
    12: "Fabbricazione di prodotti farmaceutici"
}

FUNZIONE_LAVORATIVA = {
    1: "Vendite",
    2: "Informatica",
    3: "Altro",
    4: "Business Development",
    5: "Management",
    6: "Industria manifatturiera",
    7: "Ingegneria",
    8: "Consulenza",
    9: "Marketing",
    10: "Amministrativo",
    11: "Contabilità / revisione dei conti",
    12: "Aggiungi una funzione lavorativa"
}

QUALIFICA = {
    1: "Software Engineer",
    2: "Venditore",
    3: "Addetto d'ambasciata",
    4: "Project Manager",
    5: "Tecnico",
    6: "Contabile",
    7: "Operaio",
    8: "Magazziniere",
    9: "Impiegato",
    10: "Impiegato amministrativo",
    11: "Ingegnere elettrico",
    12: "Stagista",
    13: "Account manager",
    14: "Specialista area"
}


class JobListing:
    def __init__(self, link , **kwargs):
        """
        Inizializza un'istanza di JobListing.

        Parameters:
        link: Il link alla lista di annunci
        kwargs: Dizionario di parametri che può includere:
            - livello_esperienza (int): chiave per il livello di esperienza
            - tipo_lavoro (int): chiave per il tipo di lavoro
            - distanza (int): chiave per la modalità di lavoro (in sede/remoto)
            - settore (int): chiave per il settore industriale
            - funzione_lavorativa (int): chiave per la funzione lavorativa
            - qualifica (int): chiave per la qualifica richiesta
        """
        # Inizializza tutti gli attributi a None
        self.link = link
        self.livello_esperienza = None
        self.tipo_lavoro = None
        self.distanza = None
        self.settore = None
        self.funzione_lavorativa = None
        self.qualifica = None

        # Aggiorna gli attributi specificati nei kwargs
        for key, value in kwargs.items():
            if key == 'livello_esperienza' and value in LIVELLO_ESPERIENZA:
                self.livello_esperienza = LIVELLO_ESPERIENZA[value]
            elif key == 'tipo_lavoro' and value in TIPO_LAVORO:
                self.tipo_lavoro = TIPO_LAVORO[value]
            elif key == 'distanza' and value in DISTANZA:
                self.distanza = DISTANZA[value]
            elif key == 'settore' and value in SETTORE:
                self.settore = SETTORE[value]
            elif key == 'funzione_lavorativa' and value in FUNZIONE_LAVORATIVA:
                self.funzione_lavorativa = FUNZIONE_LAVORATIVA[value]
            elif key == 'qualifica' and value in QUALIFICA:
                self.qualifica = QUALIFICA[value]

    def __str__(self):
        """
        Restituisce una rappresentazione leggibile dell'istanza di JobListing.
        """
        attributes = {
            "Livello di esperienza": self.livello_esperienza,
            "Tipo di lavoro": self.tipo_lavoro,
            "Distanza": self.distanza,
            "Settore": self.settore,
            "Funzione lavorativa": self.funzione_lavorativa,
            "Qualifica": self.qualifica
        }

        return "\n".join([f"{key}: {value}" for key, value in attributes.items() if value is not None])