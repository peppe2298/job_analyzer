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

    # job_selection = jobs.iloc[:1]

    graph = get_graph()
    image_data = BytesIO(graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API))
    image = Image.open(image_data)
    image.save('my_graph.png', format='png')

    jobs_elaborated = pd.DataFrame()

    for index, job in jobs.iterrows():
        result_state = State()
        result_state['announce'] = job['Dettaglio']
        result_state['name'] = job['Mansione'] if 'Mansione' in job else ''
        result_state['company'] = job['Azienda'] if 'Azienda' in job else ''
        result_state['city'] = job['Città'] if 'Città' in job else ''
        result_state['region'] = job['Regione'] if 'Regione' in job else ''
        result_state['state'] = job['Stato'] if 'Stato' in job else ''
        result_state['work_mode'] = job['Tipo'] if 'Tipo' in job else ''
        result_state= graph.invoke(result_state)
        serie = cast_job_to_serie(result_state)
        new_df = serie.to_frame().T
        jobs_elaborated = pd.concat([jobs_elaborated, new_df], ignore_index=True)
        print(f'{index} lavori processati')

        if (index % 500) == 0:
            jobs_elaborated.to_csv('jobs_elaborated.csv', index=False)

    print(jobs_elaborated.head(10))




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pd.set_option('display.max_columns', None)  # Visualizza tutte le colonne
    pd.set_option('display.width', None)  # Adatta la larghezza del display
    start_job_analyzer()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

