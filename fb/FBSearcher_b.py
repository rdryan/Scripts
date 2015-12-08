#!/usr/bin/env python
from __future__ import print_function
from selenium import webdriver
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from time import sleep
import getpass
import sys
import logging
import random
import requests

if sys.version[0] == '3': raw_input=input   # for python 2/3 cross compatibility

# source:
# https://www.reddit.com/r/Python/comments/396aau/fb_eraser_automate_deleting_your_old_facebook/
class Searcher(object):
    def __init__(self, email, password, wait=1):
        """
        Set up the searcher
        :return: Null
        """
        service_args = [
            #'--proxy=127.0.0.1:8087',
            #'--proxy=127.0.0.1:8580',
            #'--proxy-type=socks5',
            #'--proxy-type=https',
            '--ignore-ssl-errors=true',
            ]
            
        self.driver = webdriver.PhantomJS(service_args=service_args)

        # self.driver = webdriver.Firefox()
        # self.driver = webdriver.PhantomJS()
        #self.driver = webdriver.Chrome()
        self.driver2  = None
        self.email = email
        self.password = password
#         self.profile_name = "zuck"            # this will end up being the facebook user name
        self.count = 0                      # counter of number of elements deleted
        self.wait = wait
        self.selenium_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
        self.selenium_logger.setLevel(logging.INFO)
        logging.basicConfig(filename = 'selenium.log', level = logging.DEBUG)

    def quit(self):
        """
        Quit the program (close out the browser)
        :return: Null
        """
        self.driver.quit()

    def login(self):
        """
        Log in to Facebook, set profile name
        :return: Null
        """
        self.driver.get('https://www.facebook.com/login/')
        email_element = self.driver.find_element_by_id('email')
        email_element.send_keys(self.email)
        password_element = self.driver.find_element_by_id('pass')
        password_element.send_keys(self.password)
        password_element.submit()

        soup = BeautifulSoup(self.driver.page_source)
        profile_link = soup.find('a', {'title': 'Profile'})
        self.profile_name = profile_link.get('href')[25:]    # link appears as http://www.facebook.com/PROFILE

    def search(self, keyword):
        self.driver.get('https://www.facebook.com/search/str/'+keyword+'/keywords_pages')
        sleep(self.wait)

    #def _get_page_id(self, id_object):
    def _get_page_id(self, page_name):
        #page_name = id_object.get_attribute("href").split("/").pop(-2)
        r = requests.get("http://mobile.facebook.com/"+page_name+"/info/?tab=page_info")
        print(r.status_code)
        if r.status_code == 404:
            print("Page Not Found")
            return None
        
        self.driver.get("http://mobile.facebook.com/"+page_name+"/info/?tab=page_info")
            
        try:
            print("search xpath")
            ahrefs_objs = self.driver.find_elements_by_xpath("//a[contains(@href,'posts')]")
        except:
            print("Not find posts")
    
        if len(ahrefs_objs) == 0:
            print("not find posts")
            return None
    
        real_page_id_splitted = ahrefs_objs[0].get_attribute("href").split("/")
        #real_page_id = real_page_id_splitted[2]
        real_page_id = real_page_id_splitted.pop(3)
        logging.debug(real_page_id_splitted.__str__())
        
        print(real_page_id)
        return real_page_id

    def _get_page_name(self, id_object):
        page_id = id_object.get_attribute("href").split("/").pop(-2)
        return page_id


    def _is_it_end_of_page(self):
        self.driver.find_element_by_xpath(".//*[@id='browse_end_of_results_footer']/div/div/div")


    def collect_pageids(self):
        # soup = BeautifulSoup(self.driver.page_source)
        # TODO: need to pick out each of the page's link (and the group name), just log them to screen
        # consider the delete_element method as an example
        # For example: https://www.facebook.com/search/str/epilepsy/keywords_pages
        # has "EpilepsySociety", and "epilepsysupports", etc as list of page ids
        # logging.info(pageid)
        page_id_xpath = ".//*[@class='_gll']/a"
        #page_ids_elems = self.driver.find_elements_by_xpath(page_id_xpath)
        page_ids_elems = self.driver.find_elements_by_xpath(page_id_xpath)
        page_names = list(map(self._get_page_name, page_ids_elems))
        print(page_names)
        
        page_ids=[]
        for page_name in page_names:
            print("page_name..")
            print(page_name)
            page_ids.append(self._get_page_id(page_name))
        logging.debug(page_ids)

        print(page_ids)
        return page_ids

        
    def go_to_activity_page(self):
        """
        Go to the activity page and prepare to start deleting
        :return: Null
        """
        if not self.profile_name:
            # the user hasn't logged in properly
            sys.exit(-2)
        # go to the activity page (filter by 'Your Posts')
        activity_link = 'https://www.facebook.com/' + self.profile_name + '/allactivity?privacy_source=activity_log&log_filter=cluster_11'
        self.driver.get(activity_link)
        sleep(self.wait)
    

    def scroll_down(self):
        """
        Executes JS to scroll down on page.
        Use if having trouble seeing elements
        :return:
        """
        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        sleep(self.wait)

    def delete_element(self):
        """
        Find the first available element and delete it
        :return: Null
        """

        # click hidden from timeline so the delete button shows up
        soup = BeautifulSoup(self.driver.page_source)
        # Priority: highlights, allowed, hidden
        menu_button = soup.find('a', {'aria-label': 'Highlighted on Timeline'})
        if menu_button is None:
            menu_button = soup.find('a', {'aria-label': 'Allowed on Timeline'})
        if menu_button is None:
            menu_button = soup.find('a', {'aria-label': 'Hidden from Timeline'})
        if menu_button is None:
            menu_button = soup.find('a', {'aria-label': 'Shown on Timeline'})
        menu_element = self.driver.find_element_by_id(menu_button.get('id'))
        menu_element.click()
        sleep(self.wait)

        # now that the delete button comes up, find the delete link and click
        # sometimes it takes more than one click to get the delete button to pop up
        if menu_button is not None:
            i = 0
            while i < 3:
                try:
                    self.driver.find_element_by_link_text('Delete').click()
                    break
                except:
                    print('[*] Clicking menu again')
                    menu_element.click()
                    i += 1
        sleep(self.wait)

        # click the confirm button, increment counter and display success
        self.driver.find_element_by_class_name('layerConfirm').click()
        self.count += 1
        print('[+] Element Deleted ({count} in total)'.format(count=self.count))
        sleep(self.wait)


if __name__ == '__main__':
    keyword ="irritable bowel syndrome"
    searcher = Searcher(email="", password="", wait=1)
    print("begin login")
    searcher.login()
    print("login ok, start search..")
    searcher.search(keyword)

    #comment this use if for fast test
    #while True:
    if True:
        try:
            #searcher._is_it_end_of_page()
            page_names = random.shuffle(searcher.collect_pageids())

            for page_name in page_names:
                #sleep(self.wait)
                print(page_names)
            
        except:
            searcher.scroll_down()

    searcher.driver.close()
