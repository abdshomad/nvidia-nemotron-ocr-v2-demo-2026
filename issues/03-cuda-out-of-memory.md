# Issue: CUDA Out of Memory on GPU 0

## Symptoms / Errors

When performing OCR analysis on complex or large images sequentially, the FastAPI backend crashed with a CUDA out of memory error:
```
Error running analysis: CUDA out of memory. Tried to allocate 892.00 MiB. GPU 0 has a total capacity of 44.39 GiB of which 36.38 MiB is free. Process 1189488 has 1.42 GiB memory in use. Process 1251415 has 40.11 GiB memory in use. ...
```

## Root Cause

GPU 0 was heavily congested by other services on the host machine, including a large vLLM process occupying 41 GiB of VRAM. This left only about ~2 GiB of VRAM available on GPU 0. While the first small OCR run succeeded, subsequent runs requiring slightly larger allocations triggered the CUDA Out of Memory error.

## Implemented Solution

We inspected the available GPUs using `nvidia-smi` and found that GPU 1 was less congested, having ~8.7 GiB of free VRAM.

To redirect the Nemotron OCR Python service to use GPU 1 instead of GPU 0, we added the `CUDA_VISIBLE_DEVICES` environment variable inside the service definition in [docker-compose.yml](file:///home/aiserver/LABS/OCR/nvidia-nemotron-ocr-v2-demo-2026/docker-compose.yml):

```yaml
  nemotron-ocr-api:
    build:
      context: .
      dockerfile: ./nemotron-ocr-api/Dockerfile
    ...
    environment:
      - CUDA_VISIBLE_DEVICES=1
```

After restarting the Docker container, the service successfully mapped its PyTorch device to GPU 1, and subsequent Playwright browser tests successfully ran OCR analysis on all three sample images without any memory issues.
