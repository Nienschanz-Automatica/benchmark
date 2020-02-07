#TODO config files for benchmark and plotters

from sys import exit
from signal import signal, SIGINT

from src.Threads import ListenersThread
from src.benchmark_tools import *


if __name__ == "__main__":
    if "logs" not in os.listdir(os.getcwd()):
        os.mkdir("logs")
    os.mkdir(current_logs_dir)
    for device in devices:
        os.mkdir(os.path.join(current_logs_dir, device))
    os.mkdir(os.path.join(current_logs_dir, "RAM"))

    listeners_list = build_listeners(devices)
    listeners_thread = ListenersThread(listeners_list)

    listeners_thread.start()

    executors_threads_list = build_executors(xml_file, bin_file, devices, request_num)
    for executor_thread in executors_threads_list:
        executor_thread.start()

    def handler(signal_received, frame):
        print("\nWhait untill becnchmark is stopping!")
        listeners_thread.stop()
        listeners_thread.join()
        for executor_thread in executors_threads_list:
            executor_thread.stop()
            executor_thread.join()
            executor_thread.del_executor()
        exit(0)

    signal(SIGINT, handler)
