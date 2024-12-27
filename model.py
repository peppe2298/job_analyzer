from typing import List, Dict


class Field:
    def __init__(self, name, required=False):
        self.name = name
        self.required = required

    def __eq__(self, other):
        if isinstance(other, Field):
            return self.name == other.name
        return NotImplemented

    def __hash__(self):
        return hash(self.name)

class HardSkill(Field):
    pass

class Category(Field):
    extended_name: str
    hard_skills: List[HardSkill]

    def __init__(self, name, extended_name, required=False):
        super().__init__(name, required)
        self.name = name
        self.extended_name = extended_name


class SoftSkill(Field):
    pass


job_sectors = {
    "sviluppo_software": (
        "Sviluppo Software",
        "Gli annunci per questo settore includono spesso termini come sviluppo backend/frontend, linguaggi di programmazione (es. Java, Python) o framework come React, Angular, .NET. Possono richiedere esperienza in sviluppo mobile (Swift, Kotlin) e pratiche DevOps come CI/CD e testing automatizzato.",
        [
            "Java", "Python", "C#", "PHP", "Go", "Ruby", "Backend", "Frontend",
            "JavaScript", "React", "Angular", "Vue.js", "Spring", ".NET", "Django",
            "Laravel", "Mobile Development", "Swift", "Kotlin", "Flutter",
            "Testing e Quality Assurance", "DevOps Practices"
        ]
    ),
    "database": (
        "Database e Data Management",
        "Questi annunci si riferiscono a ruoli che richiedono competenze in gestione, ottimizzazione e manutenzione di database relazionali (SQL) e non-relazionali (MongoDB, Cassandra). È comune trovare richieste per processi ETL e Data Warehousing in ambienti aziendali complessi.",
        [
            "MongoDB", "Cassandra", "Redis", "SQL e Query Optimization",
            "Data Warehousing", "ETL Processes", "Database Administration",
            "PostgreSQL", "Oracle", "SQL Server", "MySQL"
        ]
    ),
    "sistemi": (
        "Infrastruttura e Sistemi",
        "Gli annunci per ruoli infrastrutturali richiedono competenze su piattaforme cloud (AWS, Azure, GCP), amministrazione di sistemi, sicurezza informatica e containerizzazione. Si cerca spesso esperienza in strumenti CI/CD per automatizzare i flussi di lavoro.",
        [
            "Cloud Platforms (AWS, Azure, GCP)", "Cybersecurity",
            "System Administration", "Containerization (Docker, Kubernetes)",
            "CI/CD Tools (Jenkins, GitLab CI)", "Linux", "Windows Server"
        ]
    ),
    "data_science": (
        "Data Science e AI",
        "Questi annunci spesso cercano esperti di Machine Learning, Deep Learning e Big Data. Competenze richieste includono strumenti come TensorFlow e PyTorch, oltre ad abilità in analisi predittiva, NLP e visualizzazione con Tableau o PowerBI.",
        [
            "Machine Learning", "Deep Learning", "Statistical Analysis",
            "Data Mining", "Natural Language Processing", "Computer Vision",
            "Predictive Analytics", "MLOps", "Big Data Technologies (Hadoop, Spark)",
            "Tableau", "PowerBI", "Google Looker", "Tensorflow",
            "Langchain / Agentic Applications", "PyTorch"
        ]
    ),
    "ux_designer": (
        "Design e User Experience",
        "Gli annunci nel settore UI/UX cercano esperti capaci di progettare interfacce intuitive, responsive e accessibili. Competenze in wireframing, prototipazione e UX writing sono particolarmente richieste.",
        [
            "UI/UX Design", "Wireframing e Prototyping", "Responsive Design",
            "Accessibility Standards", "UX Writing"
        ]
    ),
    "management": (
        "Management e Strategy",
        "Questi ruoli includono gestione di progetti e prodotti, con un focus su metodologie Agile (Scrum, Kanban). Si cercano anche competenze in trasformazione digitale, leadership tecnica e analisi di business per guidare il cambiamento aziendale.",
        [
            "Agile Methodologies (Scrum, Kanban)", "Project Management",
            "Product Management", "Digital Transformation",
            "Business Analysis", "Technical Leadership"
        ]
    )
}

# Definizione delle reference skills
job_soft_skills : list[str] = [
    'Problem Solving e Pensiero Analitico',
    'Comunicazione Tecnica e Business',
    'Team Collaboration e Teamwork',
    'Leadership e Influenza',
    'Time Management e Organizzazione',
    'Continuous Learning',
    'Technical Writing e Documentation',
    'Cross-functional Collaboration',
    'Mentoring e Coaching',
    'Pensiero Critico',
    'Resilienza e Gestione dello Stress',
    'Creatività e Innovazione',
    'Cultural Awareness e Diversity',
    'Etica Professionale',
    'Gestione delle Priorità',
    'Autoconsapevolezza',
    'Public Speaking',
    'Capacità di Sintesi',
    'Decision Making',
]

# Dizionari delle regioni
nord_italia = {
    "Valle d'Aosta",
    "Piemonte",
    "Liguria",
    "Lombardia",
    "Trentino-Alto Adige",
    "Veneto",
    "Friuli-Venezia Giulia",
    "Emilia-Romagna"
}

centro_italia = {
    "Toscana",
    "Umbria",
    "Marche",
    "Lazio"
}

sud_italia = {
    "Abruzzo",
    "Molise",
    "Campania",
    "Puglia",
    "Basilicata",
    "Calabria"
}

isole = {
    "Sicilia",
    "Sardegna"
}
