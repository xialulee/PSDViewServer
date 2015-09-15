# -*- coding: utf-8 -*-
"""
Created on Saturday September 12 2015

@author: xialulee. xialulee@sina.com
"""

from __future__ import division
from bottle     import route, run, template, response
from psd_tools  import PSDImage
from cStringIO  import StringIO
from os         import path, listdir
from sys        import argv
from PIL        import Image

if __name__ == '__main__':
    rootDir = argv[1]


def psd2image(psdPath):
    psd   = PSDImage.load(psdPath)
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
    
    
@route('/ls')    
@route('/<psdPath:path>/ls')
def ls(psdPath=''):
    return template('''
<body bgcolor="grey">
%absPath = path.join(rootDir, psdPath)    
%for item in listdir(absPath):
     %url = '/'.join((psdPath, item))
     %url = '/' + url if psdPath else url
     %if path.splitext(item)[1].lower() == '.psd':
         <a href="{{url}}/fullsize">
             <img src="{{url}}/thumbnail"/>
         </a>
     %elif path.isdir(absPath):
         <a href="{{url}}/ls">{{item}}</a>
         <br/>
     %end
%end
</body>
    ''', rootDir=rootDir, psdPath = psdPath, listdir=listdir, path=path)

    
@route('/index')
def index():
    return ls('')

    
    
@route('/<psdPath:path>/thumbnail')
def thumbnailRender(psdPath):
    psdPath   = path.join(rootDir, psdPath)
    maxHeight = 300
    image     = psd2image(psdPath)
    stream    = image2stream(image, format='jpeg', maxHeight=maxHeight)
    return stream.read()
    
@route('/<psdPath:path>/fullsize')
def imageRender(psdPath):
    psdPath   = path.join(rootDir, psdPath)
    image     = psd2image(psdPath)
    stream    = image2stream(image, format='jpeg')
    response.set_header('Content-type', 'image/jpeg')
    return stream.read()

run(host='', port=8045)
