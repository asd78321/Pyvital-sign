import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# constants
# 0:Frames	1:BreathingRate	2:HeartRate	3:EnergyBreath	4:EnergyHeart	5:ChestMovement	6:time




def plot_stata(vital_file,Breath_data,Heart_data,Heart_Energy_data):
    label_list = ['Breath','Heart','Heart_Energy_data']
    time_series = np.arange(len(vital_file)) + 1
    data_list = []
    data_list.append(Breath_data)
    data_list.append(Heart_data)
    # data_list.append(ChestMovement)
    data_list.append(Heart_Energy_data)
    print("data classes:{}".format(np.array(data_list).shape[0]))
    for i in range(np.array(data_list).shape[0]):
        plt.plot(time_series, data_list[i], label=label_list[i])

    # plt.axvline(60,color = 'red')
    plt.xlabel('Frame(s)')
    plt.ylabel('BPM(s)')
    plt.legend(loc = 2)
    plt.grid()
    plt.show()


def main():
    filename = './vital.xls'
    vital = np.array(pd.read_excel(filename))
    # vital = vital[60:,:]
    Breath_data = vital[:, 1]
    Heart_data = vital[:, 2]
    chest_data = vital[:,5]
    Heart_Energy_data = vital[:,4]
    normal_HE = Heart_Energy_data*100/max(Heart_Energy_data)
    plot_stata(vital,Breath_data,Heart_data,normal_HE)

if __name__ == "__main__":
    main()