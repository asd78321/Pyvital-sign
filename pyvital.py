import serial
def serialConfig(configFileName, dataPortName, userPortName):
    try:
        cliPort = serial.serial(userPortName, 115200)
        dataPort = serial.serial(dataPortName, 921600)
    except serial.SerialException as se:
        print("Serial Port 0ccupied,error = ")
        print(str(se))
        return
    
    config = [line.rstrip('\r\n') for line in open(configFileName)]
    for i in config:
        cliPort.write((i+'\n').encode())
        print(i)

    return cliPort,dataPort

def main():
    serialConfig("./6843_pplcount_debug.cfg","COM22","COM12")

if __name__ == "__main__":
    main()