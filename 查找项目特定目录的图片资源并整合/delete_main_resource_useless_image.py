# coding=utf-8
# 此脚本检索主工程图片资源，未在代码中引用的，则删除
import os
import re

# 汉语写入文件时需要
import sys
import json
import requests
import shutil

image_name_list = []
# 要搜索的路径
find_image_path = 'UXLive'
# 主工程图片路径
# find_main_project_image_path = 'UXLive/ULResource'
repeat_image_list = []
useless_image_list = []

# 将要解析的项目名称
DESPATH = sys.path[0]
IMAGE_RESOURCE_PATH = sys.path[0] + "/UXLive/ULResource/ULProfilePng.xcassets"
# RESULT_IMAGE_PATH = sys.path[0] + "/UXLive/ULShareFeatures/ULLive/Resource/ULLiveRoomPng.xcassets";
RESULT_IMAGE_PATH = ''

# 输出分隔符
SEPREATE = ' <=> '

def fileNameAtPath(filePath):
    return os.path.split(filePath)[1]

def findImageAssetsPath(aPath):
	if '.imageset' in aPath:
		image_result_list = re.split('/', aPath)
		for image_result in image_result_list:
			if '.imageset' in image_result:
				image_result_new = image_result
				if image_result_new not in repeat_image_list:
					repeat_image_list.append(image_result_new)


def findFromFile(path):
    paths = os.listdir(path)
    for aCompent in paths:
        aPath = os.path.join(path, aCompent)
        if os.path.isdir(aPath):
            findFromFile(aPath)
        elif os.path.isfile(aPath) and os.path.splitext(aPath)[1]=='.m':
            findImageName(aPath)

# 找出模块的资源路径
def findAssetsImageNameFromFile(path):
	paths = os.listdir(path)
	for aCompent in paths:
		aPath = os.path.join(path, aCompent)
		if os.path.isdir(aPath):
			if '.imageset' in aPath:
				# 把图片资源记录，稍后在主工程删除对应的图片
				findImageAssetsPath(aPath)
			else:
				findAssetsImageNameFromFile(aPath)


def isSignalNote(str):
    if '//' in str:
        return True
    if str.startswith('#pragma'):
        return True
    return False

def isLogMsg(str):
    if str.startswith('NSLog') or str.startswith('FLOG') or str.startswith('ULLog') or str.startswith('ULDebugLog') or str.startswith('ULPFunctionLog') or str.startswith('ULHttpLog') or str.startswith('ULLiveIMLog') or str.startswith('ULImageTimeLog') or str.startswith('ULPingNetLog') or str.startswith('ULMicLog') or str.startswith('ULLiveIMLog') or str.startswith('ULLiveIMLog'):
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
		# print(line)

		addImageNameToList(line)

def addImageNameToList(str):
	matchList = re.findall('@"[a-z|A-Z].*?"', str)
	if matchList:
		for str in matchList:
			new_str = 'ULString(' + str + ')'
			# 过滤汉字
			if new_str in str:
				continue
			# 带空格的也过滤
			if ' ' in str:
				continue
			# 参数为lld的也过滤
			if '%lld' in str:
				continue
			if '/' in str:
				continue
			if '.' in str:
				continue
			if '=' in str:
				continue
			if '(' in str:
				continue
			str = str.replace('@"', '')
			str = str.replace('"', '')
			iamgeset_str = str + '.imageset'
			if iamgeset_str not in image_name_list:
				image_name_list.append(iamgeset_str)

# 删除重名图片
def deleteRepeatImage():
	for image_name in image_name_list:
		for repeat_image_name in repeat_image_list:
			if image_name in repeat_image_name:
				repeat_image_list.remove(repeat_image_name)
				break;
	print(repeat_image_list)
	for repeat_image_name in repeat_image_list:
		deleteRepeatImageAtPath(repeat_image_name, IMAGE_RESOURCE_PATH)

def deleteRepeatImageAtPath(repeat_image_name, path):
	paths = os.listdir(path)
	for aCompent in paths:
		aPath = os.path.join(path, aCompent)
		if os.path.isdir(aPath):
			if repeat_image_name in aPath:
				shutil.rmtree(aPath, ignore_errors = True)
				break
			else:
				deleteRepeatImageAtPath(repeat_image_name, aPath)

# 给主工程总资源目录，自动删除
def deleteRepeatImageAtMainPath(repeat_image_name, path):
	paths = os.listdir(path)
	for aCompent in paths:
		aPath = os.path.join(path, aCompent)
		if os.path.isdir(aPath):
			if '.xcassets' in aPath:
				# 把图片资源记录，稍后在主工程删除对应的图片
				deleteRepeatImageAtPath(repeat_image_name, aPath)
			else:
				deleteRepeatImageAtMainPath(repeat_image_name, aPath)

def findFromFile(path):
	paths = os.listdir(path)
	for aCompent in paths:
		aPath = os.path.join(path, aCompent)
		if os.path.isdir(aPath):
			if 'ULShareFeatures' not in aPath:
				findFromFile(aPath)
		elif os.path.isfile(aPath) and os.path.splitext(aPath)[1]=='.m':
			findImageName(aPath)

if __name__ == '__main__':
	findFromFile(find_image_path)
	os.chdir(IMAGE_RESOURCE_PATH)
	now_path = os.getcwd()
	findAssetsImageNameFromFile(now_path)
	useless_image_list = repeat_image_list.copy()

	# 去主工程删除重名的图片
	deleteRepeatImage()
	# print(repeat_image_list)
