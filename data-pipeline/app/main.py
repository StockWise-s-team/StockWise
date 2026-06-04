import time
from app.scheduler import start_scheduler

def main():
    scheduler = start_scheduler()
    print("Data pipeline started. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    main()
