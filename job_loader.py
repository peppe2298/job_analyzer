import pandas as pd

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