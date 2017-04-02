import urllib
import re


base_url = "https://finance.yahoo.com/q?s="

list = ["aapl","amd","goog","nflx"]
realNameList = ["Apple","Amd","Google","Netflix"]

i = 0

while i < len(list):
    url = base_url +list[i] +"&ql=1"
    htmlfile = urllib.urlopen(url)
    htmltext = htmlfile.read()
    regex = '<span id="yfs_184_'+list[i] +'">(.+?)</span>'
    pattern = re.compile(regex)
    price = re.findall(pattern, htmltext)
    print "The price of ", realNameList[i], " is: ", price
    i += 1

