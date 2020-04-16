import serial
import time
import numpy as np
import struct
import matplotlib.animation as animation
import matplotlib.pyplot as plt

global CLIport, Dataport
CLIport = {}
Dataport = {}
byteBuffer = np.zeros(2**15,dtype = 'uint8')
byteBufferLength = 0
dataBin = [None] * 288
magicWord = [2, 1, 4, 3, 6, 5, 8, 7]

# Byte sizes for different values
magicWord  = 8
fftOrPeak  = 4
# ------------------------------------------------------------------


def serialConfig(configFileName, dataPortName, userPortName):
    try:
        cliPort = serial.Serial(userPortName, 115200)
        dataPort = serial.Serial(dataPortName, 921600,timeout=0.01)
    except serial.SerialException as se:
        print("Serial Port 0ccupied,error = ")
        print(str(se))
        return
    
    config = [line.rstrip('\r\n') for line in open(configFileName)]
    for i in config:
        cliPort.write((i+'\n').encode())
        print(i)
        time.sleep(0.1)
    print("-----------------------------------------------------------------------")
    return cliPort,dataPort


def readAndParseData(Dataport):
    global byteBuffer, byteBufferLength

    # Constants
    magicWord = [2, 1, 4, 3, 6, 5, 8, 7]

    readBuffer = Dataport.read(Dataport.in_waiting)
    byteVec=np.frombuffer(readBuffer,dtype='uint8')
    framedata=[]

    if np.all(byteVec[0:8] == magicWord):
        subFrameNum = struct.unpack('I', readBuffer[24:28])[0]
        numTLVs = struct.unpack('h', readBuffer[48:50])[0]
        typeTLV = struct.unpack('I',readBuffer[52:56])[0]
        lenTLv = struct.unpack('I',readBuffer[56:60])[0]# include length of tlvHeader(8bytes)
        numPoints = (lenTLv-8)//20
        # print(subFrameNum,":",numTLVs,"type:",typeTLV,"length:",lenTLv,'numPoints:',numPoints)
        Startidx = 60 # TLVpointCLOUD start index
        # print(range(numPoints))
        if typeTLV == 6 and numPoints>0:
            # Initialize variables
            x=[]
            y=[]
            z=[]
            pointClouds=[]
            range_list=[]
            azimuth_list=[]
            elevation_list=[]
            doppler_list=[]
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
                Startidx +=20
            # print("r:", len(range_list), "a:", len(azimuth_list), "e:", len(elevation_list), "d:", len(doppler_list))
            r=np.multiply(range_list[:],np.cos(elevation_list))
            x=np.multiply(r[:],np.sin(azimuth_list[:]))
            y=np.multiply(r[:],np.cos(azimuth_list[:]))
            z=np.multiply(range_list[:],np.sin(elevation_list))
            # print("x:",len(x),"y:",len(y),"z:",len(z))


        return subFrameNum,x,y,z
    else:
        subFrameNum=[]
        x=[]
        y=[]
        z=[]
        return subFrameNum,x,y,z


def main():
    configFileName = "./6843_pplcount_debug.cfg"
    dataPortName = "COM22"
    userPortName = "COM12"

    # Configurate the serial port
    CLIport, Dataport = serialConfig(configFileName, dataPortName, userPortName)
    while True:
        try:
            numframes,x,y,z = readAndParseData(Dataport)
            time.sleep(0.1)  # Sampling frequency of 30 Hz
        except KeyboardInterrupt:
            Dataport.close()  # 清除序列通訊物件
            CLIport.write(('sensorStop\n').encode())
            CLIport.close()
            print('再見！')






if __name__ == "__main__":
    main()