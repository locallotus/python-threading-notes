http://jessenoller.com/blog/2009/02/01/python-threads-and-the-global-interpreter-lock
http://effbot.org/zone/wide-finder.htm

Also see: https://pypi.python.org/pypi/processing/ (multi-processing instead of threading, bypassing the GIL, albeit losing shared resources and forcing IPC mechanisms)

A Thread is simply an agent spawned by the application to perform work independent of the parent process.
While the term Thread and threading have referred to the concept of spawning (forking) multiple processes,
more frequently they refer specifically to a pthread, or a worker which is spawned by the parent process,
and which shares that parent's resources.

Both processes and threads are created within a given programming language and then scheduled to run,
either by the interpreter itself (commonly known as "green threads"), or by the operating system ("native threads").
Threads which are scheduled by the operating system are governed by the operating system's scheduler, which dictates many things.
Among them is the usage and allocation of multiple processor resources for the execution of the child threads.

Now, what's the difference between a thread and a process which you can create if both are simply workers spawned by the parent
and scheduled by the operating system or interpreter? Threads fundamentally differ from processes in that they are light weight and share memory.
The term "light weight" refers to the up-front cost of performing the operating system level process creation
(and the requirement of passing a large amount of information and state to the spawned process).
Sharing memory speaks to one of the benefits of using threads over processes.
Namely, threads can share state, objects, and other information with each other and the main thread of execution (this is normally called shared context).
Threads, as they live within the space of a single process, share all of the parent's address space.

==========================================================

Python Thread Support

To quote the Python thread module documentation:
"The design of this module is loosely based on Java's threading model.
However, where Java makes locks and condition variables basic behavior of every object, they are separate objects in Python.
Python's Thread class supports a subset of the behavior of Java's Thread class. Currently, there are no priorities,
no thread groups, and threads cannot be destroyed, stopped, suspended, resumed, or interrupted.
The static methods of Java's Thread, when implemented, are mapped to module-level functions."

Python's thread support, obviously, is loosely based off of Java's (something many a Java-to-Python convert has been happy for, and stymied by).
Python's thread implementation is very simple at it's core, and builds easily on the concept of individualized workers and shared state.
It provides all of the threaded programming primitives: locks, semaphores, and all the normal goodies that come with a good threaded implementation.

Let's look at the simplest thread example:

from threading import Thread

def myfunc():
    print "hello, world!"

thread1 = Thread(target=myfunc)
thread1.start()
thread1.join()

There, you've got a multi-threaded application in seven lines of code.
This little script has two threads: the main thread, and the ''thread1'' object we created. Obviously, here, I'm not sharing anything.
What we are doing is simple: I am creating a new Thread object and passing it a function to run.
We are then calling ''start()'', which sends the thread off to be executed.
The ''join()'' method blocks the main application execution until the thread that we've called ''join()'' on exits,
this prevents a generic "poll the thread until it is done" loop one might otherwise construct.

Python's library has "two" threading-related modules: thread and threading.
Two is in quotation marks because really it's only got one that most people would care about, and that's threading.
The threading module builds on the primitives from the thread module that we mentioned earlier.
Threading is built using thread, and there are few, if any, reasons for most developers to use the thread module directly.

Let's take a moment to revisit the statement that Python's thread support is a Java-Like implementation.
Let's set a basic Python example next to a simple Java example. First Java,

MyThreadDemo.java:

package com.demo.threads;
public class MyThreadDemo {
    public static void main( String[] args ) {
        MyThread foobar = new MyThread();
        Thread1 = new Thread(foobar);
        Thread1.start();
    }
}

Now, let's do the same thing, with Python:

from threading import Thread

class MyThread(Thread):
    def run(self):
        print "I am a thread!"

foobar = MyThread()
foobar.start()
foobar.join()

