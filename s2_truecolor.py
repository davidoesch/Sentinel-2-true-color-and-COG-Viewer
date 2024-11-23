"""
Sentinel-2 Image True Color Script

This script is designed to process Sentinel-2 L2A imagery, applying contrast, gamma,
and saturation enhancements to optimize visual clarity and representation of the data.
The approach is based on the popular Sentinel Hub custom script
"L2A Optimized" (https://custom-scripts.sentinel-hub.com/custom-scripts/sentinel-2/l2a_optimized/),
which provides enhanced image adjustments specifically tailored for Sentinel-2 data.

Key features of this script include:
    - Contrast and gamma adjustments to highlight important details
    - Saturation enhancement to improve color differentiation
    - Efficient tile-by-tile processing to create a cloud-optimized GeoTIFF (COG)
      with JPEG compression and BigTIFF format for large images

The script uses `rasterio` for file I/O and relies on `numpy` for efficient array processing.
The output is a COG format TIFF file, making it suitable for large-area geospatial visualization.
"""

import rasterio
import numpy as np
from rasterio.windows import Window

# Constants for image adjustment
MAX_R = 3.0
MID_R = 0.13
SATURATION = 1.2
GAMMA = 1.8
GAMMA_OFFSET = 0.01
GAMMA_OFFSET_POW = GAMMA_OFFSET ** GAMMA
GAMMA_OFFSET_RANGE = (1 + GAMMA_OFFSET) ** GAMMA - GAMMA_OFFSET_POW

def adj(arr, tx, ty, max_c):
    """Adjust image contrast based on input values."""
    arr_clipped = np.clip(arr / max_c, 0, 1)
    return arr_clipped * (arr_clipped * (tx / max_c + ty - 1) - ty) / (
        arr_clipped * (2 * tx / max_c - 1) - tx / max_c
    )

def adj_gamma(arr):
    """Apply gamma correction to the array."""
    return (np.power((arr + GAMMA_OFFSET), GAMMA) - GAMMA_OFFSET_POW) / GAMMA_OFFSET_RANGE

def clip(arr):
    """Clip array values to the range [0, 1]."""
    return np.clip(arr, 0, 1)

def sat_enh(arr_r, arr_g, arr_b):
    """Enhance image saturation."""
    avg_saturation = (arr_r + arr_g + arr_b) / 3.0 * (1 - SATURATION)
    return [
        clip(avg_saturation + arr_r * SATURATION),
        clip(avg_saturation + arr_g * SATURATION),
        clip(avg_saturation + arr_b * SATURATION),
    ]

def sRGB(arr):
    """Convert linear RGB values to sRGB."""
    return np.where(arr <= 0.0031308, 12.92 * arr, 1.055 * (arr ** (1 / 2.4)) - 0.055)

def process_image(r, g, b):
    """
    Process RGB bands through contrast, gamma adjustments, and saturation enhancement.

    Parameters:
        r, g, b: Numpy arrays for the red, green, and blue bands.

    Returns:
        A numpy array with processed RGB values.
    """
    r_adj = adj_gamma(adj(r, MID_R, 1, MAX_R))
    g_adj = adj_gamma(adj(g, MID_R, 1, MAX_R))
    b_adj = adj_gamma(adj(b, MID_R, 1, MAX_R))

    # Apply saturation enhancement
    r, g, b = sat_enh(r_adj, g_adj, b_adj)
    return np.stack([sRGB(r), sRGB(g), sRGB(b)], axis=0)  # Shape: (3, height, width)

# File paths for input and output
input_tiff = (
    "https://data.geo.admin.ch/ch.swisstopo.swisseo_s2-sr_v100/"
    "2019-02-26t102021/ch.swisstopo.swisseo_s2-sr_v100_mosaic_2019-02-26t102021_bands-10m.tif"
)
output_tiff = "output_cog_large.tif"

# Configuration for the output COG
TILE_SIZE = 1024
JPEG_QUALITY = 75
BLOCK_SIZE = 512

with rasterio.open(input_tiff) as src:
    # Set up profile for output COG with compression and tiling
    cog_profile = src.profile.copy()
    cog_profile.update({
        'driver': 'COG',
        'dtype': 'uint8',
        'count': 3,  # RGB bands
        'compress': 'JPEG',
        'jpeg_quality': JPEG_QUALITY,
        'blockxsize': BLOCK_SIZE,
        'blockysize': BLOCK_SIZE,
        'tiled': True,
        'BIGTIFF': 'YES',
        'NUM_THREADS': 'ALL_CPUS'
    })

    # Write processed data to output COG file
    with rasterio.open(output_tiff, 'w', **cog_profile) as dst:
        for ji, window in src.block_windows(1):
            # Read each RGB band for the tile and normalize values
            r = src.read(1, window=window) / 10000
            g = src.read(2, window=window) / 10000
            b = src.read(3, window=window) / 10000

            # Apply processing functions to the RGB data
            processed = process_image(r, g, b)

            # Convert processed data to uint8 and write to the output file
            processed = (processed * 255).astype(np.uint8)
            dst.write(processed, window=window)

print(f"COG saved at: {output_tiff}")
