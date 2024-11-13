import asyncio
import logging
import csv
from instagrapi import Client
import os

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Autenticação com instagrapi
def authenticate():
    client = Client()
    username = os.getenv("INSTAGRAM_USERNAME")
    password = os.getenv("INSTAGRAM_PASSWORD")
    if not username or not password:
        logger.error("Credenciais do Instagram não configuradas.")
        raise SystemExit("Erro: Credenciais do Instagram não configuradas.")
    client.login(username, password)
    return client

def save_posts_to_tsv(posts, filename):
    """ Salva informações dos posts em um arquivo TSV. """
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(["Id", "Legenda", "Curtidas", "Comentários", "Postado"])
        for post in posts:
            writer.writerow([
                post.pk,
                post.caption_text[:100],  # Limitar o texto da legenda a 100 caracteres
                post.like_count,
                post.comment_count,
                post.taken_at
            ])
    logger.info(f"Posts salvos em {filename}")

def fetch_user_posts(client, username):
    """ Busca posts de um usuário específico. """
    user_id = client.user_id_from_username(username)
    posts = client.user_medias(user_id, amount=5)  # Limita a 5 posts
    save_posts_to_tsv(posts, f"{username}_posts.tsv")

def fetch_hashtag_posts(client, hashtag):
    """ Busca posts de uma hashtag específica. """
    posts = client.hashtag_medias_recent(hashtag, amount=5)  # Limita a 5 posts
    save_posts_to_tsv(posts, f"{hashtag}_hashtag_posts.tsv")

async def main():
    client = authenticate()
    username = "casabahia"
    hashtag = "blackfriday"
    fetch_user_posts(client, username)
    fetch_hashtag_posts(client, hashtag)

if __name__ == "__main__":
    asyncio.run(main())
