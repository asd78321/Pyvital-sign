import serial  # pyserial 3.4
import os
import time
import numpy as np
import struct
import xlwt
import sys
import math

#sys.path.append('{}\\LABEL.py'.format(os.getcwd))
sys.path.append('C:\\Users\\70639wimoc\\PycharmProjects\\Pyvital-sign')
from LABEL import Ui_MainWindow
from PyQt5 import QtWidgets

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
        self.ui.pushButton.toggle()
        self.ui.pushButton.clicked.connect(lambda :self.exitUI())
        self.ui.pushButton_2.toggle()
        self.ui.pushButton_2.clicked.connect(lambda :self.do_run_movie())
        self.show()
        MainWindow.demo(self)

        # self.ui.label.setText('Hello World!')
    def exitUI(self):
        self.book.save(r'.\vital.xls')
        app.closeAllWindows()
        sys.exit()
    def do_run_movie(self):

        # Call ssi script(Openface) in sub-terminal
        subprocess.call("start C:\\Users\\70639wimoc\\Desktop\\demo_movie-ori\\demo_movie-ori\\do_run_movie", shell=True)

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
            time.sleep(0.08)
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
                    subFrameNum = struct.unpack('I', readBuffer[i * pack_length + 20:i * pack_length + 24])[0] # Header(40)

                    unwrapPhasePeak_mm = struct.unpack('f', readBuffer[
                                                            i * pack_length + header_length + 16:i * pack_length + header_length + 20])[
                        0]  # count(0~) * pack_length(288) + header_length(Packet_Header:40 + TLV Header:8)
                    sumEnergyBreath = struct.unpack('f', readBuffer[
                                                         i * pack_length + header_length + 76:i * pack_length + header_length + 80])[
                        0]
                    sumEnergyHeart = struct.unpack('f', readBuffer[
                                                        i * pack_length + header_length + 80:i * pack_length + header_length + 84])[
                        0]
                    BreathEst_FFT = struct.unpack('f', readBuffer[i * pack_length + header_length + 44:i * pack_length + header_length + 48])[
                        0]  # 40:frameHeader and 8:type/len bytes 288:maxPacketlen
                    HeartEst_FFT = struct.unpack('f', readBuffer[i * pack_length + header_length + 28:i * pack_length + header_length + 32])[0]

                    # print("numFrame: ",subFrameNum,"Breath: ",round(BreathEst_FFT),'s/min',"Heart: ",round(HeartEst_FFT),'s/min')
                    Phlist.append(unwrapPhasePeak_mm)
                    Blist.append(BreathEst_FFT)
                    Hlist.append(HeartEst_FFT)
                    BNlist.append(sumEnergyBreath)
                    HNlist.append(sumEnergyHeart)
                    numframes.append(subFrameNum)

                isnull = 0
                return Blist, Hlist, BNlist, HNlist, numframes, Phlist, isnull
        else:
            isnull = 1
            return [], [], [], [], [], [], isnull

    def saveData(self):
        book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        self.book = book
        self.sheet = self.book.add_sheet('test', cell_overwrite_ok=True)

        self.sheet.write(0, 0, 'Frames')
        self.sheet.write(0, 1, 'BreathingRate')
        self.sheet.write(0, 2, 'HeartRate')
        self.sheet.write(0, 3, 'EnergyBreath')
        self.sheet.write(0, 4, 'EnergyHeart')
        self.sheet.write(0, 5, 'ChestMovement')
        self.sheet.write(0, 6, 'time')

        return self.sheet


    def demo(self):
        # configFileName = "./6843_pplcount_debug.cfg"
        configFileName = "{}\\xwr1642_profile_VitalSigns_20fps_Front.cfg".format("C:\\Users\\70639wimoc\\PycharmProjects\\Pyvital-sign")
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

        # constants
        exPhase = 0
        c = 3 * 10 ** 8
        f = 79 * 10 ** 9

        trailer_time = 3920
        Wavelength = c / f
        while True:
            try:
                time.sleep(0.05)  # Sampling frequency of 250 Hz
                # ---------------------------------------vital sign---------------------------------------------------------------------
                Blist, Hlist, BNlist, HNlist, numframes, PHlist, isnull = MainWindow.readAndParseData(Dataport)

                # print(isnull)
                if isnull == 0 and numframes != []:
                    for i in range(len(numframes)):
                        numframe = numframes[i]
                        fHlist = Hlist[i]
                        fBlist = Blist[i]
                        fHNlist = HNlist[i]
                        fBNlist = BNlist[i]

                        fPHlist = PHlist[i]
                        chestmovement = ((PHlist[i] - exPhase) / (4 * math.pi)) / Wavelength
                        exPhase = PHlist[i]

                        write_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        sheet.write(numframe, 0, numframe)
                        sheet.write(numframe, 1, round(fBlist))
                        sheet.write(numframe, 2, round(fHlist))
                        sheet.write(numframe, 3, fBNlist)
                        sheet.write(numframe, 4, fHNlist)
                        sheet.write(numframe, 5, chestmovement)
                        sheet.write(numframe, 6, write_time)

                        # if numframe == 200:
                        #     os.system("start C:\\Users\\asd78\\PycharmProjects\\Pyvital-sign\\soundeffect\\rivier_20s.mp3")
                        # if numframe ==450:
                        #     os.system("start C:\\Users\\asd78\\PycharmProjects\\Pyvital-sign\\soundeffect\\whistle.mp3")

                        self.book.save(r'.\{}.xls'.format(savename))

                        # print("frames:{}, h:{}, b:{}".format(numframe,round(fHlist),round(fBlist)))
                        self.ui.lcdNumber.setDigitCount(len(str(round(fHlist))))
                        self.ui.lcdNumber.display(round(fHlist))
                        self.ui.lcdNumber_2.setDigitCount(len(str(round(fBlist))))
                        self.ui.lcdNumber_2.display(round(fBlist))
                        self.ui.lcdNumber_3.setDigitCount(len(str(numframe)))
                        self.ui.lcdNumber_3.display(numframe)

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

                        # if numframe == 80 + trailer_time:
                        #     Dataport.close()  # 清除序列通訊物件
                        #     CLIport.write(('sensorStop\n').encode())
                        #     CLIport.close()
                        #     print("'sensorStop\n'")
                        #     app.closeAllWindows()
                        #     break
                        #     sys.exit()

                else:
                    continue
            except:
                Dataport.read(Dataport.in_waiting)
                print("Frames:{} Unexpected error:{} bufferlength:{},".format(numframe, sys.exc_info()[0],
                                                                              len(Dataport.read(Dataport.in_waiting))))
                continue


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    sys.exit(app.exec_())
