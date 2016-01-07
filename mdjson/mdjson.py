#!/usr/bin/env python
#coding:utf-8
#**************************************************
# Copyright (c) 2016. All Rights Reserved
# rdryan186@outlook.com
#**************************************************

import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# open json file to js object
filename = raw_input("please input json file:")

f = file(filename)
js = json.load(f)
f.close()

# copy js to a output json structure
jso = js

# process each category
m = 0
for category in js:
    key = category.keys()[0] #hot,new,appliances, etc
    
    if 'hot' in key:    #jump 'hot' category
        m = m+1
        continue

    obj = category[key]

    # sort the object by enddate
    obj = sorted(obj, key=lambda t:t['enddate'])

    # change the id from 0 to len-1
    for i in range(len(obj)):
        obj[i]['id'] = str(i)

    # restore the outpu json structure
    jso[m][key] = obj
    m = m+1


# output json to outfile
ofilename = "md_" + filename
fo = open(ofilename,'w')
#json.dump(jso, fo, ensure_ascii=False, indent=4)
json.dump(jso, fo, indent=4)
fo.close()

print "output file is: " + ofilename
print "json file process finished!"


