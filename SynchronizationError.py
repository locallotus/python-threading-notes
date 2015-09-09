# http://jessenoller.com/blog/2009/02/01/python-threads-and-the-global-interpreter-lock

'''
Shared Memory. Take, for instance, the synchronization error.
Synchronization errors occur when you have two threads accessing a common mutable chunk of data,
whether it's a function that in turn modifies or calls something else,
or something like a shared dictionary where the two attempt to alter the same key at once (more on this later).
Synchronization errors are generally hanging out behind the school smoking with... Race conditions!
'''
from threading import Thread

class myObject(object):
    def __init__(self):
        self._val = 1
    def get(self):
        return self._val
    def increment(self):
        self._val += 1

def t1(ob):
    ob.increment()
    print 't1:', ob.get() == 2

def t2(ob):
    ob.increment()
    print 't2:', ob.get() == 2

ob = myObject()

# Create two threads modifying the same ob instance
thread1 = Thread(target=t1, args=(ob,))
thread2 = Thread(target=t2, args=(ob,))

# Run the threads
thread1.start()
thread2.start()
thread1.join()
thread2.join()

'''
The banality of the code notwithstanding, one of the two tests will always fail.
This is because both threads are incrementing an unlocked, global value. This is a simple example of a synchronization error,
one of the threads beats the other to access a shared resource, and the assertion fails.
Errors such as this are common. Alarmingly so, given that when people begin exploring threaded programming,
their first instinct is to share everything (whereas many concurrency solutions are referred to as "shared-nothing").

Deadlocks occur when your application seizes up while any number of threads lock-up waiting for the other threads to free required resources, never to return.
'''