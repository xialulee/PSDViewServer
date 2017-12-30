# -*- coding: utf-8 -*-
"""
Created on Saturday September 12 2015

@author: xialulee. xialulee@sina.com
"""


from pathlib import Path
from sys import argv
from io import BytesIO
from xml.dom import minidom
from bottle import route, run, template, response
from psd_tools import PSDImage
from PIL import Image


if __name__ == '__main__':
    root_path = Path(argv[1])
    
    

def list_dir(path):
    bridge_sort_path = path / '.BridgeSort'
    if bridge_sort_path.exists():
        doc = minidom.parse(str(bridge_sort_path))
        r = doc.documentElement
        files = r.getElementsByTagName('files')[0]
        items = files.getElementsByTagName('item')
        #return [item.getAttribute('key')[:-14] for item in items]
        for item in items:
            yield Path(item.getAttribute('key')[:-14])
    else:
        return path.iterdir()
        
        

def psd_to_image(psd_path):
    psd   = PSDImage.load(psd_path)
    merge = psd.as_PIL()
    return merge


    
def image_to_stream(image, format, max_height=None):
    if max_height:
        size  = image.size
        ratio = max_height / size[1]
        image = image.resize((int(size[0]*ratio), max_height), Image.ANTIALIAS)
    
    stream = BytesIO()
    image.save(stream, format=format)
    stream.seek(0)
    return stream

    
    
@route('/ls')    
@route('/<psd_path:path>/ls')
def ls(psd_path=''):
    return template('''
<body bgcolor="grey">
%abs_path = root_path / psd_path
%for item in list_dir(abs_path):
    %url = '/'.join((psd_path, str(item)))
    %url = '/'+url if psd_path else url
    %if item.suffix == '.psd':
        <a href="{{url}}/fullsize">
            <img src="{{url}}/thumbnail"/>
        </a>
    %elif abs_path.is_dir():
        <a href="{{url}}/ls">{{str(item)}}</a>
        <br/>
    %end
%end
</body>
''', root_path=root_path, psd_path=psd_path, list_dir=list_dir)

    
        
@route('/index')
def index():
    return ls('')
   
    

@route('/<psd_path:path>/thumbnail')
def thumbnail_render(psd_path):
    abs_path = root_path / psd_path
    max_height = 300
    image = psd_to_image(abs_path)
    stream = image_to_stream(image, format='png', max_height=max_height)
    return stream.read()
    


@route('/<psd_path:path>/fullsize')
def image_render(psd_path):
    abs_path = root_path / psd_path
    image = psd_to_image(abs_path)
    stream = image_to_stream(image, format='jpeg')
    response.set_header('Content-type', 'image/jpeg')
    return stream.read()



run(host='', port=8045)
