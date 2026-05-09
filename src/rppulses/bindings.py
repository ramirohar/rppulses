import ctypes
import numpy as np
from numpy import typing as npt
from pathlib import Path

_zcopy_pulses = ctypes.CDLL(Path(__file__).parent / "zcopy_pulses.so")

_zcopy_pulses.count.restype = ctypes.c_size_t  # count
_zcopy_pulses.count.argtypes = [
    ctypes.POINTER(ctypes.c_int16),  # data
    ctypes.c_size_t,  # n
    ctypes.c_int16,  # threshold
]

def count(data: npt.NDArray[np.int16], threshold):
    """
    Count falling edges in a int16 signal.
    Returns the total count of pulses.
    """
    ptr = data.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))
    return _zcopy_pulses.count(ptr, len(data), ctypes.c_int16(threshold))

_zcopy_pulses.find.restype = None
_zcopy_pulses.find.argtypes = [
    ctypes.POINTER(ctypes.c_int16),  # data
    ctypes.c_size_t,                 # n
    ctypes.c_int16,                  # threshold
    ctypes.POINTER(ctypes.c_uint8),  # out
]

def find(data: np.ndarray, threshold: int) -> np.ndarray:
    """
    Find falling edges in a int16 signal.
    Returns a uint8 array where 0xFF marks an edge, 0x00 otherwise.
    """
    out  = np.zeros(len(data), dtype=np.uint8)

    _zcopy_pulses.find(
        data.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
        ctypes.c_size_t(len(data)),
        ctypes.c_int16(threshold),
        out.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
    )
    return out.nonzero()[0] - 1
    