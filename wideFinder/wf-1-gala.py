# http://memojo.com/~sgala/blog/2007/09/29/Python-Erlang-Map-Reduce

import re
from collections import defaultdict

import time, sys
if sys.platform == "win32":
    timer = time.clock
else:
    timer = time.time

t0, t1 = timer(), time.clock()

matches = (re.search(r"GET /ongoing/When/\d\d\dx/(\d\d\d\d/\d\d/\d\d/[^ .]+) ",line)
                   for line in file("o1000k.ap"))
mapp    = (match.groups()[0] for match in matches if match)

count=defaultdict(int)
for page in mapp:
    count[page] +=1

for key in sorted(count.keys(), key=count.get)[-10:]:
    pass # print "%40s = %s" % (key, count[key])

print timer() - t0, time.clock() - t1

for key in sorted(count.keys(), key=count.get)[-10:]:
    print "%40s = %s" % (key, count[key])
