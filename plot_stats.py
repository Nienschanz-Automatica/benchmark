import os
import yaml
from src.Plotters import RAMPlotter, DevicesDataPlotter

with open("plotting.cfg", "r") as stream:
    cfg = yaml.safe_load(stream)

logs_dir = cfg["actual_logs_dir"]

for dir in os.listdir(logs_dir):
    if dir == "CPU":
        csv_file = [file for file in os.listdir(os.path.join(logs_dir, dir)) if file[-4:] == ".csv"][0]
        csv_file = os.path.join(logs_dir, dir, csv_file)
        cpu_plotter = DevicesDataPlotter(csv_file)
        cpu_plotter.parse_data()
        cpu_utilisation_fig = cpu_plotter.plot_utilisation("dots")
        cpu_temperature_fig = cpu_plotter.plot_temperature()
        cpu_plotter.save_figure(cpu_utilisation_fig, "cpu_util.png")
        cpu_plotter.save_figure(cpu_temperature_fig, "cpu_temp.png")

    elif dir == "MYRIAD":
        hddl_file = [file for file in os.listdir(os.path.join(logs_dir, dir)) if file[-4:] == ".csv"][0]
        hddl_file = os.path.join(logs_dir, dir, hddl_file)

        hddl_plotter = DevicesDataPlotter(hddl_file)
        hddl_plotter.parse_data()
        hddl_utilisation_fig = hddl_plotter.plot_utilisation("line")
        hddl_temperature_fig = hddl_plotter.plot_temperature()

        hddl_plotter.save_figure(hddl_utilisation_fig, "hddl_util.png")
        hddl_plotter.save_figure(hddl_temperature_fig, "hddl_temp.png")


    elif dir == "RAM":
        ram_file = [file for file in os.listdir(os.path.join(logs_dir, dir)) if file[-4:] == ".csv"][0]
        ram_file = os.path.join(logs_dir, dir, ram_file)
        ram_plotter = RAMPlotter(ram_file)
        ram_plotter.parse_data()
        ram_utilisation_fig = ram_plotter.plot_utilisation()
        ram_plotter.save_figure(ram_utilisation_fig, "ram_util.png")

