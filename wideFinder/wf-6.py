# a multi-process, memory-mapped implementation.  lots of code here;
# this one could definitely benefit from a support library...

import re, sys, os
from collections import defaultdict

import threading, Queue, subprocess
import marshal, struct

# configuration

try:
    CPUS = int(sys.argv[1])
except:
    CPUS = 2

executable = [sys.executable]
if sys.platform == "win32":
    executable.append("-u") # use raw mode on windows

import mmap
filemap = None

def process(file, chunk):
    global filemap, fileobj
    if filemap is None or fileobj.name != file:
        fileobj = open(file, "rb")
        filemap = mmap.mmap(
            fileobj.fileno(), os.path.getsize(file), access=mmap.ACCESS_READ
            )
    d = defaultdict(int)
    for file in pat.findall(filemap, chunk[0], chunk[0]+chunk[1]):
        d[file] += 1
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

class Worker(threading.Thread):
    def run(self):
        process = subprocess.Popen(
            executable + [sys.argv[0], "--process"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
            )
        stdin = process.stdin
        stdout = process.stdout
        while 1:
            cmd = queue.get()
            if cmd is None:
                stdin.write("0\n")
                break
            putobject(stdin, cmd)
            result.append(getobject(stdout))
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

if "--process" in sys.argv:

    stdin = sys.stdin
    stdout = sys.stdout
    while 1:
        args = getobject(stdin)
        if args is None:
            sys.exit(0) # terminate
        result = process(*args)
        putobject(stdout, result)

else:

    queue = Queue.Queue()
    result = []

    # fire up a bunch of workers (typically one per core)
    for i in range(CPUS):
        w = Worker()
        w.setDaemon(1)
        w.start()

    chunksize = max(1, os.path.getsize(FILE) / CPUS / (1024*1024))

    # distribute the chunks
    for chunk in getchunks(FILE, chunksize*1024*1024):
        queue.put((FILE, chunk))

    # wait for the tasks to finish
    queue.join()

    # merge the incoming data
    count = defaultdict(int)
    for item in result:
        for key, value in item.items():
            count[key] += value

    # process result
    for key in sorted(count, key=count.get)[:10]:
        pass # print "%40s = %s" % (key, count[key])

    print timer() - t0, time.clock() - t1

# --------------------------------------------------------------------

    for key in sorted(count, key=count.get)[-10:]:
        print "%40s = %s" % (key, count[key])
