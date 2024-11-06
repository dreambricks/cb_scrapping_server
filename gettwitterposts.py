import requests
import logging
import csv

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Função para buscar as últimas menções a um usuário específico
def fetch_mentions(username, bearer_token):
    url = f"https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {
        "query": f"@{username}",  # Termo de pesquisa
        "tweet.fields": "created_at,author_id,text"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        tweets = response.json().get('data', [])
        return tweets
    except requests.exceptions.HTTPError as e:
        if response.status_code == 400:
            logger.error("Erro de requisição: Parâmetros inválidos ou formato de consulta incorreto.")
        else:
            logger.error(f"Erro ao buscar menções: {e}")
        return None

# Função para salvar as menções em um arquivo TSV
def save_mentions_to_tsv(tweets, filename="mentions.tsv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(["Data", "Autor ID", "Texto"])
        for tweet in tweets:
            writer.writerow([tweet['created_at'], tweet['author_id'], tweet.get('text', '')])

if __name__ == "__main__":
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAHwowwEAAAAAhUAqc0AaPESi0lNUPigFjx%2B0nmk%3DqS0lZ0FRvRdh6s7cmmYTTZ274GqfMHu253y5nOX8RomEGEJjER"
    username = "CasasBahia"

    logger.info("Buscando as últimas menções...")
    tweets = fetch_mentions(username, bearer_token)
    
    if tweets:
        save_mentions_to_tsv(tweets)
        logger.info("Menções salvas em mentions.tsv.")
    else:
        logger.error("Falha ao obter menções.")
