# This is a sample Python script.
# Press Maiusc+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables.graph import MermaidDrawMethod
from io import BytesIO
from PIL import Image
import pandas as pd

from agents import job_preprocess_agent, check_category_agent
from job_examinator import get_graph, State
from job_loader import get_jobs, cast_job_to_serie
from model import job_sectors


def start_job_analyzer():

    jobs = get_jobs()

    job_selection = jobs.iloc[:10]

    graph = get_graph()
    image_data = BytesIO(graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API))
    image = Image.open(image_data)
    image.save('my_graph.png', format='png')

    jobs_elaborated = pd.DataFrame()

    for index, job in job_selection.iterrows():
        result_state = State()
        result_state['announce'] = job['Dettaglio']
        result_state['name'] = job['Mansione'] if 'name' in job else ''
        result_state['company'] = job['Azienda'] if 'company' in job else ''
        result_state['city'] = job['Città'] if 'city' in job else ''
        result_state['region'] = job['Regione'] if 'region' in job else ''
        result_state['state'] = job['Stato'] if 'state' in job else ''
        result_state= graph.invoke(result_state)
        serie = cast_job_to_serie(result_state)
        new_df = serie.to_frame().T
        jobs_elaborated = pd.concat([jobs_elaborated, new_df], ignore_index=True)
        print(f'{index} lavori processati')

    print(jobs_elaborated.head(10))




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pd.set_option('display.max_columns', None)  # Visualizza tutte le colonne
    pd.set_option('display.width', None)  # Adatta la larghezza del display
    start_job_analyzer()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

