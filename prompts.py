from langchain_core.prompts import ChatPromptTemplate

# Prompt per l'analisi del contratto e livello
contract_level_prompt = ChatPromptTemplate.from_template("""
Analizza il seguente annuncio di lavoro. Identifica SOLO le informazioni ESPLICITAMENTE menzionate riguardo:

1. Il tipo di contratto:
   Cerca SOLO menzioni esplicite di:
   - stage
   - determinato
   - indeterminato
   NON dedurre il tipo di contratto da altri indizi.

2. Il livello di esperienza, basato su:
   - Junior: 0-2 anni di esperienza
   - Mid-level: menzione esplicita di 3-5 anni di esperienza
   - Senior: menzione esplicita di più di 5 anni di esperienza

IMPORTANTE:
- Inserisci una stringa vuota se l'informazione non è ESPLICITAMENTE menzionata
- NON fare deduzioni o supposizioni
- Se ci sono ambiguità, usa una stringa vuota

Restituisci SOLO i due valori separati da virgola, senza altro testo.
Esempi formato:
- Se hai certezza di entrambi: indeterminato, senior
- Se manca certezza sul contratto: , senior
- Se manca certezza sul livello: indeterminato,
- Se non hai certezze: ,

Annuncio:
{job_posting}
""")

# Prompt per l'estrazione delle skill non catalogate
skills_prompt = ChatPromptTemplate.from_template("""
Analizza il seguente annuncio di lavoro e mantieni solo le parti relative alle soft skill e hard skill richieste.
Rimuovi tutte le altre informazioni non pertinenti come benefit aziendali, descrizione dell'azienda, etc.
Mantieni la formattazione originale delle skill.

Annuncio:
{job_posting}
""")

check_category_prompt = ChatPromptTemplate.from_template("""
Settore da verificare: {category}
Criteri per identificare il settore (indicatori da cercare nell'annuncio): {category_description}

Testo dell'annuncio di lavoro da analizzare:
{job_posting}

Analizza se nell'annuncio sono presenti gli indicatori specificati nei criteri.
Rispondi SOLO con:
- True: se l'annuncio contiene gli indicatori del settore
- False: se l'annuncio non contiene gli indicatori del settore
""")

hard_skill_match = ChatPromptTemplate.from_template("""
Analizza il seguente annuncio di lavoro e identifica quali delle skill fornite sono richieste.
IMPORTANTE: Se trovi una skill richiesta che ha un nome diverso ma si riferisce alla stessa tecnologia presente nella lista fornita, 
devi restituire il nome ESATTO presente nella lista di input.

Ad esempio:
- Se nella lista c'è "React.js" e nell'annuncio trovi "React" o "ReactJS", restituisci "React.js"
- Se nella lista c'è "MySQL" e nell'annuncio trovi "SQL", restituisci "MySQL" solo se è chiaro che si riferisce specificamente a MySQL

Restituisci SOLO le skill richieste, una per riga.
Se una skill non è menzionata o non è chiaramente richiesta, non includerla.

Annuncio di lavoro:
{job_description}

Lista delle skill da verificare (usa ESATTAMENTE questi nomi):
{skills}

Skill richieste (una per riga):
""")

soft_skill_match = ChatPromptTemplate.from_template("""
Analizza il seguente annuncio di lavoro e identifica quali delle soft skill fornite sono richieste.
IMPORTANTE: Se trovi una skill richiesta che ha un nome diverso ma si riferisce alla stessa tecnologia presente nella lista fornita, 
devi restituire il nome ESATTO presente nella lista di input.

Ad esempio:
- Se nella lista c'è "Leadership e Influenza" e nell'annuncio trovi "Capacità di influenzare gli altri" o "possesso di leadership", restituisci "React.js"
- Se nella lista c'è "Team Collaboration e Teamwork" e nell'annuncio trovi "Capacità di lavorare in team", restituisci "Team Collaboration e Teamwork"

Restituisci SOLO le skill richieste, una per riga.
Se una skill non è chiaramente richiesta, non includerla.

Annuncio di lavoro:
{job_description}

Lista delle soft skill da verificare (usa ESATTAMENTE questi nomi):
{skills}

Skill richieste (una per riga):
""")