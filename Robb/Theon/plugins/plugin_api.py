from linux import sysinfo,load,cpu_mac,cpu,memory,network,host_alive

def LinuxSysInfo():
    return sysinfo.collect()

def WindowsSysInfo():
    from windows import sysinfo as win_sysinfo
    return win_sysinfo.collect()

def gGetLinuxCpuStatus():
    return cpu.monitor()

def host_alive_check():
    return host_alive.monitor()

def GetLinuxMemstatus():
    return memory.monitor()

def GetMacCPU():
    return cpu_mac.monitor()

def GetLinuxNetworkStatus():
    return network.monitor()

# def get_memory_info():
#     return memory.monitor()