import schedule
import time
import subprocess
import sqlite3
from datetime import datetime

def run_scraper():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Running scraper...")
    subprocess.run(["python", "scraper.py"])
    print("Scraper done. Running blog generator...")
    subprocess.run(["python", "blog_generator.py"])
    print("All done! Website updated with fresh scholarships.")

# Run once immediately on start
run_scraper()

# Then run every day at 8:00 AM automatically
schedule.every().day.at("08:00").do(run_scraper)

print("\nAuto-runner is active. Scholarships will refresh every day at 8 AM.")
print("Keep this window open. Press Ctrl+C to stop.\n")

while True:
    schedule.run_pending()
    time.sleep(60)