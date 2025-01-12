# This is a sample Python script.
# Press Maiusc+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from langchain_core.runnables.graph import MermaidDrawMethod
from io import BytesIO
from PIL import Image
import pandas as pd

from job_examinator import get_graph, State
from job_loader import get_jobs, cast_job_to_serie


def start_job_analyzer():

    jobs = get_jobs()

    graph = get_graph()
    image_data = BytesIO(graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API))
    image = Image.open(image_data)
    image.save('my_graph.png', format='png')

    jobs_elaborated = pd.DataFrame()

    for index, job in jobs.iterrows():

        result_state = State(
            id = job['id'] if 'id' in job else '',
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

            result_state = graph.invoke(result_state)
            serie = cast_job_to_serie(result_state)
            new_df = serie.to_frame().T
            jobs_elaborated = pd.concat([jobs_elaborated, new_df], ignore_index=True)

        except Exception as e:
            print(f'Lavoro {job["id"]} non importato: {str(e)}\n')

        print(f'{index} lavori processati')

        if (index % 10) == 0:
            jobs_elaborated.to_csv('jobs_elaborated.csv', index=False)

    print(jobs_elaborated.head(10))




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pd.set_option('display.max_columns', None)  # Visualizza tutte le colonne
    pd.set_option('display.width', None)  # Adatta la larghezza del display
    start_job_analyzer()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

