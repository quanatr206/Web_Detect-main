import platform
import psutil
import json
import GPUtil
import cpuinfo


class SystemInfoService:
    @staticmethod
    def get_system_info():
        """
        Thu thập thông tin hệ thống của máy tính người dùng
        """
        system_info = {
            "os": {
                "system": platform.system(),
                "version": platform.version(),
                "release": platform.release(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            },
            "cpu": {
                "brand": cpuinfo.get_cpu_info().get("brand_raw", "Unknown"),
                "cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "usage_percent": psutil.cpu_percent(),
            },
            "memory": {
                "total": round(psutil.virtual_memory().total / (1024**3), 2),  # GB
                "available": round(
                    psutil.virtual_memory().available / (1024**3), 2
                ),  # GB
                "used": round(psutil.virtual_memory().used / (1024**3), 2),  # GB
                "percent": psutil.virtual_memory().percent,
            },
            "disk": {
                "total": round(psutil.disk_usage("/").total / (1024**3), 2),  # GB
                "used": round(psutil.disk_usage("/").used / (1024**3), 2),  # GB
                "free": round(psutil.disk_usage("/").free / (1024**3), 2),  # GB
                "percent": psutil.disk_usage("/").percent,
            },
        }

        # Lấy thông tin GPU nếu có
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                system_info["gpu"] = []
                for gpu in gpus:
                    system_info["gpu"].append(
                        {
                            "name": gpu.name,
                            "driver": gpu.driver,
                            "memory_total": round(gpu.memoryTotal / 1024, 2),  # GB
                            "memory_used": round(gpu.memoryUsed / 1024, 2),  # GB
                            "memory_free": round(gpu.memoryFree / 1024, 2),  # GB
                            "temperature": gpu.temperature,
                            "load": gpu.load * 100,  # Convert to percentage
                        }
                    )
        except Exception as e:
            system_info["gpu"] = {"error": str(e)}

        return system_info
