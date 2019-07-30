# coding=utf-8
# 这是一个查找项目中未国际化的脚本

import os
import re

# 汉语写入文件时需要
import sys
import shutil
import fileinput

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

# 解析结果存放的路径

WDESPATH2 = sys.path[0] + "/result.log"

DESPATH3 = sys.path[0] + "/strings.xml"

# 输出分隔符
SEPREATE = ' <=> '

def fileNameAtPath(filePath):
    return os.path.split(filePath)[1]

def isSignalNote(str):
	str = str.strip()
	if '//' in str:
		return True
	if str.startswith('#pragma'):
		return True
	return False

def isLogMsg(str):
	str = str.strip()
	if str.startswith('NSLog') or str.startswith('FLOG') or str.startswith('ULLog') or str.startswith('ULDebugLog') or str.startswith('ULPFunctionLog') or str.startswith('ULHttpLog') or str.startswith('ULLiveIMLog') or str.startswith('ULImageTimeLog') or str.startswith('ULPingNetLog') or str.startswith('ULMicLog') or str.startswith('ULLiveIMLog') or str.startswith('ULLiveIMLog') or str.startswith('ULVirtualModelLog'):
		return True
	return False

def isInvalidLine(str):
	str = str.strip()
	if str.startswith('#i') or str.startswith('@') or str.startswith('+') or str.startswith('-') or str.startswith('}') or str.startswith('static'):
		return True
	return False

# 找出所有图片资源的名字
def findImageName(filePath):
	fileName = fileNameAtPath(filePath)
	isMutliNote = False
	isHaveWriteFileName = False
	count = 0;
	# f = open(filePath)
	for line in fileinput.input(filePath, inplace=1):
	# for index, line in enumerate(f):
        #多行注释
		line2 = line
		if '/*' in line:
			isMutliNote = True
		if '*/' in line:
			isMutliNote = False
		if isMutliNote:
			print(line2,end = '')
			continue
        #单行注释
		if isSignalNote(line2):
			print(line2,end = '')
			continue
		#打印信息
		if isLogMsg(line2):
			print(line2,end = '')
			continue
		#过滤无效行
		if isInvalidLine(line2):
			print(line2,end = '')
			continue
		matchList = re.findall(u'@"[\u4e00-\u9fff].*?"|@"[0-9|A-Z|a-z| |%@]+[\u4e00-\u9fff].*?"', line2)
		if matchList:
			for match_str in matchList:
				new_str = 'ULString(' + match_str
				log_str = 'Log(' + match_str + ')'
				if new_str not in line2 and log_str not in line2:
					new_str = 'ULString(' + match_str + ')'
					line2 = line2.replace(match_str, new_str)	
			print(line2,end = '')
		else:
			print(line2,end = '')

def addImageNameToList(str):
	# matchList = re.findall('@".*?"', str)
	if matchList:
		for match_str in matchList:
			match_str = match_str.replace('@', '')
			if match_str not in image_name_list:
				image_name_list.append(match_str)
				match_str = match_str + ' = "";'
				if match_str not in string_name_list:
						string_name_list.append(match_str)

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
	fileinput.close()
