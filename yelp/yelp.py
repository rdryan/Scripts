# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from bs4 import BeautifulSoup
import urlparse
import urllib2
import time
import socket

start_urls = (
    'http://www.yelp.com/http://www.yelp.com/search?find_desc=Restaurants&find_loc=San+Francisco%2C+CAsearch?find_desc=Restaurants&find_loc=San+Francisco%2C+CA',
   )


        
def get_request(url):
    print "request to: ", url
    req = urllib2.Request(url)

    try:
        response = urllib2.urlopen(req, timeout=100)
        return response
    except urllib2.URLError, e:
        print "Some Error happened"
        return False
    except socket.timeout, e:
        print "Socket Time Out"
        return False
 
def parse(response):
    if not response:
        return
    
    html = response.read()
    
    sel = BeautifulSoup(html, 'html.parser')
    #infos = sel.findAll('h3',attrs={'class':'search-result-title'})
    infos = sel.findAll('span',attrs={'class':'indexed-biz-name'})
    
    for info in infos:
        i = info.find('a')['href']
        url_i = "http://%s%s" %(urlparse.urlparse(response.url).hostname, i)
        response = get_request(url_i)
        parse_listing(response)

    next = sel.find('a',attrs={'class':'page-option prev-next next'})
    if not next:
        return 

    url_i = "http://%s%s" % (urlparse.urlparse(response.url).hostname, next['href'])
    print "=== next page ===", url_i
    time.sleep(2)
    parse(get_request(url_i))


def parse_listing(response):
    if not response:
        return
    
    html = response.read()
    sel = BeautifulSoup(html, 'html.parser')

    names = sel.find('h1',attrs={'class':'biz-page-title embossed-text-white shortenough'})
    if names:
        print names.text.strip()
        item['name'] = names.text.strip()
  
    website = sel.find('div',attrs={'class':'biz-website'})
    if website:
        print website.find('a').text.strip()
        item['website'] = website.find('a').text.strip()
    
    email = sel.find('div',attrs={'class':'biz-email'})
    if email:
        print email.find('a').text.strip()
        item['email'] = email.find('a').text.strip()

    ofile.write('"%s",' % (item['name'].encode('utf-8')))
    ofile.write('"%s",' % (item['website'].encode('utf-8')))
    ofile.write('"%s"\n' % (item['email'].encode('utf-8')))


#######################################################################################
## Main function
#######################################################################################
item = dict()
item['name'] = ''
item['website'] = ''
item['email'] = ''

global ofile
ofile = open('infos-%s.csv' % (time.strftime("%Y-%m-%d-%H")), 'w+')
ofile.write('name,website,email\n')

# all url are put in a list called 'url_list.txt'
print "will open url_list.txt to get url list for scraping"
url_lists = open('url_list.txt','r')
for url in url_lists:
    parse(get_request(url))

url_lists.close()
ofile.close()


