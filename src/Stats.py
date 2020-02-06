import os
import sys
import yaml
import psutil
from time import sleep
import subprocess
import pandas as pd
import numpy as np


class CpuStatsListener():
    def __init__(self, log_dir):
        self.devices = []
        self.log_file_name = os.path.join(log_dir, "CPU", "cpu.xlsx")
        self.saved = False

    def info(self):
        print("CPU INFO:")
        for device in self.devices:
            device.info()

    def clear_devices_data(self):
        for device in self.devices:
            device.clear_fields()

    def get_statistic(self):
        df = pd.DataFrame()
        for device in self.devices:
            name = device.name
            time = device.time
            util = np.array(device.util)
            temperature = np.array(device.temperature)
            new_df = pd.DataFrame({"name":name,
                                   "time": time,
                                   "utilisation": util,
                                   "temperature": temperature})
            df = df.append(new_df)
        return df

    def update(self, update_time):
        self.update_cpu_usage()
        self.update_cpu_temperature()
        self.update_time(update_time)
        if len(self.devices[0].util) > 10:
            statistic = self.get_statistic()
            if not self.saved:
                statistic.to_excel(self.log_file_name, index=False)
                self.saved = True
            else:
                old_statistic = pd.read_excel(self.log_file_name, usecols=lambda x: 'Unnamed' not in x)
                full_statistic = old_statistic.append(statistic)
                full_statistic.to_excel(self.log_file_name, index=False)
            self.clear_devices_data()

    def update_time(self, update_time):
        for device in self.devices:
            device.update_time(update_time)

    def update_cpu_usage(self):
        cpu_usage = psutil.cpu_percent(percpu=True)
        if not len(self.devices):
            devices_names = ["cpu{}".format(i+1) for i in range(len(cpu_usage))]
            self.devices = [Device(name) for name in devices_names]
        for device, usage in zip(self.devices, cpu_usage):
            device.update_util(usage)

    def update_cpu_temperature(self):
        temperature_data = psutil.sensors_temperatures()
        cores_data = temperature_data["coretemp"]
        cores_current_temperature = [data.current for data in cores_data]
        if len(cores_current_temperature) == len(self.devices):
            for device, temperature in zip(self.devices, cores_current_temperature):
                device.update_temperature(temperature)
        else:
            labels = [data.label for data in cores_data]
            actual_temperature = []
            for label, temperature in zip(labels, cores_current_temperature):
                if "core" in label.lower():
                    actual_temperature.append(temperature)
            if len(actual_temperature) == len(self.devices):
                for device, temperature in zip(self.devices, actual_temperature):
                    device.update_temperature(temperature)
            else:
                cores_per_device = len(self.devices) / len(actual_temperature)
                cores_per_device = int(cores_per_device)
                for i in range(cores_per_device):
                    for device, temperature in zip(self.devices[i::cores_per_device], actual_temperature):
                        device.update_temperature(temperature)


class HDDLStatsListener():
    def __init__(self, path_to_hddldaemon, log_dir):
        self.log_file_name = os.path.join(log_dir, "HDDL", "hddl.xlsx")
        self.saved = False
        self.devices = []
        start_daemon_command = os.path.join(path_to_hddldaemon, "hddldaemon")
        self.encoding_type = "utf-8"
        self.running = False
        print("Please wait. Loading may take a few minutes.")
        self.daemon = self.init_daemon(start_daemon_command)
        self.wait_for_loading()
        self.key_words = ["deviceId", "util%", "thermal"]
        self.data_dtypes = [str, float, float]
        self.key_words_idx = 0

    def info(self):
        print("HDDL INFO:")
        for device in self.devices:
            device.info()

    def clear_devices_data(self):
        for device in self.devices:
            device.clear_fields()

    def get_statistic(self):
        df = pd.DataFrame()
        for device in self.devices:
            name = device.name
            time = device.time
            util = np.array(device.util)
            temperature = np.array(device.temperature)
            new_df = pd.DataFrame({"name":name,
                               "time": time,
                               "utilisation": util,
                               "temperature": temperature})
            df = df.append(new_df)
        return df

    def update_time(self, update_time):
        for device in self.devices:
            device.update_time(update_time)

    def update(self, update_time):
        full_update = False
        current_key_word = self.get_current_key_word()
        current_dtype = self.get_current_dtype()
        daemon_output = self.read_daemon_info()
        ret, data = self.try_to_grub_data(daemon_output, current_key_word, current_dtype)
        if ret:
            if current_key_word == "deviceId":
                if len(data) != len(self.devices):
                    self.devices = [Device(device_name) for device_name in data]
                self.update_key_words_idx()
            elif current_key_word == "util%":
                for device, util in zip(self.devices, data):
                    device.update_util(util)
                self.update_key_words_idx()
            elif current_key_word == "thermal":
                for device, temperature in zip(self.devices, data):
                    device.update_temperature(temperature)
                self.update_key_words_idx()
                full_update = True
                self.update_time(update_time)
        if full_update:
            if len(self.devices[0].util) > 10:
                statistic = self.get_statistic()
                if not self.saved:
                    statistic.to_excel(self.log_file_name, index=False)
                    self.saved = True
                else:
                    old_statistic = pd.read_excel(self.log_file_name, usecols=lambda x: 'Unnamed' not in x)
                    full_statistic = old_statistic.append(statistic)
                    full_statistic.to_excel(self.log_file_name, index=False)
                self.clear_devices_data()
        return full_update

    def try_to_grub_data(self, data, key_word, dst_dtype=None):
        if key_word in data:
            splited_data = self.split_str_data(data)
            splited_data = self.remove_label_from_data(splited_data)
            if key_word == "thermal":
                splited_data = [val[:-3] for val in splited_data] # removing "(0)"
            if not isinstance(dst_dtype, type(None)):
                splited_data = self.str_to_dtype(splited_data, dst_dtype)
            return True, splited_data
        else:
            return False, None

    def init_daemon(self, command):
        return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

    def wait_for_loading(self):
        ready_key_words = ["SERVICE", "IS", "READY"]
        loading_counter = 0
        while not self.running:
            data = self.read_daemon_info()
            ready_key_words_id_data = [word in data for word in ready_key_words]
            if all(ready_key_words_id_data):
                self.running = True
            else:
                loading_counter = self.animate_loading(loading_counter)
        print("\n")

    def read_daemon_info(self):
        data = self.daemon.stdout.readline()
        str_data = data.decode(encoding=self.encoding_type)
        return str_data

    def animate_loading(self, loading_counter):
        animation = "|/-\\"
        sys.stdout.write("\r" + "Loading " + animation[loading_counter % len(animation)])
        loading_counter += 1
        sys.stdout.flush()
        sleep(0.1)
        return loading_counter

    def split_str_data(self, str_data):
        splited_data = str_data.split("|")
        splited_data = [item.strip("% \n") for item in splited_data]
        splited_data = [item for item in splited_data if len(item)]
        return splited_data

    def remove_label_from_data(self, data):
        return data[1:]

    def str_to_dtype(self, list_of_strings, dtype):
        dst_list = [dtype(val) for val in list_of_strings]
        return dst_list

    def update_key_words_idx(self):
        self.key_words_idx += 1
        if self.key_words_idx >= len(self.key_words):
            self.key_words_idx = 0

    def get_current_key_word(self):
        return self.key_words[self.key_words_idx]

    def get_current_dtype(self):
        return self.data_dtypes[self.key_words_idx]


class Device():
    def __init__(self, name):
        self.name = name
        self.util = []
        self.temperature = []
        self.time = []

    def clear_fields(self):
        self.util = []
        self.temperature = []
        self.time = []

    def update_time(self, update_time):
        self.time.append(update_time)

    def update_util(self, util):
        self.util.append(util)

    def update_temperature(self, temperature):
        self.temperature.append(temperature)

    def info(self):
        print("\t{}".format(self.name))
        print("\tutilisation: {}".format(self.util))
        print("\ttemperature: {}".format(self.temperature))
        print("\ttime: {}".format(self.time))

class RamListener():
    def __init__(self, log_dir):
        self.log_dir = log_dir
        self.total = None
        self.available = []
        self.used = []
        self.percents = []
        self.time = []

    def update(self):
        pass

    def update_time(self, update_time):
        self.time.append(update_time)

    def update_total(self, value):
        self.total = value

    def update_available(self, val):
        self.available.append(val)

    def update_used(self, val):
        self.used.append(val)

    def update_percents(self, val):
        self.percents.append(val)

    def info(self):
        print("RAM INFO:")
        print("\ttotal: {}".format(self.total))
        print("\tavailable: {}".format(self.available))
        print("\tused: {}".format(self.used))
        print("\tpercents: {}".format(self.percents))
        print("\ttime: {}".format(self.time))
