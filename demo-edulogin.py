# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Author: Morrow
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image,ImageEnhance
import os
import time
# import urllib
import pytesseract
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
if 'HTTP_PROXY' in os.environ: del os.environ['HTTP_PROXY'] # 取消http代理
f = open('pswd.txt')
s = f.read()
url = s.split(' ')[0].split('@')[1] # 链接
username = s.split(' ')[1].split('@')[1] # 账号
password = s.split(' ')[2].split('@')[1] # 密码


def code_ocr(pic_filename):
	'''
		本函数识别传入图片中的验证码,确保传入的参数为图片路径
	'''
	img = Image.open(pic_filename) # 按路径打开图片
	img = img.convert('L') # 图片二值化/灰度加强
	img_ehc = ImageEnhance.Contrast(img) # 对比度增强
	img_ehc = img_ehc.enhance(3.5)
	v_code = pytesseract.image_to_string(img_ehc)
	verifycode = ''
	for i in v_code:
		# 对tesseract.exe引擎识别出来的字符串进行判断,如果不为字母或数字则不进入统计
		if i.isalpha() or i.isdigit(): # 遍历字符串,如果字符是字母或数字则累加
			verifycode += i
	return verifycode


def autologin():
	'''
		利用selenium中webdriver驱动启动浏览器
	'''
	dr = webdriver.Firefox()
	# dr = webdriver.Chrome()
	# dr.set_window_size(700,550)
	dr.get(url)
	error_num = 1

	while True:
		txtUserName = dr.find_element_by_id('txtUserName')
		txtUserName.clear()
		txtUserName.send_keys(username)
		time.sleep(1)
		txtPassword = dr.find_element_by_id('txtPassword')
		txtPassword.clear()
		txtPassword.send_keys(password)
		# dr.find_element_by_xpath('//*[@id="form1"]/ul/li[3]/a').click() # 刷新一次验证码确保识别的验证码没过期
		time.sleep(1)

		# ...........................验证码识别...........................
		# pic_code = dr.find_element_by_xpath('//*[@id="VerifyCode"]')
		# pic_link = pic_code.get_attribute('src')
		# response = urllib.urlretrieve(pic_link,'yzm.jpg') # 网页上抓取验证码图片
		pic_filename = 'screen_shot.png'
		dr.get_screenshot_as_file(pic_filename) # 截浏览器整图
		img1 = Image.open(pic_filename)
		box = (780,236,864,256)  # box(left, upper, right, lower)  firefox截图参数
		# box = (664,234,744,256) # chrome截图参数
		verifycode_pic = img1.crop(box)
		verifycode_pic.save('verifycode.png')
		time.sleep(1)
		the_verifycode = code_ocr('verifycode.png')
		txtVerifyCode = dr.find_element_by_id('txtVerifyCode')
		txtVerifyCode.clear()
		txtVerifyCode.send_keys(the_verifycode)
		time.sleep(1)
		# ----------------------------------------------------------------

		btnlogin = dr.find_element_by_id('lbtnLogin') # 登录
		btnlogin.click()
		try:
			login_wait = WebDriverWait(dr, 3)
			login_wait.until(lambda dr: dr.find_element_by_xpath('//*[@id="mainFrame"]').is_displayed()) # 如果登陆成功会打破循环进入下一步
			print '尝试%d次登录成功' % error_num
			break
		except Exception as e:
			print '登录失败%d次,错误代码:' % error_num, e
			error_num += 1
			_alert = dr.switch_to_alert()
			_alert.accept() # 如果登录失败会循环再来一次

	w1 = dr.find_element_by_xpath('//*[@id="mainFrame"]') 
	# 由于网页结构为frameset/frame,所以需要定位到该frame下,并switch_to.      frame需要切/frameset不需要切
	dr.switch_to.frame(w1) # 切换到该frameset下	
	ic = dr.find_element_by_xpath('//*[@id="InCourse"]') # 重新对页面元素进行定位
	ic.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_StudentCourseList1_dlInCourse_ctl02_HyperLink3"]').click()
								     # ctl00_ContentPlaceHolder1_StudentCourseList1_dlInCourse_ctl03_HyperLink3
	wait = WebDriverWait(dr, 15)
	wait.until(lambda dr: dr.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_CourseIndex2_ctl01_dlCourseware_ctl01_HyperLink3"]').is_displayed())
	# time.sleep(1)
	dr.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_CourseIndex2_ctl01_dlCourseware_ctl01_HyperLink3"]').click()
	time.sleep(3) # 切换窗口最好睡2秒不然获取不到元素卡死
	all_handles = dr.window_handles # 获得所有窗口句柄
	dr.switch_to_window(all_handles[-1]) # 切换窗口焦点句柄到最后一个页面
	wait.until(lambda dr: dr.find_element_by_xpath('/html/body/div[2]/form/table/tbody/tr/td[3]/div/div[2]/div[2]/div[1]/div[1]/p[2]/b/a').is_displayed())
	course = dr.find_element_by_xpath('/html/body/div[2]/form/table/tbody/tr/td[3]/div/div[2]/div[2]/div[1]/div[2]/p[2]/b/a')
									 # /html/body/div[2]/form/table/tbody/tr/td[3]/div/div[2]/div[2]/div[1]/div[1]/p[2]/b/a

	# --------------------视频时长--------------------------
	t = course.text[-8:] # 获取视频时长
	t_lst = t.split(':')
	time_length = int(t_lst[0]) * 60 * 60 + int(t_lst[1]) * 60 + int(t_lst[2]) + 20 # 获取的时间换算成秒+30秒的预留时间
	print '视频时长: ' + t + ' ,已设置关闭时间: ' + str(time_length) + 's'
	course.click()
	# --------------------视频时长--------------------------

	time.sleep(5) # 弹出窗口加载等待
	all_handles = dr.window_handles
	print '目前所有窗口句柄:',all_handles
	dr.switch_to_window(all_handles[-1]) # 切换窗口焦点句柄到最后一个页面
	try:
		# dr.find_element_by_xpath('/html/body/form/table/tbody/tr/td[1]/div/div[4]/input')
		dr.switch_to_alert().accept() # 接受弹出的对话框
		time.sleep(1)
		dr.switch_to_alert().accept() # 有的网页会连续弹出2个alert警告框
		print '播放页面 alert多弹了一个窗口'
	except Exception as e:
		print '播放页面 alert弹出正常'
	print '课程视频播放开始'
	time.sleep(time_length) # 按视频时长等待

	# --------------------课程打分--------------------------
	dr.find_element_by_xpath('/html/body/form/table/tbody/tr/td[1]/div/div[5]/div/table/tbody/tr[1]/td/ul/li[5]').click()
	time.sleep(2)
	button = dr.find_element_by_xpath('//*[@id="RateButton"]') # 给课程打分
	ActionChains(dr).click(button).perform() # 为什么要用actionchains模拟鼠标左键点击呢,我也不知道,我直接定位元素click不行
	# --------------------课程打分--------------------------
	
	dr.find_element_by_xpath('/html/body/form/table/tbody/tr/td[1]/div/div[4]/input').click()  # 结束
	time.sleep(2)
	dr.switch_to_alert().accept() # 接受弹出的对话框
	time.sleep(2)
	dr.get('http://www.baidu.com') # 清空页面,避免还有数据出现关不了浏览器的情况
	dr.switch_to_alert().accept()
	time.sleep(2)
	dr.close()
	print '窗口已关闭...'
	time.sleep(5)
	dr.quit()

if __name__ == '__main__':
	t1 = time.time()
	autologin()
	t2 = time.time()
	t3 = t2 - t1
	print '本次测试一共耗费%.2f秒' % t3
