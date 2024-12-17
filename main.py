# This is a sample Python script.
# Press Maiusc+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables.graph import MermaidDrawMethod
from io import BytesIO
from PIL import Image
import pandas as pd

from agents import job_preprocess_agent, check_category_agent
from job_examinator import get_graph
from job_loader import get_jobs
from model import job_sectors


def start_job_analyzer():

    jobs = get_jobs()

    job = jobs.iloc[10]

    agent = job_preprocess_agent()

    print(job['Dettaglio'])

    print('\n\n\n\n')

    result = agent.invoke({"job_posting": job['Dettaglio']})

    print("Contratto e Livello:", result["contract_info"])
    print("\nSkill richieste:\n", result["skills"])

    agent = check_category_agent()

    category = job_sectors['sistemi']

    result = agent.invoke({
        "category": category[0],
        "category_description": category[1],
        "job_posting": job['Dettaglio']
    })

    print(result)

    # graph = get_graph()
    # image_data = BytesIO(graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API))
    # image = Image.open(image_data)
    # image.save('my_graph.png', format='png')

    #TODO iterare sul csv lanciando il graph, convertire lo stato di ogni esecuzione di grafo in una riga per un nuovo csv


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pd.set_option('display.max_columns', None)  # Visualizza tutte le colonne
    pd.set_option('display.width', None)  # Adatta la larghezza del display
    start_job_analyzer()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

