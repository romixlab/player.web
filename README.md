player.web
==========
Very simple music player written in Python using CherryPy and UIkit from YOOtheme. How it works? You upload some songs using web ui to server, press play button, and server plays all the files infinitely via mplayer.
For example you can use it if you want to build some sort of mass notification system or something like that...
Installation
------------
Clone to some dir:  
`git clone https://github.com/romixlab/player.web.git`  
Install CherryPy  
`pip install cherrypy`  
And run it!  
`python player.web.py`  
Then go to ip:9090. You can change interface binding and port in server.conf file. There is simple authentication, change users and passwords in users.json file.
