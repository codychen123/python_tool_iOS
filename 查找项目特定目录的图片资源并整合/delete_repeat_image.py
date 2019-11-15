# coding=utf-8

import os
import re

# 汉语写入文件时需要
import sys
import json
import requests
import shutil

image_name_list = []
# 要搜索的路径
find_image_path = 'UXLive/ULShareFeatures'
# 主工程图片路径
# find_main_project_image_path = 'UXLive/ULResource'
repeat_image_list = []

# 将要解析的项目名称
DESPATH = sys.path[0]
IMAGE_RESOURCE_PATH = sys.path[0] + "/UXLive/ULResource"
# RESULT_IMAGE_PATH = sys.path[0] + "/UXLive/ULShareFeatures/ULLive/Resource/ULLiveRoomPng.xcassets";
RESULT_IMAGE_PATH = ''

# 输出分隔符
SEPREATE = ' <=> '

def findImageAssetsPath(imagePath):
	paths = os.listdir(imagePath)
	for aCompent in paths:
		aPath = os.path.join(imagePath, aCompent)
		if os.path.isdir(aPath):
			if '.imageset' in aPath:
				xcassets = '.xcassets'
				if 'cn' in aPath:
					xcassets = '.xcassets/cn'
				elif 'jp' in aPath:
					xcassets = '.xcassets/jp'
				pattern = '%s/.*.imageset'%(xcassets)
				image_result_list = re.findall(pattern, aPath)
				for image_result in image_result_list:
#                    print(aPath)
					image_result = image_result.replace('%s/'%(xcassets), '')
					if image_result not in repeat_image_list:
						repeat_image_list.append(image_result)
			else:
				findImageAssetsPath(aPath)


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
			if '.xcassets' in aPath:
				# 把图片资源记录，稍后在主工程删除对应的图片
				findImageAssetsPath(aPath)
			else:
				findAssetsImageNameFromFile(aPath)

# 删除重名图片
def deleteRepeatImage():
	for repeat_image_name in repeat_image_list:
		deleteRepeatImageAtPath(repeat_image_name, IMAGE_RESOURCE_PATH)

def deleteRepeatImageAtPath(repeat_image_name, path):
	paths = os.listdir(path)
	for aCompent in paths:
		aPath = os.path.join(path, aCompent)
		if os.path.isdir(aPath):
			if '/%s'%(repeat_image_name) in aPath:
				print('repeat_image_name=%s, aPath=%s'%(repeat_image_name, aPath))
				shutil.rmtree(aPath, ignore_errors = True)
				break
			else:
				deleteRepeatImageAtPath(repeat_image_name, aPath)

if __name__ == '__main__':
	os.chdir(find_image_path)
	now_path = os.getcwd()
	findAssetsImageNameFromFile(now_path)
	# 去主工程删除重名的图片
	deleteRepeatImage()
