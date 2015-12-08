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
        print "Add to whitelist: ", line
        white.append(line)

    print "**** whitelist add finished! ****"
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
        print "****** There are ", len(listings), "mail(s) ******"
        
        for listing in listings:
            number, size = listing.split()
            response, lines, octets = p.top(number, 0)
            
            message = email.message_from_string('\n'.join(lines))
            subject = message['Subject']
            mailfrom = message['From']

            print "mail from ---- ", mailfrom
            print "---- subject: ", subject
            #print "subject ====", email.Header.decode_header(subject)[0][0]
            
            # if mail address is not in whitelist, jump to the next
            isInWhitelist = False
            
            for t in whitelists:
                if t in mailfrom:
                    isInWhitelist = True

            if not isInWhitelist:
                print "**** this address is not in whitelist, ignore"
                continue
            
            print "**** this address is in whitelist, will process it"
                    
            allowed_mimetypes = ["application/octet-stream","text/csv"]

            response, lines, octets = p.retr(number)
            message = email.message_from_string('\n'.join(lines))
                    

            for part in message.walk():
                #Maybe comment out the following line, after debug
                print "****content_type is: ", part.get_content_type()
                
                #body
                #if part.get_content_type() == 'text/plain':
                    #body = part.get_payload(decode=True)
                    #print "body:\n %s\n" % body
                
                #attachment
                if part.get_content_type() in allowed_mimetypes:
                    filename = part.get_filename()
                    
                    if filename==None:
                        print "**** Not find an attachment, ignore"
                        continue
                    filename = email.Header.decode_header(filename)[0][0]
                    
                    if not 'csv' in filename:
                        print "**** Not find csv file in attachment, ignore"
                        continue
                    
                    print "**** Extract csv file: ", filename
                    
                    data = part.get_payload(decode=True)
                    f = file(filename,'wb')
                    f.write(data)
                    f.close()

                    # delete this mail, Dangerous!!!
                    #print "delete this mail"
                    #p.dele(number)

    finally:
        p.quit()

    return


#the main process
if __name__ == "__main__":
        
    whitelists = getWhitelist() 
    
    print "****begin to process email****"
    readEmail()
        
