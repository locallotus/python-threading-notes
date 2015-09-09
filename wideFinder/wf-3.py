# chunked access

import re
from collections import defaultdict

FILE = "o1000k.ap"

def getchunks(file, size=1024*1024):
    # scan a file, and yield sequence of (start, size) chunk descriptors
    # where all chunks contain full lines
    f = open(file, "rb")
    while 1:
        start = f.tell()
        f.seek(size, 1)
        s = f.readline() # skip forward to next line ending
        yield start, f.tell() - start
        if not s:
            break

if 0:

    def process(file, chunk):
        # collect statistics for a chunk (process lines)
        f = open(file, "rb")
        f.seek(chunk[0])
        d = defaultdict(int)
        search = pat.search
        for line in f.read(chunk[1]).splitlines():
            if "GET /ongoing/When" in line:
                m = search(line)
                if m:
                    d[m.group(1)] += 1
        return d

else:

    def process(file, chunk):
        # collect statistics for a chunk (process entire chunk)
        f = open(file, "rb")
        f.seek(chunk[0])
        d = defaultdict(int)
        s = f.read(chunk[1])
        for page in pat.findall(s):
            d[page] += 1
        return d

# --------------------------------------------------------------------
# main program

import time, sys
if sys.platform == "win32":
    timer = time.clock
else:
    timer = time.time

t0, t1 = timer(), time.clock()

pat = re.compile(r"GET /ongoing/When/\d\d\dx/(\d\d\d\d/\d\d/\d\d/[^ .]+) ")

count = defaultdict(int)

for chunk in getchunks(FILE):
    for key, value in process(FILE, chunk).items():
        count[key] += value

for key in sorted(count, key=count.get)[:10]:
    pass # print "%40s = %s" % (key, count[key])

print timer() - t0, time.clock() - t1

# --------------------------------------------------------------------

for key in sorted(count, key=count.get)[-10:]:
    print "%40s = %s" % (key, count[key])
