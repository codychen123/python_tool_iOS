# coding=utf-8
# 这是一个查找项目中未国际化的脚本

import os
import re

# 汉语写入文件时需要
import sys
import json
import requests
import shutil

image_name_list = []
string_name_list = []
# 要搜索的路径
find_image_path = 'UXLive/ULShareFeatures'
# 主工程图片路径
# find_main_project_image_path = 'UXLive/ULResource'

# 将要解析的项目名称
DESPATH = sys.path[0]
IMAGE_RESOURCE_PATH = sys.path[0] + "/UXLive/ULResource"
RESULT_IMAGE_PATH = sys.path[0] + "/UXLive/ULShareFeatures/ULLive/Resource/ULLiveRoomPng.xcassets";

sharefeature_f = open('sharefeature.txt', 'w')
pika_now_f = open('pika_now.txt', 'r')
pika_now_text = pika_now_f.readlines()

# 解析结果存放的路径

WDESPATH2 = sys.path[0] + "/result.log"

DESPATH3 = sys.path[0] + "/strings.xml"

# 输出分隔符
SEPREATE = ' <=> '

def fileNameAtPath(filePath):
    return os.path.split(filePath)[1]

def isSignalNote(str):
    if '//' in str:
        return True
    if str.startswith('#pragma'):
        return True
    return False

def isLogMsg(str):
    if str.startswith('NSLog') or str.startswith('FLOG') or str.startswith('ULLog') or str.startswith('ULDebugLog') or str.startswith('ULPFunctionLog') or str.startswith('ULHttpLog') or str.startswith('ULLiveIMLog') or str.startswith('ULImageTimeLog') or str.startswith('ULPingNetLog') or str.startswith('ULMicLog') or str.startswith('ULLiveIMLog') or str.startswith('ULLiveIMLog') or str.startswith('ULVirtualModelLog'):
        return True
    return False

def isInvalidLine(str):
	if str.startswith('#i') or str.startswith('@') or str.startswith('+') or str.startswith('-') or str.startswith('}'):
		return True
	return False

# 找出所有图片资源的名字
def findImageName(filePath):
	f = open(filePath)
	fileName = fileNameAtPath(filePath)
	isMutliNote = False
	isHaveWriteFileName = False
	count = 0;
	for index, line in enumerate(f):
        #多行注释
		line2 = line.strip()
		if '/*' in line:
			isMutliNote = True
		if '*/' in line:
			isMutliNote = False
		if isMutliNote:
			continue
        
        #单行注释
		if isSignalNote(line2):
			continue
        
        #打印信息
		if isLogMsg(line2):
			continue

		#过滤无效行
		if isInvalidLine(line2):
			continue
		# print(line)
		# if 'imageNamed' in line:
		addImageNameToList(line2)
		# elif 'ImageNormalName' in line:
		# 	addImageNameToList(line)

def addImageNameToList(str):
	# matchList = re.findall('@".*?"', str)
	matchList = re.findall(u'@"[\u4e00-\u9fff].*?"|@"[0-9|A-Z|a-z| |%@]+[\u4e00-\u9fff].*?"', str)
	if matchList:
		for match_str in matchList:
			match_str = match_str.replace('@', '')
			if match_str not in image_name_list:
				image_name_list.append(match_str)
				match_str = match_str + ' = "";'
				if match_str not in string_name_list:
						string_name_list.append(match_str)

def moveImageToPath():
	for image_name in image_name_list:
		try:
			findImageAssetsPath(image_name, IMAGE_RESOURCE_PATH)
		except Exception as err:
			raise(err)

def findImageAssetsPath(imageName, imagePath):
	paths = os.listdir(imagePath)
	for aCompent in paths:
		aPath = os.path.join(imagePath, aCompent)
		if os.path.isdir(aPath):
			# 对比文件夹名字是否相等
			if imageName in aPath:
				print(aPath)
				new_path = RESULT_IMAGE_PATH + '/%s'%(imageName)
				print(new_path)
				shutil.move(aPath, new_path)
				break
			else:
				findImageAssetsPath(imageName, aPath)



def findFromFile(path):
	paths = os.listdir(path)
	for aCompent in paths:
		aPath = os.path.join(path, aCompent)
		if os.path.isdir(aPath):
			findFromFile(aPath)
		elif os.path.isfile(aPath) and os.path.splitext(aPath)[1]=='.m':
			findImageName(aPath)
		elif os.path.isfile(aPath) and os.path.splitext(aPath)[1]=='.h':
			findImageName(aPath)

if __name__ == '__main__':
	os.chdir(find_image_path)
	now_path = os.getcwd()
	findFromFile(now_path)
	for match_str in image_name_list:
		for line in pika_now_text:
			if match_str in line:
				match_str = match_str + ' = "";'
				print(match_str)
				string_name_list.remove(match_str)
				break
	for match_str in string_name_list:
		sharefeature_f.write(match_str + '\n')
	sharefeature_f.close()
