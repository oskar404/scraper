#!/usr/bin/env python3
"""
Parse invoice data provided as PDF files to row based textual data
"""

# Initial idea to user wscraperwiki from:
# https://schoolofdata.org/2013/08/16/scraping-pdfs-with-python-and-the-scraperwiki-module/

import argparse
import json
import scraperwiki
import sys
import xml.etree.ElementTree
from os.path import basename, isfile, splitext


def _default_cfgfile():
    filebase, _ = splitext(basename(__file__))
    return filebase + '.json'


CFGFILE = _default_cfgfile()


def read_data(file):
    assert isfile(file), f"Missing file: {file}"
    with open(file, 'rb') as f:
        return f.read()


def scrape(data):
    """Scrape PDF via XML to rows

    The XML produced is expected to have structure:

    <root>
        <page>
            <text top="" font="3"></text>
        </page>
    </root>

    Only <text> element names are searched and processed
    """
    result = {}
    xml_str = scraperwiki.pdftoxml(data)
    root = xml.etree.ElementTree.fromstring(xml_str)
    page_id = 0
    for page in root:
        page_id += 1
        for text in page.iter(tag='text'):
            if text.get('font') == '3':
                text_id = (page_id, text.get('top'))
                row = result.get(text_id, '')
                if row and len(row) < 60:
                    row = row + ' ' * (60-len(row))
                result[text_id] = row + text.text
    return result


def read_cfg(file):
    """Read configuration file and return list of (start,end) tuples """
    result = []
    if isfile(file):
        with open(file) as f:
            cfg = json.load(f)
        for entry in cfg:
            if 'start' in entry:
                filter = (entry['start'], entry.get('end', None))
                result.append(filter)
    return result


def create_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'path',
        help='Path to PDF invoice file')
    parser.add_argument(
        '-s', '--start', '-f', '--from',
        help='Print data starting from row containing the text',
        default='')
    parser.add_argument(
        '-e', '--end', '-t', '--to',
        help='Print data ending to row containing the text',
        default='')
    parser.add_argument(
        '-c', '--config',
        help='If --start not defined use configuration',
        default=CFGFILE)
    return parser


def filter_output(rows, start, end):
    start_found = False if start else True
    end_found = False
    for row in rows.values():
        if not start_found:
            start_found = True if start in row else False
        # Include start and end rows into output
        if start_found and not end_found:
            print(row)
        if end and not end_found and start_found:
            end_found = True if end in row else False


def main():
    parser = create_parser()
    args = parser.parse_args()
    rows = scrape(read_data(args.path))
    if args.start:
        filter_output(rows, args.start, args.end)
    else:
        configs = read_cfg(args.config)
        for cfg in configs:
            filter_output(rows, cfg[0], cfg[1])


if __name__ == "__main__":
    main()
