from urllib.request import urlopen
import urllib.request
from urllib.request import Request, urlopen
from datetime import datetime, date, timedelta
import pandas as pd
import os, time, random
import numpy as np
import pickle

#revision html scraper jan 14h
def html_scraper_galatec(url):
    page=url
    web_byte = urlopen(url).read()
    html = web_byte.decode('utf8')
    
    #req = Request(page, headers={'User-Agent': 'Mozilla/6.1'})
    #web_byte = urlopen(req).read()
    #html = web_byte.decode('utf-8')    
    
    date=datetime.now()

    #keypart='"NEW","price":{"__typename":"DeprecatedVatMoney","amountIncl"'
    keypart2='statt <!-- -->'
    keypart3='mit Gutscheincode</span>'
    if html.find(keypart2)!=-1:
        discount='Y'
        title_index=html.find(keypart2)
        start_index=title_index + len(keypart2)
        end_index=start_index+2
        while html[end_index-1:end_index]!=('<'):
            end_index=end_index+1
        discount_reference=html[start_index:end_index-1]
        
        keypart_price='<strong class="sc-1aeovxo-1 eKzvSf">'
        title_index=html.find(keypart_price)
        start_index=title_index + len(keypart_price)
        end_index=start_index+2
        while html[end_index-1:end_index]!=('<'):
            end_index=end_index+1
        price=html[start_index:end_index-1]   
    
    elif html.find(keypart3)!=-1:
        discount='Y'
        discount_reference='Gutscheincode'
        
        title_index=html.find(keypart3)
        start_index=title_index + len(keypart3)
        end_index=start_index+2
        while html[end_index-1:end_index]!=('<'):
            end_index=end_index+1
        price=html[start_index:end_index-1]        
    else:
        discount='N'
        discount_reference=None
        keypart='price:amount" content="'
        title_index=html.find(keypart)
        start_index=title_index + len(keypart)
        end_index=start_index+2
        while html[end_index-1:end_index]!=('"'):
            end_index=end_index+1
        price=html[start_index:end_index-1]

    if price=='lass=':#means no price available
        price=None
    else:
        price=price        
        
    keypart='</script><title>'
    title_index=html.find(keypart)
    start_index=title_index + len(keypart)
    end_index=start_index+2
    while html[end_index-2:end_index]!=('- '):
        end_index=end_index+1
    name=html[start_index:end_index-2-1]

    keypart='<noscript><span>'
    title_index=html.find(keypart)
    start_index=title_index + len(keypart)
    end_index=start_index+2
    while html[end_index-1:end_index]!=('<'):
        end_index=end_index+1
    description=html[start_index:end_index-1]
    if ('<' in description) or ('>' in description) :
        description=None

    keypart='Artikelnummer'
    keypart2='<div>'
    title_index=html.find(keypart)
    title_index2=html[title_index:].find(keypart2)
    start_index=title_index+title_index2 + len(keypart2)
    end_index=start_index+2
    while html[end_index-1:end_index]!=('<'):
        end_index=end_index+1
    articlenumber=html[start_index:end_index-1]
    if '<' in articlenumber or '>' in articlenumber:
        #try this, sometimes artikelnummer is to be found right after colon :
        keypart='Artikelnummer: '
        title_index=html.find(keypart)
        start_index=title_index+len(keypart)
        end_index=start_index+2
        while html[end_index-1:end_index]!=('"'):
            end_index=end_index+1
        articlenumber=html[start_index:end_index-1]
    
    keypart='header-availability'
    keypart2='<br/>'
    title_index=html.find(keypart)
    title_index2=html[title_index:].find(keypart2)
    start_index=title_index +title_index2 + len(keypart2)
    end_index=start_index+2
    while html[end_index-1:end_index]!=('<'):
        end_index=end_index+1
    storage=html[start_index:end_index-1]
    if ('<' in storage) or ('>' in storage) :
        storage=None
    
    keypart='header-availability">'
    keypart2='>'
    title_index=html.find(keypart)
    title_index2=html[title_index+len(keypart):].find(keypart2)
    start_index=title_index +len(keypart) +title_index2 +len(keypart2)
    end_index=start_index+2
    while html[end_index-1:end_index]!=('<'):
        end_index=end_index+1
    delivery=html[start_index:end_index-1]
    
    keypart='<strong class="sc-tmgjmw-0">noch '
    if html.find(keypart)!=-1:
        limited='Y'
        title_index=html.find(keypart)
        start_index=title_index + len(keypart)
        end_index=start_index+2
        while html[end_index-1:end_index]!=('<'):
            end_index=end_index+1
        limited_value=html[start_index:end_index-1]
    else:
        limited='N'
        limited_value=None    
    
    keypart='"position":1,"name":"'
    title_index=html.find(keypart)
    start_index=title_index + len(keypart)
    end_index=start_index+2
    while html[end_index-1:end_index]!=('"'):
        end_index=end_index+1
    product_type1=html[start_index:end_index-1]
    
    keypart='"position":2,"name":"'
    title_index=html.find(keypart)
    start_index=title_index + len(keypart)
    end_index=start_index+2
    while html[end_index-1:end_index]!=('"'):
        end_index=end_index+1
    product_type2=html[start_index:end_index-1]
    
    keypart='"position":3,"name":"'
    title_index=html.find(keypart)
    start_index=title_index + len(keypart)
    end_index=start_index+2
    while html[end_index-1:end_index]!=('"'):
        end_index=end_index+1
    if html[start_index:end_index-1]==" class=":
        product_type3=product_type2
    else:
        product_type3=html[start_index:end_index-1]
    
    source_link=url
    
    snapshot={
        'date':date,
        'price':price,
        'product_type1':product_type1,
        'product_type2':product_type2,
        'product_type3':product_type3,
        'name':name,
        'description':description,
        'articlenumber': articlenumber,
        'storage':storage,
        'delivery':delivery,
        'discount':discount,
        'discount_reference':discount_reference,
        'limited':limited,
        'limited_value':limited_value,
        'source_link':source_link
        #'html':html #for debugging get access to html by removing previous two hashes     
    }
    return snapshot #snapshot is a dictionary