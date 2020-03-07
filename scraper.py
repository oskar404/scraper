#!/usr/bin/env python3
"""
Parse invoice data provided as PDF files to row based textual data
"""

# Initial idea to user wscraperwiki from:
# https://schoolofdata.org/2013/08/16/scraping-pdfs-with-python-and-the-scraperwiki-module/

import argparse
import os
import scraperwiki
import sys
import xml.etree.ElementTree


def read_data(file):
    assert os.path.isfile(file), f"Missing file: {file}"
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
    filter_output(rows, args.start, args.end)


if __name__ == "__main__":
    main()
