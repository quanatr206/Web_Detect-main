import platform
import psutil
import GPUtil
import cpuinfo


def check_system_configuration():
    """Check and return of Information System"""
    system_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "cpu": cpuinfo.get_cpu_info()["brand_raw"],
        "ram_total": round(psutil.virtual_memory().total / (1024**3), 2),  # GB
        "ram_available": round(psutil.virtual_memory().available / (1024**3), 2),  # GB
    }

    # Kiểm tra GPU nếu có
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            system_info["gpu"] = []
            for gpu in gpus:
                system_info["gpu"].append(
                    {
                        "name": gpu.name,
                        "memory_total": gpu.memoryTotal,
                        "memory_free": gpu.memoryFree,
                    }
                )
        else:
            system_info["gpu"] = None
    except:
        system_info["gpu"] = None

    return system_info


def is_system_compatible_for_trt(system_info):
    """Check if your system is compatible with running TensorRT models"""
    # Yêu cầu tối thiểu
    min_ram = 4  # GB

    # Kiểm tra RAM
    if system_info["ram_total"] < min_ram:
        return False, "Khong du Ram"

    # Kiểm tra GPU (TensorRT cần NVIDIA GPU)
    if system_info["gpu"] is None:
        return False, "Khong tim thay GPU NVIDIA"

    return True, "He thong  du cau hinh"


if __name__ == "__main__":
    try:
        print("Cheking System...")
        system_info = check_system_configuration()
        print("Information System:", system_info)
        compatible, message = is_system_compatible_for_trt(system_info)
        print(f"Results: {compatible}, {message}")
    except Exception as e:
        print(f"Error: {str(e)}")
