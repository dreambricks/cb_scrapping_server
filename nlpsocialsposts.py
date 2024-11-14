import spacy
import pandas as pd
from langdetect import detect, LangDetectException
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_models():
    """Carrega os modelos de linguagem para inglês, português e espanhol do spaCy."""
    try:
        nlp_en = spacy.load("en_core_web_sm")
        nlp_pt = spacy.load("pt_core_news_sm")
        nlp_es = spacy.load("es_core_news_sm")
        logger.info("Modelos de linguagem carregados com sucesso.")
        return nlp_en, nlp_pt, nlp_es
    except Exception as e:
        logger.error(f"Falha ao carregar os modelos de linguagem: {e}")
        raise

def detect_language(text):
    """Detecta o idioma do texto fornecido."""
    try:
        return detect(text)
    except LangDetectException:
        return 'unknown'

def process_text(text, nlp_en, nlp_pt, nlp_es):
    """Processa o texto usando o modelo de linguagem apropriado baseado no idioma detectado."""
    lang = detect_language(text)
    if lang == 'en':
        doc = nlp_en(text)
    elif lang == 'pt':
        doc = nlp_pt(text)
    elif lang == 'es':
        doc = nlp_es(text)
    else:
        logger.info(f"Idioma não identificado ou suportado para o texto: {text}")
        return []
    return [(ent.text, ent.label_) for ent in doc.ents]

def analyze_file(file_path, nlp_en, nlp_pt, nlp_es):
    """Analisa o arquivo TSV e processa cada descrição com o modelo apropriado."""
    try:
        df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
        logger.info(f"Arquivo {file_path} carregado com sucesso.")
        
        df['Entities'] = df['Description'].apply(lambda x: process_text(x, nlp_en, nlp_pt, nlp_es))
        
        output_path = file_path.replace('.tsv', '_processed.tsv')
        df.to_csv(output_path, sep='\t', index=False)
        logger.info(f"Arquivo processado salvo em {output_path}")
    except Exception as e:
        logger.error(f"Erro ao processar o arquivo {file_path}: {e}")

if __name__ == "__main__":
    nlp_en, nlp_pt, nlp_es = load_models()
    files = ['blackfriday_trending_videos.tsv', 'casasbahia_mentions.tsv', 'casasbahia_videos.tsv', 'hashtags_tweets.tsv']
    for file in files:
        analyze_file(file, nlp_en, nlp_pt, nlp_es)
