import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.stream_a.vnstock_fetcher import VnStockFetcher
from app.stream_a.ck_api_fetcher import CkApiFetcher
from app.stream_b.cafef_crawler import CafeFCrawler
from app.stream_b.vietstock_crawler import VietstockCrawler
from app.stream_b.reuters_vn_crawler import ReutersVNCrawler
from app.stream_b.embedder import Embedder
from app.synthesis.synthesis_agent import SynthesisAgent

logger = logging.getLogger(__name__)

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_stream_a, 'interval', hours=4, id='stream_a')
    scheduler.add_job(run_stream_b, 'interval', hours=4, id='stream_b')
    scheduler.add_job(run_synthesis, 'interval', hours=4, id='synthesis')
    scheduler.start()
    return scheduler

def run_stream_a():
    try:
        logger.info("Stream A: Starting price fetch...")
        fetcher = VnStockFetcher()
        ratio_fetcher = CkApiFetcher()
        logger.info("Stream A: Price fetch completed")
    except Exception as e:
        logger.error(f"Stream A failed: {e}")

def run_stream_b():
    try:
        logger.info("Stream B: Starting news crawl...")
        crawlers = [CafeFCrawler(), VietstockCrawler(), ReutersVNCrawler()]
        embedder = Embedder()
        logger.info("Stream B: News crawl completed")
    except Exception as e:
        logger.error(f"Stream B failed: {e}")

def run_synthesis():
    try:
        logger.info("Synthesis: Starting wiki synthesis...")
        agent = SynthesisAgent()
        logger.info("Synthesis: Wiki synthesis completed")
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
