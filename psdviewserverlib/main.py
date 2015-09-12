# -*- coding: utf-8 -*-
"""
Created on Fri May 02 15:48:27 2014

@author: xialulee. xialulee@sina.com
"""

from __future__ import division
from bottle     import route, run, template, response
from psd_tools  import PSDImage
from cStringIO  import StringIO
from glob       import glob
from os         import path
from PIL        import Image


def listPSD():
    psds  = glob('./psdfiles/*.psd')
    return [path.split(psd)[1] for psd in psds]

def psd2image(filename):
    psd   = PSDImage.load('./psdfiles/' + filename)
    merge = psd.as_PIL()
    return merge
    
def image2stream(image, format, maxHeight=None):
    if maxHeight:
        size  = image.size
        ratio = maxHeight / size[1]
        image = image.resize((int(size[0]*ratio), maxHeight), Image.ANTIALIAS)
    
    stream = StringIO()
    image.save(stream, format=format)
    stream.seek(0)
    return stream
    
@route('/index')
def index():
    psds = listPSD()
    return template('''
<body bgcolor="grey">
%for psd in psds:
    <a href="./psdfiles/{{psd}}/fullsize">
        <img src="./psdfiles/{{psd}}/thumbnail"/>
    </a>
</body>
%end
    ''', psds=psds, splitext=path.splitext)
    
    
@route('/psdfiles/<filename>/thumbnail')
def thumbnailRender(filename):
    maxHeight = 300
    image     = psd2image(filename)
    stream    = image2stream(image, format='jpeg', maxHeight=maxHeight)
    return stream.read()
    
@route('/psdfiles/<filename>/fullsize')
def imageRender(filename):
    image     = psd2image(filename)
    stream    = image2stream(image, format='jpeg')
    response.set_header('Content-type', 'image/jpeg')
    return stream.read()

run(host='', port=8080)
