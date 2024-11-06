import pandas as pd
from pytrends.request import TrendReq
import logging
import time

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuração do pytrends
pytrends = TrendReq(hl='pt-BR', tz=360)

# Lista de estados do Brasil
estados = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
           "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", 
           "RS", "RO", "RR", "SC", "SP", "SE", "TO"]

# Produtos populares de e-commerce para monitoramento
produtos_populares = [
    # Celulares e Telefonia
    "Celular", "iPhone", "Samsung Galaxy", "Xiaomi", "Motorola", "Nokia", "OnePlus", "Realme",
    "Smartwatch", "Fone de Ouvido Bluetooth", "Carregador Portátil", "Capinha de Celular",
    
    # Televisores
    "Smart TV", "Televisão LED", "TV 4K", "TV 8K", "TV OLED", "TV QLED", "TV 50 polegadas", 
    "Chromecast", "Fire Stick", "Apple TV", "Suporte para TV", "Caixa de Som para TV",
    
    # Eletroportáteis
    "Airfryer", "Cafeteira", "Batedeira", "Liquidificador", "Fritadeira Elétrica", 
    "Aspirador de Pó", "Ferro de Passar", "Panela Elétrica", "Ventilador", "Purificador de Água",
    "Chaleira Elétrica", "Espremedor de Frutas", "Processador de Alimentos", "Grill Elétrico",
    
    # Eletrodomésticos
    "Geladeira", "Fogão", "Micro-ondas", "Máquina de Lavar", "Lava e Seca", "Freezer", 
    "Aquecedor de Água", "Forno Elétrico", "Adega Climatizada", "Exaustor de Cozinha", 
    "Cooktop", "Depurador de Ar", "Climatizador de Ar",
    
    # Mobiliário
    "Sofá", "Cama Box", "Mesa de Jantar", "Guarda-roupa", "Escrivaninha", "Poltrona", 
    "Rack para TV", "Estante", "Cadeira de Escritório", "Colchão", "Painel para TV", 
    "Balcão de Cozinha", "Sapateira", "Armário Multiuso", "Penteadeira", "Berço", 
    "Mesa de Centro", "Cadeira Gamer", "Banqueta Alta"
]

# Função para obter as tendências de produtos em um estado específico, pesquisando uma palavra por vez
def obter_tendencias_estado(estado):
    logger.info(f"Iniciando consulta de tendências para o estado: {estado}")

    resultados = []

    # Consultar cada produto individualmente
    for index, produto in enumerate(produtos_populares):
        logger.info(f"Consultando produto: {produto}")

        try:
            pytrends.build_payload([produto], timeframe='now 7-d', geo=f'BR-{estado}')
            interesse_regiao = pytrends.interest_by_region(resolution='REGION')

            if not interesse_regiao.empty and estado in interesse_regiao.index:
                # Extrair apenas a pontuação do estado
                pontuacao = interesse_regiao.loc[estado, produto]
                resultados.append({
                    'Produto': produto,
                    'Pontuação': round(pontuacao),
                    'Estado': estado
                })

        except Exception as e:
            logger.error(f"Erro ao consultar produto {produto}: {e}")

        # Insira uma pausa a cada 5 consultas
        if index % 5 == 0 and index != 0:
            print("Esperando para evitar limite de requisições...")
            time.sleep(60)  # Aguarde 60 segundos

    # Convertendo os resultados em DataFrame
    if resultados:
        resultado_final = pd.DataFrame(resultados)
        return resultado_final
    else:
        logger.warning(f"Nenhum dado encontrado para o estado {estado}")
        return None

# Função principal para execução do código
if __name__ == "__main__":
    print("Escolha um estado da lista:", ", ".join(estados))
    estado_selecionado = input("Digite o código do estado (ex: SP): ").strip().upper()

    if estado_selecionado in estados:
        tendencias_estado = obter_tendencias_estado(estado_selecionado)

        if tendencias_estado is not None:
            tsv_filename = f"produtos_populares_{estado_selecionado.lower()}.tsv"
            tendencias_estado.to_csv(tsv_filename, sep='\t', index=False)
            logger.info(f"Tendências salvas em {tsv_filename}.")
        else:
            logger.warning("Não foi possível obter tendências para o estado selecionado.")
    else:
        logger.error("Estado inválido. Execute o programa novamente e escolha um estado válido.")
