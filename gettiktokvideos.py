import asyncio
import logging
import csv
from TikTokApi import TikTokApi
import os

# Configuração básica do logger para captura e exibição de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

"""
Obtenha seu próprio ms_token dos cookies do TikTok.com e configure como uma variável de ambiente.

    Abra o TikTok no seu navegador: Vá para TikTok.com e faça login em sua conta, se necessário.

    Abra o Inspect Tool: Clique com o botão direito em qualquer parte da página e selecione "Inspect" ou
    "Inspect Element", dependendo do seu navegador. Isso abrirá as ferramentas de desenvolvedor.

    Vá para a aba Network: Assegure-se de que está na aba "Network" (Rede).

    Interaja com o site: Faça algumas ações no site como navegar entre páginas ou vídeos. Isso garantirá
    que os cookies e requisições relevantes apareçam nas ferramentas de desenvolvedor.

    Encontre o Cookiepytho: Procure por requisições feitas ao domínio do TikTok que incluam cookies. 
    Clique numa requisição e procure nos detalhes por algo chamado ms_token nos cookies enviados na requisição.

    Copie o valor do ms_token: Esse é o token que você precisa.
"""

ms_token = os.environ.get("TIKTOK_MS_TOKEN")
if not ms_token:
    # Se o token não estiver configurado, registra um erro e encerra a execução
    logger.error("Variável de ambiente TIKTOK_MS_TOKEN não configurada.")
    raise SystemExit("Erro: ms_token não configurado.")

async def save_videos_to_tsv(videos, filename):
    """ Salva informações de vídeos em um arquivo TSV. """
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        # Escreve o cabeçalho do arquivo TSV
        writer.writerow(["ID", "Description", "Create Time", "Likes", "Comments", "Shares"])
        # Itera sobre cada vídeo e salva suas informações
        for video in videos:
            writer.writerow([
                video['id'],
                video.get('desc', 'No description provided.'),
                video['createTime'],
                video['stats']['diggCount'],
                video['stats']['commentCount'],
                video['stats']['shareCount']
            ])
    logger.info(f"Vídeos salvos em {filename}")

async def fetch_user_videos(username):
    """ Busca e armazena vídeos de um usuário específico. """
    async with TikTokApi() as api:
        try:
            await api.create_sessions(ms_tokens=[ms_token], num_sessions=1)
            user = api.user(username=username)
            videos = []
            # Busca até 5 vídeos do usuário
            async for video in user.videos(count=5):
                videos.append(video.as_dict())
            if videos:
                await save_videos_to_tsv(videos, f"{username}_videos.tsv")
        except Exception as e:
            logger.error(f"Erro ao buscar vídeos do usuário {username}: {e}")

async def fetch_trending_videos(hashtag):
    """ Busca e armazena vídeos trending de uma hashtag específica. """
    async with TikTokApi() as api:
        try:
            await api.create_sessions(ms_tokens=[ms_token], num_sessions=1)
            tag = api.hashtag(name=hashtag)
            videos = []
            # Busca até 5 vídeos trending da hashtag
            async for video in tag.videos(count=5):
                videos.append(video.as_dict())
            if videos:
                await save_videos_to_tsv(videos, f"{hashtag}_trending_videos.tsv")
        except Exception as e:
            logger.error(f"Erro ao buscar vídeos da hashtag {hashtag}: {e}")

if __name__ == "__main__":
    username = "casasbahia"
    hashtag = "blackfriday"
    logger.info("Iniciando a busca de vídeos...")
    asyncio.run(fetch_user_videos(username))
    asyncio.run(fetch_trending_videos(hashtag))
