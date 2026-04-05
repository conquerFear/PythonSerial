# serial_controller.py
import serial
import serial.tools.list_ports
import threading
import time
import sys

class SerialController:
    """串口控制类，封装所有硬件操作"""
    def __init__(self):
        self.ser = None
        self.receiving = False
        self.receive_thread = None
        self.on_data_received = None   # 回调函数，用于通知界面收到数据

    def get_ports(self):
        """串口扫描"""
        ports = []
        # 方法1：pyserial 标准方法
        try:
            for p in serial.tools.list_ports.comports():
                if p.device not in ports:
                    ports.append(p.device)
        except:
            pass
        # 方法2：Windows 主动探测，不然虚拟串口检测不到
        if sys.platform == 'win32':
            for i in range(1, 257):
                port_name = f'COM{i}'
                try:
                    test_ser = serial.Serial(port_name, timeout=0.1)
                    test_ser.close()
                    if port_name not in ports:
                        ports.append(port_name)
                except:
                    pass
        ports.sort(key=lambda x: int(''.join(filter(str.isdigit, x)) or 0))
        return ports

    def open(self, port, baudrate, bytesize=8, stopbits=1, parity='N'):
        """打开串口，参数均为标准格式"""
        try:
            parity_map = {
                'N': serial.PARITY_NONE,
                'E': serial.PARITY_EVEN,
                'O': serial.PARITY_ODD
            }
            parity = parity_map.get(parity, serial.PARITY_NONE)
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                stopbits=stopbits,
                parity=parity,
                timeout=0.5
            )
            self.receiving = True
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            return True, None
        except Exception as e:
            return False, str(e)

    def close(self):
        """关闭串口"""
        self.receiving = False
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1)
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = None

    def send(self, data):
        """发送字符串（会自动编码为 utf-8）"""
        if not self.ser or not self.ser.is_open:
            return False, "串口未打开"
        try:
            self.ser.write(data.encode('utf-8'))
            return True, None
        except Exception as e:
            return False, str(e)

    def _receive_loop(self):
        """后台接收线程"""
        while self.receiving and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting:
                    data = self.ser.readline()
                    if data:
                        text = data.decode('utf-8', errors='replace')
                        # 通过回调通知界面
                        if self.on_data_received:
                            self.on_data_received(text)
                else:
                    time.sleep(0.01)
            except Exception as e:
                print(f"接收错误: {e}")
                break

    def is_open(self):
        return self.ser is not None and self.ser.is_open