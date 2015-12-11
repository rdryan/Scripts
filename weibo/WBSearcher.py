#!/usr/bin/env python
from selenium import webdriver
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from time import sleep
import getpass
import sys
import logging

class Searcher(object):

    def __init__(self, email, password, wait=1):

        #use proxy to login, if not use, comment it out
        service_args = [
            #'--proxy=127.0.0.1:8087',
            '--proxy=10.0.13.122:3128',
            '--proxy-type=https',
            ]

        #self.driver = webdriver.PhantomJS(service_args=service_args)
        self.driver = webdriver.Chrome()
        self.email = email
        self.password = password
        self.wait = wait

    def quit(self):
        self.driver.quit()

    def login(self):
        self.driver.get('https://weibo.com/login/')
        email_element = self.driver.find_element_by_name('username')
        email_element.clear()
        email_element.send_keys(self.email)
        
        password_element = self.driver.find_element_by_name('password')
        password_element.clear()
        password_element.send_keys(self.password)

        login_element = self.driver.find_element_by_xpath('//div[@class="info_list login_btn"]/a')

        login_element.click()
        #password_element.submit()
        print "test"

        #print self.driver.page_source.encode('utf-8')
        #soup = BeautifulSoup(self.driver.page_source)
        #profile_link = soup.find('a', {'title': 'Profile'})
        #self.profile_name = profile_link.get('href')[25:]    # link appears as http://www.facebook.com/PROFILE

    def search(self, keyword):
        self.driver.get('https://www.facebook.com/search/str/'+keyword+'/keywords_pages')
        sleep(self.wait)


    def scroll_down(self):
        """
        Executes JS to scroll down on page.
        Use if having trouble seeing elements
        """
        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        sleep(self.wait)

    
        

if __name__ == '__main__':
#     """
#     Main section of script
#     """
#     # set up the command line argument parser
#     parser = ArgumentParser(description='Delete your Facebook activity.  Requires Firefox')
#     parser.add_argument('--wait', type=float, default=1, help='Explicit wait time between page loads (default 1 second)')
#     args = parser.parse_args()
# 
#     # execute the script
    email = raw_input("Please Enter Weibo login email: ")
    password = getpass.getpass("Password:")
    
    keyword="test"
    searcher = Searcher(email=email, password=password, wait=1)

    print "begin login"
    searcher.login()
    print "login ok"
    
    #searcher.search(keyword)
    
    #searcher.quit()

