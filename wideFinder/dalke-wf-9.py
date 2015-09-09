# dalke-wf-9.py
#  A version using mxTextTools 3.0 and hand-written tag table
# http://www.dalkescientific.com/writings/diary/archive/2007/10/07/wide_finder.html
'''
mxTextTools is zippy fast!

mxTextTools also implements a fast substring search algorithm.
Rather than using Martel to generate the tag table, I wrote one by hand which takes advantage of this feature:
'''
from collections import defaultdict
from mx.TextTools import *

FILE = "o1000k.ap"

import time, sys
if sys.platform == "win32":
    timer = time.clock
else:
    timer = time.time

t0, t1 = timer(), time.clock()

DIGITS = "0123456789"

count = defaultdict(int)

# using the "add_count" CallTag yields about 5% speedup vs. appending
# the result to the tag list and processing after the parsing.
def add_count(taglist, text, l, r, subtags, count=count):
    count[text[l:r]] += 1

tag_table = TagTable( (
    "start",
    # Use mxTextTool's fast "Boyer-Moore-Horspool style algorithm"
    # Failure to find the text means it's the end of the string
    (None, sWordEnd, TextSearch("GET /ongoing/When/"), MatchOk),
    # Match r"\d\d\dx/"
    (None, IsIn, DIGITS, "start"),
    (None, IsIn, DIGITS, "start"),
    (None, IsIn, DIGITS, "start"),
    (None, Word, "x/", "start"),
    # If this part matches, call 'add_count', then go to "start"
    # If the subtable does not match, then go to "start"
    (add_count, SubTable+CallTag, (
                # Match r"\d\d\d\d/\d\d/\d\d/[^ ] "
                (None, IsIn, DIGITS),
                (None, IsIn, DIGITS),
                (None, IsIn, DIGITS),
                (None, IsIn, DIGITS),
                (None, Is, "/"),
                (None, IsIn, DIGITS),
                (None, IsIn, DIGITS),
                (None, Is, "/"),
                (None, IsIn, DIGITS),
                (None, IsIn, DIGITS),
                (None, Is, "/"),
                (None, AllNotIn, " ."),
                (None, Is, " ")), "start", "start")
    ) )

# mxTextTools does not support memory mapped files, so process a
# chunk of text at a time.

# Timings for different sized chunks.  There is little variation in these numbers
# 10240K 0.964
#  1024K 0.933
#   128K 0.882
#    16K 1.17     # strange
#    12K 0.728
#    10K 0.745
#     8K 0.777
#     4K 0.962
#     1K 1.455
CHUNK = 12*1024  # best numbers on my machine

infile = open(FILE)

while 1:
    text = infile.read(CHUNK)
    # Guarantee the complete line is read
    text += infile.readline()
    if not text:
        break

    # no need to look at the return type; processing occurs by side effect
    tag(text, tag_table)

for key in sorted(count, key=count.get)[:10]:
    pass # print "%40s = %s" % (key, count[key])

print timer() - t0, time.clock() - t1

# sanity check
for key in sorted(count, key=count.get)[-10:]:
    print "%40s = %s" % (key, count[key])

'''
As you can read from the comments, mxTextTools does not use the buffer interface.
It only support strings, which can be either 8-bit or unicode. I had to use a chunking method instead.
I read CHUNK bytes followed by a readline to ensure that the resulting text only contains complete lines.

This is a very common technique and it works when there are many "records" in a large file. In this case each record is one line long.

A disadvantage of this approach is that the chunk size is tunable. You can either guess a reasonable chunk size, or run tests to find out the best value.
I started with a 1MB chunk size and worked my way down to find that 12KB gave me the fastest results.
Much to my surpise, 16K is slower than any other value I picked in the entire range, other than 1K.
(Memory and disk block sizes are usually 4K so 1K is not a reasonable chunk size.)

The best case took 0.7s and even the worst sane case at 1.2s shows that using mxTextTools is faster than dalke-wf-7,
which was my best single-threaded code at 1.3s.
But to get that speed requires using a third-party tool and learning how to use it effectively.

I commented out the tagging code, so it does everything except parsing.
The code to do the chunking and setup for mxTextTools takes about 0.36s, or about 1/2 of the time.
'''