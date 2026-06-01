# NVIDIA Nemotron OCR v2 Demo Deployment

This repository containerizes and deploys the [NVIDIA Nemotron OCR v2](https://huggingface.co/spaces/nvidia/nemotron-ocr-v2) online demo, a state-of-the-art multilingual OCR engine that extracts text and outputs bounding boxes from images.

## Architecture Overview

The system runs a **Gradio Frontend** that loads the input images, performs inference via the underlying `nemotron_ocr` package, and displays visual outputs (annotated regions and structured layouts).

Key features:
1. **Pre-built C++ Extensions**: The core `nemotron_ocr` package (including the CUDA C++ extension) is shipped as a pre-built Python wheel (`nemotron_ocr-1.0.0-cp312-cp312-linux_x86_64.whl`), eliminating the need for complex build toolchains at deploy time.
2. **Layout-aware Spatial Reconstruction**: The app reconstructs page layouts using a custom spacing algorithm, preserving horizontal text positions.
3. **GPU-Accelerated Inference**: Utilizes PyTorch and CUDA to accelerate detection, recognition, and relational tasks.

## Directory Structure

*   [AGENTS.md](AGENTS.md) - Agent guidelines and workspace configuration rules.
*   [nemotron-ocr-v2/](nemotron-ocr-v2/) - Submodule containing the Hugging Face space files (including the wheel and main `app.py`).

## Prerequisites

- **NVIDIA GPU** with CUDA 12.8 support (required for the precompiled CUDA extensions).
- **Python 3.12** (specifically needed to match the Python 3.12 wheel).
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip` for Python dependency management.

## Getting Started

### Run Locally (Development)

To run the Gradio interface locally:

1.  **Configure environment**: Ensure Python 3.12 is active.
2.  **Install dependencies**:
    ```bash
    uv pip install -r nemotron-ocr-v2/requirements.txt
    ```
3.  **Run the application**:
    ```bash
    python nemotron-ocr-v2/app.py
    ```