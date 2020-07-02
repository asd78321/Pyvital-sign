import serial
import time
import numpy as np
import struct
import xlrd,xlwt
import sys
sys.path.append('C:\\Users\\asd78\\PycharmProjects\\Pyvital-sign')
from LABEL import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets

global CLIport, Dataport
CLIport = {}
Dataport = {}
byteBuffer = np.zeros(2**15,dtype = 'uint8')
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
            dataPort = serial.Serial(dataPortName, 921600,timeout=0.04)
        except serial.SerialException as se:
            print("Serial Port 0ccupied,error = ")
            print(str(se))
            return

        config = [line.rstrip('\r\n') for line in open(configFileName)]
        for i in config:
            cliPort.write((i+'\n').encode())
            print(i)
            time.sleep(0.08)
        print("-----------------------------------------------------------------------")
        return cliPort,dataPort


    def readAndParseData(Dataport):
        global byteBuffer, byteBufferLength

        # Constants
        magicWord = [2, 1, 4, 3, 6, 5, 8, 7]

        readBuffer = Dataport.read(Dataport.in_waiting)
        byteVec=np.frombuffer(readBuffer,dtype='uint8')
        framedata=[]
        # print(len(byteVec))
        # --------------------------------For vital sign-----------------------------------------------------------------------
        if np.all(byteVec[0:8] == magicWord):
            if len(readBuffer) % 288 == 0:
                Blist = []
                Hlist = []
                numframes = []
                for i in range(len(readBuffer)//288):
                    subFrameNum = struct.unpack('I',readBuffer[i*288+20:i*288+24])[0]
                    # Tlvtype = struct.unpack('I',readBuffer[i*288+40:i*288+44])[0]
                    # Tlvlen = struct.unpack('I',readBuffer[i*288+44:i*288+48])[0]
                    BreathEst_FFT = struct.unpack('f',readBuffer[i*288+48+44:i*288+48+48])[0]# 48:frameHeader and type/len bytes 288:maxPacketlen
                    HeartEst_FFT = struct.unpack('f',readBuffer[i*288+48+28:i*288+48+32])[0]
                    # print("numFrame: ",subFrameNum,"Breath: ",round(BreathEst_FFT),'s/min',"Heart: ",round(HeartEst_FFT),'s/min')
                    Blist.append(BreathEst_FFT)
                    Hlist.append(HeartEst_FFT)
                    numframes.append(subFrameNum)
                isnull=0
                return Blist,Hlist,numframes,isnull
        else:
            isnull=1
            return [],[],[],isnull

    def saveData(self):
        book = xlwt.Workbook(encoding='utf-8',style_compression=0)
        self.book=book
        self.sheet = self.book.add_sheet('test',cell_overwrite_ok=True)


        self.sheet.write(0,0,'Frames')
        self.sheet.write(0,1,'BreathingRate')
        self.sheet.write(0,2,'HeartRate')

        return self.sheet

    def exit_ui(self):
        self.book.save(r'.\test.xls')




    def demo(self):
        # configFileName = "./6843_pplcount_debug.cfg"
        configFileName = "./xwr1642_profile_VitalSigns_20fps_Front.cfg"
        dataPortName = "COM22"
        userPortName = "COM12"


        # # Configurate the serial port
        CLIport, Dataport = MainWindow.serialConfig(configFileName, dataPortName, userPortName)
        drawh_y=np.zeros([50])
        drawb_y = np.zeros([50])
        draw_x=range(1,51)
        draw_test=np.random.randint(4, size=50)
        sheet=MainWindow.saveData(self)
        self.ui.graphicsView.setYRange(0,40,padding=0)
        self.ui.graphicsView_2.setYRange(0,250,padding=0)
        frame_count=0
        while True:
            try:
                # ---------------------------------------vital sign---------------------------------------------------------------------
                Blist,Hlist,numframes,isnull = MainWindow.readAndParseData(Dataport)
                # print(isnull)
                if isnull ==0 and numframes!=[]:
                    for i in range(len(numframes)):
                        numframe = numframes[i]
                        fHlist = Hlist[i]
                        fBlist = Blist[i]

                        sheet.write(numframe, 0, numframe)
                        sheet.write(numframe, 1, round(fBlist))
                        sheet.write(numframe, 2, round(fHlist))
                        self.book.save(r'.\test.xls')


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
                        if numframe%50==0:
                            count=50
                        else:
                            count=numframe%50
                        drawb_y[count - 1] = fBlist
                        drawh_y[count - 1] = fHlist
                        if numframe % 1 == 0:
                            self.ui.graphicsView.clear()
                            self.ui.graphicsView_2.clear()
                            self.ui.graphicsView.plot(draw_x, drawb_y,color='r')
                            self.ui.graphicsView_2.plot(draw_x, drawh_y,color='r')

                            # print("f:{},sum:{},b:{},last:{}".format(numframe,sum(drawb_y[90:99]),fBlist,drawb_y[99]))


                        app.processEvents()

                        # time.sleep(0.1)  # Sampling frequency of 30 Hz
                else:
                    continue
            except KeyboardInterrupt:
                Dataport.close()  # 清除序列通訊物件
                CLIport.write(('sensorStop\n').encode())
                CLIport.close()
                self.book.save(r'.\test.xls')
                print('再見！')





if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    sys.exit(app.exec_())

