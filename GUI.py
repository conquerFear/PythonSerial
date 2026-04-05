# gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from Serial_controller import SerialController

class SerialAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("串口助手")
        self.root.geometry("800x600")
        self.controller = SerialController()
        self.controller.on_data_received = self.on_data_received   # 设置回调

        self.create_widgets()
        self.refresh_ports()

    def create_widgets(self):
        # 串口设置区域
        param_frame = ttk.LabelFrame(self.root, text="串口设置", padding=5)
        param_frame.pack(fill=tk.X, padx=5, pady=5)

        # 第一行
        ttk.Label(param_frame, text="串口号:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.com_port = ttk.Combobox(param_frame, width=12)
        self.com_port.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(param_frame, text="波特率:").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        self.com_baud = ttk.Combobox(param_frame, width=8,
                                     values=["4800", "9600", "19200", "38400", "57600", "115200"])
        self.com_baud.set("9600")
        self.com_baud.grid(row=0, column=3, padx=5, pady=2)

        self.btn_refresh = ttk.Button(param_frame, text="刷新", command=self.refresh_ports)
        self.btn_refresh.grid(row=0, column=4, padx=5, pady=2)

        self.status_label = ttk.Label(param_frame, text="状态: 未打开", foreground="gray")
        self.status_label.grid(row=0, column=5, padx=10, pady=2)

        # 第二行
        ttk.Label(param_frame, text="数据位:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.com_bytesize = ttk.Combobox(param_frame, width=6, values=["5", "6", "7", "8"])
        self.com_bytesize.set("8")
        self.com_bytesize.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(param_frame, text="停止位:").grid(row=1, column=2, padx=5, pady=2, sticky=tk.W)
        self.com_stopbits = ttk.Combobox(param_frame, width=6, values=["1", "1.5", "2"])
        self.com_stopbits.set("1")
        self.com_stopbits.grid(row=1, column=3, padx=5, pady=2)

        ttk.Label(param_frame, text="校验位:").grid(row=1, column=4, padx=5, pady=2, sticky=tk.W)
        self.com_parity = ttk.Combobox(param_frame, width=8, values=["无(N)", "偶(E)", "奇(O)"])
        self.com_parity.set("无(N)")
        self.com_parity.grid(row=1, column=5, padx=5, pady=2)

        # 按钮 Frame
        btn_frame = ttk.Frame(param_frame)
        btn_frame.grid(row=1, column=6, columnspan=2, padx=5, pady=2, sticky=tk.E)

        self.btn_open = ttk.Button(btn_frame, text="打开串口", command=self.open_serial)
        self.btn_open.pack(side=tk.LEFT, padx=2)

        self.btn_close = ttk.Button(btn_frame, text="关闭串口", command=self.close_serial, state=tk.DISABLED)
        self.btn_close.pack(side=tk.LEFT, padx=2)

        # 接收区
        recv_frame = ttk.LabelFrame(self.root, text="数据接收", padding=5)
        recv_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.recv_text = scrolledtext.ScrolledText(recv_frame, wrap=tk.WORD, height=15)
        self.recv_text.pack(fill=tk.BOTH, expand=True)
        self.recv_text.config(state=tk.DISABLED)

        btn_clear_recv = ttk.Button(recv_frame, text="清空接收区", command=self.clear_recv)
        btn_clear_recv.pack(pady=5)

        # 发送区
        send_frame = ttk.LabelFrame(self.root, text="数据发送", padding=5)
        send_frame.pack(fill=tk.X, padx=5, pady=5)

        self.send_text = scrolledtext.ScrolledText(send_frame, wrap=tk.WORD, height=5)
        self.send_text.pack(fill=tk.BOTH, expand=True)

        btn_send = ttk.Button(send_frame, text="发送", command=self.send_data)
        btn_send.pack(pady=5)

        self.newline_var = tk.BooleanVar(value=True)
        self.chk_newline = ttk.Checkbutton(send_frame, text="发送新行", variable=self.newline_var)
        self.chk_newline.pack(pady=2)

        btn_clear_send = ttk.Button(send_frame, text="清空发送区", command=self.clear_send)
        btn_clear_send.pack(pady=2)

    def refresh_ports(self):
        ports = self.controller.get_ports()
        self.com_port['values'] = ports
        if ports:
            self.com_port.set(ports[0])
            self.status_label.config(text=f"状态: 检测到 {len(ports)} 个串口", foreground="blue")
        else:
            self.com_port.set('')
            self.status_label.config(text="状态: 未检测到串口，可手动输入", foreground="orange")

    def open_serial(self):
        port = self.com_port.get()
        if not port:
            messagebox.showerror("错误", "请选择或输入串口号")
            return

        baudrate = int(self.com_baud.get())
        bytesize = int(self.com_bytesize.get())
        stopbits = float(self.com_stopbits.get())
        parity = self.com_parity.get()
        # 将界面校验位字符串转为控制器需要的格式
        parity_short = {'无(N)':'N', '偶(E)':'E', '奇(O)':'O'}.get(parity, 'N')

        success, err = self.controller.open(port, baudrate, bytesize, stopbits, parity_short)
        if success:
            self.btn_open.config(state=tk.DISABLED)
            self.btn_close.config(state=tk.NORMAL)
            self.com_port.config(state=tk.DISABLED)
            self.com_baud.config(state=tk.DISABLED)
            self.com_bytesize.config(state=tk.DISABLED)
            self.com_stopbits.config(state=tk.DISABLED)
            self.com_parity.config(state=tk.DISABLED)
            self.btn_refresh.config(state=tk.DISABLED)
            self.status_label.config(
                text=f"状态: 已打开 {port} @ {baudrate}bps, {bytesize}数据位, {stopbits}停止位, {parity}校验",
                foreground="green"
            )
        else:
            messagebox.showerror("错误", f"打开串口失败:\n{err}")

    def close_serial(self):
        self.controller.close()
        self.btn_open.config(state=tk.NORMAL)
        self.btn_close.config(state=tk.DISABLED)
        self.com_port.config(state=tk.NORMAL)
        self.com_baud.config(state=tk.NORMAL)
        self.com_bytesize.config(state=tk.NORMAL)
        self.com_stopbits.config(state=tk.NORMAL)
        self.com_parity.config(state=tk.NORMAL)
        self.btn_refresh.config(state=tk.NORMAL)
        self.status_label.config(text="状态: 已关闭", foreground="gray")

    def send_data(self):
        if not self.controller.is_open():
            messagebox.showerror("错误", "串口未打开")
            return
        data = self.send_text.get("1.0", tk.END).rstrip("\n")
        if data:
            if self.newline_var.get():
                data += "\n"
            success, err = self.controller.send(data)
            if not success:
                messagebox.showerror("错误", f"发送失败: {err}")

    def on_data_received(self, text):
        """接收数据的回调（由串口控制器调用）"""
        self.recv_text.config(state=tk.NORMAL)
        self.recv_text.insert(tk.END, text)
        self.recv_text.see(tk.END)
        self.recv_text.config(state=tk.DISABLED)

    def clear_recv(self):
        self.recv_text.config(state=tk.NORMAL)
        self.recv_text.delete("1.0", tk.END)
        self.recv_text.config(state=tk.DISABLED)

    def clear_send(self):
        self.send_text.delete("1.0", tk.END)