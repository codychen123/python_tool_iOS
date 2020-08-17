# coding=utf-8

import os
import re

# 汉语写入文件时需要
import sys
import json
import requests
import shutil

image_name_list = []
image_name_copy_list = []
# 要搜索的路径
find_image_path = 'UXLive/ULShareFeatures/ULGroup'
# 主工程图片路径
# find_main_project_image_path = 'UXLive/ULResource'

# 将要解析的项目名称
DESPATH = sys.path[0]
IMAGE_RESOURCE_PATH = sys.path[0] + "/UXLive/ULResource"
# RESULT_IMAGE_PATH = sys.path[0] + "/UXLive/ULShareFeatures/ULLive/Resource/ULLiveRoomPng.xcassets";
RESULT_IMAGE_PATH = ''

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
		# if 'image' in line:
			# addImageNameToList(line)
		# elif 'ImageNormalName' in line:
		# 	addImageNameToList(line)

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

def moveImageToPath():
	image_name_copy_list = image_name_list
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
			# 对比图片是否带参数，如果带参数，剔除参数，进行模糊匹配
			if '%' in imageName:
				new_imageName_list = re.findall('[a-z|A-Z].*%', imageName)
				for new_imageName in new_imageName_list:
					new_imageName = new_imageName.replace('%', '')
					# 匹配以这个名字开头的图片
					new_imageName_1 = '/' + new_imageName
					if new_imageName_1 in aPath:
						print('iamgeName_1 = %s, path = %s'%(new_imageName_1, aPath))
					else:
						# print('iamgeName = %s, path = %s'%(new_imageName_1, aPath))
						findImageAssetsPath(new_imageName, aPath)
					break
			else:
				# 对比文件夹名字是否相等
				imageName_1 = '/' + imageName
				if imageName_1 in aPath:
					# print('iamgeName = %s, path = %s'%(imageName_1, aPath))
					# print(new_path)
					if '.imageset' in imageName:
						# 如果名称全部匹配,例如/rules_of_the_background.imageset，说明此路径存在，可以直接移动
						new_path = RESULT_IMAGE_PATH + '/%s'%(imageName)
						# new_path = RESULT_IMAGE_PATH
						print('old = %s, new = %s'%(aPath, new_path))
						# 判断是否为空文件夹
						if not os.listdir(aPath):
							# print(aPath)
							shutil.rmtree(aPath)
						else:
							shutil.move(aPath, new_path)
							shutil.rmtree(aPath, ignore_errors = True)
						if imageName in image_name_copy_list:
							image_name_copy_list.remove(imageName)
						break
					else:
						# 如果名称匹配不全，例如avatark_animate_ ,实际为avatark_animate_11.imageset, 进行模糊匹配，规则：参数+数字,然后对比
						imageName_list = re.findall('%s.*imageset'%imageName_1, aPath)
						for imageName_2 in imageName_list:
							imageName_result = imageName_2.replace(imageName_1, '')
							imageName_result = imageName_result.replace('.imageset', '')
							# 如果剩下来的只有数字，匹配成功，否则匹配失败
							if imageName_result.isdigit():
								# print(imageName_2)
								new_path = RESULT_IMAGE_PATH + imageName_2
								# new_path = RESULT_IMAGE_PATH
								print('old = %s, new = %s'%(aPath, new_path))
							# 判断是否为空文件夹
								if not os.listdir(aPath):
									print(aPath)
									shutil.rmtree(aPath)
								else:
									shutil.move(aPath, new_path)
									shutil.rmtree(aPath, ignore_errors = True)
								if imageName in image_name_copy_list:
									image_name_copy_list.remove(imageName)
							else:
								findImageAssetsPath(imageName, aPath)
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

# 找出模块的资源路径
def findAssetsFromFile(path):
	paths = os.listdir(path)
	for aCompent in paths:
		aPath = os.path.join(path, aCompent)
		if os.path.isdir(aPath):
			if '.xcassets' in aPath:
				global RESULT_IMAGE_PATH
				RESULT_IMAGE_PATH = aPath
				print(RESULT_IMAGE_PATH)
				break
			else:
				findAssetsFromFile(aPath)

if __name__ == '__main__':
	os.chdir(find_image_path)
	now_path = os.getcwd()
	findAssetsFromFile(now_path)
	findFromFile(now_path)

	moveImageToPath()
	print('剩余未移除的列表/n%s'%image_name_copy_list)
