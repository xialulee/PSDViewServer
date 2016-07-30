# -*- coding: utf-8 -*-
"""
Created on Saturday September 12 2015

@author: xialulee. xialulee@sina.com
"""

from __future__ import division
import os
from os         import path, listdir
from sys        import argv, getfilesystemencoding
from cStringIO  import StringIO
from xml.dom    import minidom
from bottle     import route, run, template, response
from psd_tools  import PSDImage
from PIL        import Image


if __name__ == '__main__':
    root_path = argv[1]


def list_dir(path):
    bridge_sort_path = os.path.join(path, '.BridgeSort')
    if os.path.exists(bridge_sort_path):
        doc = minidom.parse(bridge_sort_path)
        r = doc.documentElement
        files = r.getElementsByTagName('files')[0]
        items = files.getElementsByTagName('item')
        return [item.getAttribute('key')[:-14].encode(getfilesystemencoding())\
            for item in items]
    else:
        return listdir(path)
        


def encode_path(path):
    return path.decode(getfilesystemencoding()).encode('UTF-8')
    
    
def decode_path(path):
    return path.decode('UTF-8').encode(getfilesystemencoding())


def psd_to_image(psd_path):
    psd   = PSDImage.load(psd_path)
    merge = psd.as_PIL()
    return merge
    
def image_to_stream(image, format, max_height=None):
    if max_height:
        size  = image.size
        ratio = max_height / size[1]
        image = image.resize((int(size[0]*ratio), max_height), Image.ANTIALIAS)
    
    stream = StringIO()
    image.save(stream, format=format)
    stream.seek(0)
    return stream
    
    
@route('/ls')    
@route('/<psd_path:path>/ls')
def ls(psd_path=''):
    return template('''
<body bgcolor="grey">
%abs_path = path.join(root_path, psd_path) 
%for item in listdir(abs_path):
     %item = encode_path(item)
     %url = '/'.join((psd_path, item))
     %url = '/' + url if psd_path else url
     %if path.splitext(item)[1].lower() == '.psd':
         <a href="{{url}}/fullsize">
             <img src="{{url}}/thumbnail"/>
         </a>
     %elif path.isdir(abs_path):
         <a href="{{url}}/ls">{{item}}</a>
         <br/>
     %end
%end
</body>
    ''', root_path=root_path, 
         psd_path=psd_path, 
         listdir=list_dir, 
         path=path,
         encode_path=encode_path)

    
@route('/index')
def index():
    return ls('')
   
    
@route('/<psd_path:path>/thumbnail')
def thumbnail_render(psd_path):
    psd_path   = decode_path(psd_path)
    psd_path   = path.join(root_path, psd_path)
    max_height = 300
    image     = psd_to_image(psd_path)
    stream    = image_to_stream(image, format='png', max_height=max_height)
    return stream.read()
    
@route('/<psd_path:path>/fullsize')
def image_render(psd_path):
    psd_path   = decode_path(psd_path)
    psd_path   = path.join(root_path, psd_path)
    image     = psd_to_image(psd_path)
    stream    = image_to_stream(image, format='jpeg')
    response.set_header('Content-type', 'image/jpeg')
    return stream.read()

run(host='', port=8045)
