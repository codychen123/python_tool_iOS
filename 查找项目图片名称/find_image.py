#!/usr/bin/python
# -*- coding: utf-8 -*-

import xlrd
import os
import re
import sys

f2 = open('find_image.txt','w+', encoding='utf-8')
DESPATH = sys.path[0]

def find_image(path):
	f1 = open(path,'r')
	infos = f1.readlines()
	for line in infos:
		line = str(line)
		# print(line.strip())
		if 'imageNamed:' in line:
			# print(line)
			matchList = re.findall(u'imageNamed:.*?"]', line)
			if matchList:
				line = matchList[0]
				line = line.replace('imageNamed:@"', '')
				line = line.replace('"]', '')
				print(line)
				f2.write(line + '\n')
	f1.close()
	# f2.close()
	# os.remove('chagne_text.txt')
	# os.rename('chagne_text_1.txt', 'chagne_text.txt')

def findFromFile(path):
    paths = os.listdir(path)
    for aCompent in paths:
        aPath = os.path.join(path, aCompent)
        if os.path.isdir(aPath):
            findFromFile(aPath)
        elif os.path.isfile(aPath) and os.path.splitext(aPath)[1]=='.m':
            find_image(aPath)


findFromFile(DESPATH)
