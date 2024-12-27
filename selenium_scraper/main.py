# This is a sample Python script.
from pandas import DataFrame
# Press Maiusc+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Import Packages
from selenium import webdriver
import time
import datetime
import pandas as pd
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import StaleElementReferenceException
from urllib.parse import urlparse, parse_qs

from model import JobListing, SETTORE, FUNZIONE_LAVORATIVA, QUALIFICA, DISTANZA, TIPO_LAVORO, LIVELLO_ESPERIENZA


def retry_on_stale(func, riassunto, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return func(riassunto)
        except StaleElementReferenceException:
            print(f'errore {attempt}')
            if attempt == max_attempts - 1:  # Se è l'ultimo tentativo
                print('limite raggiunto, dettagli saltati')
                return []  # Rilancia l'eccezione
            time.sleep(1)
            continue

def get_texts(riassunto):
    # Prendo il primo span figlio
    primo_span = riassunto.find_element(By.TAG_NAME, "span")

    # Trovo tutti gli span figli dentro il primo span
    span_figli = primo_span.find_elements(By.TAG_NAME, "span")

    testi = []
    # Estraggo il testo da ogni span
    for span in span_figli:
        testi.append(span.text)

    return testi

def do_page_scrape(driver, lista_lavori_per_pagina, df, job):

    li_elements = lista_lavori_per_pagina.find_elements(By.XPATH, "./li")

    # Iteriamo su ogni li
    for li in li_elements:
        try:

            # Scrolliamo fino all'elemento li
            driver.execute_script("arguments[0].scrollIntoView(true);", li)
            time.sleep(1)  # Breve pausa per permettere lo scroll

            # Prendiamo prima i dati all'interno del li
            mansione = li.find_element(By.CLASS_NAME, "artdeco-entity-lockup__title").text
            azienda = li.find_element(By.CLASS_NAME, "artdeco-entity-lockup__subtitle").text
            luogo = li.find_element(By.CLASS_NAME, "artdeco-entity-lockup__caption").text

            print(mansione)
            # Ora clicchiamo sul li
            li.click()
            time.sleep(1)
            print("cliccato")

            current_url = driver.current_url
            parsed_url = urlparse(current_url)
            query_string = parsed_url.query
            query_params = parse_qs(query_string)
            current_job_id = query_params.get('currentJobId', [''])[0]


            # Aspettiamo e prendiamo il dettaglio da tutta la pagina
            wait = WebDriverWait(driver, 10)

            riassunto = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'job-details-jobs-unified-top-card__job-insight--highlight')))

            print("dettagli presi")

            caratteristiche = retry_on_stale(get_texts, riassunto)

            for caratteristica in caratteristiche:
                print(caratteristica)

            wait_dettaglio = WebDriverWait(driver, 10)
            # Aspettiamo e prendiamo il dettaglio da tutta la pagina
            dettaglio = wait_dettaglio.until(EC.presence_of_element_located((By.CLASS_NAME, "jobs-description__container"))).text

            print('dettaglio estratto')

            distanza = DISTANZA[job.distanza] if job.distanza is not None else caratteristiche[0] if caratteristiche.__len__() == 3 else None
            tipo_lavoro  = TIPO_LAVORO[job.tipo_lavoro] if job.tipo_lavoro is not None else caratteristiche[1] if caratteristiche.__len__() == 3 else None
            livello_esperienza = LIVELLO_ESPERIENZA[job.livello_esperienza] if job.livello_esperienza is not None else caratteristiche[2] if caratteristiche.__len__() == 3 else None
            settore = SETTORE[job.settore] if job.settore is not None else None
            funzione_lavorativa = FUNZIONE_LAVORATIVA[job.funzione_lavorativa] if job.funzione_lavorativa is not None else None
            qualifica = QUALIFICA[job.qualifica] if job.qualifica is not None else None

            # Creiamo una nuova riga come Series e la aggiungiamo al DataFrame
            nuova_riga = pd.Series({
                'id': current_job_id,
                'mansione': mansione,
                'azienda': azienda,
                'luogo': luogo,
                'distanza': distanza,
                'tipo_lavoro': tipo_lavoro,
                'livello_esperienza': livello_esperienza,
                'dettaglio': dettaglio,
                'settore': settore,
                'funzione_lavorativa': funzione_lavorativa,
                'qualifica': qualifica
            })
            # Aggiungiamo la riga al DataFrame
            df.loc[len(df)] = nuova_riga

        except Exception as e:
            print(f"Errore durante l'elaborazione di un elemento: {e}")
            # In caso di errore, aggiungiamo valori nulli


def click_next_page(driver) -> bool:
    paginazione = driver.find_element(By.CLASS_NAME, 'jobs-search-pagination')

    # Troviamo l'li che contiene il div active
    li_active = paginazione.find_element(By.XPATH, ".//li[./button[contains(@class, 'jobs-search-pagination__indicator-button--active')]]")

    # Cerchiamo il successivo usando find_elements (plurale)
    next_li = li_active.find_elements(By.XPATH, "following-sibling::li[1]")

    # Controlliamo se esiste
    if next_li:  # Se la lista non è vuota
        next_li[0].click()
        return True
    else:
        return False




def linkedin_job_scraper(job: JobListing, driver: WebDriver):


    df = pd.DataFrame(columns=['id', 'mansione', 'azienda', 'luogo', 'distanza', 'tipo_lavoro', 'livello_esperienza', 'dettaglio', 'settore', 'funzione_lavorativa', 'qualifica'])

    driver.implicitly_wait(10)
    driver.get(job.link)

    # Find number of job listings
    job_results = driver.find_element(By.CLASS_NAME, 'jobs-search-results-list__subtitle')
    job_results = job_results.text.replace(' risultati', '')
    job_results = pd.to_numeric(job_results)
    print(job_results)

    current_page = driver.find_element(By.CLASS_NAME, 'jobs-search-pagination__indicator-button--active').text
    current_page = pd.to_numeric(current_page)
    print(current_page)

    next_page_clicked = True
    paginazione = driver.find_element(By.CLASS_NAME, 'jobs-search-pagination')

    while next_page_clicked:
        lista_lavori_per_pagina = paginazione.find_element(By.XPATH, "./preceding-sibling::ul[1]")
        do_page_scrape(driver, lista_lavori_per_pagina, df, job)
        next_page_clicked = click_next_page(driver)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result_string = f"result-{timestamp}.csv"
    df.to_csv(result_string, index=False)



# Press the green button in the gutter to run the script.
def create_job_list() -> list[JobListing]:
    job_lists: list[JobListing] = []

    # job_lists.append(JobListing('https://www.linkedin.com/jobs/search/?currentJobId=4085168619&f_E=1&f_TPR=r86400&geoId=103350119&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true', livello_esperrienza=1))
    job_lists.append(JobListing('https://www.linkedin.com/jobs/search/?currentJobId=4094512773&f_C=1073&f_PP=101085706&origin=JOB_SEARCH_PAGE_JOB_FILTER&sortBy=R'))

    return job_lists

if __name__ == '__main__':

    # df = pd.DataFrame(columns=['Mansione', 'Azienda', 'Luogo', 'Tipo', 'Durata', 'Livello', 'Dettaglio'])
    # Load the web driver and get the url


    service = Service(executable_path='/snap/bin/firefox.geckodriver')
    fp = FirefoxProfile('/home/peppe/firefox_profiles')

    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.profile = fp

    web_driver = webdriver.Firefox(service=service, options=options)


    jobs = create_job_list()

    for job_detail in jobs:
        print(f"Effettuo scraping su : {job_detail}")
        try:
            linkedin_job_scraper(job_detail, web_driver)
            print('Scraping completato!')
        except Exception as e:
            print('Scraping fallito')

    # while True:
    #     user_input = input("Inserisci URL di scraping: ")
    #     if user_input.lower() == 'stop':
    #         break
    #
    #     # Qui puoi processare l'input dell'utente
    #     print(f"Effettuo scraping su : {user_input}")
    #     try:
    #         linkedin_job_scraper(user_input)
    #         print('Scraping completato!')
    #     except Exception as e:
    #         print('Scraping fallito')

    # df.to_csv('risultati.csv', index=False)

    print("Ciclo terminato!")


