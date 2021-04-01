# coding=utf-8

import os
import re
import sys
from pypinyin import slug, Style
import shutil

# 要搜索的路径，更换路径即可
find_str_path = 'UXLive/ULShareFeatures/ULFaceAssemble'

# 白名单内文件不做检索
file_white_list = ['ULCoreBaseDef.h','ULSpecialFontDownloadItem.m','ULColumnDetailModel.m','ULWechatProxy.m','ULContentDef.h','ULDownloader.m','ULScreenShotManager.h','ULLiveGiftForLottieDownLoadManager.m','Signature.h','rc4.h','ExpressionDetector.m','WBMediaCfg.m','ULFaceAssembleManager.m','UXCharacterUpdater.m','UXCharacterAVGCache.m','ULFaceAssembleDownloaderManager.m']
# 未抽成国际化的文案
string_name_list = set()
# 国际化文案头部 ULString
string_name_head = ''
# 国际化文案头部引用文件，路径
string_name_import_head = ''
string_name_import_head_filepath = ''
# 组件bundle Localizable文件路径
string_bundle_path_list = []
# 国际化文案新增,k->"ULAudioStringtiaohuifu",v->"条回复"
string_key_list_add = {}
# bundle Localizable文件内容,k->"ULAudioStringtiaohuifu",v->"条回复",k->"条回复",v->"ULAudioStringtiaohuifu"
bundle_data_dict = {}

def fileNameAtPath(filePath):
    return os.path.split(filePath)[1]

def is_signal_note(str):
    if '//' in str:
        return True
    if str.startswith('#pragma'):
        return True
    return False

def is_log_msg(str):
    if str.startswith('NSLog') or str.startswith('FLOG') or str.startswith('ULLog') or str.startswith('ULDebugLog') or str.startswith('ULPFunctionLog') or str.startswith('ULHttpLog') or str.startswith('ULLiveIMLog') or str.startswith('ULImageTimeLog') or str.startswith('ULPingNetLog') or str.startswith('ULMicLog') or str.startswith('ULLiveIMLog') or str.startswith('ULLiveIMLog') or str.startswith('ULVirtualModelLog') or 'NSAssert' in str or '@"获取苹果商品信息失败"' in str or '"购买苹果商品失败' in str or '@param ' in str or 'ULFaceAssembleLog' in str:
        return True
    return False

def is_invalid_line(str):
	if str.startswith('#i') or str.startswith('+') or str.startswith('-') or str.startswith('}'):
		return True
	return False

# 找出未翻译成key的字符串
def find_str(filePath):
	file_data_list = []
	has_import_string_head = False
	need_import_string_head = False
	import_string_line_index = 0
	with open(filePath, 'r') as f:
		for index, line in enumerate(f):
			line2 = line.strip()
			# 判断有没有引入字符串头文件
			if string_name_import_head in line:
				has_import_string_head = True
			elif '#import' in line:
				import_string_line_index = index
			# 单行注释、打印信息、过滤无效行
			if '/*' in line or '*/' in line or is_signal_note(line2) or is_log_msg(line2) or is_invalid_line(line2):
				file_data_list.append(line)
				continue
			matchList = re.findall(u'@"[\u4e00-\u9fff].*?"[); ,\]]|@"[0-9|A-Z|a-z| |%@]+[\u4e00-\u9fff].*?"[); ,\]]|@"[#《》&~()*\[]+.*[\u4e00-\u9fff].*?"[); ,\]]', line2)
			if matchList:
				need_import_string_head = True
				for match_str in matchList:
					match_str = str(match_str).strip(')').strip(';').strip('\]').strip(',').strip()
					match_str_no_at = str(match_str).strip('@')
					trans_str = get_correct_trans_str(match_str_no_at)
					# 已经替换过了，但是没有抽出来key
					if string_name_head + '(' + match_str + ')' in line2:
						line = line.replace(match_str, trans_str)
					# ulstring
					elif 'ULString' + '(' + match_str + ')' in line2:
						line = line.replace('ULString' + '(' + match_str + ')', string_name_head + '(' + trans_str + ')')
					else:
						line = line.replace(match_str, string_name_head + '(' + trans_str + ')')
			file_data_list.append(line)
	# 检查是否需要导入stringkey文件
	if need_import_string_head and not has_import_string_head:
		import_line = '#import' + ' "' + string_name_import_head + '"' + '\n'
		file_data_list.insert(import_string_line_index + 1, import_line)
	if need_import_string_head:
		with open(filePath, 'w') as f:
			for line in file_data_list:
				f.write(line)


def get_correct_trans_str(match_str):
	# 检查这个key是否已经在国际化文件里了
	trans_res_str = ''
	if match_str in bundle_data_dict.keys():
		trans_res_str = 'k' + str(bundle_data_dict.get(match_str)).strip('"')
	else:
		# 添加到string key
		trans_pinyin_str = slug(match_str, errors='ignore', separator='')
		# 3PH+英文/拼音概括（3代表占位符个数3个，依次类推）
		ph_num = str(match_str).count('%@')
		if ph_num > 0:
			trans_pinyin_str = str(ph_num) + 'PH' + trans_pinyin_str
		if len(trans_pinyin_str) > 50 - len(string_name_head):
			trans_pinyin_str = trans_pinyin_str[0:50 - len(string_name_head)]
		trans_res_str = '"' + string_name_head + trans_pinyin_str + '"'
		index = 0
		while (trans_res_str in bundle_data_dict.keys()):
			index += 1
			trans_res_str = '"' + string_name_head + trans_pinyin_str + str(index) + '"'
		bundle_data_dict[trans_res_str] = match_str
		bundle_data_dict[match_str] = trans_res_str
		string_key_list_add[trans_res_str] = match_str
		trans_res_str = 'k' + trans_res_str.strip('"')

	string_name_list.add(match_str)
	return trans_res_str

def find_file(path):
	paths = os.listdir(path)
	for aCompent in paths:
		aPath = os.path.join(path, aCompent)
		if os.path.isdir(aPath):
			find_file(aPath)
		elif os.path.isfile(aPath) and (os.path.splitext(aPath)[1]=='.m' or os.path.splitext(aPath)[1]=='.h') and aPath.split('/')[-1] not in file_white_list:
			find_str(aPath)

def config_data(path):
	paths = os.listdir(path)
	for aCompent in paths:
		aPath = os.path.join(path, aCompent)
		if os.path.isdir(aPath):
			config_data(aPath)
		if os.path.isfile(aPath) and os.path.splitext(aPath)[1] == '.h':
			# config ulstring名字
			if len(string_name_head) <= 0 and ('Config' in aPath or 'String' in aPath):
				get_file_string_head(aPath)
			# config stringkey文件信息
			if len(string_name_import_head_filepath) <= 0 and ('StringKeyDef.h' in aPath):
				get_string_key_data(aPath)
		elif 'Localizable.strings' in aPath and ('String.bundle' in path or 'Setting.bundle' in path):
			get_bundle_path(aPath)

def get_bundle_path(path):
	string_bundle_path_list.append(path)
	if 'KilaRes' in path and ('String.bundle' in path or 'Setting.bundle' in path):
		# 以克拉为准构造dict
		with open(path, 'r', encoding='utf-16') as f:
			for line in f.readlines():
				if '=' in line:
					res_list = re.findall('".*?"', line)
					if bundle_data_dict.get(res_list[0]) == None:
						bundle_data_dict[res_list[0]] = res_list[1]
					if bundle_data_dict.get(res_list[1]) == None:
						bundle_data_dict[res_list[1]] = res_list[0]

def get_string_key_data(path):
	global string_name_import_head_filepath
	string_name_import_head_filepath = path

def get_file_string_head(path):
	with open(path, 'r') as f:
		for line in f.readlines():
			if 'ULLocalizedStringFormBundle(' in line:
				res_list = line.split(' ')
				global string_name_head
				string_name_head = res_list[1].replace('(x)','')
				global string_name_import_head
				string_name_import_head = path.split('/')[-1]
				break;

def add_string_to_file():
	if len(string_key_list_add.keys()) > 0:
		file_data_list = []
		right_index = 0
		with open(string_name_import_head_filepath, 'r') as f:
			for index, line in enumerate(f):
				if 'static NSString *const' in line:
					right_index = index
				file_data_list.append(line)
		for key,value in string_key_list_add.items():
			line = 'static NSString *const k' + str(key).strip('"') + ' = ' + '@' + key + ';' + '\n'
			file_data_list.insert(right_index + 1, line)

		with open(string_name_import_head_filepath, 'w') as f:
			for line in file_data_list:
				f.write(line)

def add_string_to_bundle():
	if len(string_key_list_add.keys()) > 0:
		for path in string_bundle_path_list:
			with open(path, 'a', encoding='utf-16') as f:
				for key, value in string_key_list_add.items():
					line = key + ' = ' +  value + ';' + '\n'
					f.write(line)

def deal_with_new_key():
	add_string_to_file()
	add_string_to_bundle()

if __name__ == '__main__':
	os.chdir(find_str_path)
	now_path = os.getcwd()
	# 初始化需要操作的
	config_data(now_path)
	find_file(now_path)
	deal_with_new_key()
	print(string_name_list)

