#!/usr/bin/env python3

import os
import time
import sys
import numpy as np
import csv
from PIL import Image

# Add vessel_metrics to the Python path
sys.path.append('./vessel_metrics/scripts')
import vessel_metrics as vm


def format_sig(x, sig=4):
    """Format a numeric value to `sig` significant digits (returns str)."""
    try:
        if np.isnan(x):
            return "nan"
        return format(x, f'.{sig}g')
    except Exception:
        return str(x)


def get_pixel_size_from_dims(dims):
    """
    Try to extract a pixel size (microns per pixel) from dims returned by preprocess_czi.
    This function is defensive because the exact structure of `dims` may vary.
    Returns (px_y, px_x, unit_name) where unit_name is typically 'micrometers' if detected.
    If unknown, returns (1.0, 1.0, 'pixels') — meaning 1 pixel == 1 "unit".
    """
    # Defaults
    px_y = px_x = 1.0
    unit = 'pixels'  # fallback unit label

    # If dims is a dict and contains typical keys
    if isinstance(dims, dict):
        # common keys might be 'PhysicalSizeY', 'PhysicalSizeX' or similar
        for key in dims:
            kl = key.lower()
            if 'physical' in kl or 'voxel' in kl or 'spacing' in kl:
                try:
                    # try various likely keys
                    if 'y' in kl:
                        px_y = float(dims[key])
                    if 'x' in kl:
                        px_x = float(dims[key])
                except Exception:
                    pass
        # if both still default but dims dict contains numeric values, try to take any numeric items
        numeric_vals = [v for v in dims.values() if isinstance(v, (int, float))]
        if len(numeric_vals) >= 2:
            px_y, px_x = float(numeric_vals[0]), float(numeric_vals[1])
            unit = 'micrometers'
    elif isinstance(dims, (list, tuple, np.ndarray)):
        # some libraries return (z_spacing, y_spacing, x_spacing)
        try:
            dims_list = list(dims)
            # prefer y and x entries if available
            if len(dims_list) >= 3:
                # assume (z, y, x)
                px_y = float(dims_list[1])
                px_x = float(dims_list[2])
                unit = 'micrometers'
            elif len(dims_list) == 2:
                px_y = px_x = float(dims_list[0])
                unit = 'micrometers'
            elif len(dims_list) == 1:
                px_y = px_x = float(dims_list[0])
                unit = 'micrometers'
        except Exception:
            px_y = px_x = 1.0
            unit = 'pixels'
    else:
        # unknown type: leave defaults
        px_y = px_x = 1.0
        unit = 'pixels'

    # If px_x or px_y look like 0 or None, fall back to 1.0
    try:
        if px_x is None or px_x == 0:
            px_x = 1.0
        if px_y is None or px_y == 0:
            px_y = 1.0
    except Exception:
        px_x = px_y = 1.0

    return float(px_y), float(px_x), unit


def main():
    print(">>> Script started successfully.", flush=True)
    print(f"Working directory: {os.getcwd()}", flush=True)
    print(f"Python version: {sys.version}", flush=True)
    print("Checking if file exists...", flush=True)

    data_path = './'  # Current directory
    file_name = '201126 DT 2 channel.czi'
    output_dir = 'vessel_analysis_output'

    os.makedirs(output_dir, exist_ok=True)

    print("=== Vessel Metrics Pipeline ===", flush=True)
    print(f"Processing: {os.path.join(data_path, file_name)}", flush=True)

    print("Sleeping 10s before loading CZI to confirm pipeline is running...", flush=True)
    time.sleep(10)
    print("Continuing to load CZI...", flush=True)

    try:
        # Step 1: Load CZI file (CD31 channel = 1)
        print("Loading CZI file...", flush=True)
        volume, dims = vm.preprocess_czi(data_path, file_name, channel=1)
        print(f"Loaded volume shape: {volume.shape}", flush=True)
        print(f"Physical dimensions: {dims}", flush=True)

        # infer pixel size (microns per pixel) if available
        px_y, px_x, unit_name = get_pixel_size_from_dims(dims)
        print(f"Interpreted pixel size: y={px_y} {unit_name}/px, x={px_x} {unit_name}/px", flush=True)

        volume = volume.astype(np.float32)

        # Step 2: Create 2D projection by max intensity along Z
        print("Creating 2D projection...", flush=True)
        vessel_raw = np.max(volume, axis=0)
        print(f"2D projection shape: {vessel_raw.shape}", flush=True)

        # Save original fluorescence projection as PNG
        original_image_path = os.path.join(output_dir, "original_projection_fixed_test3.png")
        Image.fromarray(
            (vessel_raw / np.max(vessel_raw) * 255).astype(np.uint8)
        ).save(original_image_path)
        print(f"Saved original projection image: {original_image_path}", flush=True)

        # Step 3: Preprocess for segmentation
        print("Preprocessing for segmentation...", flush=True)
        vessel_preproc = vm.preprocess_seg(vessel_raw)

        # Step 4: Segment vessels
        print("Segmenting vessels...", flush=True)
        vessel_seg = vm.segment_image(
            vessel_preproc,
            filter='frangi',
            sigma1=range(1, 8, 1),
            sigma2=range(10, 20, 5),
            hole_size=50,
            ditzle_size=500,
            thresh=60,
            preprocess=True,
            multi_scale=True
        )
        print("Segmentation complete", flush=True)

        # Save raw segmentation image
        seg_path = os.path.join(output_dir, "vessel_segmentation18000_fixed_test3.png")
        Image.fromarray((vessel_seg * 255).astype(np.uint8)).save(seg_path)
        print(f"Saved vessel segmentation image: {seg_path}", flush=True)

        # Step 5: Skeletonization
        print("Skeletonizing vessels...", flush=True)
        skel, edges, branchpoints = vm.skeletonize_vm(vessel_seg)

        # Save skeleton image
        skel_path = os.path.join(output_dir, "vessel_skeleton18000_fixed_test3.png")
        Image.fromarray((skel * 255).astype(np.uint8)).save(skel_path)
        print(f"Saved vessel skeleton image: {skel_path}", flush=True)

        # Step 6: Calculate metrics
        print("Calculating vessel metrics...", flush=True)
        _, edge_labels = vm.cv2.connectedComponents(edges)

        # whole_anatomy_diameter returns viz, list_of_(segment_id, diameter)
        viz, output_diameters = vm.whole_anatomy_diameter(vessel_preproc, vessel_seg, edge_labels)

        # Extract numeric diameters and included segment IDs
        included_segments = [int(sid) for (sid, d) in output_diameters]
        diameter_values = [float(d) for (sid, d) in output_diameters]

        # compute per-segment lengths (in pixels) using edge_labels
        lengths_pixels = [int(np.count_nonzero(edge_labels == sid)) for sid in included_segments]

        net_length = vm.network_length(edges)  # presumably in pixels
        _, vessel_density, _ = vm.vessel_density(vessel_preproc, vessel_seg, 16, 16)
        bp_density, _ = vm.branchpoint_density(vessel_seg)

        # If no diameters found, safe defaults
        if len(diameter_values) > 0:
            mean_diameter_px = float(np.mean(diameter_values))
            std_diameter_px = float(np.std(diameter_values))
        else:
            mean_diameter_px = 0.0
            std_diameter_px = 0.0

        # convert px -> physical units if available
        # use average pixel size in x/y for diameter conversion
        mean_pixel_size = (px_x + px_y) / 2.0
        mean_diameter_phys = mean_diameter_px * mean_pixel_size
        std_diameter_phys = std_diameter_px * mean_pixel_size

        # Save overlay visualization (scaled to 0-255)
        overlay_path = os.path.join(output_dir, "vessel_segmentation_overlay_test2.png")
        Image.fromarray((viz * 255).astype(np.uint8)).save(overlay_path)
        print(f"Saved vessel segmentation overlay image: {overlay_path}", flush=True)

        # Step 7: Export metrics to CSV
        metrics_path = os.path.join(output_dir, "vessel_metrics2.csv")
        with open(metrics_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Metric', 'Value', 'Unit'])

            writer.writerow(['Total Network Length (skeleton pixels)', format_sig(net_length), 'pixels'])
            # if physical conversion for length is desired: net_length * mean_pixel_size
            writer.writerow(['Total Network Length (physical)', format_sig(net_length * mean_pixel_size), unit_name + '/px * pixels'])

            writer.writerow(['Vessel Density', format_sig(vessel_density), 'ratio'])
            writer.writerow(['Branchpoint Density', format_sig(bp_density), 'per unit area'])

            writer.writerow(['Mean Diameter (pixels)', format_sig(mean_diameter_px), 'pixels'])
            writer.writerow([f'Mean Diameter ({unit_name})', format_sig(mean_diameter_phys), unit_name])

            writer.writerow(['Std Diameter (pixels)', format_sig(std_diameter_px), 'pixels'])
            writer.writerow([f'Std Diameter ({unit_name})', format_sig(std_diameter_phys), unit_name])

            writer.writerow(['Number of Vessels (counted segments)', format_sig(len(diameter_values)), 'count'])
            writer.writerow(['Image Width', vessel_raw.shape[1], 'pixels'])
            writer.writerow(['Image Height', vessel_raw.shape[0], 'pixels'])
        print(f"Saved vessel metrics CSV: {metrics_path}", flush=True)

        # Export individual vessel data (both pixels and physical units)
        vessel_data_path = os.path.join(output_dir, "individual_vessels2.csv")
        with open(vessel_data_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Vessel_ID', 'Segment_ID', 'Length_pixels', f'Length_{unit_name}', 'Mean_Diameter_pixels', f'Mean_Diameter_{unit_name}'])

            for idx, (seg_id, diam_px, length_px) in enumerate(zip(included_segments, diameter_values, lengths_pixels)):
                length_phys = length_px * mean_pixel_size
                diam_phys = diam_px * mean_pixel_size
                writer.writerow([
                    idx + 1,
                    seg_id,
                    format_sig(length_px),
                    format_sig(length_phys),
                    format_sig(diam_px),
                    format_sig(diam_phys)
                ])
        print(f"Saved individual vessel data CSV: {vessel_data_path}", flush=True)

        print("\n=== Analysis Complete ===", flush=True)
        print(f"Outputs saved to directory: {output_dir}", flush=True)

    except Exception as e:
        import traceback
        print(f"Error during processing: {e}", flush=True)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

