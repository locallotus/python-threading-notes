# Used for >python benchmarking_GIL_effects.py funcToBench4.py
def function_to_run():
    import urllib
    for i in range(10):
        f = urllib.urlopen("http://localhost:8005")
        f.read()