# About

## SK
Jednoduchý program na stiahnutie búd zo stránky http://boudy.info a ich uloženie
vo formáte GPX.

## EN
Simple program to get huts from http://boudy.info and save them in GPX format.

# Dependencies
```
bs4
retryz
argparse
```

# Usage
```
usage: ./boudy2gpx.py [-h] [-u URL] [-o OUTFILENAME] [-t TIMEOUT] [-r RETRIES]
                      [-v]

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     url
  -o OUTFILENAME, --output OUTFILENAME
                        Output file. If not specified, then stdout
  -t TIMEOUT, --timeout TIMEOUT
                        HTTP request timeout
  -r RETRIES, --retries RETRIES
                        Number of attempts to get hut
  -v, --verbose         Verbose
```
