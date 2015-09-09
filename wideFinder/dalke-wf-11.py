# dalke-wf-11.py  fast string ops, chunk-based reader, post-process filter
# http://www.dalkescientific.com/writings/diary/archive/2007/10/07/wide_finder.html
'''
Chunked reading can beat mmap?

I did test a chunk-driven version of this last code, instead of using a mmap'ed file.
Strange thing is that with a tuned chunk size I could get the performance to be faster than using a mmap'ed file.
It looks like I'll be using a chunk size of 14K in future code!
Though I don't know what chunks would be faster than mmap here.
If you're interested, here it is:
'''

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

# Choosing the right chunk size affect the timings.  Here
# are performance numbers for my machine.
#     255K  1.1477599144 1.12
#      64K  1.18760800362 1.17
#      32K  1.2726931572 1.25
#      16K  1.44729995728 1.42
#      14K  0.951714038849 0.94  # the mmap version is slower, at 1.0 seconds!
#      12K  0.967882871628 0.95
#      10K  0.983233213425 0.97
#       8K  1.02103090286 1.0

CHUNKSIZE = 14*1024

def count_file(filename):
    count = defaultdict(int)
    infile = file(filename)

    # For the first pass, including everything which is a reasonable match.
    # It's faster to count everything and filter later than it is to do
    # the filtering now.
    while 1:
        text = infile.read(CHUNKSIZE)
        text += infile.readline()
        if not text:
            break
        i = j = 0
        while 1:
            i = text.find('GET /ongoing/When/', j)
            if i == -1:
                break
            j = text.find(' ', i+19)
            field = text[i:j]
            count[field] += 1

    # The previous code included fields which aren't allowed by the
    # regular expression.
    new_count = {}
    for k, v in count.iteritems():
        # because of the way the key was saved, I didn't keep the
        # trailing space.  Add it back here so the regexp can be used unchanged.
        k = k + " "
        m = pat.search(k)
        if m:
            new_count[m.group(1)] = v
    return new_count

count = count_file(FILE)

for key in sorted(count, key=count.get)[:10]:
    pass # print "%40s = %s" % (key, count[key])

print timer() - t0, time.clock() - t1

# sanity check
for key in sorted(count, key=count.get)[-10:]:
    print "%40s = %s" % (key, count[key])

'''
It's all a bad idea

While it's the fastest of the pure-Python solution, it's not one you should aspire to follow.
It's pretty unusual code, as you can see in part by the extra comments I added to help clarify things.
It's more prone to accidental breakage if one filter changes without updating the other. It's longer, which means it takes longer to write and to understand.
And usually a savings of a second (30%-60%) from the easily understood and maintained version isn't worth the extra problems.

Instead, think of it as a practice piece - a way to hone your skills so that when you do need to get
30% faster code you'll have some ideas of what you can try out and how to measure your results.
'''