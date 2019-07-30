# coding=utf-8
import re

pika_list = []

file = open('pika_room_api.txt','w') 
# pika_file = open('pika_room_api.txt','w') 
f = open("ULHttpTimeLog.txt","r+")       # 返回一个文件对象   
lines_content = f.readlines()              		 # 调用文件的 readline()方法  
for line_content in lines_content:
	if '?' in line_content:
			# print(line_content)
			contents = re.findall('v119.*\?', line_content)
			for content in contents:
				content = content.replace('v119', '')
				content = content.replace('?', '')
				if content not in pika_list:
					pika_list.append(content)
					file.write('%s\n'%content)
	else:
			contents = re.findall('v119.* ', line_content)
			for content in contents:
				content = content.replace('v119', '')
				content = content.replace(' ', '')
				if content not in pika_list:
					pika_list.append(content)
					file.write('%s\n'%content)


# kila_contents = file.readlines()
# pika_contents = pika_file.readlines()
# for kila_content in kila_contents:
# 	print(kila_content)
	# for pika_content in pika_contents:
	# 	if kila_content == pika_content:
	# 			print('%s = %s'@(kila_content, pika_content)




f.close()
file.close()

