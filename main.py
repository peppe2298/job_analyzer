import pandas as pd

from model.graph.graph import JobAnalyzerGraph
from model.graph.state import State
from service.job_services import JobServices


def start_job_analyzer():

    jov_service = JobServices()

    jobs = jov_service.get_jobs()

    job_analyzer = JobAnalyzerGraph()
    image = job_analyzer.generate_image()
    image.save('my_graph.png', format='png')

    jobs_elaborated = pd.DataFrame()

    for index, job in jobs.iterrows():

        result_state = State(
            id = job['id'] if 'id' in job else '',
            data_estrazione = job['data_estrazione'] if 'data_estrazione' in job else '',
            data = job['data'] if 'data' in job else '',
            announce = job['dettaglio'] if 'dettaglio' in job else '',
            name = job['mansione'] if 'mansione' in job else '',
            company = job['azienda'] if 'azienda' in job else '',
            city = job['città'] if 'città' in job else '',
            region = job['regione'] if 'regione' in job else '',
            state = job['stato'] if 'stato' in job else '',
            macro_region = job['macro_regione'] if 'macro_regione' in job else '',
            work_mode = job['distanza'] if 'distanza' in job else '',
            work_type = job['tipo_lavoro'] if 'tipo_lavoro' in job else '',
            experience = job['livello_esperienza'] if 'livello_esperienza' in job else '',
            job_sector = job['settore'] if 'settore' in job else '',
            job_area = job['funzione_lavorativa'] if 'funzione_lavorativa' in job else '',
            qualification = job['qualifica'] if 'qualifica' in job else ''
        )

        try:

            result_state = job_analyzer.graph.invoke(result_state)
            serie = jov_service.cast_job_to_serie(result_state)
            new_df = serie.to_frame().T
            jobs_elaborated = pd.concat([jobs_elaborated, new_df], ignore_index=True)

        except Exception as e:
            print(f'Lavoro {job["id"]} non importato: {str(e)}\n')

        print(f'{index} lavori processati')

        if (index % 10) == 0:
            jobs_elaborated.to_csv('jobs_elaborated.csv', index=False)





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pd.set_option('display.max_columns', None)  # Visualizza tutte le colonne
    pd.set_option('display.width', None)  # Adatta la larghezza del display
    start_job_analyzer()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

