# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 22:28:31 2020

@author: BIIC
"""
import serial
import time
import numpy as np
import struct
import xlwt
import math
import sys
import os


def serialConfig(configFileName, dataPortName, userPortName):
    try:
        cliPort = serial.Serial(userPortName, 115200)
        dataPort = serial.Serial(dataPortName, 921600, timeout=0.05)
    except serial.SerialException as se:
        print("Serial Port 0ccupied,error = ")
        print(str(se))
        return

    config = [line.rstrip('\r\n') for line in open(configFileName)]
    for i in config:
        cliPort.write((i + '\n').encode())
        print(i)
        time.sleep(0.1)
    print("-----------------------------------------------------------------------")
    return cliPort, dataPort


def readAndParseData(Dataport):
    global byteBuffer, byteBufferLength

    # Constants
    magicWord = [2, 1, 4, 3, 6, 5, 8, 7]

    init_UnwrapPhasePeak = 0
    readBuffer = Dataport.read(Dataport.in_waiting)
    byteVec = np.frombuffer(readBuffer, dtype='uint8')
    framedata = []
    # print(len(byteVec))
    # --------------------------------For vital sign-----------------------------------------------------------------------
    if len(byteVec) > 8:
        if np.all(byteVec[0:8] == magicWord):
            pack_length = 288
            header_length = 48

            if len(readBuffer) % pack_length == 0:
                Blist = []
                Hlist = []
                BNlist = []
                HNlist = []
                Phlist = []
                numframes = []
                for i in range(len(readBuffer) // pack_length):
                    subFrameNum = struct.unpack('I', readBuffer[i * pack_length + 20:i * pack_length + 24])[
                        0]  # Header(40)

                    unwrapPhasePeak_mm = struct.unpack('f', readBuffer[
                                                            i * pack_length + header_length + 16:i * pack_length + header_length + 20])[
                        0]  # count(0~) * pack_length(288) + header_length(Packet_Header:40 + TLV Header:8)
                    sumEnergyBreath = struct.unpack('f', readBuffer[
                                                         i * pack_length + header_length + 76:i * pack_length + header_length + 80])[
                        0]
                    sumEnergyHeart = struct.unpack('f', readBuffer[
                                                        i * pack_length + header_length + 80:i * pack_length + header_length + 84])[
                        0]
                    BreathEst_FFT = struct.unpack('f', readBuffer[
                                                       i * pack_length + header_length + 44:i * pack_length + header_length + 48])[
                        0]  # 40:frameHeader and 8:type/len bytes 288:maxPacketlen
                    HeartEst_FFT = struct.unpack('f', readBuffer[
                                                      i * pack_length + header_length + 28:i * pack_length + header_length + 32])[
                        0]
                    # print("numFrame: ",subFrameNum,"Breath: ",round(BreathEst_FFT),'s/min',"Heart: ",round(HeartEst_FFT),'s/min')
                    Phlist.append(unwrapPhasePeak_mm)
                    Blist.append(BreathEst_FFT)
                    Hlist.append(HeartEst_FFT)
                    BNlist.append(sumEnergyBreath)
                    HNlist.append(sumEnergyHeart)
                    numframes.append(subFrameNum)

                isnull = 0
                return Blist, Hlist, BNlist, HNlist, numframes, Phlist, isnull

            isnull = 1
            return [], [], [], [], [], [], isnull

        else:
            isnull = 1
            return [], [], [], [], [], [], isnull


def saveData():
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    book.book = book
    sheet = book.add_sheet('test', cell_overwrite_ok=True)
    sheet.write(0, 0, 'Frames')
    sheet.write(0, 1, 'BreathingRate')
    sheet.write(0, 2, 'HeartRate')
    sheet.write(0, 3, 'EnergyBreath')
    sheet.write(0, 4, 'EnergyHeart')
    sheet.write(0, 5, 'ChestMovement')
    sheet.write(0, 6, 'time')

    return book, sheet


def main():
    configFileName = "C:\\Users\\70639wimoc\\PycharmProjects\\demo_movie\\Pyvital-sign-develop\\Pyvital-sign-develop\\xwr1642_profile_VitalSigns_20fps_Front.cfg"
    dataPortName = "COM5"
    userPortName = "COM10"
    CLIport, Dataport = serialConfig(configFileName, dataPortName, userPortName)
    magicWord = [2, 1, 4, 3, 6, 5, 8, 7]
    savename = "testvital"
    book, sheet = saveData()

    # constants
    exPhase = 0
    c = 3 * 10 ** 8
    f = 79 * 10 ** 9
    Wavelength = c / f

    while True:
        try:
            try:
                Blist, Hlist, BNlist, HNlist, numframes, Phlist, isnull = readAndParseData(Dataport)
                if isnull == 0 and numframes != []:
                    for i in range(len(numframes)):
                        numframe = numframes[i]
                        fHlist = Hlist[i]
                        fBlist = Blist[i]
                        fHNlist = HNlist[i]
                        fBNlist = BNlist[i]
                        fPHlist = Phlist[i]
                        chestmovement = ((fPHlist - exPhase) / (4 * math.pi)) / Wavelength
                        exPhase = fPHlist
                        write_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        print("frame:{} Heart:{} Breath:{} HN:{} BN:{}".format(numframe,fHlist,fBlist,fHNlist,fBNlist))

                        sheet.write(numframe, 0, numframe)
                        sheet.write(numframe, 1, round(fBlist))
                        sheet.write(numframe, 2, round(fHlist))
                        sheet.write(numframe, 3, fBNlist)
                        sheet.write(numframe, 4, fHNlist)
                        sheet.write(numframe, 5, chestmovement)
                        sheet.write(numframe, 6, write_time)
                        book.save(r'./{}.xls'.format(savename))

                    time.sleep(0.05)
            except:
                continue

        except KeyboardInterrupt:
            book.save(r'./{}.xls'.format(savename))
            break
            Dataport.close()  # 清除序列通訊物件
            CLIport.write(('sensorStop\n').encode())
            CLIport.close()
            # self.book.save(r'C:\\Users\\BIIC\\Desktop\\{}.xls'.format(savename))
            print('再見！')


if __name__ == "__main__":
    main()
