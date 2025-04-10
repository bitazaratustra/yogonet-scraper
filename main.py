from http.client import HTTPException
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv
import asyncio
from google.oauth2 import service_account

load_dotenv()
logger = logging.getLogger(__name__)

def init_selenium():
    options = webdriver.ChromeOptions()
    options.binary_location = '/usr/bin/chromium'
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=options)

async def scrape_articles():
    driver = None
    try:
        driver = init_selenium()
        driver.set_page_load_timeout(30)
        driver.get("https://www.yogonet.com/international/")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.slot.noticia.cargada"))
        )

        articles = []
        article_containers = driver.find_elements(By.CSS_SELECTOR, "div.slot.noticia.cargada")

        for container in article_containers:
            article_data = {
                "title": "",
                "kicker": "",
                "image": "",
                "link": "",
                "word_count": 0,
                "char_count": 0,
                "capital_words": 0
            }
            try:
                title_elem = container.find_element(By.CSS_SELECTOR, "h2.titulo a")
                article_data["title"] = title_elem.text.strip()
                article_data["link"] = title_elem.get_attribute("href")

                kicker_elem = container.find_element(By.CSS_SELECTOR, "div.volanta")
                article_data["kicker"] = kicker_elem.text.strip()

                img_elem = container.find_element(By.CSS_SELECTOR, "div.imagen img")
                article_data["image"] = img_elem.get_attribute("src")

                if article_data["title"]:
                    words = article_data["title"].split()
                    article_data["word_count"] = len(words)
                    article_data["char_count"] = len(article_data["title"])
                    article_data["capital_words"] = len(
                        [word for word in words if word and word[0].isupper()]
                    )

                articles.append(article_data)
            except Exception as e:
                logger.error(f"Error procesando artículo: {str(e)}", exc_info=True)
                continue

        return articles

    except Exception as e:
        logger.error(f"Error general en scraping: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error en scraping: {str(e)}")

    finally:
        if driver:
            driver.quit()

def process_data(articles: list) -> pd.DataFrame:
    try:
        df = pd.DataFrame(articles)
        df['title'] = df['title'].fillna('').astype(str)
        df['kicker'] = df['kicker'].fillna('').astype(str)
        df['image'] = df['image'].fillna('').astype(str)
        df['link'] = df['link'].fillna('').astype(str)
        df['word_count'] = df['word_count'].fillna(0).astype('int32')
        df['char_count'] = df['char_count'].fillna(0).astype('int32')
        df['capital_words'] = df['capital_words'].fillna(0).astype('int32')
        return df.drop_duplicates(subset=['link'])
    except Exception as e:
        logger.error(f"Error procesando datos: {str(e)}", exc_info=True)
        raise HTTPException(status_code=422, detail=f"Error en procesamiento de datos: {str(e)}")

async def load_to_bigquery(df: pd.DataFrame):
    try:
        credentials = service_account.Credentials.from_service_account_file(
            "/app/creds.json",
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        client = bigquery.Client(
            credentials=credentials,
            project=credentials.project_id
        )
        job = client.load_table_from_dataframe(
            df,
            os.getenv("BQ_TABLE_ID"),
            job_config=bigquery.LoadJobConfig(
                schema=[
                    bigquery.SchemaField("title", "STRING"),
                    bigquery.SchemaField("kicker", "STRING"),
                    bigquery.SchemaField("image", "STRING"),
                    bigquery.SchemaField("link", "STRING"),
                    bigquery.SchemaField("word_count", "INTEGER"),
                    bigquery.SchemaField("char_count", "INTEGER"),
                    bigquery.SchemaField("capital_words", "INTEGER"),
                ],
                write_disposition="WRITE_APPEND"
            )
        )
        await asyncio.to_thread(job.result)
        logger.info("Datos cargados en BigQuery")
    except Exception as e:
        logger.error(f"Error en BigQuery: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error BigQuery: {str(e)}")


async def run_scraper():
    try:
        articles = await scrape_articles()
        df = process_data(articles)
        await load_to_bigquery(df)
        return {
            "status": "success",
            "articles_processed": len(df),
            "message": f"{len(df)} artículos procesados"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error general: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno")


if __name__ == "__main__":
    run_scraper()
