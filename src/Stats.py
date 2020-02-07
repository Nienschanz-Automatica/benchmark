import os
import sys
import psutil
import subprocess
import pandas as pd
from time import sleep


class CpuStatsListener():
    def __init__(self, log_dir, save_every_minutes):
        self.devices = []
        self.log_file_name = os.path.join(log_dir, "CPU", "cpu.xlsx")
        self.save_every_minutes = save_every_minutes
        self.saved = False

    def ready_to_save(self):
        seconds = self.save_every_minutes * 60
        dst_records_num = int(seconds // 5)
        if len(self.devices):
            return len(self.devices[0].util) == dst_records_num
        else:
            return False

    def info(self):
        if len(self.devices):
            print("CPU INFO:")
        for device in self.devices:
            device.info()

    def clear_devices_data(self):
        for device in self.devices:
            device.clear_fields()

    def get_statistic(self):
        df = pd.DataFrame()
        for device in self.devices:
            device_data = device.get_data_dict()
            new_df = pd.DataFrame(device_data)
            df = df.append(new_df, ignore_index=True)
        df = df.sort_values(by=["time", "name"])
        return df

    def update(self, update_time):
        self.update_devices_list()
        self.update_cpu_usage()
        self.update_cpu_temperature()
        self.update_time(update_time)
        if self.ready_to_save():
            statistic = self.get_statistic()
            self.save_statistic(statistic)
            self.clear_devices_data()

    def save_statistic(self, statistic):
        if not self.saved:
            statistic.to_excel(self.log_file_name)
            self.saved = True
        else:
            old_statistic = pd.read_excel(self.log_file_name, usecols=lambda x: 'Unnamed' not in x)
            full_statistic = old_statistic.append(statistic)
            full_statistic.to_excel(self.log_file_name)

    def update_time(self, update_time):
        for device in self.devices:
            device.update_time(update_time)

    def update_devices_list(self):
        if not len(self.devices):
            cpu_usage = psutil.cpu_percent(percpu=True)
            devices_names = ["cpu{}".format(i+1) for i in range(len(cpu_usage))]
            self.devices = [Device(name) for name in devices_names]

    def update_cpu_usage(self):
        cpu_usage = psutil.cpu_percent(percpu=True)
        for device, usage in zip(self.devices, cpu_usage):
            device.update_util(usage)

    def update_cpu_temperature(self):
        temperature_data = psutil.sensors_temperatures()
        cores_data = temperature_data["coretemp"]
        actual_temperature = self.get_only_cores_temperature(cores_data)
        if len(actual_temperature) == len(self.devices):
            for device, temperature in zip(self.devices, actual_temperature):
                device.update_temperature(temperature)
        else:
            cores_per_device = len(self.devices) / len(actual_temperature)
            cores_per_device = int(cores_per_device)
            for i in range(cores_per_device):
                for device, temperature in zip(self.devices[i::cores_per_device], actual_temperature):
                    device.update_temperature(temperature)

    def get_only_cores_temperature(self, cores_data):
        cores_current_temperature = [data.current for data in cores_data]
        if len(cores_current_temperature) == len(self.devices):
            return cores_current_temperature
        else:
            labels = [data.label for data in cores_data]
            actual_temperature = []
            for label, temperature in zip(labels, cores_current_temperature):
                if "core" in label.lower():
                    actual_temperature.append(temperature)
            return actual_temperature


class HDDLStatsListener():
    def __init__(self, path_to_hddldaemon, log_dir, save_every_minutes):
        self.log_file_name = os.path.join(log_dir, "HDDL", "hddl.xlsx")
        self.save_every_minutes = save_every_minutes
        self.saved = False
        self.devices = []
        start_daemon_command = os.path.join(path_to_hddldaemon, "hddldaemon")
        self.running = False
        print("Please wait. Loading may take a few minutes.")
        self.daemon = self.init_daemon(start_daemon_command)
        self.wait_for_loading()
        self.key_words = ["deviceId", "util%", "thermal", "Time:"]
        self.data_dtypes = [str, float, float, str]
        self.key_words_idx = 0

    def ready_to_save(self):
        seconds = self.save_every_minutes * 60
        dst_records_num = int(seconds // 5)
        if len(self.devices):
            return len(self.devices[0].util) == dst_records_num
        else:
            return False

    def info(self):
        if len(self.devices):
            print("HDDL INFO:")
        for device in self.devices:
            device.info()

    def clear_devices_data(self):
        for device in self.devices:
            device.clear_fields()

    def get_statistic(self):
        df = pd.DataFrame()
        for device in self.devices:
            device_data = device.get_data_dict()
            new_df = pd.DataFrame(device_data)
            df = df.append(new_df)
        df = df.sort_values(by=["time", "name"])
        return df

    def update(self):
        full_update = False
        current_key_word = self.get_current_key_word()
        current_dtype = self.get_current_dtype()
        daemon_output = self.read_daemon_info()
        is_actual_data, data = self.parse_hddl_daemon_outout(daemon_output, current_key_word, current_dtype)
        if is_actual_data:
            full_update = self.do_update_by_key(current_key_word, data)
            self.update_key_words_idx()
        if full_update:
            if self.ready_to_save():
                statistic = self.get_statistic()
                self.save_statistic(statistic)
                self.clear_devices_data()
        return full_update, data

    def do_update_by_key(self, update_key, data):
        update_dict = {"deviceId": self.update_devices_list,
                        "util%": self.update_devices_utilisation,
                        "thermal": self.update_devices_temperature,
                        "Time:": self.update_time}
        return update_dict[update_key](data)

    def update_time(self, update_time):
        for device in self.devices:
            device.update_time(update_time)
        full_update = True
        return full_update

    def update_devices_list(self, data):
        if not len(self.devices):
            self.devices = [Device(device_name) for device_name in data]
        full_update = False
        return full_update

    def update_devices_utilisation(self, data):
        for device, util in zip(self.devices, data):
            device.update_util(util)
        full_update = False
        return full_update

    def update_devices_temperature(self, data):
        for device, temperature in zip(self.devices, data):
            device.update_temperature(temperature)
        full_update = False
        return full_update

    def save_statistic(self, statistic):
        if not self.saved:
            statistic.to_excel(self.log_file_name, index=False)
            self.saved = True
        else:
            old_statistic = pd.read_excel(self.log_file_name, usecols=lambda x: 'Unnamed' not in x)
            full_statistic = old_statistic.append(statistic)
            full_statistic.to_excel(self.log_file_name)

    def parse_hddl_daemon_outout(self, data, key_word, dst_dtype=None):
        if key_word in data:
            if key_word == "Time:":
                splited_data = data.split(" ")
                splited_data = splited_data[-1]
                splited_data = splited_data.split(".")
                return  True, splited_data[0]
            splited_data = self.split_str_data(data)
            splited_data = self.remove_label_from_data(splited_data)
            if key_word == "thermal":
                splited_data = [val[:-3] for val in splited_data] # removing "(0)" and "(1)"
            if not isinstance(dst_dtype, type(None)):
                splited_data = self.convert_str_to_dtype(splited_data, dst_dtype)
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

    def read_daemon_info(self):
        data = self.daemon.stdout.readline()
        str_data = data.decode(encoding="utf-8")
        return str_data

    def animate_loading(self, loading_counter):
        animation = "|/-\\"
        sys.stdout.write("\r" + "Loading " + animation[loading_counter])
        loading_counter += 1
        if loading_counter == len(animation):
            loading_counter = 0
        sys.stdout.flush()
        sleep(0.05)
        return loading_counter

    def split_str_data(self, str_data):
        splited_data = str_data.split("|")
        splited_data = [item.strip("% \n") for item in splited_data]
        splited_data = [item for item in splited_data if len(item)]
        return splited_data

    def remove_label_from_data(self, data):
        return data[1:]

    def convert_str_to_dtype(self, list_of_strings, dtype):
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

    def get_data_dict(self):
        data_dict = {"time": self.time,
                     "name": self.name,
                     "utilisation": self.util,
                     "temperature": self.temperature}
        return data_dict

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
        if len(self.util):
            print("\tdevice {}".format(self.name))
            print("\t\tutilisation: {}".format(self.util[-1]))
            print("\t\ttemperature: {}".format(self.temperature[-1]))
            print("\t\ttime: {}".format(self.time[-1]))


class RamListener():
    def __init__(self, log_dir, save_every_minutes):
        self.log_file_name = os.path.join(log_dir, "RAM", "ram.xlsx")
        self.save_every_minutes = save_every_minutes
        self.saved = False
        self.total = None
        self.available = []
        self.used = []
        self.percents = []
        self.time = []

    def ready_to_save(self):
        seconds = self.save_every_minutes * 60
        dst_records_num = int(seconds // 5)
        if len(self.available):
            return len(self.available) == dst_records_num
        else:
            return False

    def get_statistic(self):
        data_dict = {"time": self.time,
                     "total": self.total,
                     "available": self.available,
                     "used": self.used,
                     "percents": self.percents}
        df = pd.DataFrame(data_dict)
        df = df.sort_values("time")
        return data_dict

    def save_statistic(self, statistic):
        if not self.saved:
            statistic.to_excel(self.log_file_name, index=False)
            self.saved = True
        else:
            old_statistic = pd.read_excel(self.log_file_name, usecols=lambda x: 'Unnamed' not in x)
            full_statistic = old_statistic.append(statistic)
            full_statistic.to_excel(self.log_file_name)

    def update(self, time):
        memory_data = psutil.virtual_memory()
        self.update_total(memory_data.total)
        self.update_available(memory_data.available)
        self.update_used(memory_data.used)
        self.update_percents(memory_data.percent)
        self.update_time(time)
        if self.ready_to_save():
            ram_data = self.get_statistic()
            self.save_statistic(ram_data)
            self.clear_data()

    def bytes_to_readable(self, size, precision=2):
        suffixes = ['B', 'KB', 'MB', 'GB']
        suffixIndex = 0
        while size > 1024 and suffixIndex < 3:
            suffixIndex += 1  # increment the index of the suffix
            size = size / 1024.0  # apply the division
        size = round(size, precision)
        return "{} {}".format(size, suffixes[suffixIndex])


    def clear_data(self):
        self.available = []
        self.used = []
        self.percents = []
        self.time = []

    def update_time(self, update_time):
        self.time.append(update_time)

    def update_total(self, value):
        if self.total is None:
            self.total = self.bytes_to_readable(value)

    def update_available(self, val):
        self.available.append(self.bytes_to_readable(val))

    def update_used(self, val):
        self.used.append(self.bytes_to_readable(val))

    def update_percents(self, val):
        self.percents.append(val)

    def info(self):
        if len(self.available):
            print("RAM INFO:")
            print("\ttotal: {}".format(self.total))
            print("\tavailable: {}".format(self.available[-1]))
            print("\tused: {}".format(self.used[-1]))
            print("\tpercents: {}".format(self.percents[-1]))
            print("\ttime: {}".format(self.time[-1]))
