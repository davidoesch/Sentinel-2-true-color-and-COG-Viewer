
# Sentinel 2 True Color Cloud-Optimized GeoTIFF (COG) Generator and Viewer
This repository provides tools for creating and visualizing enhanced true color Cloud-Optimized GeoTIFFs (COGs) from Sentinel-2 L2A satellite imagery. The project includes a Python script for generating COGs and an HTML/JavaScript-based web viewer for displaying them. The enhancement techniques applied are adapted from [Sentinel Hub's L2A Optimized script](https://custom-scripts.sentinel-hub.com/custom-scripts/sentinel-2/l2a_optimized/), and include contrast, gamma, and saturation adjustments. This project is ideal for users interested in visualizing high-quality satellite imagery in a geospatial web context.

## Features

- **True Color Enhancement**: Contrast, gamma, and saturation adjustments based on the L2A optimized script for visual clarity.
- **Python COG Generation**: Efficient tile-based processing using `rasterio` to output COGs with BigTIFF and JPEG compression for scalable use.
- **Interactive Web Viewer**: A Leaflet-based viewer that supports visualization of COGs with custom CRS (EPSG:2056) and toggling base layers.
- **No Data Masking**: Removes no-data (black) patches from visualized imagery based on Sentinel Hub's L2A mask criteria.

## Getting Started

### Prerequisites

- **Python 3.7+**
  - Required libraries: `rasterio`, `numpy`, `dask`, and `georaster-layer-for-leaflet`
  - Install libraries via:
    ```bash
    pip install rasterio numpy dask georaster-layer-for-leaflet
    ```
- **HTML/JavaScript**
  - Basic knowledge of Leaflet and JavaScript is helpful for customizing the web viewer.
  - Dependencies (loaded via CDN in HTML):
    - Leaflet, Proj4JS, and georaster-layer-for-leaflet.

### Installation

Clone this repository:
```bash
git clone https://github.com/yourusername/true-color-cog-generator
cd true-color-cog-generator
