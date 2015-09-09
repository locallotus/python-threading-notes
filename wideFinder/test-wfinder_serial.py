# http://www.dehora.net/journal/2007/10/wfinder_serialpy.html
# also http://www.serpentine.com/blog/2007/09/25/what-the-heck-is-a-wide-finder-anyway/

'''
So, here's a serial version in Python, for compare/contrast with the original Ruby one Tim wrote for Beautiful Code.
The core code:

    r=re.compile(r".*GET /ongoing/When/200x/\d{4}/\d{2}/\d{2}/([^ ]+) ")
    matches  = filter(lambda x:x != None, [r.match(line) for line in file(filename)])
    pages={}
    for m in matches:
	    pages[m.group(1)]=pages.setdefault(m.group(1),0)+1
    for item in sorted(pages.items(), key=operator.itemgetter(1), reverse=True)[:10]:
        print item

This will eat a 250mb logfile in about 5s. Over 750Mb it takes ~15s. Over 1.5Gb it takes ~55s.

It seeks over the file creating pairs of (start,offset) that let multiple threads read chunks of a file (seek/chunk is Bryan O'Sullivan's idea, check out his Haskell version).
It seems to better for larger files than the serial version. But ultimately you have to go to multiple processes and then to multiple disks (and not just because of the GIL).
'''

import sys
import re
import operator
import os
import datetime, time

class TimeProfiler:
    """ A utility class for profiling execution time for code """
    def __init__(self):
        # Dictionary with times in seconds
        self.timedict = {}

    def mark(self, slot=''):
        """ Mark the current time into the slot 'slot' """
        # Note: 'slot' has to be string type
        # we are not checking it here.
        self.timedict[slot] = time.time()

    def unmark(self, slot=''):
        """ Unmark the slot 'slot' """
        # Note: 'slot' has to be string type
        # we are not checking it here.
        if self.timedict.has_key(slot):
            del self.timedict[slot]

    def lastdiff(self):
        """ Get time difference between now and the latest marked slot """
        # To get the latest slot, just get the max of values
        return time.time() - max(self.timedict.values())

    def elapsed(self, slot=''):
        """ Get the time difference between now and a previous
        time slot named 'slot' """
        # Note: 'slot' has to be marked previously
        return time.time() - self.timedict.get(slot)

    def diff(self, slot1, slot2):
        """ Get the time difference between two marked time
        slots 'slot1' and 'slot2' """
        return self.timedict.get(slot2) - self.timedict.get(slot1)

    def maxdiff(self):
        """ Return maximum time difference marked """
        # Difference of max time with min time
        times = self.timedict.values()
        return max(times) - min(times)

    def timegap(self):
        """ Return the full time-gap since we started marking """
        # Return now minus min
        times = self.timedict.values()
        return time.time() - min(times)

    def cleanup(self):
        """ Cleanup the dictionary of all marks """
        self.timedict.clear


if __name__ == "__main__":
    from timeit import Timer
    filename=sys.argv[1]
    profiler = TimeProfiler()
    profiler.mark()

    r=re.compile(r".*GET /ongoing/When/200x/\d{4}/\d{2}/\d{2}/([^ ]+) ")
    matches  = filter(lambda x:x != None, [r.match(line) for line in file(filename)])
    pages={}

    for m in matches:
	    pages[m.group(1)]=pages.setdefault(m.group(1),0)+1

    for item in sorted(pages.items(), key=operator.itemgetter(1), reverse=True)[:10]:
        print item

    print "serial", str(profiler.timegap())
