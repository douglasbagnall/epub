#!/usr/bin/python

import sys
import getopt
import re
import gzip
import os
import zipfile

from lxml import etree
from lxml import objectify

from debug import debug, debugging, assert_d

class Book(object):
    def __init__(self, book_id, book_path):
        self.book_id = book_id
        self.book_path = book_path
        if not os.path.exists(book_path):
            raise Exception('Can\'t find book path "' + book_path + '"')
        self.scandata = None

    def get_book_id(self):
        return self.book_id

    def get_book_path(self):
        return self.book_path

    def get_scandata_path(self):
        paths = [
            os.path.join(self.book_path, self.book_id + '_scandata.xml'),
            os.path.join(self.book_path, 'scandata.xml'),
            os.path.join(self.book_path, 'scandata.zip'),
            ]
        for sd_path in paths:
            if os.path.exists(sd_path):
                return sd_path
        raise Exception('No scandata found')

    def get_scandata(self):
        if self.scandata is None:
            scandata_path = self.get_scandata_path()
            (base, ext) = os.path.splitext(scandata_path)
            if ext.lower() == '.zip':
                z = zipfile.ZipFile(scandata_path, 'r')
                scandata_str = z.read('scandata.xml')
                z.close()
                self.scandata = objectify.fromstring(scandata_str)
                scandata_pages = self.scandata.pageData.page
            else:
                self.scandata = objectify.parse(self.
                                                get_scandata_path()).getroot()
                scandata_pages = self.scandata.xpath('/book/pageData/page')
            self.leaves = {}
            for page in scandata_pages:
                self.leaves[int(page.get('leafNum'))] = page
        return self.scandata

    def get_page_data(self, leaf):
        if leaf in self.leaves:
            return self.leaves[leaf]
        else:
            return None

    def get_metadata_path(self):
        return os.path.join(self.book_path, self.book_id + '_meta.xml')

    def get_abbyy(self):
        return gzip.open(os.path.join(self.book_path,
                                      self.book_id + '_abbyy.gz'), 'rb')

    # get python string with image data - from .jp2 image in zip
    def get_image(self, i, width=700, height=900,
                  quality=90,
                  region='{0.0,0.0},{1.0,1.0}',
                  img_type='jpg'):
        zipf = os.path.join(self.book_path,
                            self.book_id + '_jp2.zip')
        image_path = (self.book_id + '_jp2/' + self.book_id + '_'
                      + str(i).zfill(4) + '.jp2')
        try:
            z = zipfile.ZipFile(zipf, 'r')
            info = z.getinfo(image_path) # for to check it exists
            z.close()
        except KeyError:
            return None
        return image_from_zip(zipf, image_path,
                              width, height, quality, region, img_type)

if not os.path.exists('/tmp/stdout.ppm'):
    os.symlink('/dev/stdout', '/tmp/stdout.ppm')
 
# get python string with image data - from .jp2 image in zip
def image_from_zip(zipf, image_path,
                   width, height, quality, region, img_type):
    if not os.path.exists(zipf):
        raise Exception('Zipfile missing')

    if img_type == 'jpg':
        output = os.popen('unzip -p ' + zipf + ' ' + image_path
                      + ' | kdu_expand -region "' + region + '"'
                      +   ' -reduce 2 '
                      +   ' -no_seek -i /dev/stdin -o /tmp/stdout.ppm'
#                      + ' | pamscale -xyfit ' + str(width) + ' ' + str(height)
                      + ' | pnmscale -xysize ' + str(width) + ' ' + str(height)
                      + ' | pnmtojpeg -quality ' + str(quality))
    elif img_type == 'ppm':
        output = os.popen('unzip -p ' + zipf + ' ' + image_path
                      + ' | kdu_expand -region "' + region + '"'
                      +   ' -reduce 2 '
                      +   ' -no_seek -i /dev/stdin -o /tmp/stdout.ppm'
#                      + ' | pamscale -xyfit ' + str(width) + ' ' + str(height))
                      + ' | pnmscale -xysize ' + str(width) + ' ' + str(height))
    else:
        raise 'unrecognized image type'
    return output.read()

# ' | pnmscale -xysize ' + str(width) + ' ' + str(height)

# Adapted from http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
def iso_639_23_to_iso_639_1(marc_code):
    mapping = {
        'aar':'aa',
        'abk':'ab',
        'ave':'ae',
        'afr':'af',
        'aka':'ak',
        'amh':'am',
        'arg':'an',
        'ara':'ar',
        'asm':'as',
        'ava':'av',
        'aym':'ay',
        'aze':'az',
        'bak':'ba',
        'bel':'be',
        'bul':'bg',
        'bih':'bh',
        'bis':'bi',
        'bam':'bm',
        'ben':'bn',
        'bod':'bo',
        'tib':'bo',
        'bre':'br',
        'bos':'bs',
        'cat':'ca',
        'che':'ce',
        'cha':'ch',
        'cos':'co',
        'cre':'cr',
        'ces':'cs',
        'cze':'vs',
        'chu':'cu',
        'chv':'cv',
        'cym':'cy',
        'wel':'cy',
        'dan':'da',
        'deu':'de',
        'ger':'de',
        'div':'dv',
        'dzo':'dz',
        'ewe':'ee',
        'ell':'el',
        'gre':'el',
        'eng':'en',
        'epo':'eo',
        'spa':'es',
        'est':'et',
        'eus':'eu',
        'baq':'eu',
        'fas':'fa',
        'per':'fa',
        'ful':'ff',
        'fin':'fi',
        'fij':'fj',
        'fao':'fo',
        'fra':'fr',
        'fre':'fr',
        'fry':'fy',
        'gle':'ga',
        'gla':'gd',
        'glg':'gl',
        'grn':'gn',
        'guj':'gu',
        'glv':'gv',
        'hau':'ha',
        'heb':'he',
        'hin':'hi',
        'hmo':'ho',
        'hrv':'hr',
        'hat':'ht',
        'hun':'hu',
        'hye':'hy',
        'arm':'hy',
        'her':'hz',
        'ina':'ia',
        'ind':'id',
        'ile':'ie',
        'ibo':'ig',
        'iii':'ii',
        'ipk':'ik',
        'ido':'io',
        'isl':'is',
        'ice':'is',
        'ita':'it',
        'iku':'iu',
        'jpn':'ja',
        'jav':'jv',
        'kat':'ka',
        'geo':'ka',
        'kon':'kg',
        'kik':'ki',
        'kua':'kj',
        'kaz':'kk',
        'kal':'kl',
        'khm':'km',
        'kan':'kn',
        'kor':'ko',
        'kau':'kr',
        'kas':'ks',
        'kur':'ku',
        'kom':'kv',
        'cor':'kw',
        'kir':'ky',
        'lat':'la',
        'ltz':'lb',
        'lug':'lg',
        'lim':'li',
        'lin':'ln',
        'lao':'lo',
        'lit':'lt',
        'lub':'lu',
        'lav':'lv',
        'mlg':'mg',
        'mah':'mh',
        'mri':'mi',
        'mao':'mi',
        'mkd':'mk',
        'mac':'mk',
        'mal':'ml',
        'mon':'mn',
        'mar':'mr',
        'msa':'ms',
        'may':'ms',
        'mlt':'mt',
        'mya':'my',
        'bur':'my',
        'nau':'na',
        'nob':'nb',
        'nde':'nd',
        'nep':'ne',
        'ndo':'ng',
        'nld':'nl',
        'dut':'nl',
        'nno':'nn',
        'nor':'no',
        'nbl':'nr',
        'nav':'nv',
        'nya':'ny',
        'oci':'oc',
        'oji':'oj',
        'orm':'om',
        'ori':'or',
        'oss':'os',
        'pan':'pa',
        'pli':'pi',
        'pol':'pl',
        'pus':'ps',
        'por':'pt',
        'que':'qu',
        'roh':'rm',
        'run':'rn',
        'ron':'ro',
        'rum':'ro',
        'rus':'ru',
        'kin':'rw',
        'san':'sa',
        'srd':'sc',
        'snd':'sd',
        'sme':'se',
        'sag':'sg',
        'sin':'si',
        'slk':'sk',
        'slo':'sk',
        'slv':'sl',
        'smo':'sm',
        'sna':'sn',
        'som':'so',
        'sqi':'sq',
        'alb':'sq',
        'srp':'sr',
        'ssw':'ss',
        'sot':'st',
        'sun':'su',
        'swe':'sv',
        'swa':'sw',
        'tam':'ta',
        'tel':'te',
        'tgk':'tg',
        'tha':'th',
        'tir':'ti',
        'tuk':'tk',
        'tgl':'tl',
        'tsn':'tn',
        'ton':'to',
        'tur':'tr',
        'tso':'ts',
        'tat':'tt',
        'twi':'tw',
        'tah':'ty',
        'uig':'ug',
        'ukr':'uk',
        'urd':'ur',
        'uzb':'uz',
        'ven':'ve',
        'vie':'vi',
        'vol':'vo',
        'wln':'wa',
        'wol':'wo',
        'xho':'xh',
        'yid':'yi', 
        'yor':'yo',
        'zha':'za',
        'zho':'zh',
        'chi':'zh',
        'zul':'zu',
        }
    if marc_code in mapping:
        return mapping[marc_code]
    else:
        return marc_code
        
if __name__ == '__main__':
    sys.stderr.write('I\'m a module.  Don''t run me directly!')
    sys.exit(-1)
