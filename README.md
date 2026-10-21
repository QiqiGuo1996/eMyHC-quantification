# eMyHC_Quanti: quantification of muscle injury and regeneration

[![DOI](https://zenodo.org/badge/DOI/[DOI].svg)](https://doi.org/[DOI])

English | [中文](README.zh-CN.md)

eMyHC_Quanti segments skeletal muscle fibers in WGA-stained cross-sections, identifies centrally nucleated fibers (CNFs) to define the injured region, and measures the area fraction of a regeneration marker (embryonic myosin heavy chain, eMyHC, or another red marker) within that region. It also reports fiber cross-sectional area (CSA).

The analysis runs in a web browser from a single HTML file. Images are processed locally and are not uploaded. Optionally, fibers can be segmented with [Cellpose](https://github.com/MouseLand/cellpose) on the user's own GPU.

This repository accompanies: [Authors]. [Title]. *[Journal]* ([year]). https://doi.org/[article DOI]

## Contents

| File | Description |
| --- | --- |
| `eMyHC_Quanti.html` | The analysis tool (open in a browser) |
| `cellpose_server.py` | Optional: runs Cellpose locally and opens the tool with a one-click "Segment with Cellpose" button |
| `cellpose_batch.py` | Optional: segments a folder of images with Cellpose and saves label images for import |
| `CHANGELOG.md`, `CITATION.cff`, `LICENSE`, `THIRD_PARTY_NOTICES.md` | Version history, citation metadata, license, third-party licenses |

## Quick start

1. Open `eMyHC_Quanti.html` in Chrome, Edge, Firefox or Safari (2023 or later).
2. Load an image, or click **Try a sample image**.
3. Check the channel assignment (WGA, DAPI, marker) and the pixel size. For Keyence BZ-X TIFFs the pixel size is read from the file automatically.
4. Click **Run analysis**, inspect the overlay, correct fibers if needed, and export the results as CSV.

An internet connection is needed the first time a TIFF is opened, because the TIFF decoder is loaded from a public CDN.

## Input

- Transverse cryosections stained with WGA (fiber outlines), DAPI (nuclei) and a marker (for example eMyHC).
- RGB composites (PNG, JPG, TIFF) or multichannel TIFFs with one channel per page (8-bit, 16-bit or 32-bit float).
- BigTIFF files cannot be read by browsers; downscale them in Fiji first.

### Pixel size and Keyence stitched images

All areas depend on the pixel size. Keyence BZ-X software downscales stitched images on saving when the stitched image exceeds about 12.5 megapixels, by a factor that depends on the number of tiles. Images acquired with identical settings can therefore have different pixel sizes (for a 20× objective with 2×2 binning, 0.7549 µm/pixel unscaled, larger after downscaling). The tool reads the true pixel size from the Keyence metadata of each file. Files re-saved by other software usually lose this metadata; the pixel size must then be entered by hand.

To analyze a batch at identical resolution, set **Downscale for processing** to **Common**: every image is rescaled from its own pixel size to the common working resolution.

## Analysis workflow

**1. Fiber segmentation (built-in).** The WGA channel is background-subtracted and smoothed. Dark regions surrounded by brighter rings are taken as fiber centers (h-minima of the WGA intensity), and a marker-controlled watershed on the WGA intensity grows each fiber from its center. Each fiber then keeps its own interior plus the half of its WGA membrane on its own side, so its boundary lies on the middle of the membrane and gaps beyond the membrane are excluded. A membrane mask at 0.7 × the Otsu threshold gives the area inside the membrane and the distance to the membrane. Gaps and interstitium are rejected by inner area, inscribed radius, solidity (area ÷ convex-hull area) and shape index (area ÷ area of the largest inscribed circle).

**1′. Fiber segmentation with Cellpose (optional).** Cellpose label images can replace the built-in segmentation, either through `cellpose_server.py` (one click in the page) or by importing `*_cp_masks.tif` files made with `cellpose_batch.py`. Each Cellpose object is trimmed in the same way to its interior and the near half of its membrane, and objects touching the image edge or outside the area range are excluded.

**2. Central nuclei.** The nuclear channel is background-subtracted, smoothed and thresholded (Otsu). The fiber core is the part farther than the core inset from the membrane (capped at 40% of the inscribed radius for small fibers). A fiber with at least the minimum nuclear area in its core is centrally nucleated.

**3. Marker-positive fibers.** The marker channel is background-subtracted, smoothed and thresholded. A fiber is marker-positive when the marker covers at least the set fraction of its area (optionally measured over the fiber plus a margin outside it).

**4. Injured region.** By default the injured region is the union of all CNFs. Optionally, marker-positive fibers without central nuclei, and fiber-free areas (drawn by hand, detected as DAPI-dense, or selected among undetected regions) can be added.

**5. Primary outcome.**

```
Marker+ fraction (%) = marker+ area within the injured region / injured area × 100
```

With the default settings, both terms include only centrally nucleated fibers: marker signal in fibers without central nuclei and in the interstitium is excluded. Marker+ area is counted as marker-positive pixels (default) or as the whole area of marker-positive fibers.

**6. Fiber area.** CSA of each fiber (to the middle of the membrane), mean ± SD and median for all, injured, non-injured and marker-positive injured fibers.

## Parameters

Defaults are shown; use the same parameters for every image in an experiment. All parameters, thresholds and the segmentation source are written to the exported CSV.

| Group | Parameter | Default | Notes |
| --- | --- | --- | --- |
| Scale | Pixel size | From Keyence metadata | Enter by hand if the file has none |
| Scale | Downscale for processing | Auto | *Common* rescales all images to one resolution |
| Fiber segmentation | WGA threshold | Auto (0.7 × Otsu) | |
| Fiber segmentation | Fiber area range | 100–15,000 µm² | Minimum applies to the area inside the membrane; lower it for very small fibers |
| Fiber segmentation | Exclude fibers touching the edge | On | |
| Separation | Min. solidity | 0.9 | |
| Separation | Max. shape index | 4 | |
| Separation | Max. nuclear area in a fiber | 0 (off) | |
| Central nuclei | Nuclear threshold | Auto (Otsu) | |
| Central nuclei | Core inset | 4 µm | |
| Central nuclei | Min. nuclear area in core | 6 µm² | |
| Marker | Marker threshold | Auto (Otsu) | Set a fixed value; see Limitations |
| Marker | Area fraction for marker+ fiber | 20% | |
| Marker | Marker+ area method | Pixels | Alternative: whole marker+ fibers |
| Marker | Margin for marker+ call | 0 µm | |
| Marker | Count marker+ fibers as injured | Off | |
| Fiber-free areas | Auto-detect DAPI-dense areas | Off | |

## Manual correction

Click a fiber to see its measurements. Shortcuts: **C** toggles central nucleation, **R** toggles marker positivity, **X** excludes or restores a fiber. **Draw fiber**, **Draw red+** and **Draw injured area** add what the automatic analysis missed. Click a grey (undetected) region to see why it was rejected, set it to *Injured*, *Non-injured* or *By category*, or convert it to a fiber (shortcuts I, N, F). All corrections are recorded in the CSV.

## Cellpose (optional)

Requires Python and, for speed, an NVIDIA GPU.

```
conda create -n cellpose python=3.10 -y
conda activate cellpose
pip install "cellpose[gui]" tifffile imagecodecs
python -c "import torch; print(torch.cuda.is_available())"     # should print True
```

**One click:** put `cellpose_server.py` and `eMyHC_Quanti.html` in the same folder and run `python cellpose_server.py`. The tool opens at http://127.0.0.1:8765 (on Windows, macOS, Linux desktops and WSL); load an image and click **Segment with Cellpose (local GPU)**. Use `--model <path>` for a fine-tuned model and `--diam_um` to set the fiber diameter for Cellpose 3 models.

**Batch:** `python cellpose_batch.py <folder>` writes `<image>_cp_masks.tif` for every `*_Merge.tif`; load the image in the tool and **Import Cellpose masks**.

## Output

The summary shows the marker+ fraction of the injured region, numbers of fibers and CNFs, injured area, marker+ area and fibers, and fiber-area statistics. The CSV contains the summary, fiber-area statistics, all parameters (with tool version, analysis time, image name and segmentation source) and one row per fiber. The overlay can be exported as PNG.

## Validation

Compare the automated results with manual quantification on a random subset of sections (for example two blinded raters counting CNFs and marker+ fibers and tracing fibers), and report agreement as intraclass correlation coefficients and Bland–Altman plots. Validation results for the accompanying study are reported in [Supplementary Fig. x].

## Limitations

- The marker threshold strongly affects the marker+ fraction. Set a fixed threshold for the whole experiment, chosen so that secondary-only controls are essentially negative.
- Segmentation relies on WGA membrane staining. Check the overlay for fibers that are merged, split or missed, and correct them or use Cellpose.
- Marker-positive fibers sectioned outside their central nucleus are not counted as injured with the default settings, which makes the marker+ fraction conservative.
- One image is analyzed at a time in the browser; use `cellpose_batch.py` to prepare segmentations for many images.

## How to cite

Please cite the article above and the archived software version:

> [Authors]. eMyHC_Quanti: quantification of muscle injury and regeneration (v2.3.0). *Zenodo* https://doi.org/[DOI] ([year]).

If you use Cellpose segmentation, also cite Cellpose. Citation metadata are in `CITATION.cff`.

## Use of AI tools

The source code was generated with the assistance of a large language model (Claude, Anthropic). The authors specified the analysis procedure, reviewed the code and validated its output against manual quantification, and take full responsibility for the code.

## License

MIT License (see `LICENSE`). Third-party components are listed in `THIRD_PARTY_NOTICES.md`.

## Contact

[Name], [Institution], [email]. Please report problems through the GitHub issue tracker.

## References

1. Otsu, N. A threshold selection method from gray-level histograms. *IEEE Trans. Syst. Man Cybern.* **9**, 62–66 (1979).
2. Borgefors, G. Distance transformations in digital images. *Comput. Vis. Graph. Image Process.* **34**, 344–371 (1986).
3. Vincent, L. & Soille, P. Watersheds in digital spaces: an efficient algorithm based on immersion simulations. *IEEE Trans. Pattern Anal. Mach. Intell.* **13**, 583–598 (1991).
4. Stringer, C., Wang, T., Michaelos, M. & Pachitariu, M. Cellpose: a generalist algorithm for cellular segmentation. *Nat. Methods* **18**, 100–106 (2021).
