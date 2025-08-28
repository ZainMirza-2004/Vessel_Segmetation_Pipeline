<div align="center">
    
# Vessel Segmentation Pipeline

<div align="center">

![Pipeline Demo](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

**A fully optimized workflow for analyzing vascular structures in complex tumor microenvironments**

[📖 Documentation](#documentation) • [🚀 Quick Start](#quick-start) • [🔬 Features](#features) • [📊 Examples](#examples) • [🤝 Contributing](#contributing)

---

*Built by [Muhammad Mirza](https://github.com/ZainMirza-2004) | Extending the original [vessel_metrics](vessel_metrics) framework*

</div>

## 🌟 Overview

The Vessel Segmentation Pipeline revolutionizes vascular analysis in tumor microenvironments by providing a comprehensive, automated workflow that transforms raw microscopy data into quantitative insights about vessel architecture, morphology, and function.

### 🎯 What It Does

- **🔍 Intelligent Vessel Detection**: Advanced segmentation using multiple filter types (Frangi, Meijering, Sato, Jerman)
- **🕸️ Network Architecture Analysis**: Skeletonization with branch point and endpoint detection
- **📏 Precise Measurements**: Automated diameter calculation at user-defined intervals
- **📈 Comprehensive Metrics**: Length, density, tortuosity, and branching analysis
- **🖼️ Multi-Channel Support**: Integrate additional markers (pericytes, etc.)
- **⚡ High Performance**: Optimized for large images and complex datasets

---

## 🔬 Key Features

### 🔧 Advanced Image Processing
```
✅ Multi-format support (.czi, .tif, .png, and more)
✅ Background suppression and contrast enhancement  
✅ Multi-scale vessel enhancement algorithms
✅ Artifact removal and morphological refinement
```

### 🎯 Precision Segmentation
```
✅ Tumor microenvironment-optimized parameters
✅ Multiple vessel filter algorithms available
✅ Morphological post-processing for accuracy
✅ Handles both microvasculature and major vessels
```

### 🕷️ Network Analysis
```
✅ Enhanced skeletonization with error correction
✅ Intelligent branch point detection
✅ Parent-child segment relationship mapping
✅ Complex network topology analysis
```

### 📊 Quantitative Metrics
```
✅ Automated diameter measurements
✅ Segment length and tortuosity calculation
✅ Vessel density and branching metrics
✅ Statistical analysis-ready outputs
```

---

## 🚀 Quick Start

### 📦 Installation

1. **Clone the repository**
```bash
git clone https://github.com/ZainMirza-2004/Vessel_Segmetation_Pipeline.git
cd Vessel_Segmetation_Pipeline
```

2. **Set up Python environment**
```bash
# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate   # Linux/macOS
# OR
venv\Scripts\activate      # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

> **💡 GPU Note**: For CPU-only systems, install PyTorch CPU version:
> ```bash
> pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
> ```

### ⚡ Usage Example

```python
import vessel_metrics as vm
import numpy as np

# 📁 Load and preprocess your data
data_path = 'data/sample_ims/'
file = 'sample.czi'
volume = vm.preprocess_czi(data_path, file, channel=0)

# 🔄 Prepare image slice
slice_thickness = np.round(len(volume)/2).astype(np.uint8)
reslice = vm.reslice_image(volume, slice_thickness)
vessel_raw = reslice[0]

# 🎨 Preprocess for optimal segmentation
vessel_preproc = vm.preprocess_seg(vessel_raw)

# 🎯 Segment vessels with advanced filtering
vessel_seg = vm.segment_image(
    vessel_preproc, 
    filter='meijering',
    sigma1=range(1,8,1),
    sigma2=range(10,20,5), 
    hole_size=50,
    ditzle_size=500,
    thresh=60,
    preprocess=True,
    multi_scale=True
)

# 🕸️ Extract vascular architecture
skel, edges, bp = vm.skeletonize_vm(vessel_seg)

# 📏 Calculate precise vessel diameters
viz, diameters = vm.whole_anatomy_diameter(vessel_preproc, vessel_seg, edges)
```

---

## 📊 Pipeline Outputs

| File | Description | Use Case |
|------|-------------|----------|
| `img.png` | 🖼️ Original image/z-projection | Visual reference |
| `label.png` | 🎯 Vessel segmentation mask | Validation & analysis |
| `vessel_labels.png` | 🕸️ Skeleton + segment overlay | Quality control |
| `vessel_diameters.txt` | 📏 Per-segment diameter data | Quantitative analysis |
| `vessel_density.txt` | 📊 Regional density metrics | Statistical studies |

---

## 🎨 Visualization Examples

<div align="center">

### Before → After Pipeline Processing

| Original Image | Segmented Vessels | Skeletonized Network |
|:--------------:|:-----------------:|:-------------------:|
| Raw microscopy data | Precise vessel masks | Quantified architecture |

*Transform complex vascular images into quantifiable data*

</div>

---

## 🔧 Advanced Configuration

### 🎛️ Segmentation Parameters

```python
# Fine-tune segmentation for your specific data
vm.segment_image(
    image,
    filter='frangi',        # Options: frangi, meijering, sato, jerman
    sigma1=range(1,10,1),   # Small vessel detection range
    sigma2=range(15,25,5),  # Large vessel detection range
    thresh=65,              # Segmentation threshold
    multi_scale=True        # Enhanced multi-scale processing
)
```

### 📏 Diameter Measurement Options

```python
# Customize diameter calculation
vm.whole_anatomy_diameter(
    raw_image,
    segmented_vessels,
    skeleton_edges,
    interval=5,             # Measurement interval (pixels)
    method='gradient'       # Diameter calculation method
)
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

- 🐛 **Report bugs** via [GitHub Issues](https://github.com/ZainMirza-2004/Vessel_Segmetation_Pipeline/issues)
- 💡 **Suggest features** for tumor microenvironment analysis
- 🔧 **Submit pull requests** with improvements
- 📖 **Improve documentation** and examples

### 🌟 Contributors

Special thanks to the original [vessel_metrics](vessel_metrics) developers:
- **S.D. McGarry** - University of Calgary
- **S. Childs** - University of Calgary

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support & Contact

- 👨‍💻 **Author**: Muhammad Mirza
- 🌐 **GitHub**: [@ZainMirza-2004](https://github.com/ZainMirza-2004)
- 📧 **Issues**: [Report here](https://github.com/ZainMirza-2004/Vessel_Segmetation_Pipeline/issues)

---

<div align="center">

**⭐ Star this repository if it helps your research!**

*Advancing vascular analysis in tumor microenvironments, one vessel at a time.*

</div>
