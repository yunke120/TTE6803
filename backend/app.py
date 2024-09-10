from flask import Flask, render_template
from flask_socketio import SocketIO
from tte6803 import App, BPFType

app = Flask(__name__, static_folder='assets')
# app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 定义本地IP地址和端口号
local_ip = '192.168.0.2'
local_port = 6300

# 两个类的命名空间一样就失效了
tte6803_dev = App('/', local_ip, local_port, BPFType.TT, "以太网 2")
socketio.on_namespace(tte6803_dev)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # socketio.run(app, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)
    # engineio.async_drivers.threading
    app.run(host='0.0.0.0', port=5000, threaded=True)
