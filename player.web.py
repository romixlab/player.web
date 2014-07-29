import os
from os import path
import cherrypy
from cherrypy.lib import auth_basic
import subprocess
import signal
import cgi
import tempfile
import json

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

class StringGenerator(object):
	player = 0

	@cherrypy.expose
	def index(self):
		return file('index.html')

	@cherrypy.expose
	def play(self, url = ''):
		if len(url) == 0 and self.player == 0:
			path = os.getcwd() + '/music/'
			files = os.listdir(path)
			i = 0
			for f in files:
				files[i] = path + f
				i = i + 1
			self.player = subprocess.Popen(["mplayer", "-loop", "0", "-shuffle", "-quiet"] + files,
				stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			return 'playing'
			

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

	@cherrypy.expose
	def stop(self):
		if self.player != 0:
			cherrypy.log("killing")
			self.player.terminate()
			self.player = 0

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
		}
	}
	webapp = StringGenerator()
	cherrypy.config.update("server.conf")
	cherrypy.quickstart(webapp, '/', conf)
