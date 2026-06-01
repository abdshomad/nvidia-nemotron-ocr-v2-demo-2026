# Issue: Gradio Version Compatibility Error

## Symptoms / Errors

After resolving the PyTorch import error, the application failed to start with a TypeError:
```
/app/app.py:238: UserWarning: The parameters have been moved from the Blocks constructor to the launch() method in Gradio 6.0: theme. Please pass these parameters to launch() instead.
  with gr.Blocks(
Traceback (most recent call last):
  File "/app/app.py", line 289, in <module>
    output_text = gr.Textbox(
                  ^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/gradio/component_meta.py", line 194, in wrapper
    return fn(self, **kwargs)
           ^^^^^^^^^^^^^^^^^^
TypeError: Textbox.__init__() got an unexpected keyword argument 'show_copy_button'
```

## Root Cause

`uv pip install` installed the latest version of Gradio (6.x), which introduces breaking API changes, including the removal of the `show_copy_button` argument in favor of a general `buttons` configuration. The `nemotron-ocr-v2` submodule code expects Gradio 5.x.

## Implemented Solution

Pinned Gradio to `<6.0` in the [Dockerfile](file:///home/aiserver/LABS/OCR/nvidia-nemotron-ocr-v2-demo-2026/Dockerfile) to maintain backward compatibility with the submodule's Gradio 5.x interface layout:
```dockerfile
RUN uv pip install --system --break-system-packages --no-cache "gradio<6.0" spaces
```
This resolves the TypeError and enables the application to start and expose the UI correctly.
