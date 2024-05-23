import serial
import time
import datetime       #延时使用
import binascii
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from threading import Thread

ser = serial.Serial("COM3", 115200)     #初始化串口

# # 定义协议解析函数
# def parse_data(data):
#     # 判断数据长度是否正确
#     if len(data) < 6:
#         print("数据长度不足！")
#         return None

#     if data[0] != 0xA5 or data[1] != 0x5A:
#         print("起始标识错误！")
#         return None
#     # 判断校验和是否正确
#     data_len = int.from_bytes(data[2:4], byteorder='big')
#     check_sum = sum(data[:4+data_len]) & 0xff
#     if check_sum != data[4+data_len]:
#         print("校验和错误！")
#         return None
#     # 解析命令
#     command = data[4]
#     # 解析数据长度
#     length = int.from_bytes(data[5:7], byteorder='big')
#     # 解析数据
#     value = int.from_bytes(data[7:7+length], byteorder='big')
#     # 返回解析结果
#     return command, value
def parse_data (data):

    value=[0 for c in range(0,8)]
    for i in range(0,8):
        value[i] = data[i*2]*256+data[i*2+1]
    return value

# 读取串口数据并解析
def getData():
    firstarray_buffer = 0
    secondarray_buffer = 0
    global result
    result = 0
    while True:
        raw_data = ser.read(ser.inWaiting())
        
        #print(str(binascii.b2a_hex(raw_data)))
        if len(raw_data) > 0:
            # 串口数据中有多个协议数据包可能需要解析
            for i in range(len(raw_data)):
                
                if raw_data[i] == 0x24 and i+5 < len(raw_data):
                    
                    # 检查字节流中是否包含协议数据头
                    if raw_data[i+1] == 0x00 or 0x08:
                        # 获取协议数据包长度
                        #pack_len = len(raw_data[i+2:i+18])
                        # 检查字节数组是否完整
                        if len(raw_data[i:]) >= 18:
                            # 解析协议数据包
                            pack_data = raw_data[i+2:i+18]
                            
                            value = parse_data(pack_data)
                            if raw_data[i+1] == 0x00:
                                firstarray_buffer= value
                                #print(firstarray_buffer)
                            if raw_data[i+1] == 0x08:
                                secondarray_buffer = value
                                #print(secondarray_buffer)
                                if firstarray_buffer != 0 :
                                     
                                     result = firstarray_buffer+secondarray_buffer
                                     firstarray_buffer,secondarray_buffer = 0,0
                                     print(result)
        
                           # dt_ms = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') # 含微秒的日期时间
                            #print(dt_ms)
                            raw_data = raw_data[i+19:]
                            break

    # 关闭串口
    ser.close()

def plotGraph():
    #global result
    return

def main():
    global result
    # 创建 Thread 实例
    t1 = Thread(target=getData)
    t2 = Thread(target=plotGraph)

    # 启动线程运行
    t1.start()
    t2.start()
    while True:
        if result != 0:
            matrix = np.reshape(result, (4,4))
            sns.heatmap(matrix,vmin = 1200,vmax=1800,cmap="mako")
            plt.pause(0.01)
            plt.clf()
    # 等待所有线程执行完毕
    t1.join()  # join() 等待线程终止，要不然一直挂起
    t2.join()

def debug():
    while True:
        raw_data = ser.read(ser.inWaiting())
        print(raw_data)
        dt_ms = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') # 含微秒的日期时间
        print(dt_ms)

if __name__=="__main__":
    main()
    #debug()