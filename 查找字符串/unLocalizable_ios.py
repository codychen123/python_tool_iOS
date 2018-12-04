# coding=utf-8
# 这是一个查找项目中未国际化的脚本

import os
import re

# 汉语写入文件时需要
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import json
import requests

url = "http://fanyi.baidu.com/basetrans"

headers = {"Content-Type": "application/x-www-form-urlencoded",
"User-Agent" : "Mozilla/5.0(Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, likeGecko) Chrome/63.0.3239.84 Mobile Safari/537.36;"}


def fanyi(str):
    data = {"query": str, "from": "zh", "to": "jp"}
    r = requests.post(url, data = data, headers = headers)
    json_response = r.content.decode()
    json_response = json.loads(json_response)
    #print(json_response['trans'])
    return json_response['trans'][0]['dst']

# 将要解析的项目名称
DESPATH = sys.path[0]

# 解析结果存放的路径
WDESPATH = sys.path[0] + "/unlocalized.log"

WDESPATH2 = sys.path[0] + "/result.log"

DESPATH3 = sys.path[0] + "/strings.xml"

DESPATH4 = sys.path[0] + "/ULUserInfoHeaderUserInfoView.m"

#目录黑名单，这个目录下所有的文件将被忽略
BLACKDIRLIST = [
                #DESPATH + '/Classes/Personal/PERSetting/PERAccount', # 多级目录
                DESPATH + '/Pods', # Utils 下所有的文件将被忽略
                DESPATH + '/Document', # Utils 下所有的文件将被忽略
                DESPATH + '/UXLive/OpenSource',
                DESPATH + '/UXLive/ULResource'
                ]

# 输出分隔符
SEPREATE = ' <=> '

def isInBlackList(filePath):
    if os.path.isfile(filePath):
        return fileNameAtPath(filePath) in BLACKDIRLIST
    if filePath:
        return filePath in BLACKDIRLIST
    return False

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

def unlocalizedStrs(filePath):
    filePath2 = filePath + 'zzz'
    f = open(filePath)
    f2 = open(filePath2, 'w+')
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
            f2.write(line)
            continue
        
        #单行注释
        if isSignalNote(line2):
            f2.write(line)
            continue
        
        #打印信息
        if isLogMsg(line2):
            f2.write(line)
            continue
    
        matchList = re.findall(u'@"[\u4e00-\u9fff].*?"|@"[0-9|A-Z|a-z| ]+[\u4e00-\u9fff].*?"', line.decode('utf-8'))
        if matchList:
            if not isHaveWriteFileName:
                wf.write('\n' + fileName + '\n')
                print(fileName)
                isHaveWriteFileName = True
                count = count + 1
            #new_matchList = matchList(set(matchList))
            
            for item in matchList:
                
                #item = item.replace('>', '')
                #item = item.replace('<', '')
                #if len(item) > 0:
                    #newstring = fanyi(item);
                    
                    #wf.write(str(index + 1) + ':' + item + SEPREATE + line + '\n')
                    #result = '"' + item + '"' + ' = ' + '"' + newstring + '"' + ';' + '\n'
                    #s.add(result)
                    #print(result)
                
                newstring = 'ULString(' + item + ')'
                line = line.replace('ULString(ULString(' + item + '))', newstring);
                line = line.replace(item ,newstring)
                line = line.replace('ULString(ULString(' + item + '))', newstring);
                    #if 'ULString(ULString(' in line:
                    #line = line.replace('ULString(ULString(', 'ULString(', 1)
                    #line = line.replace('"))', '")', 1)
                print(newstring)
        f2.write(line)
    f2.close()

    os.remove(filePath)
    os.rename(filePath2,filePath)
    print('count'+ str(count))

#replace(filePath, item, newstring, index)

#print('fileCount:' + (count));

def delete2(filePath):
    f = open(filePath)
    fileName = fileNameAtPath(filePath)
    isMutliNote = False
    isHaveWriteFileName = False
    count = 0;
    for index, line in enumerate(f):
        #多行注释
        line = line.strip()
        if '/*' in line:
            isMutliNote = True
        if '*/' in line:
            isMutliNote = False
        if isMutliNote:
            continue
        
        #单行注释
        if isSignalNote(line):
            continue
        
        #打印信息
        if isLogMsg(line):
            continue
        try:
            matchList = re.findall(u'ULString(ULString(@".*[\u4e00-\u9fff].*?))', line.decode('utf-8'))
            if matchList:
                if not isHaveWriteFileName:
                    wf.write('\n' + fileName + '\n')
                    print(fileName)
                    isHaveWriteFileName = True
                    count = count + 1
                #new_matchList = matchList(set(matchList))
                
                for item in matchList:
                    oldstring = item;
                    item = item.replace('ULString(ULString(', 'ULString(')
                    item = item.replace('))', ')')
                    #if len(item) > 0:
                    #newstring = fanyi(item);
                    
                    #wf.write(str(index + 1) + ':' + item + SEPREATE + line + '\n')
                    #result = '"' + item + '"' + ' = ' + '"' + newstring + '"' + ';' + '\n'
                    #s.add(result)
                    #print(result)
                    newstring = item
                    print(newstring)
                    replace(filePath+'"2"', oldstring, newstring, index)
        except Exception,e:
            print e

#print('fileCount:' + str(count));

def replace(file_path, old_str, new_str, index):
    print(file_path)
    try:
        f = open(file_path,'a+')
        all_lines = f.readlines()
        f.seek(0)
        f.truncate()
        i = 0
        for line in all_lines:
            #if i == index:
            line = line.replace(old_str, new_str)
            f.write(line)
                #i = i + 1
        f.close()
    except Exception,e:
        print e

def findFromFile(path):
    paths = os.listdir(path)
    for aCompent in paths:
        aPath = os.path.join(path, aCompent)
        if isInBlackList(aPath):
            print('在黑名单中，被自动忽略' + aPath)
            continue
        if os.path.isdir(aPath):
            findFromFile(aPath)
        elif os.path.isfile(aPath) and os.path.splitext(aPath)[1]=='.m':
            unlocalizedStrs(aPath)
#delete2(aPath)

if __name__ == '__main__':
    s = set()
    wf = open(WDESPATH, 'w+')
    wf2 = open(WDESPATH2, 'w+')
    findFromFile(DESPATH)
    
    for item in s:
        wf2.write(item)
    
    wf.close()
    wf2.close()

