import csv
import time
import logging
import pandas as pd
from pytrends.request import TrendReq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Função para combinar os dados em um único DataFrame e salvar como TSV
def combine_and_save_trends(twitter_data, tiktok_data, google_data):
    logger.info("Combinando dados de todas as plataformas...")

    # Convertendo os dados em DataFrames
    twitter_df = pd.DataFrame(twitter_data, columns=["Hashtag", "Contagem"])
    tiktok_df = pd.DataFrame(tiktok_data, columns=["Hashtag", "Contagem"])
    google_df = google_data  # Já é um DataFrame

    # Concatenando os DataFrames
    combined_df = pd.concat([twitter_df, tiktok_df, google_df], ignore_index=True)

    # Salvando em um arquivo TSV
    tsv_filename = "all_trends.tsv"
    combined_df.to_csv(tsv_filename, sep='\t', index=False)

    logger.info(f"Dados combinados salvos em {tsv_filename}.")

# Funções para extrair tendências das plataformas
# Função para extrair tendências do Twitter usando Selenium
def get_twitter_trends(url):
    logger.info("Iniciando extração de tendências do Twitter...")
    service = Service(ChromeDriverManager().install())
    options = Options()
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        logger.info("Página do Twitter Trends carregada.")

        # Verifica e fecha possíveis pop-ups sobrepondo a página
        try:
            logger.info("Verificando pop-ups na página...")
            overlay_close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Fechar' or contains(@class, 'close')]"))
            )
            overlay_close_button.click()
            logger.info("Pop-up fechado com sucesso.")
        except (TimeoutException, NoSuchElementException):
            logger.info("Nenhum pop-up encontrado.")

        # Usa JavaScript para forçar o clique no botão
        try:
            logger.info("Procurando botão de navegação...")
            button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "tab-link-table"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            driver.execute_script("arguments[0].click();", button)
            logger.info("Botão clicado com sucesso.")
        except TimeoutException:
            logger.error("Botão de navegação não encontrado.")
            return []

        # Espera até que os elementos com os tópicos estejam visíveis
        logger.info("Esperando que os tópicos sejam carregados...")
        WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "td.topic a"))
        )

        topic_elements = driver.find_elements(By.CSS_SELECTOR, "td.topic")
        count_elements = driver.find_elements(By.CSS_SELECTOR, "td.count")

        trends = []  
        for count, topic in zip(count_elements, topic_elements):
            formatted_count = count.text.replace('.', '').replace(',', '')  # Remove pontos e vírgulas
            trends.append([topic.text, formatted_count])

        logger.info(f"Tendências extraídas: {len(trends)} itens encontrados.")
        
        # Salvar em CSV com tabulação
        csv_filename = "twitter_trends.tsv"
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(["Hashtags", "Contagem"])
            writer.writerows(trends)

        logger.info(f"Tendências salvas em {csv_filename}.")
        return trends if trends else []

    finally:
        logger.info("Fechando o navegador do Twitter Trends.")
        driver.quit()


# Função para extrair hashtags populares do TikTok usando Selenium
def get_tiktok_trends(url):
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("window-size=1300,900")  # Largura maior que 1200

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        logger.info("Página do TikTok Trends carregada.")

        # Espera até que o botão de seleção de idioma esteja presente e clique nele
        try:
            logger.info("Procurando o botão de seleção de idioma...")
            language_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-testid='cc_rimless_select_language']"))
            )
            logger.info("Botão de idioma encontrado. Clicando...")
            language_button.click()
            
            # Clica na opção "Português (Brasil)"
            logger.info("Procurando a opção 'Português (Brasil)'...")
            portuguese_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[text()='Português (Brasil)']"))
            )
            logger.info("Opção 'Português (Brasil)' encontrada. Clicando...")
            portuguese_option.click()
        except Exception as e:
            logger.error(f"Erro ao selecionar o idioma: {e}")
            return []

        # Aguarda alguns segundos para que a página seja atualizada
        logger.info("Aguardando a atualização da página...")
        time.sleep(10)

        # Fecha o pop-up do Symphony Assistant, se presente
        try:
            logger.info("Procurando o botão de fechamento do pop-up...")
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//img[@alt='TikTok Symphony Assistant' and contains(@src, 'logo_v2_close.svg')]"))
            )
            close_button.click()
            logger.info("Botão de fechar clicado com sucesso.")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Erro ao interagir com o botão de fechamento do pop-up: {e}")

        # Coleta todas as hashtags e postagens visíveis de uma vez
        logger.info("Coletando hashtags e postagens...")
        hashtag_elements = driver.find_elements(By.CSS_SELECTOR, "span[class*='CardPc_titleText__']")
        post_elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='CardPc_pavWrapper__']")

        trends = []
        for hashtag, post in zip(hashtag_elements, post_elements):
            if '#' in hashtag.text:
                # Limpa quebras de linha e texto adicional indesejado
                clean_hashtag = hashtag.text.replace('\n', ' ').strip()
                clean_post = post.text.replace('\n', ' ').replace('Postagens', '').strip()

                # Substitui 'k' ou 'K' por '000'
                if 'k' in clean_post.lower():
                    clean_post = clean_post.lower().replace('k', '000')

                trends.append([clean_hashtag, clean_post])

        if trends:
            logger.info(f"Total de hashtags e postagens extraídas: {len(trends)}")
        else:
            logger.warning("Nenhuma hashtag ou postagem encontrada.")

        # Salvar em formato CSV sem aspas
        csv_filename = "tiktok_trends.tsv"
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t', quoting=csv.QUOTE_MINIMAL, escapechar='\\')
            writer.writerow(["Hashtag", "Contagem"])
            writer.writerows(trends)

        logger.info(f"Tendências salvas em {csv_filename}.")
        return trends

    finally:
        logger.info("Fechando o navegador do TikTok Trends.")
        driver.quit()

def get_google_trends():
    logger.info("Iniciando extração de tendências do Google Trends...")

    # Configuração da API
    pytrends = TrendReq(hl='pt-BR', tz=360)
    logger.info("API do pytrends configurada com sucesso.")

    try:
        # Obter as tendências diárias do Google Trends
        logger.info("Obtendo tendências diárias do Google Trends...")
        trends = pytrends.trending_searches(pn='brazil')
        trends.columns = ['Hashtag']  # Renomear a coluna

        # Criar uma lista para armazenar os dados de contagem
        contagens = []

        # Obter o volume de pesquisa nas últimas 24 horas para cada tendência
        for hashtag in trends['Hashtag']:
            logger.info(f"Consultando dados de interesse ao longo do tempo para: {hashtag}")
            pytrends.build_payload([hashtag], cat=0, timeframe='now 1-d', geo='BR')
            interest = pytrends.interest_over_time()

            if not interest.empty:
                # Obter o último valor de contagem (mais recente)
                last_value = interest[hashtag].iloc[-1]
                contagens.append(last_value)
            else:
                contagens.append(0)  # Adicionar 0 se não houver dados

        # Adicionar a coluna 'Contagem' ao DataFrame
        trends['Contagem'] = contagens

        # Salvar em um arquivo TSV com tabulação
        tsv_filename = "google_trends.tsv"
        trends.to_csv(tsv_filename, sep='\t', index=False)
        logger.info(f"Tendências salvas em {tsv_filename}.")

        return trends

    except Exception as e:
        logger.error(f"Erro durante a extração das tendências: {e}")
        return None

# Função principal
if __name__ == "__main__":
    # URLs para tendências
    twitter_url = 'https://trends24.in/brazil/'
    titktok_url = 'https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/pt?from=001119'

    # Extrair dados de cada plataforma
    twitter_trends_data = get_twitter_trends(twitter_url)
    tiktok_trends_data = get_tiktok_trends(titktok_url)
    google_trends_data = get_google_trends()

    # Combinar e salvar os dados extraídos
    if twitter_trends_data and tiktok_trends_data and google_trends_data is not None:
        combine_and_save_trends(twitter_trends_data, tiktok_trends_data, google_trends_data)
    else:
        logger.error("Erro ao obter dados de uma ou mais plataformas. Verifique os logs para detalhes.")

    logger.info("Processo concluído.")