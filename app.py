import io
import json
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

st.set_page_config(page_title="MediVision AI", page_icon="🩻", layout="wide")

st.markdown("""
<style>
.stApp {background: radial-gradient(circle at 10% 0%, #142746 0%, #07111f 42%, #050a13 100%); color:#eaf2ff}
section[data-testid="stSidebar"] {background:#0b1728}
h1,h2,h3 {color:#eaf2ff}
div[data-testid="stMetric"] {background:#101f34;border:1px solid #203d5b;padding:16px;border-radius:14px}
div.stButton > button {border-radius:10px;border:1px solid #3a85a8;background:#12354b;color:white}
div.stButton > button:hover {border-color:#56d7ef;color:#56d7ef}
.small-note {color:#a7bdd5;font-size:0.9rem}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("# 🩻 MediVision AI")
st.sidebar.caption("Medical Image Analysis & Research Assistant")
page = st.sidebar.radio("NAVIGATION", ["Overview", "Image Laboratory", "Research Report", "About & Safety"])
st.sidebar.markdown("---")
st.sidebar.caption("Research prototype • Not for clinical diagnosis")

def make_demo_image():
    """Create a fictional grayscale sample image for demonstrating image-processing tools."""
    y, x = np.mgrid[0:320, 0:320]
    base = 35 + 0.12*x + 0.08*y
    ellipse = (((x-160)/78)**2 + ((y-158)/112)**2) < 1
    image = np.where(ellipse, 125 + 24*np.sin(x/12) + 15*np.cos(y/17), base)
    rng = np.random.default_rng(7)
    image = np.clip(image + rng.normal(0, 8, image.shape), 0, 255).astype(np.uint8)
    cv2.circle(image, (130, 135), 22, 185, -1)
    cv2.circle(image, (192, 185), 16, 70, -1)
    return image

def analyze_image(gray, method, strength):
    if method == "Original grayscale":
        return gray.copy()
    if method == "Contrast enhancement (CLAHE)":
        clahe = cv2.createCLAHE(clipLimit=float(strength), tileGridSize=(8, 8))
        return clahe.apply(gray)
    if method == "Denoising":
        return cv2.fastNlMeansDenoising(gray, None, h=int(3 + strength * 3), templateWindowSize=7, searchWindowSize=21)
    if method == "Edge detection":
        low = int(30 + strength * 20)
        return cv2.Canny(gray, low, low * 2)
    if method == "Threshold segmentation":
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, out = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return out
    if method == "Adaptive threshold":
        return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 3)
    return gray.copy()

def make_pdf(report):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("MediVision AI — Image Research Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph("Educational research prototype. This report is not a medical diagnosis.", styles["Italic"]),
        Spacer(1, 12),
        Paragraph("Analysis summary", styles["Heading2"]),
    ]
    rows = [["Field", "Value"]] + [[str(k), str(v)] for k, v in report.items()]
    table = Table(rows, colWidths=[165, 330], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#16344f")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#b8c7d8")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#eef4f8")]),
        ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(table)
    story += [Spacer(1, 14), Paragraph("Interpretation and limitations", styles["Heading2"]),
              Paragraph("Image-processing outputs depend on image quality and selected parameters. Brightness, contrast, edges, and threshold regions are computational features only. They do not establish the presence or absence of a disease. Use only authorized, de-identified images and consult qualified medical professionals for clinical interpretation.", styles["BodyText"])]
    doc.build(story)
    return buffer.getvalue()

if "original" not in st.session_state:
    st.session_state.original = None
if "processed" not in st.session_state:
    st.session_state.processed = None
if "analysis" not in st.session_state:
    st.session_state.analysis = {}

if page == "Overview":
    st.markdown("# MediVision AI")
    st.markdown("### Medical Image Analysis & Research Assistant")
    st.markdown("A Python-powered image-processing laboratory for learning, experimentation, and reproducible research.")
    a,b,c,d = st.columns(4)
    a.metric("Processing methods", "6")
    b.metric("Supported uploads", "PNG / JPG / JPEG")
    c.metric("External API keys", "0")
    d.metric("Clinical status", "Research only")
    st.markdown("## Research workflow")
    cols = st.columns(3)
    cols[0].markdown("### 01 · Import\nUpload an authorized image or use a generated sample.")
    cols[1].markdown("### 02 · Analyze\nApply image enhancement, denoising, edge detection, or segmentation.")
    cols[2].markdown("### 03 · Export\nReview metrics and create a downloadable research report.")
    st.info("For a quick demonstration, open **Image Laboratory** and choose **Use generated demo image**. The generated sample is fictional and is not a real medical scan.")
    st.markdown("## Built with")
    st.write("Python · Streamlit · OpenCV · NumPy · Pandas · Plotly · Pillow · ReportLab")

elif page == "Image Laboratory":
    st.markdown("# Image Laboratory")
    st.caption("Upload only images you are authorized to use. Avoid identifiable patient data.")
    uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    c1, c2 = st.columns([1, 1])
    use_demo = c1.button("Use generated demo image", use_container_width=True)
    clear = c2.button("Clear current image", use_container_width=True)
    if clear:
        st.session_state.original = None
        st.session_state.processed = None
        st.session_state.analysis = {}
        st.rerun()
    if uploaded is not None:
        try:
            pil = Image.open(uploaded).convert("RGB")
            rgb = np.array(pil)
            st.session_state.original = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            st.session_state.image_name = Path(uploaded.name).name
        except Exception as exc:
            st.error(f"Could not read this image: {exc}")
    elif use_demo:
        st.session_state.original = make_demo_image()
        st.session_state.image_name = "synthetic_demo_image.png"
    if st.session_state.original is not None:
        gray = st.session_state.original
        method = st.selectbox("Processing method", [
            "Original grayscale", "Contrast enhancement (CLAHE)", "Denoising",
            "Edge detection", "Threshold segmentation", "Adaptive threshold"
        ])
        strength = st.slider("Processing strength", 1, 5, 3)
        processed = analyze_image(gray, method, strength)
        st.session_state.processed = processed
        st.session_state.analysis = {
            "Image name": st.session_state.get("image_name", "uploaded_image"),
            "Analysis method": method,
            "Parameter strength": strength,
            "Image width (px)": int(gray.shape[1]),
            "Image height (px)": int(gray.shape[0]),
            "Pixel count": int(gray.size),
            "Original mean intensity (0-255)": round(float(np.mean(gray)), 2),
            "Original standard deviation": round(float(np.std(gray)), 2),
            "Processed mean intensity (0-255)": round(float(np.mean(processed)), 2),
            "Processed standard deviation": round(float(np.std(processed)), 2),
            "Processed unique intensity values": int(np.unique(processed).size),
            "Generated at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        left, right = st.columns(2)
        left.markdown("#### Original grayscale")
        left.image(gray, clamp=True, use_container_width=True)
        right.markdown(f"#### Result · {method}")
        right.image(processed, clamp=True, use_container_width=True)
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Width", f"{gray.shape[1]} px")
        m2.metric("Height", f"{gray.shape[0]} px")
        m3.metric("Mean intensity", f"{np.mean(gray):.1f}/255")
        m4.metric("Intensity variation", f"{np.std(gray):.1f}")
        hist = pd.DataFrame({
            "Intensity": np.arange(256),
            "Original": np.bincount(gray.ravel(), minlength=256),
            "Processed": np.bincount(processed.ravel(), minlength=256)
        })
        fig = px.line(hist, x="Intensity", y=["Original", "Processed"], title="Pixel intensity distribution")
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("Download processed image (PNG)", data=cv2.imencode(".png", processed)[1].tobytes(),
                           file_name="medivision_processed.png", mime="image/png")
        st.download_button("Download analysis data (JSON)", data=json.dumps(st.session_state.analysis, indent=2),
                           file_name="medivision_analysis.json", mime="application/json")
    else:
        st.warning("Upload an image or choose the generated demo image to begin.")

elif page == "Research Report":
    st.markdown("# Research Report Center")
    st.write("Generate a summary of the most recent image analysis. No image is sent to an external service.")
    if st.session_state.analysis:
        report = st.session_state.analysis.copy()
        st.dataframe(pd.DataFrame(list(report.items()), columns=["Metric", "Value"]), use_container_width=True, hide_index=True)
        st.download_button("Download PDF research report", data=make_pdf(report),
                           file_name="MediVision_AI_Research_Report.pdf", mime="application/pdf")
        st.download_button("Download CSV summary",
                           data=pd.DataFrame(list(report.items()), columns=["Metric", "Value"]).to_csv(index=False),
                           file_name="MediVision_AI_Research_Report.csv", mime="text/csv")
    else:
        st.info("Run an analysis in Image Laboratory first. Your report will appear here.")

elif page == "About & Safety":
    st.markdown("# About MediVision AI")
    st.write("MediVision AI is an educational prototype demonstrating image processing and research reporting with Python.")
    st.markdown("### Methods implemented")
    st.write("- CLAHE contrast enhancement\n- Non-local means denoising\n- Canny edge detection\n- Otsu threshold segmentation\n- Adaptive thresholding\n- Pixel-intensity statistics and histograms")
    st.markdown("### Responsible use")
    st.warning("This application is not a medical device and must not be used to diagnose, screen, or treat any condition. It does not detect cancer, tumors, fractures, or other diseases. Results are image-processing demonstrations only. Use de-identified, authorized images and rely on qualified clinicians for medical decisions.")
    st.markdown("### Limitations")
    st.write("The current version uses classical image-processing algorithms rather than a clinically validated AI model. Performance depends on image format, quality, and parameters. The generated sample is synthetic.")
    st.markdown("### Project metadata")
    st.write("Project: MediVision AI | Language: Python | Interface: Streamlit | Vision: OpenCV | Reports: ReportLab")
