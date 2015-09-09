# sourced from http://effbot.org/zone/wide-finder.htm
# also see http://www.dalkescientific.com/writings/diary/archive/2007/10/07/wide_finder.html
# and http://www.dehora.net/journal/2007/10/wfinder_serialpy.html
# and http://www.serpentine.com/blog/2007/09/25/what-the-heck-is-a-wide-finder-anyway/
# and http://www.tbray.org/ongoing/When/200x/2007/11/16/WF-Parallel-IO
# and http://www.tbray.org/ongoing/When/200x/2007/10/07/WF-Roundup

'''
Summary #

In this article, we took a relatively fast Python implementation and optimized it, using a number of tricks:

Pre-compiled RE patterns
Fast filtering of candidate lines
Chunked reading
Multiple processes
Memory mapping, combined with support for RE operations on mapped buffers

This reduced the time needed to parse 200 megabytes of log data from 6.7 seconds to 0.8 seconds on the test machine.
Or in other words, the final version is over 8 times faster than the original Python version,
and (potentially) 600 times faster than Tim’s original Erlang version.

However, it should be noticed that the benchmark I’ve been using focuses on processing speed, not disk speed.
The code will most likely behave differently on cold caches (and will definitely take longer to run),
on machines with different disk systems, and of course also on machines with additional cores.
'''

'''
Reading a large file for parsing
First A Multi-Threaded Python Solution
Followed by A Multi-Processor Python Solution

To run multiple subtasks in parallel, we need to split the task up in some way.
Since the program reads a single text file, the easiest way to do that is to split the file into multiple pieces on the way in.
Here’s a simple function that rushes through the file, splitting it up in 1 megabyte chunks, and returns chunk offsets and sizes:
'''

def getchunks(file, size=1024*1024):  # default param: 1 MB (1024*1024 bytes)
    f = open(file)
    while 1:
        start = f.tell()
        f.seek(size, 1)
        s = f.readline()
        yield start, f.tell() - start
        if not s:
            break

for chunk in getchunks('o1000k.ap'):
    print chunk

'''
Note the use of readline to make sure that each chunk ends at a newline character.
(Without this, there’s a small chance that we’ll miss some entries here and there.
This is probably not much of a problem in practice, but let’s stick to the exact solution for now.)

So, given a list of chunks, we need something that takes a chunk, and produces a partial result.
Here’s a first attempt, where the map and reduce steps are combined into a single loop:
'''

from collections import defaultdict

import re
pat = re.compile(r"GET /ongoing/When/\d\d\dx/(\d\d\d\d/\d\d/\d\d/[^ .]+) ")

def process(file, chunk):
    f = open(file)
    f.seek(chunk[0])
    d = defaultdict(int)
    search = pat.search
    for line in f.read(chunk[1].splitlines()):
        if "GET /ongoing/When" in line:
            m = search(line)
            if m:
                d[m.group(1)] += 1
    return d

'''
Note that we cannot loop over the file itself, since we need to stop when we reach the end of it.
The above version solves this by reading the entire chunk, and then splitting it into lines.

To test this code, we can loop over the chunks and feed them to the process function, one by one, and combine the result:
'''
count = defaultdict(int)
for chunk in getchunks(file):
    for key, value in process(file, chunk).items():
        count[key] += value

'''
This version is a bit slower than the non-chunked version on my machine; one pass over the 200 megabyte file takes about 2.6 seconds.

However, since a chunk is guaranteed to contain a full set of lines, we can speed things up a bit more by looking for matches in the chunk itself instead of splitting it into lines:
'''

def process(file, chunk):
    f = open(file)
    f.seek(chunk[0])
    d = defaultdict(int)
    for page in pat.findall(f.read(chunk[1])):
        d[page] += 1
    return d

'''
With this change, the time drops to 1.8 seconds (3.7x faster than the original version).

The next step is to set things up so we can do the processing in parallel.
First, we’ll call the process function from a standard “worker thread” wrapper:
'''

import threading, Queue

# job queue
queue = Queue.Queue()  # thread-safe Queue

# result queue (list object)
result = []

class Worker(threading.Thread):
    def run(self):
        while 1:
            args = queue.get()
            if args is None:
                break
            result.append(process(*args))  # list.append is atomic in CPython
            queue.task_done()

'''
This uses the standard “worker thread” pattern, with a thread-safe Queue for pending jobs,
and a plain list object to collect the results (list.append is an atomic operation in CPython).

To finish the script, just create a bunch of workers, give them something to do (via the queue),
and collect the results into a single dictionary:
'''

for i in range(4):
    w = Worker()
    w.setDaemon(1)
    w.start()

for chunk in getchunks(file):
    queue.put((file, chunk))

queue.join()

count = defaultdict(int)
for item in result:
    for key, value in item.items():
        count[key] += value

'''
With a single thread, this runs in about 1.8 seconds (same as the non-threaded version).
When we increase the number of threads, things are improved:

Two threads: 1.9 seconds
Three: 1.7 seconds
Four to eight: 1.6 seconds

For this specific test, the ideal number appears to be three threads per CPU.
With fewer threads, the CPUs will occasionally get stuck waiting for I/O.

Or perhaps they’re waiting for the interpreter itself;
Python uses a global interpreter lock to protect the interpreter internals from simultaneous access,
so there’s probably some fighting over the interpreter going on as well.
To get even more performance out of this, we need to get around the lock in some way.

Luckily, for this kind of problem, the solution is straightforward.

A Multi-Processor Python Solution

To fully get around the interpreter lock, we need to run each subtask in a separate process.
An easy way to do that is to let each worker thread start an associated process, send it a chunk, and read back the result.
To make things really simple, and also portable, we’ll use the script itself as the subprocess, and use a special option to enter “subprocess” mode.

Here’s the updated worker thread:
'''

import subprocess, sys

executable = [sys.executable]
if sys.platform == "win32":
    executable.append("-u")  # use raw mode on windows

class Worker(threading.Thread):
    def run(self):
        process = subprocess.Popen(
            executable + [sys.argv[0], "--process"],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE
        )
        stdin = process.stdin
        stdout = process.stdout
        while 1:
            cmd = queue.get()
            if cmd is None:
                putobject(stdin, None)
                break
            putobject(stdin, cmd)
            result.append(getobject(stdout))
            queue.task_done()

'''
where the getobject and putobject helpers are defined as:
'''

import marshal, struct

def putobject(file, object):
    data = marshal.dumps(object)
    file.write(struct.pack("I", len(data)))
    file.write(data)
    file.flush()

def getobject(file):
    try:
        n = struct.unpack("I", file.read(4))[0]
    except struct.error:
        return None
    return marshal.loads(file.read(n))

'''
The worker thread runs a copy of the script itself, and passes in the “—process” option.
To enter subprocess mode, we need to look for that before we do anything else:
'''

if "--process" in sys.argv:
    stdin = sys.stdin
    stdout = sys.stdout
    while 1:
        args = getobject(stdin)
        if args is None:
            sys.exit(0) # done
            result = process(*args)
            putobject(stdout, result)
        else:
            # ... create worker threads ...
            pass

'''
With this approach, the processing time drops to 1.2 seconds, when using two threads/processes (one per CPU).
But that’s about as good as it gets; adding more processes doesn’t really improve things on this machine.

Memory Mapping

So, is this the best we can get? Not quite. We can speed up the file access as well, by switching to memory mapping:
'''

import mmap
import os

filemap = None

def process(file, chunk):
    global filemap, fileobj
    if filemap is None or fileobj.name != file:
        fileobj = open(file)
        filemap = mmap.mmap(
            fileobj.fileno(),
            os.path.getsize(file),
            access=mmap.ACCESS_READ
        )
    d = defaultdict(int)
    for file in pat.findall(filemap, chunk[0], chunk[0]+chunk[1]):
        d[file] += 1
    return d

'''
Note that findall can be applied directly to the mapped region, thanks to Python’s internal memory buffer interface.
Also note that the mmap module doesn’t support windowing, so the code needs to map the entire file in each subprocess.
This can result in overly excessive use of virtual memory on some platforms
(running this on your own log files if you’re on a shared web server is not necessarily a good idea. Yes, I’ve tried ;-).

Anyway, this gets the job done in 0.9 seconds, with the original chunk size.
But since we’re mapping the entire file anyway in each subprocess, we can increase the chunk size to reduce the process communication overhead.
With 50 megabyte chunks, the script runs in just under 0.8 seconds.
'''