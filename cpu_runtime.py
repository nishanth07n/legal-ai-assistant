import os

CPU_ONLY_ENV = {
    "CUDA_VISIBLE_DEVICES": "",
    "HIP_VISIBLE_DEVICES": "",
    "ROCR_VISIBLE_DEVICES": "",
    "ONEAPI_DEVICE_SELECTOR": "opencl:cpu",
    "SYCL_DEVICE_FILTER": "cpu",
    "PYTORCH_ENABLE_MPS_FALLBACK": "0",
}


def force_cpu_runtime():
    for key, value in CPU_ONLY_ENV.items():
        os.environ.setdefault(key, value)
