import pandas as pd
from numpy import max as npmax
from matplotlib import pyplot as plt


class DevicesDataPlotter():
    def __init__(self, path_to_csv_file):
        self.data = pd.read_csv(path_to_csv_file)
        self.devices_names = []
        self.utils_data = []
        self.temperature_data = []
        self.time = []

    def parse_data(self):
        self.devices_names = self.data["name"].unique()
        self.time = self.str_time_data_to_minutes()
        for device in self.devices_names:
            utilisation = self.data[self.data["name"] == device]["utilisation"].values
            temperature = self.data[self.data["name"] == device]["temperature"].values
            self.utils_data.append(utilisation)
            self.temperature_data.append(temperature)

    def time_str_to_min(self, time_str):
        ftr = [3600,60,1]
        return sum([a*b / 60 for a,b in zip(ftr, map(int, time_str.split(':')))])

    def str_time_data_to_minutes(self):
        time = self.data["time"].unique()
        time_in_min = [self.time_str_to_min(t) for t in time]
        min_time = min(time_in_min)
        return [t - min_time for t in time_in_min]

    def plot_utilisation(self, plot_type="line"):
        fig = plt.figure(figsize=(15, 10))
        plt.ylim(ymin= -10, ymax=npmax(self.utils_data)+10)
        plt.title("Devices utilisation (%)")
        plt.ylabel("Devices utilisation (%)")
        plt.xlabel("Time (min)")
        for name, util in zip(self.devices_names, self.utils_data):
            if plot_type == "line":
                plt.plot(self.time, util, label=name)
            else:
                plt.scatter(self.time, util, label=name)
            plt.legend(bbox_to_anchor=(1.00, 1.0), loc='upper left')
        return fig

    def plot_temperature(self, plot_type="line"):
        fig = plt.figure(figsize=(15, 10))
        plt.ylim(ymin= -10, ymax=npmax(self.temperature_data)+10)
        plt.title("Devices temperature (°C)")
        plt.ylabel("Devices temperature (°C)")
        plt.xlabel("Time (min)")
        for name, temp in zip(self.devices_names, self.temperature_data):
            if plot_type == "line":
                plt.plot(self.time, temp, label=name)
            else:
                plt.scatter(self.time, temp, label=name)
            plt.legend(bbox_to_anchor=(1.00, 1.0), loc='upper left')
        return fig

    def save_figure(self, figure, file_name):
        figure.savefig(file_name, dpi=200)


class RAMPlotter():
    def __init__(self, path_to_csv_file):
        self.data = pd.read_csv(path_to_csv_file)
        self.utils_data = []
        self.time = []

    def parse_data(self):
        self.time = self.str_time_data_to_minutes()
        self.utils_data = self.data["percents"]

    def time_str_to_min(self, time_str):
        ftr = [3600, 60, 1]
        return sum([a * b / 60 for a, b in zip(ftr, map(int, time_str.split(':')))])

    def str_time_data_to_minutes(self):
        time = self.data["time"].unique()
        time_in_min = [self.time_str_to_min(t) for t in time]
        min_time = min(time_in_min)
        return [t - min_time for t in time_in_min]

    def plot_utilisation(self, plot_type="line"):
        fig = plt.figure(figsize=(15, 10))
        plt.ylim(ymin= -10, ymax=110)
        plt.title("RAM usage (%)")
        plt.ylabel("RAM usage (%)")
        plt.xlabel("Time (min)")
        if plot_type == "line":
            plt.plot(self.time, self.utils_data, label="usage (%)")
        else:
            plt.scatter(self.time, self.utils_data, label="usage (%)")
        plt.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left')
        return fig

    def save_figure(self, figure, file_name):
        figure.savefig(file_name, dpi=200)