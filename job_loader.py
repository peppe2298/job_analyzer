import pandas as pd

from job_examinator import State
from model import SoftSkill, Category, job_sectors
from prompts import soft_skill_match


def separa_luogo(row) -> [str, str, str]:
    valori = row['Luogo'].split(',')
    if len(valori) == 3:
        return valori[0].strip(), valori[1].strip(), valori[2].strip()
    elif len(valori) == 2:
        return '', valori[0].strip(), valori[1].strip()
    else:
        return '', '', valori[0].strip()

def get_jobs() -> pd.DataFrame:
    df = pd.read_csv('jobs_scraping.csv')
    df['Mansione'] = df['Mansione'].str.split('\n').str[0]
    df['Tipo'] = df['Luogo'].str.extract(r'\((.*?)\)')
    df['Luogo'] = df['Luogo'].str.replace(r'\(.*?\)', '', regex=True)

    df[['Città', 'Regione', 'Stato']] = df.apply(separa_luogo, axis=1, result_type='expand')

    df.drop('Luogo', axis=1, inplace=True)
    df.drop('Durata', axis=1, inplace=True)
    df.drop('Livello', axis=1, inplace=True)

    return df

def cast_job_to_serie(job: State) -> pd.Series:
    serie: pd.Series = pd.Series()

    serie['name'] = job['name'] if 'name' in job else ''
    serie['company'] = job['company'] if 'company' in job else ''
    serie['ral'] = job['ral'] if 'ral' in job else 0
    serie['type'] = job['type'] if 'type' in job else ''
    serie['city'] = job['city'] if 'city' in job else ''
    serie['region'] = job['region'] if 'region' in job else ''
    serie['state'] = job['state'] if 'state' in job else ''
    serie['contract_type'] = job['contract_type'] if 'name' in job else ''

    soft_skills: set[SoftSkill] = job['soft_skills']

    for soft_skill in soft_skills:
        soft_skill_name = soft_skill.name
        serie[soft_skill_name] = soft_skill.required

    categories: set[Category] = job['categories']

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