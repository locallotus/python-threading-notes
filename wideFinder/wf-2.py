# a slightly optimized version of Santiago Gala's original Python
# implementation.  see:
# http://memojo.com/~sgala/blog/2007/09/29/Python-Erlang-Map-Reduce

import re
from collections import defaultdict

FILE = "o1000k.ap"

import time, sys
if sys.platform == "win32":
    timer = time.clock
else:
    timer = time.time

t0, t1 = timer(), time.clock()

pat = re.compile(r"GET /ongoing/When/\d\d\dx/(\d\d\d\d/\d\d/\d\d/[^ .]+) ")

search = pat.search

# map
matches = (search(line) for line in open(FILE, "rb") if "GET /ongoing/When" in line)
mapp    = (match.group(1) for match in matches if match)

# reduce
count = defaultdict(int)
for page in mapp:
    count[page] +=1

for key in sorted(count, key=count.get)[:10]:
    pass # print "%40s = %s" % (key, count[key])

print timer() - t0, time.clock() - t1

# sanity check
for key in sorted(count, key=count.get)[-10:]:
    print "%40s = %s" % (key, count[key])
