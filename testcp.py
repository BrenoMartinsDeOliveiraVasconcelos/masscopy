import time
import os

stime = time.time()
os.system("cp test_files/* -r test_output")
etime = time.time()

print(f"{etime-stime:.2f}s")
