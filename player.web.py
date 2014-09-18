import os
from os import path
import cherrypy
from cherrypy.lib import auth_basic
import subprocess
import signal
import cgi
import tempfile
import json
import schedule
import time
import threading

def validate_password(realm, username, password):
	with open('users.json') as users_file:
		users = json.load(users_file)
		return username in users and users[username] == password

class myFieldStorage(cgi.FieldStorage):
	def make_file(self, binary = None):
		return tempfile.NamedTemporaryFile()

def noBodyProcess():
	"""Sets cherrypy.request.process_request_body = False, giving
	us direct control of the file upload destination. By default
	cherrypy loads it to memory, we are directing it to disk."""
	cherrypy.request.process_request_body = False

cherrypy.tools.noBodyProcess = cherrypy.Tool("before_request_body", noBodyProcess)

class PlayerApp(object):
	player = 0
	schedule_thread = threading.Event()

	def load_schedule(self):
		with open('schedule.json') as j:
			sch = json.load(j)
			for time in sch["play"]:
				schedule.every().day.at(time).do(self.play)
				print(time)
			for time in sch["stop"]:
				schedule.every().day.at(time).do(self.stop_mplayer)

	def run_schedule(self, cease_continuous_run, interval=1):
		class ScheduleThread(threading.Thread):
			name = 'schedule'
			@classmethod
			def run(cls):
				while not cease_continuous_run.is_set():
					schedule.run_pending()
					time.sleep(interval)

		continuous_thread = ScheduleThread()
		continuous_thread.start()

	def __init__(self):
		cherrypy.engine.subscribe('stop', self.cherrypy_stopping)
		cherrypy.engine.subscribe('start', self.cherrypy_starting)

	def cherrypy_starting(self):
		self.schedule_thread.set()
		self.load_schedule()

	def cherrypy_stopping(self):
		if self.schedule_thread != 0:
			self.schedule_thread.set()

	@cherrypy.expose
	def index(self):
		return file('index.html')

	@cherrypy.expose
	def play(self):
		if self.player == 0:
			path = os.getcwd() + '/music/'
			files = os.listdir(path)
			i = 0
			for f in files:
				files[i] = path + f
				i = i + 1
			self.player = subprocess.Popen(["mplayer", "-loop", "0", "-shuffle", "-quiet"] + files,
				stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

	@cherrypy.expose
	def splay(self):
		if self.schedule_thread.is_set():
			self.schedule_thread.clear()
			self.run_schedule(self.schedule_thread)
			

	@cherrypy.expose
	def next(self):
		if self.player != 0:
			self.player.stdin.write(">")

	@cherrypy.expose
	def prev(self):
		if self.player != 0:
			self.player.stdin.write("<")

	@cherrypy.expose
	def volup(self):
		if self.player != 0:
			self.player.stdin.write("*")

	@cherrypy.expose
	def voldown(self):
		if self.player != 0:
			self.player.stdin.write("/")

	def stop_mplayer(self):
		if self.player != 0:
			self.player.terminate()
			self.player = 0

	@cherrypy.expose
	def stop(self, all = False):
		self.stop_mplayer()
		self.schedule_thread.set()

	@cherrypy.expose
	@cherrypy.tools.json_out()
	def ls(self):
		path = os.getcwd() + '/music/'
		return os.listdir(path)

	@cherrypy.expose
	def rm(self, file):
		f = os.getcwd() + '/music/' + file
		os.remove(f)

	@cherrypy.expose
	def rmall(self):
		path = os.getcwd() + '/music/'
		files = os.listdir(path)
		for f in files:
			os.remove(path + f)

	@cherrypy.expose
	def state(self):
		if not self.schedule_thread.is_set():
			return 'schedule'
		if self.player == 0:
			return 'stopped'
		else:
			return 'playing'

	@cherrypy.expose
	@cherrypy.tools.noBodyProcess()
	def upload(self, theFile = None):
		lcHDRS = {}
		for key, val in cherrypy.request.headers.iteritems():
			lcHDRS[key.lower()] = val
		formFields = myFieldStorage(fp = cherrypy.request.rfile,
									headers = lcHDRS,
									environ = {'REQUEST_METHOD': 'POST'},
									keep_blank_values = True)
		theFiles = formFields['theFiles']
		if not hasattr(theFiles, '__getslice__'): #if only one file is selected theFiles is not an array
			theFiles = [theFiles]
		for theFile in theFiles:
			if theFile.filename == "record.wav":
				if os.path.isfile('./rec/record.wav'):
					os.remove('./rec/record.wav')
				os.link(theFile.file.name, './rec/' + theFile.filename)
				path = os.getcwd()
				subprocess.call(["mplayer", "-quiet", './rec/announcement.mp3', './rec/record.wav'])
				os.remove('./rec/record.wav')
			else:
				os.link(theFile.file.name, './music/' + theFile.filename)

if __name__ == '__main__':
	musicdir = os.getcwd() + '/music'
	if not os.path.exists(musicdir):
	    os.makedirs(musicdir)
	conf = {
		'/': {
			'tools.sessions.on': True,
			'tools.staticdir.root': os.path.abspath(os.getcwd()),
			'tools.auth_basic.on': True,
			'tools.auth_basic.realm': 'localhost',
			'tools.auth_basic.checkpassword': validate_password
		},
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': "./public"
		},
		'/music': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': "./music"
		}
	}


	webapp = PlayerApp()
	cherrypy.config.update("server.conf")
	cherrypy.quickstart(webapp, '/', conf)



	
