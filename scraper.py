#!/usr/bin/env python3
"""
Initial idea from:
https://schoolofdata.org/2013/08/16/scraping-pdfs-with-python-and-the-scraperwiki-module/
"""
import scraperwiki
import sys


def read_data(file):
    with open(file, 'rb') as f:
        return f.read()


def main():
    assert len(sys.argv) == 2, "Missing input"
    data = read_data(sys.argv[1])
    xml = scraperwiki.pdftoxml(data)
    print(xml)


if __name__ == "__main__":
    main()
