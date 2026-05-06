import time
from apscheduler.schedulers.background import BackgroundScheduler

def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: print("Stream A: fetching prices..."), 'interval', hours=4)
    scheduler.add_job(lambda: print("Stream B: crawling news..."), 'interval', hours=4)
    scheduler.start()
    print("Data pipeline started. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    main()
