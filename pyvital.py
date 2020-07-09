import serial
import time
import numpy as np
import struct
import xlwt
import sys

sys.path.append('C:\\Users\\70639wimoc\\PycharmProjects\\Pyvital-sign')
from LABEL import Ui_MainWindow
from PyQt5 import QtWidgets
import os

global CLIport, Dataport
import subprocess

CLIport = {}
Dataport = {}
byteBuffer = np.zeros(2 ** 15, dtype='uint8')
byteBufferLength = 0
dataBin = [None] * 288
magicWord = [2, 1, 4, 3, 6, 5, 8, 7]


# ------------------------------------------------------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        MainWindow.demo(self)

        # self.ui.label.setText('Hello World!')

    def serialConfig(configFileName, dataPortName, userPortName):
        try:
            cliPort = serial.Serial(userPortName, 115200)
            dataPort = serial.Serial(dataPortName, 921600, timeout=0.04)
        except serial.SerialException as se:
            print("Serial Port 0ccupied,error = ")
            print(str(se))
            return

        config = [line.rstrip('\r\n') for line in open(configFileName)]
        for i in config:
            cliPort.write((i + '\n').encode())
            print(i)
            time.sleep(0.08)
        print("-----------------------------------------------------------------------")
        return cliPort, dataPort

    def readAndParseData(Dataport):
        global byteBuffer, byteBufferLength

        # Constants
        magicWord = [2, 1, 4, 3, 6, 5, 8, 7]

        readBuffer = Dataport.read(Dataport.in_waiting)
        byteVec = np.frombuffer(readBuffer, dtype='uint8')
        framedata = []
        # print(len(byteVec))
        # --------------------------------For vital sign-----------------------------------------------------------------------
        if np.all(byteVec[0:8] == magicWord):
            pack_length = 288
            header_length = 48
            if len(readBuffer) % pack_length == 0:
                Blist = []
                Hlist = []
                BNlist=[]
                HNlist=[]
                numframes = []
                for i in range(len(readBuffer) // pack_length):
                    subFrameNum = struct.unpack('I', readBuffer[i * pack_length + 20:i * pack_length + 24])[0]
                    # Tlvtype = struct.unpack('I',readBuffer[i*288+40:i*288+44])[0]
                    # Tlvlen = struct.unpack('I',readBuffer[i*288+44:i*288+48])[0]
                    sumEnergyBreath = struct.unpack('f', readBuffer[i * pack_length +header_length+76:i * pack_length + header_length +80])[0]
                    sumEnergyHeart = struct.unpack('f', readBuffer[i * pack_length +header_length + 80:i * pack_length + header_length + 84])[0]
                    BreathEst_FFT = struct.unpack('f', readBuffer[i * pack_length + 48 + 44:i * pack_length + 48 + 48])[
                        0]  # 40:frameHeader and 8:type/len bytes 288:maxPacketlen
                    HeartEst_FFT = struct.unpack('f', readBuffer[i * 288 + 48 + 28:i * 288 + 48 + 32])[0]
                    # print("numFrame: ",subFrameNum,"Breath: ",round(BreathEst_FFT),'s/min',"Heart: ",round(HeartEst_FFT),'s/min')
                    Blist.append(BreathEst_FFT)
                    Hlist.append(HeartEst_FFT)
                    BNlist.append(sumEnergyBreath)
                    HNlist.append(sumEnergyHeart)
                    numframes.append(subFrameNum)
                isnull = 0
                return Blist, Hlist, BNlist, HNlist,numframes, isnull
        else:
            isnull = 1
            return [], [], [],[],[],isnull

    def saveData(self):
        book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        self.book = book
        self.sheet = self.book.add_sheet('test', cell_overwrite_ok=True)

        self.sheet.write(0, 0, 'Frames')
        self.sheet.write(0, 1, 'BreathingRate')
        self.sheet.write(0, 2, 'HeartRate')
        self.sheet.write(0, 3, 'EnergyBreath')
        self.sheet.write(0, 4, 'EnergyHeart')
        self.sheet.write(0,5,'time')

        return self.sheet

    def exit_ui(self):
        self.book.save(r'.\test.xls')

    def demo(self):
        # configFileName = "./6843_pplcount_debug.cfg"
        configFileName = "C:\\Users\\70639wimoc\\PycharmProjects\\Pyvital-sign\\xwr1642_profile_VitalSigns_20fps_Front.cfg"
        dataPortName = "COM5"
        userPortName = "COM10"

        # # Configurate the serial port
        CLIport, Dataport = MainWindow.serialConfig(configFileName, dataPortName, userPortName)
        savename = "vital"
        if os.path.isfile("./{}".format(savename)):
            savename = "vital"
        drawh_y = np.zeros([50])
        drawb_y = np.zeros([50])
        draw_x = range(1, 51)
        draw_test = np.random.randint(4, size=50)
        sheet = MainWindow.saveData(self)
        self.ui.graphicsView.setYRange(0, 40, padding=0)
        self.ui.graphicsView_2.setYRange(0, 250, padding=0)
        frame_count = 0

        # Call ssi script(Openface) in sub-terminal
        # subprocess.call("start D:\demo_movie\do_run_movie", shell=True)
        # os.system("D:\demo_movie\do_run_movie")

        while True:
            try:
                # ---------------------------------------vital sign---------------------------------------------------------------------
                Blist, Hlist, BNlist, HNlist, numframes, isnull = MainWindow.readAndParseData(Dataport)
                # print(isnull)
                if isnull == 0 and numframes != []:
                    for i in range(len(numframes)):
                        numframe = numframes[i]
                        fHlist = Hlist[i]
                        fBlist = Blist[i]
                        fHNlist =HNlist[i]
                        fBNlist= BNlist[i]
                        write_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        sheet.write(numframe, 0, numframe)
                        sheet.write(numframe, 1, round(fBlist))
                        sheet.write(numframe, 2, round(fHlist))
                        sheet.write(numframe,3,fBNlist)
                        sheet.write(numframe,4,fHNlist)
                        sheet.write(numframe,5,write_time)

                        self.book.save(r'.\{}.xls'.format(savename))

                        # print("frames:{}, h:{}, b:{}".format(numframe,round(fHlist),round(fBlist)))
                        self.ui.lcdNumber.setDigitCount(len(str(round(fHlist))))
                        self.ui.lcdNumber.display(round(fHlist))
                        self.ui.lcdNumber_2.setDigitCount(len(str(round(fBlist))))
                        self.ui.lcdNumber_2.display(round(fBlist))
                        self.ui.lcdNumber_3.setDigitCount(len(str(numframe)))
                        self.ui.lcdNumber_3.display(numframe)
                        # if numframe<=100:
                        #     drawb_y[numframe - 1] = fBlist
                        #     drawh_y[numframe - 1] = fHlist
                        # else:
                        #     drawb_y[0:98] = drawb_y[1:99]
                        #     drawh_y[0:98] = drawh_y[1:99]
                        #     drawb_y[99] = fBlist
                        #     drawh_y[99] = fHlist
                        if numframe % 50 == 0:
                            count = 50
                        else:
                            count = numframe % 50
                        drawb_y[count - 1] = fBlist
                        drawh_y[count - 1] = fHlist
                        if numframe % 1 == 0:
                            self.ui.graphicsView.clear()
                            self.ui.graphicsView_2.clear()
                            self.ui.graphicsView.plot(draw_x, drawb_y)
                            self.ui.graphicsView_2.plot(draw_x, drawh_y)

                            # print("f:{},sum:{},b:{},last:{}".format(numframe,sum(drawb_y[90:99]),fBlist,drawb_y[99]))

                        app.processEvents()

                        # time.sleep(0.1)  # Sampling frequency of 30 Hz
                else:
                    continue
            except KeyboardInterrupt:
                Dataport.close()  # 清除序列通訊物件
                CLIport.write(('sensorStop\n').encode())
                CLIport.close()
                self.book.save(r'.\{}.xls'.format(savename))
                print('再見！')


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    sys.exit(app.exec_())
