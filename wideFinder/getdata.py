import urllib, os

if not os.path.isfile("o10k.ap"):
    urllib.urlretrieve("http://www.tbray.org/tmp/o10k.ap", "o10k.ap")

if not os.path.isfile("o1000k.ap"):
    data = open("o10k.ap").read()
    file = open("o1000k.ap", "w")
    file.writelines(data for i in range(100))
    file.close()
