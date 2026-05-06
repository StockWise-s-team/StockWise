from apscheduler.schedulers.background import BackgroundScheduler
from app.stream_a.vnstock_fetcher import VnStockFetcher
from app.stream_a.ck_api_fetcher import CkApiFetcher
from app.stream_b.cafef_crawler import CafeFCrawler
from app.stream_b.vietstock_crawler import VietstockCrawler
from app.stream_b.reuters_vn_crawler import ReutersVNCrawler
from app.stream_b.embedder import Embedder
from app.synthesis.synthesis_agent import SynthesisAgent

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_stream_a, 'interval', hours=4, id='stream_a')
    scheduler.add_job(run_stream_b, 'interval', hours=4, id='stream_b')
    scheduler.add_job(run_synthesis, 'interval', hours=4, id='synthesis')
    scheduler.start()
    return scheduler

async def run_stream_a():
    fetcher = VnStockFetcher()
    ratio_fetcher = CkApiFetcher()
    pass

async def run_stream_b():
    crawlers = [CafeFCrawler(), VietstockCrawler(), ReutersVNCrawler()]
    embedder = Embedder()
    pass

async def run_synthesis():
    agent = SynthesisAgent()
    pass
