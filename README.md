player.web
==========
Very simple music player written in Python using CherryPy and UIkit from YOOtheme. How it works? You upload some songs using web ui to server, press play button, and server plays all the files infinitely via mplayer (in addition thereis simple scheduling). Also you can record a message and broadcast it.
In first place it was written for a mass notification system.
Installation
------------
Clone to some dir:  
`git clone https://github.com/romixlab/player.web.git`  
Install CherryPy  
`pip install cherrypy`
Install schedule
`pip install schedule`
And run it!  
`python player.web.py`  
Then go to ip:9090. You can change interface binding and port in server.conf file. There is simple authentication, change users and passwords in users.json file.
Screenshots
-----------
![player.web](https://cloud.githubusercontent.com/assets/6066470/4253287/20837ffa-3a9e-11e4-8b1c-d550c702adf0.jpg)

