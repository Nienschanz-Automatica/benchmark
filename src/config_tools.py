def parse_devices(devices_str):
    devices = devices_str.split(",")
    devices = [device.strip(" ") for device in devices]
    return devices