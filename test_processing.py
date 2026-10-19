import numpy as np
from app import analyze_image, make_demo_image

def test_demo_image_is_grayscale():
    image = make_demo_image()
    assert image.ndim == 2
    assert image.dtype == np.uint8

def test_processing_methods_return_same_dimensions():
    image = make_demo_image()
    methods = [
        "Original grayscale", "Contrast enhancement (CLAHE)", "Denoising",
        "Edge detection", "Threshold segmentation", "Adaptive threshold"
    ]
    for method in methods:
        result = analyze_image(image, method, 3)
        assert result.shape == image.shape
        assert result.dtype == np.uint8
