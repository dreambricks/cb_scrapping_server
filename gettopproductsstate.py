import pandas as pd
from pytrends.request import TrendReq
import logging
import time
import random

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuração do pytrends
pytrends = TrendReq(hl='pt-BR', tz=360)

# Lista de estados do Brasil
states  = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
           "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", 
           "RS", "RO", "RR", "SC", "SP", "SE", "TO"]

# Produtos populares de e-commerce organizados por categoria
product_categories  = {
    'Telefonia': ["Celular", "iPhone", "Samsung Galaxy", "Xiaomi", "Motorola"],
    'Eletrônicos': ["Smart TV", "Chromecast", "Fire Stick", "Televisão LED", "TV 4K", "TV 8K", "TV OLED"],
    'Eletroportáteis': ["Airfryer", "Cafeteira", "Batedeira", "Liquidificador", "Aspirador de Pó", "Ferro de Passar"],
    'Eletrodomésticos': ["Geladeira", "Fogão", "Micro-ondas", "Máquina de Lavar", "Lava e Seca", "Freezer"],
    'Mobiliário': ["Sofá", "Cama Box", "Estante", "Mesa de Jantar", "Guarda-roupa", "Escrivaninha", "Poltrona"]
}

# # Produtos populares de e-commerce para monitoramento
# produtos_populares = [
#     # Celulares e Telefonia
#     "Celular", "iPhone", "Samsung Galaxy", "Xiaomi", "Motorola", "Nokia", "OnePlus", "Realme",
#     "Smartwatch", "Fone de Ouvido Bluetooth", "Carregador Portátil", "Capinha de Celular",
    
#     # Televisores
#     "Smart TV", "Televisão LED", "TV 4K", "TV 8K", "TV OLED", "TV QLED", "TV 50 polegadas", 
#     "Chromecast", "Fire Stick", "Apple TV", "Suporte para TV", "Caixa de Som para TV",
    
#     # Eletroportáteis
#     "Airfryer", "Cafeteira", "Batedeira", "Liquidificador", "Fritadeira Elétrica", 
#     "Aspirador de Pó", "Ferro de Passar", "Panela Elétrica", "Ventilador", "Purificador de Água",
#     "Chaleira Elétrica", "Espremedor de Frutas", "Processador de Alimentos", "Grill Elétrico",
    
#     # Eletrodomésticos
#     "Geladeira", "Fogão", "Micro-ondas", "Máquina de Lavar", "Lava e Seca", "Freezer", 
#     "Aquecedor de Água", "Forno Elétrico", "Adega Climatizada", "Exaustor de Cozinha", 
#     "Cooktop", "Depurador de Ar", "Climatizador de Ar",
    
#     # Mobiliário
#     "Sofá", "Cama Box", "Mesa de Jantar", "Guarda-roupa", "Escrivaninha", "Poltrona", 
#     "Rack para TV", "Estante", "Cadeira de Escritório", "Colchão", "Painel para TV", 
#     "Balcão de Cozinha", "Sapateira", "Armário Multiuso", "Penteadeira", "Berço", 
#     "Mesa de Centro", "Cadeira Gamer", "Banqueta Alta"
#]


def get_trends_by_state(state):
    logger.info(f"Iniciando consulta de tendências para o estado: {state}")
    results = []

    for category, products in product_categories.items():
        logger.info(f"Consultando categoria: {category}")
        # Seleciona um subconjunto aleatório de produtos para consulta
        selected_products = random.sample(products, min(len(products), random.randint(3, 5)))
        for product in selected_products:
            try:
                pytrends.build_payload([product], timeframe='now 7-d', geo=f'BR-{state}')
                regional_interest = pytrends.interest_by_region(resolution='REGION')
                if state in regional_interest.index:
                    score = regional_interest.loc[state, product]
                    results.append({
                        'Estado': state,
                        'Produto': product
                    })

            except Exception as e:
                logger.error(f"Erro ao consultar produto {product}: {e}")

            # Espera aleatória entre consultas para evitar bloqueio
            time.sleep(random.randint(120, 900))  # Espera de 2 a 15 minutos

    return pd.DataFrame(results) if results else None

def process_all_regions():
    for state in states:
        logger.info(f"Processando o estado {state}")
        state_results  = get_trends_by_state(state)
        if state_results  is not None:
            filename = f"tendencias_{state.lower()}.tsv"
            state_results .to_csv(filename, sep='\t', index=False)
            logger.info(f"Tendências salvas em {filename}.")
        else:
            logger.warning(f"Nenhum dado encontrado para o estado {state}")

if __name__ == "__main__":
    process_all_regions()
