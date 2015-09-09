# dalke-wf-7.py
# http://www.dalkescientific.com/writings/diary/archive/2007/10/07/wide_finder.html
'''
mmap and re playing together using the buffer interface

Python has a concept called a buffer interface. Strings and a few other data types, including memory-mapped files, implement the buffer interface.
String operations (like 'find') and regular expressions can work on buffer objects. Which means I am able to apply the regular expression directly to a memory-mapped file.
'''
import re, os, mmap
from collections import defaultdict

FILE = "o1000k.ap"

import time, sys
if sys.platform == "win32":
    timer = time.clock
else:
    timer = time.time

t0, t1 = timer(), time.clock()

pat = re.compile(r"GET /ongoing/When/\d\d\dx/(\d\d\d\d/\d\d/\d\d/[^ .]+) ")

fileobj = open(FILE)
filemap = mmap.mmap(fileobj.fileno(), os.path.getsize(FILE), access=mmap.ACCESS_READ)

count = defaultdict(int)
for m in pat.findall(filemap):
    count[m] +=1

for key in sorted(count, key=count.get)[:10]:
    pass # print "%40s = %s" % (key, count[key])

print timer() - t0, time.clock() - t1

# sanity check
for key in sorted(count, key=count.get)[-10:]:
    print "%40s = %s" % (key, count[key])

'''
In my original code I used finditer instead of findall to find all the matches.
The finditer returns match objects while findall only returns the matching text.
(But read the docs because findall returns a tuple instead of a string if there is more than one group in the pattern.)
Making the extra objects takes time and I was able to make my code about 5% faster using findall.

Had I not tried to implement my code first, I wouldn't have thought of trying 'finditer'.
Had I not compared my result to Fredrik's I wouldn't have thought of using 'findall'.
Becoming a better programmer means you have to do both.

My single-threaded dalke-wf-7.py runs in 1.3s. Compare that to Fredrik's best single-threaded version at 1.7s and his best dual-process version wf-6.py at 1.0s.
I think this is the best performance and cleanest code you can get using this general approach, though I would like a shorter way to open a memory-mapped file.
I count 12 non-blank/non-timing lines while Tim's original Ruby code has 11. His machine looks about 1/2 the speed of mine so this Python code is roughly 2-3 faster than his Ruby.
That's about what I've seen in other performance comparisons between the two languages.
'''