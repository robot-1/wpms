import os

import tornado.ioloop
from tornado.options import define, options, parse_command_line
import tornado.web
import tornado.autoreload

import socketio

define('port', default=5000, help="run on the given port", type=int)
define('debug', default=False, help='run in debug mode')

sio = socketio.AsyncServer(async_mode='tornado', cors_allowed_origins='*')


@sio.event
async def connect(sid, environ, auth):
    print('Connect', sid)
    await sio.emit('my_response', {'data': 'Dashboard connected'}, room=sid)
    # tornado.ioloop.IOLoop.current().spawn_callback(background_task)
    # tornado.ioloop.IOLoop.current().spawn_callback(background_task)

@sio.event
async def disconnect(sid):
    print('Client disconnected')
    await sio.emit('my_response', {'data': "RPi Jomalig Disconnected"}, room='/dashboard')


@sio.event
async def join_dashboard(sid, msg):
    print(sid, msg)
    sio.enter_room(sid, '/dashboard')
    if msg == "RPI":
        print("RPI JOINED ROOM")
        await sio.emit('my_response', {'data': "RPi Jomalig Connected"}, room='/dashboard')


@sio.event
async def ping_from_client(sid):
    await sio.sleep(0.5)
    await sio.emit('pong_from_server', room=sid)

@sio.event
async def client_latency(sid, msg):
    await sio.emit('client_latency', {'data': msg.get('data')},
                   room='/dashboard')


@sio.event
async def tasks_event(sid, msg):
    print(sid, msg)
    await sio.emit('run_task', msg, room="/dashboard")
#     def get_current_user(self):
#         pass


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        print(self.request.headers.get('Authorization'))
        self.render("index.html")

# class LoginHandler(BaseHandler):
#     def get(self):
#         self.write('<html><body><form action="/login" method="post">'
#                    'Name: <input type="text" name="name">'
#                    '<input type="submit" value="Sign in">'
#                    '</form></body></html>')
#
#     def post(self):
#         self.set_secure_cookie("user", self.get_argument("name"))
#         self.redirect("/")


def addwatchfiles(*paths):
    for p in paths:
        file_path = os.path.abspath(p)
        print(file_path)
        tornado.autoreload.watch(file_path)


if __name__ == "__main__":
    parse_command_line()
    app = tornado.web.Application([
        (r'/', MainHandler),
        (r'/socket.io/', socketio.get_tornado_handler(sio)),
        #(r'/api/sensor/([^/]+)?', SensorHandler),
        #(r'/api/data/([^/]+)?', DataHandler),
        #(r'/api/tcpmon/([^/]+)?', TcpMonHandler)
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=options.debug,
    )
    app.listen(options.port)
    tornado.autoreload.start()
    addwatchfiles('templates/index.html')
    tornado.ioloop.IOLoop.current().start()
