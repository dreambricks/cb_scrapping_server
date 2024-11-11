import os
import requests
import csv
import argparse
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuração do token de autenticação
bearer_token = os.environ.get("BEARER_TOKEN")
if not bearer_token:
    logger.error("BEARER_TOKEN não encontrado. Configure-o como uma variável de ambiente.")

search_url = "https://api.twitter.com/2/tweets/search/recent"

def bearer_oauth(r):
    """
    Função de autenticação Bearer.
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    logger.info(f"Requisição para URL: {response.url}")
    if response.status_code != 200:
        logger.error(f"Erro na requisição: {response.status_code} - {response.text}")
        return None
    return response.json()

def fetch_mentions(username, max_results):
    max_results = max(10, min(max_results, 100))
    query = f"@{username} -is:retweet"
    query_params = {
        'query': query,
        'tweet.fields': 'created_at,author_id,text',
        'max_results': max_results
    }
    logger.info(f"Buscando menções para @{username}...")
    response_json = connect_to_endpoint(search_url, query_params)
    return response_json.get("data", []) if response_json else []

def fetch_tweets_by_hashtags(hashtags, max_results):
    max_results = max(10, min(max_results, 100))
    query = " OR ".join(f"#{hashtag}" for hashtag in hashtags) + " -is:retweet"
    query_params = {
        'query': query,
        'tweet.fields': 'created_at,author_id,text',
        'max_results': max_results
    }
    logger.info(f"Buscando tweets com hashtags: {', '.join(hashtags)}")
    response_json = connect_to_endpoint(search_url, query_params)
    return response_json.get("data", []) if response_json else []

def save_to_tsv(tweets, filename):
    if not tweets:
        logger.info(f"Nenhum dado para salvar em {filename}")
        return

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(["Data", "Autor ID", "Texto"])
        for tweet in tweets:
            # Substitui tabulações e quebras de linha no texto do tweet
            cleaned_text = tweet['text'].replace('\n', ' ').replace('\t', ' ')
            writer.writerow([tweet['created_at'], tweet['author_id'], cleaned_text])
    logger.info(f"Resultados salvos em {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Buscar menções e tweets com hashtags.")
    parser.add_argument("--username", type=str, help="Usuário para buscar menções.")
    parser.add_argument("--hashtags", nargs="+", type=str, help="Lista de hashtags para buscar tweets.")
    parser.add_argument("--max_results", type=int, default=10, help="Máximo de resultados (entre 10 e 100).")
    args = parser.parse_args()

    # Buscar menções ao usuário se o username for fornecido
    if args.username:
        mentions = fetch_mentions(args.username, args.max_results)
        save_to_tsv(mentions, f"{args.username}_mentions.tsv")

    # Buscar tweets com hashtags se hashtags forem fornecidas
    if args.hashtags:
        hashtag_tweets = fetch_tweets_by_hashtags(args.hashtags, args.max_results)
        save_to_tsv(hashtag_tweets, "hashtags_tweets.tsv")
