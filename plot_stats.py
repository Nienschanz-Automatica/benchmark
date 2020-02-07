from src.Plotters import RAMPlotter, DevicesDataPlotter

ram_csv = "/home/user/Desktop/07-02-2020|14:33:58/RAM/ram.csv"
hddl_csv = "/home/user/Desktop/07-02-2020|14:33:58/HDDL/hddl.csv"
cpu_csv = "/home/user/Desktop/07-02-2020|14:33:58/CPU/cpu.csv"

hddl_plotter = DevicesDataPlotter(hddl_csv)
hddl_plotter.parse_data()
hddl_utilisation_fig = hddl_plotter.plot_utilisation("line")
hddl_temperature_fig = hddl_plotter.plot_temperature()

hddl_plotter.save_figure(hddl_utilisation_fig, "hddl_util.png")
hddl_plotter.save_figure(hddl_temperature_fig, "hddl_temp.png")


cpu_plotter = DevicesDataPlotter(cpu_csv)
cpu_plotter.parse_data()
cpu_utilisation_fig = cpu_plotter.plot_utilisation("dots")
cpu_temperature_fig = cpu_plotter.plot_temperature()
cpu_plotter.save_figure(cpu_utilisation_fig, "cpu_util.png")
cpu_plotter.save_figure(cpu_temperature_fig, "cpu_temp.png")

ram_plotter = RAMPlotter(ram_csv)
ram_plotter.parse_data()
ram_utilisation_fig = ram_plotter.plot_utilisation()
ram_plotter.save_figure(ram_utilisation_fig, "ram_util.png")
