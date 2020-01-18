# coding=utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
import time
import datetime
from bs4 import BeautifulSoup
import requests
import json
import zipfile
import os
import shutil
import sys
import getopt

# 账户信息 
username = ""
password = ""
# 网站信息
aliyun_login_url = 'https://signin.aliyun.com/login.htm'
# 阿里云存储日志的列表
aliyun_get_zipList_url = 'https://oss.console.aliyun.com/ajax/bucket/file/list_objects.json?_cacheBusting=1545129931470&bucket=klive-jp-res&region=oss-ap-northeast-1&maxKeys=100'
aliyun_get_zip_download_url = 'http://klive-jp-res.oss-ap-northeast-1.aliyuncs.com'
# http://uxin-zb-picture.oss-cn-shenzhen.aliyuncs.com
# https://oss.console.aliyun.com/ajax/bucket/file/list_objects.json?_cacheBusting=1545206862812&bucket=uxin-zb-picture&region=oss-cn-shenzhen&maxKeys=100

# roomid查询信息
pika_roomid_query_url = 'http://api.pikapika.live/api/v1/room/queryByIdForH5'
kila_roomid_query_url = 'http://api.kilakila.cn/api/v1/room/queryByIdForH5'

# 是否要拉一天的日志，如果用户没输入具体小时，那就拉一天的日志
need_load_oneDayList = False
# 拉取的时间戳差距，如果精确到分，则拉时间点左右2小时的日志，如果精确到小时，拉时间点左右5小时的日志
load_timestamp_disparity = 0
# 要查询的时间。单位秒
global query_timestamp
# 精确到小时的查询时间差，为前后2小时
query_timestamp_hour = 7200 
# 精确到分的查询时间差，为前后30分钟
query_timestamp_min = 1800

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
#根据浏览器下自行修改

headers['Cookie'] = 'gr_user_id=a11ecd75-ae49-4853-b332-6d7ef973a8d0; Hm_lvt_603ab75906557bfe372ca494468e3e1b=1523261865; Hm_lpvt_603ab75906557bfe372ca494468e3e1b=1523261944; user_id=q9A0J5Jo; user_session=a8d9a123-9644-462b-b187-2ba087e7f508; 0a1b4118dd954ec3bcc69da5138bdb96_gr_last_sent_sid_with_cs1=718060fd-2dca-44b0-9d56-1714a3b50f57; 0a1b4118dd954ec3bcc69da5138bdb96_gr_last_sent_cs1=105038; 0a1b4118dd954ec3bcc69da5138bdb96_gr_cs1=105038'
#根据浏览器F12下的Request Headers->Cookie自行复制上去即可

option = webdriver.ChromeOptions()
option.add_argument('headless')
driver = webdriver.Chrome(chrome_options=option)

def loginRRD(username, password):
    try:
        print(u'准备登陆阿里云oss...')
        driver.get(aliyun_login_url)
        # 用户输入界面
        elem_user = driver.find_element_by_id("user_principal_name")
        elem_user.send_keys(username)
        # print(elem_user)
        elem_user_click_next = driver.find_element_by_id("J_FormNext")
        elem_user_click_next.click()
        time.sleep(1)
        # 用户密码输入界面
        #password_ims
        elem_pwd = driver.find_element_by_id("password_ims")
        elem_pwd.send_keys(password)
        elem_pwd_click_next = driver.find_element_by_id("u22")
        elem_pwd_click_next.click()

        print(u'登录成功')
    except Exception as e:
        print("error")
    finally:
        print(u'sss')
    getZip()

def getZip():
	global aliyun_get_zipList_url
	requests_url = aliyun_get_zipList_url
	requests_params_value = 'app_log/%s/%s'%(user_time, user_uid)
	requests_url = requests_url + '&prefix=%s'%requests_params_value
	driver.get(requests_url)
	html = BeautifulSoup(driver.page_source,'lxml')
	result_str = html.text
	# print(requests_url)
	result_dic = json.loads(result_str)
	objectList = result_dic["data"]["objectList"]
    # print(query_timestamp)
	global load_timestamp_disparity
	global aliyun_get_zip_download_url
	i = 0
	for object_dic in objectList:
		zip_unix_time = int(object_dic["timeModified"]/1000)
		zip_name = object_dic["name"]
		zip_path = object_dic["path"]
		result_time = zip_unix_time - int(query_timestamp)
		abs_result_time = abs(result_time)
		if int(abs_result_time) < load_timestamp_disparity:
			ltime = time.localtime(zip_unix_time)
			zip_time = time.strftime("%Y-%m-%d %H:%M:%S", ltime)
			# print(load_timestamp_disparity)
			r = requests.get('%s/%s'%(aliyun_get_zip_download_url, zip_path))
			with open(zip_name, "wb") as code:
				code.write(r.content)
			now_cwd = os.getcwd()
			old_cwd = now_cwd + '/' + zip_name
			new_cwd = '%s/'%zip_time
            #解压、换名、删除zip包
			unzip_file(old_cwd, new_cwd)		
			i += 1
	print('已为你寻找到%s个log文件'%i)

        
def unzip_file(zfile_path, unzip_dir):
    f = zipfile.ZipFile(zfile_path,'r')
    for file in f.namelist():
        f.extract(file,unzip_dir)
    os.remove(zfile_path)

def getTimestamp():
    global user_time
    now_year = 0
    user_month = 1
    user_day = 1
    user_hour = 0
    user_min = 0
    # 开始分割字符串
    if user_time.startswith('201'):
        print('')
    else:
        now_time = datetime.datetime.now()
        now_year = now_time.year
        user_time = '%s-%s'%(now_year, user_time)

    if ' ' in user_time:
        data_list = user_time.split(' ')
        # 分割年月日
        user_time_to_day = data_list[0]
        user_time = user_time_to_day
        data_list_to_day = user_time_to_day.split('-')
        now_year = data_list_to_day[0]
        user_month = data_list_to_day[1]
        user_day = data_list_to_day[2]   
        # 分割时分秒
        user_time_to_second = data_list[1]
        if ':' in user_time_to_second:
            toSecond_list = user_time_to_second.split(':')
            user_hour = toSecond_list[0]
            user_min = toSecond_list[1]
        else:
            user_hour = user_time_to_second
    else:
        print('☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ️只有日期,没有小时，将为你拉取当天全部日志 ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ️')
        data_list = user_time.split('-')
        now_year = data_list[0]
        user_month = data_list[1]
        user_day = data_list[2]    

    dateC =datetime.datetime(int(now_year), int(user_month), int(user_day), int(user_hour), int(user_min))
    timestamp = time.mktime(dateC.timetuple())
    timestamp = int(timestamp)
    global load_timestamp_disparity
    if int(user_hour) == 0:
        need_load_oneDayList = True
        load_timestamp_disparity = 86400
    elif int(user_min) > 0:
        # 如果精确到分 拉取前后30分钟
        load_timestamp_disparity = query_timestamp_min
        print('☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ️将为你拉取时间点前后30分钟内的日志 ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ️')
    else:
        # 如果精确到小时 拉取前后2小时
        print('☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ️将为你拉取时间点前后2小时内的日志 ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ️')
        load_timestamp_disparity = query_timestamp_hour
    return timestamp

def deleteOldDir():
	now_cwd = os.getcwd()
	dirs = os.listdir(now_cwd)
	for dir in dirs:
		dir_path = now_cwd + '/' + dir
		if os.path.isdir(dir_path):
			shutil.rmtree(dir_path)

def beginInput():
	print("-----请输入用户uid或者房间号roomid-----")
	global user_uid
	global query_timestamp
	global user_time
	global load_timestamp_disparity
	user_uid = input()
	user_uid_lenth = len(user_uid)
	if user_uid_lenth == 19:
		# roomid
		r = requests.get('%s?roomId=%s'%(pika_roomid_query_url, user_uid))
		result_dic = json.loads(r.text)
		if result_dic["h"]["code"] == 200:
			print('☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ 请求房间信息成功！☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆')
			print('准备拉取该时间点日志...')
			user_uid = result_dic["b"]["uid"]
			query_timestamp = result_dic["b"]["liveStartTime"]/1000
			ltime = time.localtime(query_timestamp)
			user_time = time.strftime("%Y-%m-%d", ltime)
			user_time_start = time.strftime("%Y-%m-%d %H:%M:%S", ltime)
			load_timestamp_disparity = query_timestamp_hour
			# print('%s%s%s'%(user_uid, query_timestamp, user_time))
			print('☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ 该主播%s开播时间为%s，请查找该时间点附近的日志 ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆'%(user_uid ,user_time_start))
		else:
			print('roomid 信息有误，请确认')
			return;
	else:
		print("-----请输入日期（%Y-%m-%d %H:%M:%S格式例如: 2018-08-08,默认可以不用输入年份:08-08,如果只记得小时则输入 08-08 08）-----")
		user_time = input()
		query_timestamp = getTimestamp()
	loginRRD(username, password)	

def get_parameter():
	opts, args = getopt.getopt(sys.argv[1:], "ht:", ["help", "type="])
	for op, value in opts:
		if op in ("-h", "--help", "help"):
			print("  -t --type [0,1,0为pika日志，1为kila日志，默认为0]\n")
			sys.exit()
		elif op in ("-t", "--type"):
			if (value not in ("0","1")):
				print("ERROR:-t --type only can use 0, 1")
				sys.exit()
			elif int(value) == 1:
				print('-----已经切换到查询kila日志路线-----')
				global aliyun_get_zipList_url
				global aliyun_get_zip_download_url
				aliyun_get_zipList_url = 'https://oss.console.aliyun.com/ajax/bucket/file/list_objects.json?_cacheBusting=1545206862812&bucket=uxin-zb-picture&region=oss-cn-shenzhen&maxKeys=100'
				aliyun_get_zip_download_url = 'http://uxin-zb-picture.oss-cn-shenzhen.aliyuncs.com'



def main():
	get_parameter()
	deleteOldDir()
	beginInput()
 
if __name__ == '__main__':
    main()

