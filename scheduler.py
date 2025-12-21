import time
from parser import run_parser

print("🚀 Scheduler ishga tushdi")

while True:
    run_parser()
    time.sleep(60 * 30)  # 30 daqiqa
