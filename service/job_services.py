import pandas as pd

from model.graph.state import SoftSkill, Category, State
from model.job_info import job_sectors
from model.regions import nord_italia, centro_italia, sud_italia, isole

class JobServices:

    @staticmethod
    def _separa_luogo(row) -> [str, str, str]:
        valori = row['luogo'].split(',')
        if len(valori) == 3:
            return valori[0].strip(), valori[1].strip(), valori[2].strip()
        elif len(valori) == 2:
            return '', valori[0].strip(), valori[1].strip()
        else:
            return '', '', valori[0].strip()

    @staticmethod
    def _determina_macro_regione(row) -> str:
        regione = row['regione']

        if regione is None or regione == '':
            return 'unset'

        regione_lower = regione.lower()  # Trasformare tutto in minuscolo per ignorare il case sensitive

        # Comparare con i dizionari
        if any(regione_lower == r.lower() for r in nord_italia):
            return "Nord Italia"
        elif any(regione_lower == r.lower() for r in centro_italia):
            return "Centro Italia"
        elif any(regione_lower == r.lower() for r in sud_italia):
            return "Sud Italia"
        elif any(regione_lower == r.lower() for r in isole):
            return "Isole"
        else:
            return "unset"

    @staticmethod
    def get_jobs() -> pd.DataFrame:

        df = pd.read_csv('jobs_scraping.csv')

        df['mansione'] = df['mansione'].str.split('\n').str[0]

        df['luogo'] = df['luogo'].str.replace(r'\(.*?\)', '', regex=True)
        df[['città', 'regione', 'stato']] = df.apply(JobServices._separa_luogo, axis=1, result_type='expand')
        df.drop('luogo', axis=1, inplace=True)

        df['macro_regione'] = df.apply(JobServices._determina_macro_regione, axis=1)

        return df

    @staticmethod
    def cast_job_to_serie(job_state: State) -> pd.Series:
        serie: pd.Series = pd.Series()

        serie['id'] = job_state['id'] if 'id' in job_state else ''
        serie['name'] = job_state['name'] if 'name' in job_state else ''
        serie['company'] = job_state['company'] if 'company' in job_state else ''
        serie['city'] = job_state['city'] if 'city' in job_state else ''
        serie['region'] = job_state['region'] if 'region' in job_state else ''
        serie['state'] = job_state['state'] if 'state' in job_state else ''
        serie['macro_region'] = job_state['macro_region'] if 'macro_region' in job_state else ''
        serie['work_mode'] = job_state['work_mode'] if 'work_mode' in job_state else ''
        serie['work_type'] = job_state['work_type'] if 'work_type' in job_state else ''
        serie['experience'] = job_state['experience'] if 'experience' in job_state else ''
        serie['job_sector'] = job_state['job_sector'] if 'job_sector' in job_state else ''
        serie['job_area'] = job_state['job_area'] if 'job_area' in job_state else ''
        serie['qualification'] = job_state['qualification'] if 'qualification' in job_state else ''
        serie['ral'] = job_state['ral'] if 'ral' in job_state else ''
        serie['company_sector'] = job_state['company_sector'] if 'company_sector' in job_state else ''
        serie['company_revenue'] = job_state['company_revenue'] if 'company_revenue' in job_state else ''
        serie['company_registered_office_state'] = job_state['company_registered_office_state'] if 'company_registered_office_state' in job_state else ''

        soft_skills: set[SoftSkill] = job_state['soft_skills']

        for soft_skill in soft_skills:
            soft_skill_name = soft_skill.name
            serie[soft_skill_name] = soft_skill.required

        categories: set[Category] = job_state['categories']

        other_category: bool = True

        for category in categories:

            category_name = category.name
            serie[category_name] = category.required

            if category.required:
                other_category = False
                for skill in category.hard_skills:
                    hard_skill_name = skill.name
                    serie[hard_skill_name] = skill.required
                continue

            for skill_name in job_sectors[category_name][2]:
                hard_skill_name = skill_name
                serie[hard_skill_name] = False

            serie['Altro Settore'] = other_category

        return serie