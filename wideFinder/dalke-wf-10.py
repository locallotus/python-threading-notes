# http://www.dalkescientific.com/writings/diary/archive/2007/10/07/wide_finder.html
'''
Making a faster standard library approach

As I was writing an email to Fredrik describing these results,
I came up with another approach to speeding up the performance, using only the standard library.

Fredrik showed that using a two-level filter, with a quick exclusion test using string operations followed by the regular expression test,
was faster than doing only the regular expression test. Quoting him:

The RE engine does indeed use special code for literal prefixes,
but the superlinear substring search algorithm that was introduced in 2.5 is a lot faster in cases like this, so this simple change gives a noticable speedup.
This works because the only about 20% of the lines in the input file matches the quick test and the simple string test is

% python -m timeit -s 's="This is a test.  I was here."*4; t="testXYZ"' 't in s'
10000000 loops, best of 3: 0.194 usec per loop
% python -m timeit -s 'import re;s="This is a test.  I was here."*4; t=re.compile("testXYZ")' 't.search(s)'
1000000 loops, best of 3: 0.98 usec per loop
% python -c 'print 0.98/0.194'
5.05154639175
%

roughly 5 times faster than the regular expression test.
My observation was that I can defer the regular expression test until later.
Use the quick string test to find all substrings starting with "GET /ongoing/When/" and ending with the " ".
This will include some extra substrings. Tally all of the substrings, including the false positives.
This will do extra work but the tallying code is very fast.
Once the file has been parsed, post-process the counts dictionary and remove those keys which are not allowed by the regular expression.

This works because there are many duplicate keys. Nearly 50% of the entries which pass the quick string test are duplicates.
The keys in the counts dictionary are unique, which mean only one regular expression test needs to be done, instead of one for each match.

If most of the entries were under /ongoing/When/ and most were unique then these optimizations would be a net slowdown.
You have to understand your data as well as the software in order to figure out how to improve things, and there will be tradeoffs.

Remember also I mentioned that string operations are available for buffer objects?
This means I can do the fast find directly on the memory-mapped file, rather than using a chunk reader.
I'll do the quick search for the leading part of the pattern to search for, then another search for the trailing " " (space) character.
'''

# dalke-wf-10.py  fast string ops, mmap, post-process filter
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
search = pat.search


def count_file(filename):
    count = defaultdict(int)
    fileobj = open(FILE)
    filemap = mmap.mmap(fileobj.fileno(), os.path.getsize(FILE), access=mmap.ACCESS_READ)
    i = j = 0
    # For the first pass, including everything which is a reasonable match.
    # It's faster to count everything and filter later than it is to do
    # the filtering now.
    while 1:
        i = filemap.find("GET /ongoing/When/", j)
        if i == -1:
            break
        j = filemap.find(' ', i+19)
        field = filemap[i:j]
        count[field] += 1

    # The previous code included fields which aren't allowed by the
    # regular expression.  Filter those which don't match the regexp.
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
Variable lookups in module scope are slower than lookups in local scope so I introduced the count_file function to get a bit more speed.
I didn't generate numbers for this one but experience says it's nearly always a performance advantage.

The resulting dalke-wf-10 code finishes in 1.0s. Yes, you read that right. It's faster than the mmap/findall solution of dalke-wf-7.py, which took 1.3s.
Still not as fast as mxTextTools at 0.7s, but this solution uses only the standard library.
'''