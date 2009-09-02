#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import getopt
import re
import os
import gzip
import zipfile

from lxml import etree
from lxml import objectify
from lxml import html
import lxml

import epub
import process_abbyy
import common

# remove me for faster execution
debugme = True
if debugme:
    from  pydbgr.api import debug
else:
    def debug():
        pass

def main(argv):
    book_id = common.get_book_id()
    z = zipfile.ZipFile(book_id + '.epub', 'w')
    add_to_zip(z, 'mimetype', 'application/epub+zip', deflate=False)

    tree_str = epub.make_container_info()
    add_to_zip(z, 'META-INF/container.xml', tree_str)

    manifest_items = [
        { 'id':'ncx',
          'href':'toc.ncx',
          'media-type':'application/x-dtbncx+xml'
          }
        ]
    spine_items = []
    guide_items = []
    navpoints = []
    for (itemtype, info, item) in process_abbyy.generate_epub_items(book_id):
        nav_number = 0
        if itemtype == 'content':
            manifest_items.append(info)
            add_to_zip(z, 'OEBPS/'+info['href'], item)
        elif itemtype == 'spine':
            spine_items.append(info)
        elif itemtype == 'guide':
            guide_items.append(info)
        elif itemtype == 'navpoint':
            info['id'] = 'navpoint-' + str(nav_number)
            info['playOrder'] = str(nav_number)
            nav_number += 1
            navpoints.append(info)

    meta_info_items = process_abbyy.get_meta_items(book_id)

    tree_str = epub.make_opf(meta_info_items,
                         manifest_items,
                         spine_items,
                         guide_items);
    add_to_zip(z, 'OEBPS/content.opf', tree_str)

    tree_str = epub.make_ncx(navpoints);
    add_to_zip(z, 'OEBPS/toc.ncx', tree_str)

    z.close()

def usage():
#    print 'usage: abbyy_to_epub.py book_id abbyy.xml scandata.xml book_id'
    print 'usage: abbyy_to_epub.py'

def add_to_zip(z, path, s, deflate=True):
    info = zipfile.ZipInfo(path)
    info.compress_type = zipfile.ZIP_DEFLATED if deflate else zipfile.ZIP_STORED
    info.external_attr = 0666 << 16L # fix access
    info.date_time = (2009, 12, 25, 0, 0, 0)
    z.writestr(info, s)

if __name__ == '__main__':
    main(sys.argv[1:])

# bad char? iso-8859-1 - '—' = 80 e2 94