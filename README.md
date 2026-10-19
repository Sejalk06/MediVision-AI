# MediVision AI
### Medical Image Analysis & Research Assistant

MediVision AI is an educational Python application demonstrating classical image-processing workflows through a modern Streamlit interface.

## Features
- Upload PNG/JPG/JPEG images or generate a fictional demo image.
- Grayscale preview, CLAHE contrast enhancement, denoising, Canny edge detection, Otsu thresholding, and adaptive thresholding.
- Pixel intensity statistics and interactive histograms.
- Download processed PNG images, JSON/CSV analysis data, and PDF reports.
- No paid APIs or cloud credentials required.

## Important safety note
This is an educational research prototype, not a medical device. It does not diagnose disease or provide clinical advice. Do not upload identifiable patient data. Use only images you are authorized to analyze.

## Run locally (Windows / VS Code)
1. Install Python 3.11 or 3.12.
2. Extract this repository and open the `MediVision-AI` folder in VS Code.
3. Open Terminal in that folder and run:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

4. Open the local URL printed in the terminal (usually `http://localhost:8501`).
5. Select **Image Laboratory** and click **Use generated demo image** to test it.

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again. Alternatively use `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe -m streamlit run app.py`.

## Deploy publicly
Push `app.py`, `requirements.txt`, and `README.md` to a GitHub repository. Then visit https://share.streamlit.io, connect GitHub, select the repository, branch `main`, and entry file `app.py`. Streamlit Community Cloud will build the app and provide a public URL. Deployment may take several minutes and depends on dependency compatibility.

## Project architecture
- `app.py`: interface, image processing, visualizations, report generation.
- `requirements.txt`: Python dependencies.
- `tests/`: basic tests.

## Methods
- CLAHE: local contrast enhancement.
- Non-local means: image denoising.
- Canny: edge detection.
- Otsu threshold: automatic global threshold selection.
- Adaptive threshold: local thresholding.

## Future improvements
A separately validated pretrained model, DICOM support, segmentation overlays, image anonymization utilities, and more extensive automated tests could be added in future versions. Any model must be evaluated on an appropriate dataset and must not be represented as clinically validated without evidence.
