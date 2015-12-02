#!/usr/bin/python
import urllib, urllib2, time, sys, os
import re, random, base64
import email, poplib
from getpass import getpass

# Enter your gmail account details here so that the script can read emails
emailUsername = raw_input('Please input your Yahoo Mail Accout:')
emailPassword = getpass(prompt='Password:')

# Change this (at your own risk) if you don't use gmail 
# (e.g. to hotmail/yahoo/etc smtp servers)
emailSMTPserver = 'smtp.yahoo.com'
emailPOPserver  = 'pop.yahoo.com'

whitelists = []

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("p.log", "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  
        
def getWhitelist():
    white = []
    f = open('whitelist.txt','r')
    for line in f:
        line = line.strip()
        #print line
        white.append(line)    
    return white


def readEmail():
    choose = 0
    p = poplib.POP3_SSL(emailPOPserver)
    try:
        p.user(emailUsername)
        p.pass_(emailPassword)
    except poplib.error_proto, e:
        print "Login failed:", e
    else:
        response, listings, octets = p.list()
        for listing in listings:
            number, size = listing.split()
            response, lines, octets = p.top(number, 0)
            
            message = email.message_from_string('\n'.join(lines))
            subject = message['Subject']
            mailfrom = message['From']

            if not mailfrom in whitelists:      # if mail address is not in whitelist, jump to the next
                continue

            allowed_mimetypes = ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]

            response, lines, octets = p.retr(number)
            message = email.message_from_string('\n'.join(lines))
            
            for part in message.walk():
                if part.get_content_type() == 'text/plain':
                #if part.get_content_type() in allowed_mimetypes:
                    #name = part.get_filename()
                    #data = part.get_payload(decode=True)
                    body = part.get_payload(decode=True)
                    print "body=%s\n" % body
                    #f = file(name,'wb')
                    #f.write(data)
                    #f.close()

    finally:
        p.quit()

    return


#the main process
if __name__ == "__main__":
    
    # print output to console and DSAChecker.log
    sys.stdout = Logger()

    # get parameter
    if len(sys.argv) > 1:
        licenceNumber = sys.argv[1]
        theoryNumber = sys.argv[2]
        
    whitelists = getWhitelist()
 

    #readEmail()
        
