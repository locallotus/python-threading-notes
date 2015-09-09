# chunked access from multiple threads.  on my machine, the optimal number
# of threads appears to be 2 * number of CPU:s.

import re, sys
from collections import defaultdict
import threading, Queue

# 1: 2.7 seconds
# 2: 2.5 seconds
# 3: 2.1 seconds
# 4: 2.0 seconds
# 5: 1.9 seconds
# 6: 1.9 seconds

def process(file, chunk):
    f = open(file, "rb")
    f.seek(chunk[0])
    d = defaultdict(int)
    for page in pat.findall(f.read(chunk[1])):
        d[page] += 1
    return d

def getchunks(file, size=1024*1024):
    # yield sequence of (start, size) chunk descriptors
    f = open(file, "rb")
    while 1:
        start = f.tell()
        f.seek(size, 1)
        s = f.readline() # skip forward to next line ending
        yield start, f.tell() - start
        if not s:
            break

class Worker(threading.Thread):
    def run(self):
        while 1:
            chunk = queue.get()
            if chunk is None:
                break
            result.append(process(*chunk))
            queue.task_done()

# --------------------------------------------------------------------

import time, sys
if sys.platform == "win32":
    timer = time.clock
else:
    timer = time.time

t0, t1 = timer(), time.clock()

pat = re.compile(r"GET /ongoing/When/\d\d\dx/(\d\d\d\d/\d\d/\d\d/[^ .]+) ")

FILE = "o1000k.ap"

try:
    count = int(sys.argv[1])
except:
    count = 2

queue = Queue.Queue()
result = []

for i in range(count):
    w = Worker()
    w.setDaemon(1)
    w.start()

for chunk in getchunks(FILE):
    queue.put((FILE, chunk))

queue.join()

count = defaultdict(int)
for item in result:
    for key, value in item.items():
        count[key] += value

for key in sorted(count, key=count.get)[:10]:
    pass # print "%40s = %s" % (key, count[key])

print timer() - t0, time.clock() - t1

# --------------------------------------------------------------------

for key in sorted(count, key=count.get)[-10:]:
    print "%40s = %s" % (key, count[key])
