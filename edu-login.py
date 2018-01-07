# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Author: Morrow
from selenium import webdriver
from PIL import Image,ImageEnhance
import os
import time
import urllib2
import pytesseract
if 'HTTP_PROXY' in os.environ: del os.environ['HTTP_PROXY'] # 取消http代理
login_dict = {'url':'http://******/******',
			  'username':'******',
			  'password':'******'}


def code_ocr(pic_filename):
	'''
		本函数识别传入图片中的验证码,确保传入的参数为绝对路径
	'''
	img = Image.open(pic_filename) # 按路径打开图片
	img = img.convert('L') # 图片二值化/灰度加强
	img_ehc = ImageEnhance.Contrast(img) # 对比度增强
	img_ehc = img_ehc.enhance(4)
	v_code = pytesseract.image_to_string(img_ehc)
	verifycode = ''
	for i in v_code:
		# 对tesseract.exe引擎识别出来的字符串进行一个判断,如果不为字母或数字则不进入统计
		if i.isalpha() or i.isdigit():
			verifycode += i
	return verifycode


def autologin():
	'''
		利用selenium中webdriver驱动启动浏览器
	'''
	dr = webdriver.Firefox()
	# dr.set_window_size(400,450)
	time.sleep(2)
	dr.get(login_dict['url'])
	time.sleep(2)	

	txtUserName = dr.find_element_by_id('txtUserName')
	txtUserName.send_keys(login_dict['username'])
	txtPassword = dr.find_element_by_id('txtPassword')
	txtPassword.send_keys(login_dict['password'])	

	# ...........................验证码识别...........................
	pic_code = dr.find_element_by_xpath('//*[@id="VerifyCode"]')
	# ----------------------------------------------------------------
	pic_link = ''
	response = urllib2.urlopen(pic_link) # 网页上抓取验证码图片
	pic_ = response.read()
	pic_filename = 'C:\\Users\\Administrator\\Desktop\\verifycode.jpg'
	with open(pic_filename,'wb') as f:
		f.write(pic_)
	# ----------------------------------------------------------------
	the_verifycode = code_ocr(pic_filename)
	txtVerifyCode = dr.find_element_by_id('txtVerifyCode')
	txtVerifyCode.send_keys(the_verfycode)
	time.sleep(1)
	# ...........................验证码识别...........................	

	btnlogin = dr.find_element_by_id('lbtnLogin')
	btnlogin.click()	

	w1 = dr.find_element_by_xpath('//*[@id="mainFrame"]') 
	# 由于网页结构为frameset/frame,所以需要定位到该frame下,并swith_to.      frame需要切/frameset不需要切
	dr.swith_to.frame(w1) # 切换到该frameset下	

	ic = dr.find_element_by_xpath('//*[@id="InCourse"]') # 重新对页面元素进行定位
	ic.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_\
		StudentCourseList1_dlInCourse_ctl01_HyperLink3"]').click()   # \为续行符	

	dr.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_\
		CourseIndex2_ctl01_dlCourseware_ctl01_HyperLink3"]').click() # \为续行符	

	# next: 解决窗口焦点句柄切换问题
	all_handles = dr.window_handles # 获得所有窗口句柄
	dr.switch_to_window(all_handles[-1]) # 切换窗口焦点句柄到最后一个页面	

	# next: 解决弹出警报处理

