import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from pymodbus.client import ModbusSerialClient as ModbusClient
import time
import sys
import glob
import serial
import threading


class GUI:
    def __init__(self):
        # GUI design parameters
        self.window = tk.Tk()
        self.window.title('ModbusReader')
        self.window.geometry('410x400')
        self.n_padx = 5
        self.n_pady = 0
        self.width_cb = 10
        self.width_btn = 10
        self.width_tree = 100
        self.sticky_lb = tk.W
        self.anchor_tree = tk.CENTER
        self.cb1to6 = []
        self.lb8to9 = []
        self.lb7 = None
        self.tree = None
        # Modbus
        self.client = None
        self.port = None
        self.method = None
        self.baudrate = None
        self.parity = None
        self.stopbits = None
        self.address = None
        self.poll = 0
        self.resps = 0
        # Threads
        self.t1 = threading.Thread()
        self.t2 = threading.Thread()
        self.stop_modbus = threading.Event()
        self.stop_com = threading.Event()
        self.connected = False

    def create_label(self, txt, column, row, columnspan):
        lb = tk.StringVar()
        lb.set(txt)
        ttk.Label(self.window, textvariable=lb).grid(column=column, row=row, columnspan=columnspan, padx=self.n_padx, pady=self.n_pady, sticky=self.sticky_lb)
        return lb

    def create_combobox(self, lst, column, row, columnspan):
        cb = ttk.Combobox(self.window, width=self.width_cb, textvariable=tk.StringVar())
        cb['values'] = lst
        cb.grid(column=column, row=row, columnspan=columnspan)
        cb['state'] = 'readonly'
        return cb

    def serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def update_settings(self):
        self.port = self.cb1to6[0].get()
        self.method = self.cb1to6[1].get()
        self.baudrate = int(self.cb1to6[2].get())
        self.parity = self.cb1to6[3].get()[0]
        self.stopbits = int(self.cb1to6[4].get())
        self.address = int(self.cb1to6[5].get())
        print('Modbus Settings: '+self.port,self.method,self.baudrate,self.parity,self.stopbits,self.address)

    def init_modbus(self):
        # pass settings to Modbus function
        self.client = ModbusClient(port=self.port, method=self.method, baudrate=self.baudrate, parity=self.parity, stopbits=self.stopbits, address=self.address)
        # start counting for response
        self.poll = 0
        self.resps = 0
        self.lb8to9[0].set('Poll: '+str(self.poll))
        self.lb8to9[1].set('Resps: '+str(self.resps))

    def update_com(self, stop_com):
        while True:
            try:
                if stop_com.is_set():
                    # print("COM stopped...")
                    break
                else:
                    self.cb1to6[0]['values'] = self.serial_ports()
                    # print("COM updated...")
                    time.sleep(1)
            except Exception as e:
                print(e)
                break

    def update_modbus(self, stop_modbus):
        if self.client.connect():
            print("Connection Successful!")
            self.connected = True
            messagebox.showinfo('ModbusReader','Connection Successful!')
            port = (self.port[:15] + '...') if len(self.port) > 15 else self.port
            self.lb7.set(port+' Connected!')
            while True:
                try:
                    if stop_modbus.is_set():
                        self.client.close()
                        self.lb7.set('Not Connected...')
                        print('Disconnected...')
                        self.connected = False
                        messagebox.showinfo('ModbusReader', 'Disconnected!')
                        break
                    response = self.client.read_input_registers(0x00,6,unit=self.address)
                    if not response.isError():
                        print('Data Received...')
                        result = response.registers[0:6]
                        for i in range(6):
                            self.tree.set(i,'Value',value=result[i])
                        self.lb7.set(self.port+' Connected!')
                        self.poll +=1
                        self.resps +=1
                        self.lb8to9[0].set('Poll: '+str(self.poll))
                        self.lb8to9[1].set('Resps: '+str(self.resps))
                    else:
                        print('No Data Received...')
                        for i in range(6):
                            self.tree.set(i,'Value',value=0)
                        self.lb7.set('***No Response***')
                        self.poll += 1
                        self.lb8to9[0].set('Poll: '+str(self.poll))
                        self.lb8to9[1].set('Resps: '+str(self.resps))
                    time.sleep(1)
                except Exception as e:
                    print(e)
                    break
        else:
            self.connected = False
            messagebox.showinfo('ModbusReader','Connection Failed!')

    def load(self):
        # Labels
        text1to6 = ('Port:', 'Protocol:', 'Baudrate:', 'Parity:', 'Stopbits:', 'Address:')
        row1to6 = (0, 1, 2, 3, 4, 5)
        lb1to6 = []
        for text, row in zip(text1to6, row1to6):
            lb1to6.append(self.create_label(text, 0, row, 1))
        text7 = 'Not Connected...'
        column7 = 0
        self.lb7 = self.create_label(text7, column7, 7, 2)
        text8to9 = ('Poll: 0', 'Resps: 0')
        column8to9 = (2,3)
        for text, column in zip(text8to9, column8to9):
            self.lb8to9.append(self.create_label(text, column, 7, 1))

        # ComboBoxes
        list1 = self.serial_ports()
        list2 = ['ASCII', 'RTU']
        list3 = ['2400', '4800', '9600', '19200', '38400', '57600', '115200']
        list4 = ['EVEN', 'ODD', 'NONE']
        list5 = ['0', '1']
        list6 = ['123']
        list1to6 = [list1,list2,list3,list4,list5,list6]
        for lst, row in zip(list1to6, row1to6):
            self.cb1to6.append(self.create_combobox(lst, 1, row, 1))
        self.cb1to6[5]['state'] = 'normal'

        # Table
        columns = ('Register', 'Parameter', 'Value', 'Range')
        register = ['30001', '30002', '30003', '30004', '30005', '30006']
        parameter = ['Oil Visc', 'Visc Alarm', 'Oil Temp', 'Temp Alarm', 'Ambient Temp', 'Fault Alarm']
        value = ['0', '0', '0', '0', '0', '0']
        limit = ['0-9999', '0/1', '0-9999', '0/1', '0-9999', '0/1']
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings')
        for item in columns:
            self.tree.column(item, width=self.width_tree, anchor=self.anchor_tree)
            self.tree.heading(item,text=item)
        for i in range(len(register)):
            self.tree.insert('', tk.END, iid=i, values=(register[i], parameter[i], value[i], limit[i]))
        self.tree.grid(column=0, row=6, columnspan=4,padx=self.n_padx, pady=self.n_pady, sticky=self.sticky_lb)

        # Buttons
        ttk.Button(self.window, text="Connect", command=self.connect_modbus, width=self.width_btn).grid(column=2, row=4, columnspan=2, padx=self.n_padx, pady=self.n_pady)
        ttk.Button(self.window, text="Disconnect", command=self.disconnect_modbus, width=self.width_btn).grid(column=2, row=5, columnspan=2, padx=self.n_padx, pady=self.n_pady)

        # COM update thread
        t2 = threading.Thread(target=self.update_com,args=(self.stop_com,),daemon=True)
        t2.start()

        # loop window
        self.window.protocol('WM_DELETE_WINDOW', self.app_quit)
        self.window.mainloop()

    def connect_modbus(self):
        if self.connected:
            messagebox.showinfo('ModbusReader', 'Disconnect First!')
            return
        self.update_settings()
        self.init_modbus()
        self.stop_modbus.clear()
        self.t1 = threading.Thread(target=self.update_modbus,args=(self.stop_modbus,),daemon=True)
        self.t1.start()

    def disconnect_modbus(self):
        self.stop_modbus.set()

    def app_quit(self):
        response = messagebox.askyesno('Exit', 'Do you want to close app?')
        if response:
            self.stop_modbus.set()
            self.stop_com.set()
            self.window.quit()
            self.window.destroy()


if __name__ == '__main__':
    gui = GUI()
    gui.load()