#!/opt/conda/bin/python
import psutil
import time

last_update = 0
descriptors = list()
cbsensor_stats = dict()

MIN_UPDATE_INTERVAL = 30  # seconds
METRIC_PREFIX = "cbsensor_"
CB_PROCESS_NAMES = ["cbsensor", "cbdaemon", "python"]
GANGLIA_GROUPS = "cbsensor"
METRIC_DESCRIPTORS = {
    "cpu_percent": {
        "units": "%",
        "value_type": "double",
        "slope": "both",
        "format": "%.2f",
        "description": "CPU usage in percent",
        "groups": GANGLIA_GROUPS,
    },
    "memory_percent": {
        "units": "%",
        "value_type": "double",
        "slope": "both",
        "format": "%.2f",
        "description": "Memory usage in percent",
        "groups": GANGLIA_GROUPS,
    },
    "nproc": {
        "units": "processes",
        "value_type": "uint",
        "slope": "both",
        "format": "%u",
        "description": "Number of processes",
        "groups": GANGLIA_GROUPS,
    },
}


def get_cbsensor_metrics():
    global last_update
    global cbsensor_stats

    now = time.time()
    if now - last_update < MIN_UPDATE_INTERVAL:
        return True
    last_update = now

    selected_processes = [proc for proc in psutil.process_iter() if proc.name() in CB_PROCESS_NAMES]
    cbsensor_stats = dict(
        nproc=len(selected_processes),
        cpu_percent=sum(proc.cpu_percent() for proc in selected_processes),
        memory_percent=sum(proc.memory_percent() for proc in selected_processes),
    )
    return True


def get_cbsensor_metric(name):
    global cbsensor_stats
    if METRIC_PREFIX in name:
        name = name.replace(METRIC_PREFIX, "")
    return cbsensor_stats.get(name, 0)


def metric_init(params):
    global cbsensor_stats
    global descriptors

    get_cbsensor_metrics()

    descriptors = list()
    for name, metric in cbsensor_stats.items():
        metric = METRIC_DESCRIPTORS[name].copy()
        metric["name"] = METRIC_PREFIX + name
        metric["call_back"] = get_cbsensor_metric
        descriptors.append(metric)
    return descriptors


def metric_cleanup():
    pass


# if __name__ == '__main__':
#     metric_init({})
#     for d in descriptors:
#         v = d['call_back'](d['name'])
#         print(f"value for {d['name']} is {v}")
