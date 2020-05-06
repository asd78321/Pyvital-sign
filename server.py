import serial
import time
import numpy as np
import struct
import socket
import multiprocessing as mp
# import tensorflow as tf
import sys
import threading
import json

global CLIport, Dataport
CLIport = {}
Dataport = {}
byteBuffer = np.zeros(2 ** 15, dtype='uint8')
byteBufferLength = 0
dataBin = [None] * 288
magicWord = [2, 1, 4, 3, 6, 5, 8, 7]

input_1 = np.zeros([12, 120, 50])
input_2 = np.zeros([12, 50, 120])
input_3 = np.zeros([12, 120, 120])

configFileName = "./6843_pplcount_debug.cfg"
dataPortName = "COM22"
userPortName = "COM12"


#server init
port = 5080
server_socket = socket.socket()
server_socket.bind(("", port))
server_socket.listen(2)
print("waiting client:")
conn, address = server_socket.accept()
print("Connection from: ", str(address))
print("connect successful!!")
time.sleep(3)

# print("Socket now lisening!")
# ------------------------------------------------------------------


def serialConfig(configFileName, dataPortName, userPortName):
    try:
        cliPort = serial.Serial(userPortName, 115200)
        dataPort = serial.Serial(dataPortName, 921600, timeout=0.1)
    except serial.SerialException as se:
        print("Serial Port 0ccupied,error = ")
        print(str(se))
        return

    config = [line.rstrip('\r\n') for line in open(configFileName)]
    for i in config:
        cliPort.write((i + '\n').encode())
        print(i)
        time.sleep(0.04)
    print("-----------------------------------------------------------------------")
    print('---------------------------已啟動雷達！---------------------------------')
    return cliPort, dataPort

# # Configurate the serial port
CLIport, Dataport = serialConfig(configFileName, dataPortName, userPortName)


# 定義空間
def voxalize(x_points, y_points, z_points, x, y, z):
    # voxel切割大小修改爲（120，50，120） 叠加frame數量修改為12
    # 定義房間大小
    x_min = -3
    x_max = 3

    y_min = 0.0
    y_max = 2.5

    z_max = 3
    z_min = -3

    z_res = (z_max - z_min) / z_points
    y_res = (y_max - y_min) / y_points
    x_res = (x_max - x_min) / x_points
    # if z_min == z_max:
    #     z_res = 1
    # if y_min == y_max:
    #     y_res = 1
    # if x_min == x_max:
    #     x_res = 1

    #     新方法求取矩陣點

    pixel_x_y = np.zeros([x_points * y_points])
    pixel_y_z = np.zeros([z_points * y_points])
    pixel_x_z = np.zeros([x_points * z_points])

    for i in range(len(y)):

        x_pix = (x[i] - x_min) // x_res
        y_pix = (y[i] - y_min) // y_res
        z_pix = (z[i] - z_min) // z_res

        if x_pix > x_points:
            continue
        if y_pix > y_points:
            continue
        if z_pix > z_points:
            continue

        if x_pix == x_points:
            x_pix = x_points - 1
        if y_pix == y_points:
            y_pix = y_points - 1
        if z_pix == z_points:
            z_pix = z_points - 1

        pixel_x_y[int((y_pix) * x_points + x_pix)] = pixel_x_y[int((y_pix) * x_points + x_pix)] + 1
        pixel_y_z[int((y_pix) * z_points + z_pix)] = pixel_y_z[int((y_pix) * z_points + z_pix)] + 1
        pixel_x_z[int((z_pix) * x_points + x_pix)] = pixel_x_z[int((z_pix) * x_points + x_pix)] + 1

    pixel_x_y = np.array(pixel_x_y).reshape(x_points, y_points)
    pixel_y_z = np.array(pixel_y_z).reshape(y_points, z_points)
    pixel_x_z = np.array(pixel_x_z).reshape(x_points, z_points)

    return pixel_x_y, pixel_y_z, pixel_x_z


# ----------------------------------------------------------------------------------------------------------------------

def readAndParseData(Dataport):
    global byteBuffer, byteBufferLength

    # Constants
    magicWord = [2, 1, 4, 3, 6, 5, 8, 7]

    readBuffer = Dataport.read(Dataport.in_waiting)
    byteVec = np.frombuffer(readBuffer, dtype='uint8')
    framedata = []
    # print(len(byteVec))

    if np.all(byteVec[0:8] == magicWord) and len(readBuffer) > 52:
        subFrameNum = struct.unpack('I', readBuffer[24:28])[0]
        numTLVs = struct.unpack('h', readBuffer[48:50])[0]
        typeTLV = struct.unpack('I', readBuffer[52:56])[0]
        lenTLv = struct.unpack('I', readBuffer[56:60])[0]  # include length of tlvHeader(8bytes)
        numPoints = (lenTLv - 8) // 20
        # print("frames: ",subFrameNum,"numTLVs:",numTLVs,"type:",typeTLV,"length:",lenTLv,'numPoints:',numPoints)
        Startidx = 60  # TLVpointCLOUD start index
        # print(range(numPoints))
        if typeTLV == 6 and numPoints > 0:
            # Initialize variables
            x = []
            y = []
            z = []
            pointClouds = []
            range_list = []
            azimuth_list = []
            elevation_list = []
            doppler_list = []
            for numP in range(numPoints):
                try:
                    Prange = struct.unpack('f', readBuffer[Startidx:Startidx + 4])
                    azimuth = struct.unpack('f', readBuffer[Startidx + 4:Startidx + 8])
                    elevation = struct.unpack('f', readBuffer[Startidx + 8:Startidx + 12])
                    doppler = struct.unpack('f', readBuffer[Startidx + 12:Startidx + 16])
                    framedata.append(pointClouds)
                except:
                    continue
                range_list.append(Prange)
                azimuth_list.append(azimuth)
                elevation_list.append(elevation)
                doppler_list.append(doppler)
                pointClouds.append([range_list, azimuth_list, elevation_list, doppler_list])
                Startidx += 20
            # print("r:", len(range_list), "a:", len(azimuth_list), "e:", len(elevation_list), "d:", len(doppler_list))
            r = np.multiply(range_list[:], np.cos(elevation_list))
            x = np.multiply(r[:], np.sin(azimuth_list[:]))
            y = np.multiply(r[:], np.cos(azimuth_list[:]))
            z = np.multiply(range_list[:], np.sin(elevation_list))
            # print("x:",len(x),"y:",len(y),"z:",len(z))

            p_x_y, p_y_z, p_z_x = voxalize(120, 50, 120, x, y, z)
            isnull = 0
        return subFrameNum, p_x_y, p_y_z, p_z_x, isnull

    else:
        subFrameNum = []
        x = []
        y = []
        z = []
        isnull = 1
        return subFrameNum, x, y, z, isnull

    # ----------------------------------------------------------------------------------------------------------------------


def stack_data(frames, x, y, z):
    x = np.reshape(x, (120, 50))
    y = np.reshape(y, (50, 120))
    z = np.reshape(z, (120, 120))
    # print(input_1.size())
    if frames < 12:
        input_1[frames, :, :] = x
        input_2[frames, :, :] = y
        input_3[frames, :, :] = z

        # print("frames: ",frames+1)
        # # print("x: ",np.sum(x),"y: ",np.sum(y),"z: ",np.sum(z))
        #
        # print("xy: ",np.sum(input_1),"y_z: ",np.sum(input_2),"z_x: ",np.sum(input_3))
    else:
        input_1[0:11, :, :] = input_1[1:12, :, :]
        input_1[11, :, :] = x
        input_2[0:11, :, :] = input_2[1:12, :, :]
        input_2[11, :, :] = y
        input_3[0:11, :, :] = input_3[1:12, :, :]
        input_3[11, :, :] = z



        # print("frames: ", frames + 1)
        # print("xy: ",np.sum(input_1),"y_z: ",np.sum(input_2),"z_x: ",np.sum(input_3))

        # N_input_1 = np.reshape(input_1, (1, 12, 120, 50, 1))
        # N_input_2 = np.reshape(input_2, (1, 12, 50, 120, 1))
        # N_input_3 = np.reshape(input_3, (1, 12, 120, 120, 1))


        # print("x: ", np.sum(x), "y: ", np.sum(y), "z: ", np.sum(z))
    ix = np.sum(input_1)
    iy = np.sum(input_2)
    iz = np.sum(input_3)
    # print("frames: ",frames,"x: ",ix,"y: ",iy,"z: ",iz)

    return ix,iy,iz

# ----------------------------------------------------------------------------------------------------------------------
def transfer_data_from_queue(q):

    while True:
        data = q.get()
        try:
            if data !=[]:
                conn.send((str(data) + "\n").encode())
        except:
            Dataport.close()  # 清除序列通訊物件
            CLIport.write(('sensorStop\n').encode())
            CLIport.close()
            conn.close()
            print('---------------------------已中斷連線！----------------------------------')
            break


def demo(q):
    while True:
        try:
            numframes, x, y, z, isnull = readAndParseData(Dataport)

            #no null data
            # print(isnull)
            if isnull == 0:
                ix,iy,iz = stack_data(numframes, x, y, z)
                data = {'numframes': numframes, 'x': ix, 'y': iy, 'z': iz}
                data = json.dumps(data)
                q.put(data)
                # print(data)
            # else:
            #     continue
            # time.sleep(0.1)  # Sampling frequency of 30 Hz
        except:
            continue


def main():
    q = mp.Queue()
    p1 = threading.Thread(target=demo, args=(q,))
    p2 = threading.Thread(target=transfer_data_from_queue, args=(q,))
    p2.start()
    p1.start()

if __name__ == "__main__":
    main()



