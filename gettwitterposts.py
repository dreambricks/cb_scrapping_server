import os
import requests
import csv
import argparse
import logging

# Configuração do logger para exibir informações no console durante a execução
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Obtenção do token de autenticação do ambiente. Exibe erro se o token não estiver configurado
bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
if not bearer_token:
    logger.error("TWITTER_BEARER_TOKEN não encontrado. Configure-o como uma variável de ambiente.")

# URL para o endpoint de busca de tweets recentes na API do Twitter
search_url = "https://api.twitter.com/2/tweets/search/recent"

def bearer_oauth(r):
    """
    Função para autenticação Bearer. 
    Define o cabeçalho da requisição com o token de autenticação e um identificador de usuário para a requisição.
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    """
    Função para fazer a requisição ao endpoint fornecido.
    Exibe a URL da requisição e trata o status da resposta, retornando os dados em JSON se bem-sucedido.
    """
    response = requests.get(url, auth=bearer_oauth, params=params)
    logger.info(f"Requisição para URL: {response.url}")
    if response.status_code != 200:
        logger.error(f"Erro na requisição: {response.status_code} - {response.text}")
        return None
    return response.json()

def fetch_mentions(username, max_results):
    """
    Busca menções recentes a um usuário específico.
    - username: nome do usuário a ser buscado.
    - max_results: máximo de resultados (ajustado para valores entre 10 e 100).
    """
    max_results = max(10, min(max_results, 100))  # Limita max_results entre 10 e 100
    query = f"@{username} -is:retweet"  # Busca tweets com menções ao usuário, excluindo retweets
    query_params = {
        'query': query,
        'tweet.fields': 'created_at,author_id,text',
        'max_results': max_results
    }
    logger.info(f"Buscando menções para @{username}...")
    response_json = connect_to_endpoint(search_url, query_params)
    return response_json.get("data", []) if response_json else []

def fetch_tweets_by_hashtags(hashtags, max_results):
    """
    Busca tweets que contêm uma ou mais hashtags.
    - hashtags: lista de hashtags para busca.
    - max_results: máximo de resultados (ajustado para valores entre 10 e 100).
    """
    max_results = max(10, min(max_results, 100))  # Limita max_results entre 10 e 100
    query = " OR ".join(f"#{hashtag}" for hashtag in hashtags) + " -is:retweet"  # Monta query para múltiplas hashtags, excluindo retweets
    query_params = {
        'query': query,
        'tweet.fields': 'created_at,author_id,text',
        'max_results': max_results
    }
    logger.info(f"Buscando tweets com hashtags: {', '.join(hashtags)}")
    response_json = connect_to_endpoint(search_url, query_params)
    return response_json.get("data", []) if response_json else []

def save_to_tsv(tweets, filename):
    """
    Salva a lista de tweets em um arquivo TSV.
    - tweets: lista de tweets para salvar.
    - filename: nome do arquivo de saída.
    """
    if not tweets:
        logger.info(f"Nenhum dado para salvar em {filename}")
        return

    # Escreve o conteúdo em um arquivo TSV
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(["Create Time", "Author ID", "Description"])
        for tweet in tweets:
            # Remove tabulações e quebras de linha para manter o texto em uma única linha
            cleaned_text = tweet['text'].replace('\n', ' ').replace('\t', ' ')
            writer.writerow([tweet['created_at'], tweet['author_id'], cleaned_text])
    logger.info(f"Resultados salvos em {filename}")

if __name__ == "__main__":
    # Configura argumentos de linha de comando para o script
    parser = argparse.ArgumentParser(description="Buscar menções e tweets com hashtags.")
    parser.add_argument("--username", type=str, help="Usuário para buscar menções.")
    parser.add_argument("--hashtags", nargs="+", type=str, help="Lista de hashtags para buscar tweets.")
    parser.add_argument("--max_results", type=int, default=10, help="Máximo de resultados (entre 10 e 100).")
    args = parser.parse_args()

    # Busca menções ao usuário especificado, se fornecido
    if args.username:
        mentions = fetch_mentions(args.username, args.max_results)
        save_to_tsv(mentions, f"{args.username}_mentions.tsv")

    # Busca tweets com hashtags especificadas, se fornecidas
    if args.hashtags:
        hashtag_tweets = fetch_tweets_by_hashtags(args.hashtags, args.max_results)
        save_to_tsv(hashtag_tweets, "hashtags_tweets.tsv")
