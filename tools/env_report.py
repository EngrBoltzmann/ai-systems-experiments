"""Record hardware and software details for an experiment."""
import datetime
import json
import platform
import sys
from importlib import metadata

import psutil


def cpu_name():
    """Exact CPU model name (Windows registry), with a fallback."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
        )
        return winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
    except Exception:
        return platform.processor()


def package_versions():
    return {d.metadata["Name"]: d.version for d in metadata.distributions()}


def main():
    report = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "os": platform.platform(),
        "python": sys.version,
        "cpu_model": cpu_name(),
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "ram_total_gib": round(psutil.virtual_memory().total / 1024**3, 2),
        "packages": package_versions(),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()