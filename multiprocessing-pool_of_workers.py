# https://docs.python.org/2/library/multiprocessing.html
from multiprocessing import Pool

def f(x):
    return x*x

if __name__ == '__main__':
    pool = Pool(processes=4)  # start 4 worker processes
    result = pool.apply_async(f, [10])  # evaluate "f(10)" asynchronously
    print result.get(timeout=1)           # prints "100" unless your computer is *very* slow
    print pool.map(f, range(10))          # prints "[0, 1, 4,..., 81]"

# Note that the methods of a pool should only ever be used by the process which created it.