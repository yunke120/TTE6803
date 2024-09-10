import socket
from flask_socketio import Namespace, emit
from enum import Enum
from scapy.all import *
from utils import *
from db_ops import DatabaseOperations
from apscheduler.schedulers.background import BackgroundScheduler


class BPFType(Enum):
    """ 业务类型枚举 """
    TT = '0x88D7'
    RC = '0x0888'
    BE = '0x0800'
    PCF = '0x891D'


class App(Namespace):
    def __init__(self, _np, _ip, _port, _type, _iface):
        print('初始化')
        Namespace.__init__(self, namespace=_np)

        # 设置AS6803的阈值，最小为2.75V, 最大为4.2V
        self.MIN_VOLTAGE = 2.75 
        self.MAX_VOLTAGE = 4.2
        self.STEP_VOLTAGE = 0.010
        self.send_cmd = 'A55A08A1000000000000'
        # 创建UDP套接字
        self.sock_as6803 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # 绑定本地IP地址和端口号
            self.sock_as6803.bind((_ip, _port))
        except socket.error as e:
            print("log_msg", str(e))

        # 8808 设备
        self.sock_8808 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.manufacturers = None
        self.voltage_measured = None
        self.resistance_measured = None

        self.idx = 0    # 帧计数
        self.BPF = 'ether proto ' + _type.value  # Berkeley Packet Filter过滤语法，按照MAC_TYPE进行过滤
        self.iface = _iface 
        self.db_ops = DatabaseOperations()
        self.vol_set = 3.0

        # self.start_time = time.time()
        # self.end_time = time.time()
        # self.stop_flag = False

        self.data = [{'name': '单体电压1', 'value': 3.73},  # 发送给前端显示的数据
                     {'name': '单体电压2', 'value': 3.79},
                     {'name': '单体电压3', 'value': 3.79},
                     {'name': '单体电压4', 'value': 3.79},
                     {'name': '单体电压5', 'value': 3.79},
                     {'name': '单体电压6', 'value': 3.79},
                     {'name': '单体电压7', 'value': 3.79},
                     {'name': '单体电压8', 'value': 3.79},
                     {'name': '单体电压9', 'value': 3.79},
                     {'name': '单体电压10', 'value': 3.79},
                     {'name': '单体电压11', 'value': 3.79},
                     {'name': '单体电压12', 'value': 3.79},
                     {'name': '单体电压13', 'value': 3.79},
                     {'name': '单体电压14', 'value': 3.79},
                     {'name': '单体电压15', 'value': 3.79},
                     {'name': '单体电压16', 'value': 3.79},
                     {'name': '单体电压17', 'value': 3.79},
                     {'name': '单体电压18', 'value': 3.79},
                     {'name': '单体电压19', 'value': 3.79},
                     {'name': '单体电压20', 'value': 3.79},
                     {'name': '单体电压21', 'value': 3.79},
                     {'name': '单体电压21', 'value': 3.79},
                     {'name': '帧计数', 'value': 0},
                     {'name': '舱内温度', 'value': 0.0}]
        
        self.SAVE_FRAME_INTERVAL = 10 # 设置保存时间间隔，
        """
        由于锂电池单体电压模拟设备响应延时，发出数据后需要等待一段时间读取到的数据才是正确的
        这里利用TTE接收数据的间隔来控制延时时间，加入每一帧TTE数据间隔时间为T，则延时读取时间为 
        (T * SAVE_FRAME_INTERVAL)
        """
        
        self.cnt = self.SAVE_FRAME_INTERVAL

        self.scheduler = BackgroundScheduler()
        self.job = None
        self.increasing = True

######################### AS6803 ###################################################

    def on_connect_as6803(self, msg):
        # print(msg) # {'ip': '192.168.0.150', 'port': '5000'}
        try:
            self.sock_as6803.connect((msg['ip'], int(msg['port'])))
            emit("log_msg", "连接AS6803成功")
        except socket.error as e:
            emit("log_msg", "连接AS6803失败: "+str(e))

    def on_close_as6803(self):
        self.sock_as6803.close()

    def on_set_voltage(self, msg) -> bool:
        voltage = float(msg['voltage'])
        if voltage < self.MIN_VOLTAGE or voltage > self.MAX_VOLTAGE:
            emit("log_msg", "电压值超限: 请设置[2.75,4.2]")
            return False   # 无效通道和电压
        ch = 1
        voltage = int(voltage * 1000)
        v_hex_str = "".join(f"{voltage:08x}")
        c_hex_str = hex(ch)[2:].zfill(2)
        if sys.byteorder == 'little':
            # print("little")
            v_hex_str = ''.join(reversed([v_hex_str[i:i + 2] for i in range(0, len(v_hex_str), 2)]))
            # print(reversed_hex)
        else:
            # print("big")
            pass
        self.send_cmd = self.send_cmd[:8] + c_hex_str + self.send_cmd[10:]
        self.send_cmd = self.send_cmd[:10] + v_hex_str + self.send_cmd[18:]
        check_sum = sum(int(self.send_cmd[i:i + 2], 16) for i in range(0, len(self.send_cmd) - 2, 2)) & 0xff
        check_sum = '{:02X}'.format(check_sum)
        self.send_cmd = self.send_cmd[:-2] + check_sum
        # print(self.send_cmd)
        try:
            ret = self.sock_as6803.send(bytes.fromhex(self.send_cmd))
        except OSError as e:
            return False
        if ret == 10:
            self.vol_set = voltage/1000.0
            return True
        else:
            return False

    def on_get_voltage(self):
        cnt = 10
        # 循环接收数据
        while cnt:
            cnt = cnt - 1
            data, addr = self.sock_as6803.recvfrom(1024)  # 接收数据，最大大小为1024字节
            data = data.hex()
            voltage_list_str = []
            voltage_list = []
            # 将字符串按照 2 个字符分割并存储到列表中
            hex_list = [data[i:i + 4] for i in range(0, len(data), 4)]
            if hex_list[1] == 'b76d':
                break
        for i in range(4, 26):
            result = '%s%s' % (hex_list[i][2:], hex_list[i][:2])
            voltage = int(result, 16) / 1000
            voltage = "%.3f" % voltage + 'V'
            voltage_list_str.append(voltage)
            voltage_list.append(int(result, 16))
        return voltage_list

    def on_inc_voltage(self, msg):
        return self.on_set_voltage(msg)

    def on_dec_voltage(self, msg):
        return self.on_set_voltage(msg)

######################### TTE ###################################################

    def packet_handler(self, pkt):
        """ TTE接收回调 """
        payload = pkt.payload.raw_packet_cache
        payload_vol = payload[253:297]
        voltage_list = []
        if len(payload) != 627:
            return
        # print("---")
        # print(payload.hex())
        self.cnt = self.cnt - 1
        for i in range(0, len(payload_vol), 2):
            temp = combine_value(payload_vol[i], payload_vol[i+1]) # 合并数据
            temp = convert_voltage(temp)    # 采样值转实际值
            self.data[int(i/2)]['value'] = temp
            voltage_list.append(temp)
        self.idx += 1
        self.data[22]['value'] = self.idx
        R = self._8808_measure_resistance()
        if R < 0 :
            return
        T = R2T(R)
        self.data[23]['value'] = T
        if self.cnt == 0:
            self.db_ops.add_record(self.idx, T, self.vol_set, voltage_list) # 保存数据库
            self.cnt = self.SAVE_FRAME_INTERVAL
        emit("telemetry_value", self.data)

    def on_start_tte_recv(self):
        """启动接收"""
        # print("开始接收TTE数据")
        sniff(prn=self.packet_handler, filter=self.BPF, iface=self.iface)

######################### 8808 ###################################################
    def on_connect_8808(self, port = 20008, ip = '192.168.0.7'):
        """连接8808设备"""
        try:
            self.sock_8808.connect((ip, int(port)))
            ret = self._8808_check_connect()
            if ret is True:
                emit("log_msg", "8808连接成功")
            else:
                emit("log_msg", "8808连接失败,当前连接设备不是FLUKE表！")
        except ConnectionRefusedError as e:
            print('IP:' + ip + ',端口:' + str(port))
            emit("log_msg", "8808连接失败,设备拒绝连接！")

    def on_close_8808(self):
        """断开8808设备"""
        self.sock_8808.close()

    def _8808_check_connect(self):
        """检查8808设备是否建立连接"""
        self.sock_8808.sendall(b'*IDN?\r\n')
        self.manufacturers = self.sock_8808.recv(1024).decode(encoding='ascii')
        if 'FLUKE' in self.manufacturers:
            # print(self.manufacturers + '连接检查完成')
            return True
        else:
            # raise Exception('当前连接设备不是FLUKE表！')
            return False
    def _8808_check_response(self, response):
        """检查8808设备响应数据"""
        if '=>' in response:
            return 0
        elif '?>' in response:
            # raise Exception('检测到命令错误。由于是未知命令，所以未执行。例如，万用表接收到一个具有语法错误的输入字符串。')
            return -1
        elif '!>' in response:
            # raise Exception('执行错误或检测到与设备相关的错误。命令能够被正确解析，但是不能执行。例如，用户视图用 FREQ 执行 VDC 测量。')
            return -2

    def _8808_tranform(self, value):
        """提取数据"""
        # 处理负号
        match_neg = re.match('(^-)(.*)', value)
        match_pos = re.match('(^\\+)(.*)', value)
        if match_neg is not None:
            value = match_neg.group(2)
        elif match_pos is not None:
            value = match_pos.group(2)
        if 'VDC' in value:
            match = re.match('(.*?)E(.*)( VDC)', value)
        elif 'OHMS' in value:
            match = re.match('(.*?)E(.*)( OHMS)', value)
        num = float(match.group(1))
        if match_neg is not None:
            num = -num
        power = float(match.group(2))
        result = round(num * math.pow(10, power), 8)  # 计算 3 * 0.1 实际上不是0.3。
        return result

    def _8808_measure_resistance(self):
        """
        返回测量电阻值
        :return: 小于0是失败
        """
        self.sock_8808.sendall(b'VAL1?\r\n')
        self.resistance_measured = self.sock_8808.recv(1024).decode(encoding='ascii')
        ret = self._8808_check_response(self.resistance_measured)
        if ret != 0 :
            emit("log_msg", "命令错误！")
            return ret
        if 'OHMS' not in self.resistance_measured:
            # raise Exception('当前FLUKE测量的不是电阻值！')
            emit("log_msg", "当前FLUKE测量的不是电阻值！")
            return -3
        
        self.resistance_measured = self._8808_tranform(self.resistance_measured)
        return self.resistance_measured
    
######################### 定时任务 ###################################################
    def on_start_scheduler(self, T):
        self.scheduler.add_job(self.job_timing, 'interval', seconds=T['timing'], id="timing_job")

    def on_stop_scheduler(self):
        self.job.remove()
        self.scheduler.remove_job(id='timing_job')

    def job_timing(self):
        vol = self.vol_set

        if self.increasing:
            vol += self.STEP_VOLTAGE
            if vol >= self.MAX_VOLTAGE:
                vol = self.MAX_VOLTAGE
                self.increasing = False
                data = {'voltage', vol}
                ret = self.on_set_voltage(data)
                if ret:
                    self.vol_set = vol
                else:
                    pass
        else:
            vol -= self.STEP_VOLTAGE
            if vol <= self.MIN_VOLTAGE:
                vol = self.MIN_VOLTAGE
                self.increasing = True
                data = {'voltage', vol}
                ret = self.on_set_voltage(data)
                if ret:
                    self.vol_set = vol
                else:
                    pass

    def on_set_save_interval(self, msg):
        self.SAVE_FRAME_INTERVAL = msg['interval']


