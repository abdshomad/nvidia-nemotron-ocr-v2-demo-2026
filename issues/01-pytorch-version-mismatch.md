# Issue: PyTorch Version Mismatch Symbol Error

## Symptoms / Errors

When launching the container, the python application crashed immediately with the following error:
```
Traceback (most recent call last):
  File "/app/app.py", line 29, in <module>
    from nemotron_ocr.inference.pipeline_v2 import NemotronOCRV2
  ...
  File "/usr/local/lib/python3.12/dist-packages/nemotron_ocr_cpp/__init__.py", line 12, in <module>
    from ._nemotron_ocr_cpp import *  # noqa: F403
ImportError: /usr/local/lib/python3.12/dist-packages/nemotron_ocr_cpp/_nemotron_ocr_cpp.cpython-312-x86_64-linux-gnu.so: undefined symbol: _ZNK3c107SymBool14guard_or_falseEPKcl
```

## Root Cause

The pre-built wheel `nemotron_ocr` was compiled against PyTorch `2.8.0` or higher. However, the base Docker image `nvcr.io/nvidia/pytorch:25.01-py3` shipped with PyTorch `2.6.0a0`. The missing symbol `c10::SymBool::guard_or_false` is specific to PyTorch `2.8.0+`.

## Implemented Solution

Updated the [Dockerfile](file:///home/aiserver/LABS/OCR/nvidia-nemotron-ocr-v2-demo-2026/Dockerfile) to run the full dependency installation from [requirements.txt](file:///home/aiserver/LABS/OCR/nvidia-nemotron-ocr-v2-demo-2026/nemotron-ocr-v2/requirements.txt) instead of omitting PyTorch. Using `uv` inside the container:
```dockerfile
RUN uv pip install --system --break-system-packages --no-cache -r requirements.txt
```
This automatically upgrades the PyTorch installation inside the container to `>=2.8.0` using the `cu128` PyTorch index, satisfying the binary constraints of the precompiled wheel extension.
