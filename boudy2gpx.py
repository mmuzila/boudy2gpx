#!/usr/bin/python3

import re
from urllib.request import urlopen
import urllib
from bs4 import BeautifulSoup as BS
from retryz import retry
import sys
import argparse
import os
import socket
from xml.sax.saxutils import escape

URL = "http://boudy.info"
TIMEOUT = 3
RETRIES = 3

gpxStart = '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns="http://www.topografix.com/GPX/1/0"
xsi:schemaLocation="http://www.topografix.com/GPX/1/0
http://www.topografix.com/GPX/1/0/gpx.xsd" version="1.0"
creator="https://github.com/mmuzila/boudy2gpx">
<metadata>
<name>Boudy (www.boudy.info)</name>
</metadata>
'''

def printErr(s):
    print(s, file=sys.stderr)

def gUrl(s):
    return URL + s



def setupParser(progname):

    parser = argparse.ArgumentParser(prog=progname)
    parser.add_argument("-u", "--url", dest="url", default=URL,
            help="url", required=False)
    parser.add_argument("-o", "--output", dest="outFileName",
            help="Output file. If not specified, then stdout", required=False)
    parser.add_argument("-t", "--timeout", dest="timeout", type=float,
            help="HTTP request timeout", required=False, default=TIMEOUT)
    parser.add_argument("-r", "--retries", dest="retries", type=int,
            help="Number of attempts to get hut", required=False, default=RETRIES)
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
            help="Verbose", required=False)

    return parser

if __name__ == "__main__":
    parser = setupParser(sys.argv[0])
    arg = parser.parse_args(sys.argv[1:])

    URL = arg.url
    TIMEOUT = arg.timeout
    RETRIES = arg.retries

    progress = arg.verbose and (arg.outFileName is not None)

    @retry(on_error=(socket.timeout, urllib.error.URLError), limit=RETRIES)
    def urlopenRetry(url, timeout=None):
        return urlopen(url, timeout=timeout)

    if arg.outFileName is None:
        oF = os.fdopen(sys.stdout.fileno(), 'w')

    else:
        try:
            oF = open(arg.outFileName, "w+")
        except:
            printErr("Not possible to open output file: %s" % arg.outFileName)
            exit(1)

    url = gUrl("/index.php")
    try:
        boudyIndex = urlopenRetry(url, timeout=TIMEOUT)
    except Exception as e:
        printErr("Not possible to get: %s" % url)
        exit(1)

    try:
        soup = BS(boudyIndex, "lxml")
        aTag = soup.find(["a"], {"class":"novinky_obr_link"})
        hrefStr = aTag.attrs["href"]
        mtch = re.search("id=([0-9]+)", hrefStr)
        lastHut = int(mtch.group(1))

    except Exception as e:
        printErr("Not possible to parse: %s" % url)
        exit(1)


    oF.write(gpxStart)

    for h in range(1, lastHut + 1):


        url = gUrl("/bouda.php?id=%s" % h)
        try:
            if progress:
                print("Getting hut: %s/%s:" % (h, lastHut))

            hutHtml = urlopenRetry(url, timeout=TIMEOUT)

        except Exception as e:
            printErr("Not possible to get hut: %s" % url)
            continue

        try:
            soup = BS(hutHtml, "lxml")
            hName = soup.find(["div"], {"class":"nadpis"}).text


            mtch is None
            lat = float(0)
            lon = float(0)
            coordsDef = False
            hDesc = ""

            if soup.find("div", {"class":"chyba_nadpis"}) is not None:
                raise Exception

            for i in soup.find_all(["div","ul","p", "span"], \
                    {"class":["popis_nadpis", "popis_ul", "popis_txt", \
                    "info_gps_2", "info_gps_1"]}):

                txt = i.text
                txt = re.sub("^\s+", "", txt)
                txt = re.sub("\s+$", "", txt)

                if i.name == "div":
                    txt += ":\n"

                    for j in range(1,len(txt)):
                        txt += "="

                elif i.name == "ul":
                    txt = "> " + txt
                    txt = re.sub("\n", "\n> ", txt)
                    txt += "\n"

                elif i.name == "span":
                    mtch = re.match('\n(\d+)° (\d+)’ (\d+)(.(\d+))?” (N|S)\n \n(\d+)°'
                        + ' (\d+)’ (\d+)(.(\d+))?” (E|W)\n', i.text)
                    #print(mtch.groups())

                    if mtch is None:
                        continue

                    lat += int(mtch.group(1))
                    lat += int(mtch.group(2))/60
                    lat += int(mtch.group(3))/3600
                    if mtch.group(4) is not None:
                        lat += float(mtch.group(4)) / 360000

                    lon += int(mtch.group(7))
                    lon += int(mtch.group(8))/60
                    lon += int(mtch.group(9))/3600
                    if mtch.group(10) is not None:
                        lon += float(mtch.group(10)) / 360000

                    if mtch.group(6) == "S":
                        lat *= (-1)

                    if mtch.group(12) == "W":
                        lon *= (-1)

                    coordsDef = True

                else:
                    txt += "\n"

                if i.name != "span":
                    hDesc += txt + "\n"

            if not coordsDef:
                printErr("No coordinates. Skipping.: %s" % url)
                continue

            hName = escape(hName)
            hDesc = escape(hDesc)

            oF.write('<wpt lat="%s" lon="%s">\n' % (lat, lon))
            oF.write('<name>%s</name>\n' % hName)
            oF.write('<desc>%s</desc>\n' % hDesc)
            oF.write('<type>Boudy</type>\n')
            oF.write('<sym>m_2_4_1</sym>\n')
            oF.write('<number>%s</number>\n' % h)
            oF.write('</wpt>\n')

        except KeyboardInterrupt as e:
            exit(0)

        except Exception:
            printErr("Not possible to parse hut: %s" % url)
            continue


    oF.write('</gpx>\n')
    oF.close()
