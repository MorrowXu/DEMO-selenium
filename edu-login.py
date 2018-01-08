# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Author: Morrow
from selenium import webdriver
from PIL import Image,ImageEnhance
import os
import time
# import urllib
import pytesseract
if 'HTTP_PROXY' in os.environ: del os.environ['HTTP_PROXY'] # 取消http代理
login_dict = {'url':'http://xueli.xjtudlc.com/login1.aspx',
			  'username':'117093943010052',
			  'password':'xuhaoran123ufo'}


def code_ocr(pic_filename):
	'''
		本函数识别传入图片中的验证码,确保传入的参数为绝对路径
	'''
	img = Image.open(pic_filename) # 按路径打开图片
	img = img.convert('L') # 图片二值化/灰度加强
	img_ehc = ImageEnhance.Contrast(img) # 对比度增强
	img_ehc = img_ehc.enhance(3.5)
	v_code = pytesseract.image_to_string(img_ehc)
	verifycode = ''
	for i in v_code:
		# 对tesseract.exe引擎识别出来的字符串进行判断,如果不为字母或数字则不进入统计
		if i.isalpha() or i.isdigit():
			verifycode += i
	return verifycode


def autologin():
	'''
		利用selenium中webdriver驱动启动浏览器
	'''
	dr = webdriver.Firefox()
	# dr.set_window_size(400,450)
	dr.get(login_dict['url'])
	error_num = 1
	while True:
		time.sleep(3)
		txtUserName = dr.find_element_by_id('txtUserName')
		txtUserName.clear()
		txtUserName.send_keys(login_dict['username'])
		time.sleep(1)
		txtPassword = dr.find_element_by_id('txtPassword')
		txtPassword.clear()
		txtPassword.send_keys(login_dict['password'])
		# dr.find_element_by_xpath('//*[@id="form1"]/ul/li[3]/a').click() # 刷新一次验证码确保识别的验证码没过期
		time.sleep(1)	

		# ...........................验证码识别...........................
		# pic_code = dr.find_element_by_xpath('//*[@id="VerifyCode"]')
		# pic_link = pic_code.get_attribute('src')
		# response = urllib.urlretrieve(pic_link,'yzm.jpg') # 网页上抓取验证码图片
		pic_filename = 'C:\\Users\\Administrator\\Desktop\\screen_shot.png'
		dr.get_screenshot_as_file(pic_filename) # 截浏览器整图
		img1 = Image.open(pic_filename)
		box = (780,236,864,256)  # box(left, upper, right, lower)
		verifycode_pic = img1.crop(box)
		verifycode_pic.save('verifycode.png')

		the_verifycode = code_ocr('verifycode.png')
		txtVerifyCode = dr.find_element_by_id('txtVerifyCode')
		txtVerifyCode.clear()
		txtVerifyCode.send_keys(the_verifycode)
		time.sleep(1)
		# ----------------------------------------------------------------

		btnlogin = dr.find_element_by_id('lbtnLogin')
		btnlogin.click()
		try:
			dr.find_element_by_xpath('//*[@id="mainFrame"]') # 如果登陆成功会打破循环进入下一步
			print '尝试%d次登录成功' % error_num
			break
		except Exception as e:
			print '失败%d次,错误代码:' % error_num, e
			error_num += 1
			_alert = dr.switch_to_alert()
			_alert.accept() # 如果登陆失败会循环再来一次

	input()
	w1 = dr.find_element_by_xpath('//*[@id="mainFrame"]') 
	# 由于网页结构为frameset/frame,所以需要定位到该frame下,并switch_to.      frame需要切/frameset不需要切
	dr.switch_to.frame(w1) # 切换到该frameset下	

	ic = dr.find_element_by_xpath('//*[@id="InCourse"]') # 重新对页面元素进行定位
	ic.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_\
		StudentCourseList1_dlInCourse_ctl01_HyperLink3"]').click()   # \为续行符	

	dr.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_\
		CourseIndex2_ctl01_dlCourseware_ctl01_HyperLink3"]').click() # \为续行符	

	# next: 解决窗口焦点句柄切换问题
	all_handles = dr.window_handles # 获得所有窗口句柄
	dr.switch_to_window(all_handles[-1]) # 切换窗口焦点句柄到最后一个页面	
	input()
	# next: 解决弹出警报处理 ;未完

if __name__ == '__main__':
	autologin()
