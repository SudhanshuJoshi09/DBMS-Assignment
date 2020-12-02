# Flask Imports
from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
# The Selenium imports
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
# Utility Imports
from datetime import datetime
from os import path
import time
import re
import sqlite3
import schedule
import discord_webhook


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'


# driver = webdriver.Chrome(chrome_options=opt,service_log_path='NUL')
#put your teams credentials here
DRIVER = None
URL = "https://teams.microsoft.com"
CREDS = {'email' : '','password':''}


def login():
	""" function for logging into microsoft-teams """

	global DRIVER
	# print("logging in")
	# Filling the email field
	email_field = DRIVER.find_element_by_xpath('//*[@id="i0116"]')
	email_field.click()
	email_field.send_keys(CREDS['email'])

	DRIVER.find_element_by_xpath('//*[@id="idSIButton9"]').click()
	time.sleep(5)
	passwordField = DRIVER.find_element_by_xpath('//*[@id="i0118"]')
	passwordField.click()
	passwordField.send_keys(CREDS['password'])
	DRIVER.find_element_by_xpath('//*[@id="idSIButton9"]').click() #Sign in button
	time.sleep(5)
	DRIVER.find_element_by_xpath('//*[@id="idSIButton9"]').click() #remember login
	time.sleep(5)


def createDB():
	conn = sqlite3.connect('timetable.db')
	c=conn.cursor()
	# Create table
	c.execute('''CREATE TABLE timetable(class text, start_time text, end_time text, day text)''')
	conn.commit()
	conn.close()
	print("Created timetable Database")

@app.route('/add_class', methods=['GET', 'POST'])
def add_class():
	if request.method == 'POST':
		class_name = request.form['class_name']
		s_hours = request.form['s_hours']
		s_mins = request.form['s_mins']
		e_hours = request.form['e_hours']
		e_mins = request.form['e_mins']
		start_time = s_hours + ':' + s_mins
		end_time = e_hours + ':' + e_mins
		day = request.form['day']

		conn = sqlite3.connect('timetable.db')
		c=conn.cursor()
		c.execute("INSERT INTO timetable VALUES ('%s','%s','%s','%s')"%(class_name, start_time, end_time, day))
		conn.commit()
		conn.close()
		return redirect(url_for('add_timetable'))

	return render_template('add_class.html')


@app.route('/create_new', methods=['GET', 'POST'])
def add_timetable():

	if request.method == 'POST':
		if(not(path.exists("timetable.db"))):
			createDB()

		try:
			btn_type1 = request.form['Add']
		except:
			btn_type1 = None
		try:
			btn_type2 = request.form['End']
		except:
			btn_type2 = None

		if btn_type1:
			return render_template('end.html')
		elif btn_type2:
			return redirect(url_for('add_class'))
	return render_template('new_req.html')

@app.route('/show_timetable')
def view_timetable():
	conn = sqlite3.connect('timetable.db')
	c = conn.cursor()
	temp = []
	for row in c.execute('SELECT * FROM timetable'):
		temp.append(row)
	conn.close()
	return render_template('show_table.html', val=temp)



def joinclass(class_name,start_time,end_time):
	global DRIVER

	try_time = int(start_time.split(":")[1]) + 15
	try_time = start_time.split(":")[0] + ":" + str(try_time)

	time.sleep(5)


	classes_available = DRIVER.find_elements_by_class_name("name-channel-type")

	for i in classes_available:
		if class_name.lower() in i.get_attribute('innerHTML').lower():
			print("JOINING CLASS ",class_name)
			i.click()
			break

	time.sleep(4)
	try:
		joinbtn = DRIVER.find_element_by_class_name("ts-calling-join-button")
		joinbtn.click()

	except:
		#join button not found
		#refresh every minute until found
		k = 1
		while(k<=15):
			print("Join button not found, trying again")
			time.sleep(60)
			DRIVER.refresh()
			joinclass(class_name,start_time,end_time)
			# schedule.every(1).minutes.do(joinclass,class_name,start_time,end_time)
			k+=1
		print("Seems like there is no class today.")
		discord_webhook.send_msg(class_name=class_name,status="noclass",start_time=start_time,end_time=end_time)


	time.sleep(4)
	webcam = DRIVER.find_element_by_xpath('//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div[2]/div/div/section/div[2]/toggle-button[1]/div/button/span[1]')
	if(webcam.get_attribute('title')=='Turn camera off'):
		webcam.click()
	time.sleep(1)

	microphone = DRIVER.find_element_by_xpath('//*[@id="preJoinAudioButton"]/div/button/span[1]')
	if(microphone.get_attribute('title')=='Mute microphone'):
		microphone.click()

	time.sleep(1)
	joinnowbtn = DRIVER.find_element_by_xpath('//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div[2]/div/div/section/div[1]/div/div/button')
	joinnowbtn.click()

	discord_webhook.send_msg(class_name=class_name,status="joined",start_time=start_time,end_time=end_time)
	
	#now schedule leaving class
	tmp = "%H:%M"

	class_running_time = datetime.strptime(end_time,tmp) - datetime.strptime(start_time,tmp)

	time.sleep(class_running_time.seconds)

	DRIVER.find_element_by_class_name("ts-calling-screen").click()


	DRIVER.find_element_by_xpath('//*[@id="teams-app-bar"]/ul/li[3]').click() #come back to homepage
	time.sleep(1)

	DRIVER.find_element_by_xpath('//*[@id="hangup-button"]').click()
	print("Class left")
	discord_webhook.send_msg(class_name=class_name,status="left",start_time=start_time,end_time=end_time)

def start_browser():
	""" for running the browser """

	global DRIVER
	# Defining the default options of the web-driver
	opt = Options()
	opt.add_argument("--disable-infobars")
	opt.add_argument("start-maximized")
	opt.add_argument("--disable-extensions")
	opt.add_argument("--start-maximized")
	# Pass the argument 1 to allow and 2 to block
	opt.add_experimental_option("prefs", { \
		"profile.default_content_setting_values.media_stream_mic": 1, 
		"profile.default_content_setting_values.media_stream_camera": 1,
		"profile.default_content_setting_values.geolocation": 1, 
		"profile.default_content_setting_values.notifications": 1 
	})
	DRIVER = webdriver.Chrome(chrome_options=opt,service_log_path='NUL')
	DRIVER.get(URL)

	WebDriverWait(DRIVER,10000).until(EC.visibility_of_element_located((By.TAG_NAME,'body')))
	if("login.microsoftonline.com" in DRIVER.current_url):
		login()


def sched():
	conn = sqlite3.connect('timetable.db')
	c=conn.cursor()
	for row in c.execute('SELECT * FROM timetable'):
		#schedule all classes
		name = row[0]
		start_time = row[1]
		end_time = row[2]
		day = row[3]

		if day.lower()=="monday":
			schedule.every().monday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		elif day.lower()=="tuesday":
			schedule.every().tuesday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		elif day.lower()=="wednesday":
			schedule.every().wednesday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		elif day.lower()=="thursday":
			schedule.every().thursday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		elif day.lower()=="friday":
			schedule.every().friday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		elif day.lower()=="saturday":
			schedule.every().saturday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		elif day.lower()=="sunday":
			schedule.every().sunday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
	#Start browser
	start_browser()
	while True:
		# Checks whether a scheduled task
		# is pending to run or not
		schedule.run_pending()
		time.sleep(1)

if __name__=="__main__":
	app.run(debug=True)