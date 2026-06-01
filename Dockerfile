FROM nvcr.io/nvidia/pytorch:25.01-py3

# Install system dependencies (libgl and libglib are required for OpenCV/shapely/etc)
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy the requirements file and the wheel
COPY nemotron-ocr-v2/requirements.txt ./
COPY nemotron-ocr-v2/nemotron_ocr-1.0.0-cp312-cp312-linux_x86_64.whl ./

# Install requirements (which installs torch>=2.8.0 and other dependencies using the cu128 wheel index)
RUN uv pip install --system --break-system-packages --no-cache -r requirements.txt

# Install gradio < 6.0 and spaces (gradio v6 removes show_copy_button parameter)
RUN uv pip install --system --break-system-packages --no-cache "gradio<6.0" spaces

# Install the pre-built nemotron_ocr wheel
RUN uv pip install --system --break-system-packages --no-deps nemotron_ocr-1.0.0-cp312-cp312-linux_x86_64.whl

# Copy the rest of the application files
COPY nemotron-ocr-v2/ /app/

EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT="7860"

CMD ["python", "app.py"]
