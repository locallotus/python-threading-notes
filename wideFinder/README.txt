Code for the effbot.org article "Some Notes on Tim Bray's Wide Finder
Benchmark" (http://effbot.org/zone/wide-finder.htm).

file            time[1] 
--------------------------------------------------------------------
getdata.py              downloads and generates sample files (o10k.ap
                        and o1000k.ap).  run this first.
wf-1-gala.py    6.7s    original python implementation by Santiago
                        Gala [2]
wf-2.py         2.9s    optimized version of Santiago's script (pre-compiled regular expressions, fast exclusion of lines that can't match)
wf-3.py         3.6s    chunked serial implementation (processing the input file in chunks)
wf-4.py         1.9s    using threads to process individual chunks
wf-5.py         1.6s    using processes to process individual chunks
wf-6.py         0.8s    same, using memory mapped chunks

# See also http://www.dalkescientific.com/writings/diary/archive/2007/10/07/wide_finder.html
In this essay I'll write a few other variations, all single-threaded. To make it easier to compare, here are their times:
(A:1.3s) dalke-wf-7.py: findall on a mmap'ed file
(A:26s) dalke-wf-8.py: mxTextTools using a slow tag table
(A:0.73s) dalke-wf-9.py: mxTextTools using a fast tag table
(A:1.0s) dalke-wf-10.py: simple filter of mmap'ed file, post-filtering with regex
(A:0.95s) dalke-wf-11.py: simple filter of chunked file, post-filtering with regex
Some interesting observations: I have a faster machine than Fredrik, my wf-5 is a lot slower than his, and there is indeed room for improvement even staying within the standard library.
--------------------------------------------------------------------
1) representative wall-time from multiple runs on the o1000k.ap
   sample, on a lightly loaded Windows XP machine
2) http://memojo.com/~sgala/blog/2007/09/29/Python-Erlang-Map-Reduce

Notes:

Run the getdata.py script to download the o10k.ap sample file, and
generate the o1000k.ap file used by the scripts.

wf-4 and later takes the thread/process count as an argument.  The
count defaults to two; if you have more cores, or just want to
experiment, try passing in a larger number, e.g:

    python wf-6.py 8

The code requires Python 2.5.  To make it run under earlier versions,
you need to replace the defaultdict with a setdefault-based solution.
