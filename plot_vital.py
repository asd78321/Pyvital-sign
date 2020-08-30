import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# constants
# 0:Frames	1:BreathingRate	2:HeartRate	3:EnergyBreath	4:EnergyHeart	5:ChestMovement	6:time




def plot_stata(vital_file,Breath_data,Heart_data):
    time_series = np.arange(len(vital_file)) + 1
    plt.plot(time_series, Breath_data, color='red', label='Breath')
    plt.plot(time_series, Heart_data, color='blue', label='Heart')
    plt.legend()
    plt.grid()
    plt.show()


def main():
    filename = './vital.xls'
    vital = np.array(pd.read_excel(filename))
    Breath_data = vital[:, 1]
    Heart_data = vital[:, 2]
    plot_stata(vital,Breath_data,Heart_data)

if __name__ == "__main__":
    main()