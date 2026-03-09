"""ZPE-Bio: deterministic 8-primitive biosignal compression codec."""

from zpe_bio.codec import CodecMode, EncodedStream, compute_prd, compute_rmse, decode, encode
from zpe_bio import multimodal
from zpe_bio import wearable_wave

__all__ = [
    "CodecMode",
    "EncodedStream",
    "compute_prd",
    "compute_rmse",
    "decode",
    "encode",
    "multimodal",
    "wearable_wave",
]

__version__ = "0.2.0"
