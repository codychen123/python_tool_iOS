#!/usr/bin/python
# -*- coding: utf-8 -*-

import xlrd
import os
import re

# precommit = open('chagne_text.txt', 'r')

# worksheet = xlrd.open_workbook('文案修改20181122.xlsx')   #打开excel文件
# sheet_names= worksheet.sheet_names()    #获取excel中所有工作表名
# sheet2 = worksheet.sheet_by_name('工作表1')    #根据Sheet名获取数据

# rowNum = sheet2.nrows  # sheet行数
# colNum = sheet2.ncols  # sheet列数

def alter(file,old_str,new_str):
	f1 = open(file,'r', encoding='utf-8')
	f2 = open('chagne_text_1.txt','w+', encoding='utf-8')
	infos = f1.readlines()
	for line in infos:
		# print(line.strip())
		line1 = line.strip()
		if old_str in line1:
			line_new = line1.replace(old_str,new_str)
			f2.write(line_new + '\n')
			# print(line)
			# print(old_str)
		else:
			f2.write(line1 + '\n')
			# print(line1)
	f1.close()
	f2.close()
	os.remove('chagne_text.txt')
	os.rename('chagne_text_1.txt', 'chagne_text.txt')


def getExcelContent():
	f1 = open('chagne_text.txt','r', encoding='utf-8')
	# f2 = open('chagne_text_1.txt','w+', encoding='utf-8')
	infos = f1.readlines()
	row = 0;
	for line in infos:
		row += 1;
		if '";' in line:
			row = row;
		else:
			print(row)
	f1.close()
	# os.remove('chagne_text.txt')
	# os.rename('chagne_text_1.txt', 'chagne_text.txt')
	
		# print('第%s行内容：%s, 翻译后: %s' % (i, content, change_content))
	# alter('chagne_text.txt', content, change_content)

def getNewLine(line):
	line_new = line
	# 获取所有单元格的内容
	for i in range(rowNum):
		content = sheet2.cell_value(i, 1)
		change_content = sheet2.cell_value(i, 2)
		# print("content" + content)
		# print("change_content" + change_content)
		# print(line)
		if content in line:
			# print(content)
			line_new = line.replace(content, change_content)
			#print(line_new + '\n')
			return line_new
			# return line_new
	return line_new

getExcelContent()


