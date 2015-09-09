# Used for >python benchmarking_GIL_effects.py funcToBench2.py
'''
One common application of threaded (and non-threaded) programming is to do number crunching.
Let's take a simple, brute force approach to doing Fibonacci number crunching, noting of course that we're not sharing state here.
We are just trying to have two tasks generate a set number of Fibonacci numbers.
'''
def function_to_run():
  a, b = 0, 1
  for i in range(100000):
    a, b = b, a + b