#!/usr/bin/python
import urllib, urllib2, time, sys, os
import re, random, base64
import email, poplib
from getpass import getpass

# Enter your gmail account details here so that the script can read emails
emailUsername = raw_input('Please input your Gmail Accout:')
emailPassword = getpass(prompt='Password:')

# Change this (at your own risk) if you don't use gmail 
# (e.g. to hotmail/yahoo/etc smtp servers)
emailSMTPserver = 'smtp.gmail.com'
emailPOPserver  = 'pop.gmail.com'

whitelists = []

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

            #print "mail from =====", mailfrom
            
            # if mail address is not in whitelist, jump to the next
            isInWhitelist = False
            
            for t in whitelists:
                if t in mailfrom:
                    isInWhitelist = True

            if not isInWhitelist:
                #print "not in whitelist"
                continue
                    
            allowed_mimetypes = ["application/octet-stream"]

            response, lines, octets = p.retr(number)
            message = email.message_from_string('\n'.join(lines))
                    
            #print "subject ====", email.Header.decode_header(subject)[0][0]

            for part in message.walk():
                
                #body
                #if part.get_content_type() == 'text/plain':
                    #body = part.get_payload(decode=True)
                    #print "body:\n %s\n" % body
                
                #attachment
                if part.get_content_type() in allowed_mimetypes:
                    filename = part.get_filename()
                    
                    if filename==None:
                        continue
                    filename = email.Header.decode_header(filename)[0][0]
                    
                    if not 'csv' in filename:
                        continue
                    
                    print "extract csv file: ", filename
                    
                    data = part.get_payload(decode=True)
                    f = file(filename,'wb')
                    f.write(data)
                    f.close()

    finally:
        p.quit()

    return


#the main process
if __name__ == "__main__":
        
    whitelists = getWhitelist() 

    readEmail()
        
