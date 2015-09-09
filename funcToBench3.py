# Used for >python benchmarking_GIL_effects.py funcToBench3.py
# IO bound operation/task, reading 1000 1-kilobyte chunks off of /dev/urandom
def function_to_run():
    fh = open("/dev/urandom", "rb")
    for i in range(1000):
        fh.read(1024)