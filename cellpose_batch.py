#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch-segment muscle fibers with Cellpose and save label images for eMyHC_Quanti (v2.1+).

For every image in a folder this script:
  1. reads the true pixel size from the Keyence TIFF metadata (if present),
  2. runs Cellpose on the WGA (membrane) channel,
  3. saves <image name>_cp_masks.tif (16-bit labels: 0 = background, 1..n = fibers),
  4. writes cellpose_summary.csv with pixel size, number of fibers and run time.

Load the original image in the web tool, then "Import Cellpose masks" with the matching *_cp_masks.tif.

Examples
  python cellpose_batch.py "D:/images"
  python cellpose_batch.py "D:/images" --pattern "*_Merge.tif" --wga 1
  python cellpose_batch.py "D:/images" --model "D:/models/my_finetuned_model"
  python cellpose_batch.py "D:/images" --diam_um 35            (only used by Cellpose 3 models)
"""
import argparse, csv, fnmatch, os, re, struct, sys, time

import numpy as np
import tifffile


# ---------------------------------------------------------------- Keyence metadata
def keyence_pixel_size(path):
    """Return the pixel size in µm stored by Keyence BZ-X, or None."""
    with open(path, "rb") as f:
        data = f.read()
    text = data.decode("latin-1")
    i = text.find("<?xml")
    while i >= 0:
        chunk = text[i:i + 80000]
        m = re.search(r'<Calibration Type="System.Double">(-?\d+)</Calibration>', chunk)
        if m:
            nm = struct.unpack("<d", struct.pack("<q", int(m.group(1))))[0]
            return nm / 1000.0
        i = text.find("<?xml", i + 5)
    return None


# ---------------------------------------------------------------- image reading
def read_channel(path, index):
    """Return one channel (2-D array) of an RGB or multi-page TIFF."""
    try:
        img = np.asarray(tifffile.imread(path))
    except Exception:
        # Keyence TIFFs are LZW-compressed; tifffile needs "imagecodecs" for that, Pillow does not
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
        img = np.asarray(Image.open(path).convert("RGB"))
    if img.ndim == 2:
        return img
    if img.ndim == 3:
        if img.shape[-1] in (3, 4):        # H x W x C (RGB)
            return img[..., index]
        if img.shape[0] <= 8:              # C x H x W (multi-page)
            return img[index]
    raise ValueError("Unsupported image shape %s" % (img.shape,))


# ---------------------------------------------------------------- Cellpose
def cellpose_major_version():
    try:
        from importlib.metadata import version
        return int(version("cellpose").split(".")[0])
    except Exception:
        return 0


def build_model(args, major):
    from cellpose import models
    if args.model:
        return models.CellposeModel(gpu=not args.cpu, pretrained_model=args.model)
    if major >= 4:
        return models.CellposeModel(gpu=not args.cpu)            # Cellpose-SAM ("cpsam")
    return models.CellposeModel(gpu=not args.cpu, model_type="cyto3")


def run_model(model, img, major, px_um, args):
    kw = dict(flow_threshold=args.flow, cellprob_threshold=args.cellprob)
    if major >= 4 and not args.model:
        out = model.eval(img, **kw)                              # no channels / diameter needed
    else:
        diam = (args.diam_um / px_um) if (px_um and args.diam_um) else None
        try:
            out = model.eval(img, diameter=diam, channels=[0, 0], **kw)
        except TypeError:                                        # newer API without "channels"
            out = model.eval(img, diameter=diam, **kw)
    return out[0]


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", help="folder with the images")
    ap.add_argument("--pattern", default="*_Merge.tif", help='file pattern (default "*_Merge.tif"; use "*.tif" for all)')
    ap.add_argument("--wga", type=int, default=1, help="index of the WGA channel: 0 = red, 1 = green (default), 2 = blue")
    ap.add_argument("--out", default=None, help="output folder (default: same folder as the images)")
    ap.add_argument("--model", default=None, help="path to a fine-tuned Cellpose model (optional)")
    ap.add_argument("--diam_um", type=float, default=35.0, help="typical fiber diameter in µm (Cellpose 3 models only)")
    ap.add_argument("--flow", type=float, default=0.4, help="flow threshold (default 0.4)")
    ap.add_argument("--cellprob", type=float, default=0.0, help="cell probability threshold (default 0)")
    ap.add_argument("--recursive", action="store_true", help="include subfolders")
    ap.add_argument("--cpu", action="store_true", help="run on CPU instead of the GPU")
    ap.add_argument("--overwrite", action="store_true", help="redo images that already have masks")
    args = ap.parse_args()

    files = []
    for d, _, names in (os.walk(args.folder) if args.recursive else [(args.folder, None, os.listdir(args.folder))]):
        for n in sorted(names):
            if fnmatch.fnmatch(n.lower(), args.pattern.lower()) and "_cp_masks" not in n:
                files.append(os.path.join(d, n))
    if not files:
        sys.exit("No files matching %s in %s" % (args.pattern, args.folder))

    major = cellpose_major_version()
    try:
        import torch
        gpu = torch.cuda.is_available() and not args.cpu
    except Exception:
        gpu = False
    print("Cellpose version %s | GPU: %s | %d files" % (major or "?", "yes" if gpu else "no", len(files)))
    if not gpu and not args.cpu:
        print("Warning: no CUDA GPU found by PyTorch; running on CPU (much slower).")
    model = build_model(args, major)

    out_dir = args.out or None
    rows = []
    for k, path in enumerate(files, 1):
        name = os.path.basename(path)
        dst_dir = out_dir or os.path.dirname(path)
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, os.path.splitext(name)[0] + "_cp_masks.tif")
        if os.path.exists(dst) and not args.overwrite:
            print("[%d/%d] %s: masks exist, skipped" % (k, len(files), name))
            continue
        t0 = time.time()
        try:
            px = keyence_pixel_size(path)
            img = read_channel(path, args.wga)
            masks = run_model(model, img, major, px, args)
            n = int(masks.max())
            tifffile.imwrite(dst, masks.astype(np.uint16 if n < 65536 else np.uint32), compression="zlib")
            dt = time.time() - t0
            print("[%d/%d] %s: %d fibers, %.1f s" % (k, len(files), name, n, dt))
            rows.append([name, os.path.basename(dst), img.shape[1], img.shape[0],
                         "%.4f" % px if px else "", n, "%.1f" % dt, ""])
        except Exception as e:
            print("[%d/%d] %s: ERROR %s" % (k, len(files), name, e))
            rows.append([name, "", "", "", "", "", "", str(e)])

    summary = os.path.join(out_dir or args.folder, "cellpose_summary.csv")
    with open(summary, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Image", "Mask file", "Width px", "Height px", "Pixel size um/px (Keyence)", "Fibers (Cellpose objects)", "Seconds", "Error"])
        w.writerows(rows)
    print("Summary saved to", summary)


if __name__ == "__main__":
    main()
