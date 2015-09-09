#!/usr/bin/python

# Sourced from http://jessenoller.com/blog/2009/02/01/python-threads-and-the-global-interpreter-lock

# See NOTE on the GIL.txt
# Also see http://effbot.org/zone/wide-finder.htm

# Execute with eg: $python benchmarking_GIL_effects.py funcToBench.py

'''
Python uses a global interpreter lock to protect the interpreter internals from simultaneous access

The following tests will call a given function one time, in one hundred loops.
Iy then displays the best of 100 calls.
It cycles between a non-threaded iteration based call, a threaded call, and finally a processing module (fork and exec) call.
It iterates each test for an increasing number of calls/threads. It will go through 1, 2, 4 and finally 8 calls/threads/processes.

Why are we adding process results into this?
The answer is simple: we know in advance the GIL is going to penalize our execution, and using it sidesteps the GIL entirely, allowing us to see how fast execution could be.

For non-threaded execution, to keep things fair, we simply call the defined function sequentially the same number of times as threads/processes we would otherwise use.
All examples use new-style classes to further even the playing field, although we skip explicit ''__init__()'' setup as it's not needed.

To keep things simple, all of the timings in this are delegated to Python's timeit module.
The timeit module is designed to benchmark pieces of Python code -- generally single statements.
In our case however, it provides some nice facilities for looping over a given function a set number of times and returning to us the fastest run time.

NOTE:
>Thread and process setup add linear overhead time as shown with funcToBench.py which establishes some baseline numbers so we see the overheads
>funcToBench2.py is more processor intensive but can never benefit from multithreading, due to the GIL only allowing one thread to execute code at a time.
Multiprocessing shows a more constant time (benefit), especially with more processes vs processors, compared to the iterated and threaded tests which end up taking longer
>funcToBench3.py shows an IO bound operation/task, reading 1000 1-kilobyte chunks off of /dev/urandom, threaded and multiprocess take up almost the same time here on each test, linear benefit with scale
>funcToBench4.py performs IO using the socket module, threaded and multiprocess take up almost the same time here on each test, linear benefit with scale

Keep in mind that you would not really use threads like the benchmark script we've put together does.
Generally speaking, you'd be appending things to a queue (producer/consumer thread/worker model), taking them off, and doing other shared-state tasks.
Having a bunch of threads off running the same function, while useful, is not a common use-case for a concurrent program, unless you're splitting up and processing large data sets.

For a final example look at the results when running funcToBench4.py, using the socket module (actually urllib2 which also uses socket module).
This is the module that all network I/O goes through, it's in C, and it's thread safe.
To exclude network latency issues, connect to another computer's Apache/Nginx/NodeJS web server on the LAN (probs not optimized for load)
and we'll use urllib2 instead of the raw socket library -- urllib2 uses the socket library under the covers.
Grabbing URLs is a common enough use case, rather than just connecting to a socket over and over.
I will also lower the count of the requests since, generally speaking, jackhammering your web server makes your web server the bottleneck.
Given that this one is not tuned, we will keep it simple.

As you should see, doing I/O does, in fact, release the GIL.
The threaded examples are obviously getting faster than the single-threaded execution.
Given that most applications do perform a certain amount of I/O (most applications spend a large amount of their time in I/O)
the GIL does not prevent users from creating multi-threaded applications that can act in a concurrent manner and add speed to their applications.

Does the GIL block those people who are working in pure Python from truly taking advantage of multiple cores?
Simply put: Yes, it does.
While threads themselves are a language construct, the interpreter is the gatekeeper to the mapping between threads and the OS.
This is why Jython and IronPython have no GIL. It was simply not needed and left out of the implementation of the interpreter.

Based on the numbers, switching to processes side-steps the entire GIL issue, allowing all of the children to run concurrently.
'''

from threading import Thread
from processing import Process

class threads_object(Thread):
    def run(self):
        function_to_run()

class nothreads_object(object):
    def run(self):
        function_to_run()

class process_object(Process):
    def run(self):
        function_to_run()

def non_threaded(num_iter):
    funcs = []
    for i in range(int(num_iter)):
        funcs.append(nothreads_object())
    for i in funcs:
        i.run()

def threaded(num_threads):
    funcs = []
    for i in range(int(num_threads)):
        funcs.append(threads_object())
    for i in funcs:
        i.start()
    for i in funcs:
        i.join()

def processed(num_processes):
    funcs = []
    for i in range(int(num_processes)):
        funcs.append(process_object())
    for i in funcs:
        i.start()
    for i in funcs:
        i.join()

def show_results(func_name, results):
    print "%-23s %4.6f seconds" % (func_name, results)

if __name__ == "__main__":
    import sys
    from timeit import Timer

    repeat = 100
    number = 1

    num_threads = [ 1, 2, 4, 8 ]

    if len(sys.argv) < 2:
        print 'Usage: %s module_name' % sys.argv[0]
        print '  where module_name contains a function_to_run function'
        sys.exit(1)
    module_name = sys.argv[1]
    if module_name.endswith('.py'):
        module_name = module_name[:-3]
    print 'Importing %s' % module_name
    m = __import__(module_name)
    function_to_run = m.function_to_run

    print 'Starting tests'
    for i in num_threads:
        t = Timer("non_threaded(%s)" % i, "from __main__ import non_threaded")
        best_result = min(t.repeat(repeat=repeat, number=number))
        show_results("non_threaded (%s iters)" % i, best_result)

        t = Timer("threaded(%s)" % i, "from __main__ import threaded")
        best_result = min(t.repeat(repeat=repeat, number=number))
        show_results("threaded (%s threads)" % i, best_result)

        t = Timer("processed(%s)" % i, "from __main__ import processed")
        best_result = min(t.repeat(repeat=repeat, number=number))
        show_results("processes (%s procs)" % i, best_result)
        print "\n",

    print 'Iterations complete'
