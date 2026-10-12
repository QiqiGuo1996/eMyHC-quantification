# FiberQuant: browser-based quantification of muscle injury and regeneration

English | [中文](README.zh-CN.md)

<!-- Add the Zenodo DOI badge once the software has a DOI:
[![DOI](https://zenodo.org/badge/DOI/[DOI].svg)](https://doi.org/[DOI])
-->

**Use it online:** https://qiqiguo1996.github.io/muscle_image/

FiberQuant segments skeletal muscle fibers from wheat germ agglutinin (WGA) staining, identifies centrally nucleated fibers (CNFs) to define the injured region, and measures the area fraction of a positive marker (for example, embryonic myosin heavy chain, eMyHC) within that region.

The tool is a single self-contained HTML file. It runs in any current web browser, requires no installation, and processes images locally: no image data leave the user's computer.

This repository accompanies: [Authors]. [Title]. *[Journal]* ([year]). https://doi.org/[article DOI]

## Contents

| File | Description |
| --- | --- |
| `fiber-quant.html` | The complete tool (HTML, CSS and JavaScript) |
| `index.html` | Entry page for the online version; opens `fiber-quant.html` |
| `README.md` | This document |
| `README.zh-CN.md` | Chinese version of this document |
| `CHANGELOG.md` | Version history |
| `CITATION.cff` | Citation metadata |
| `LICENSE` | MIT License |
| `THIRD_PARTY_NOTICES.md` | Licenses of third-party libraries loaded at run time |

## Quick start

1. Open https://qiqiguo1996.github.io/muscle_image/, or download `fiber-quant.html` and open it in Chrome, Edge, Firefox or Safari (versions released in 2023 or later). Images are processed in the browser in both cases.
2. Click **Try a sample image** to explore the workflow on a synthetic image, or load your own image.
3. Assign the WGA, DAPI and marker channels, and enter the pixel size of the original image (µm per pixel).
4. Click **Run analysis**, inspect the overlay, correct misclassified fibers, and export the results as CSV.

Reading TIFF files requires an internet connection the first time, because the TIFF decoder is loaded from a public CDN. PNG and JPG files can be analyzed fully offline.

## Input requirements

- Transverse cryosections stained with WGA (fiber outlines), DAPI (nuclei) and one marker of interest.
- Either an RGB composite (PNG, JPG or TIFF) or a multichannel TIFF with one channel per page (8-bit, 16-bit or 32-bit float), such as files saved by Fiji/ImageJ.
- BigTIFF files (usually over 4 GB) cannot be read by browsers. Downscale them first in Fiji (*Image › Scale*) and save as a standard TIFF.
- Very large images are downscaled automatically to at most about 20 megapixels for processing (PNG and JPG files to about 16 megapixels when they are loaded). The effective pixel size is shown in the interface and recorded in the exported CSV.
- For 16-bit and 32-bit images, set *Intensity scaling* under *Load image*. Use *Fixed range* whenever thresholds are fixed for a whole experiment (see step 1 of the analysis workflow).

Keyence BZ-X stitched images: the software may downscale stitched images on saving, by a factor that depends on the number of tiles, so pixel size can differ between images acquired with identical settings. FiberQuant reads the calibration from Keyence TIFF metadata automatically and fills in the pixel size; files re-saved by other software usually lose this metadata, and the pixel size must then be entered by hand. To analyze a batch at identical resolution, set *Downscale for processing* to *Common*: each image is rescaled from its own pixel size to the common working resolution, so pixel-based parameters such as membrane dilation mean the same in every image.

## Analysis workflow

**1. Intensity normalization.** 16-bit and floating-point images are linearly rescaled to 8 bits in one of two ways. With *Per-image stretch* (default), each channel is rescaled between its own 0.05th and 99.95th intensity percentiles; this gives good contrast, but the same 8-bit threshold then corresponds to a different raw intensity in each image, and a nearly empty channel (such as a secondary-only control) is stretched to full range. With *Fixed range*, every channel of every image is rescaled between the same raw minimum and maximum (for example 0–4095 for a 12-bit camera), so fixed thresholds are comparable across images. The raw range applied to each channel is recorded in the CSV. 8-bit images are used as is.

**2. Fiber segmentation.** The WGA channel is background-subtracted using a smoothed, bilinearly interpolated map of local minima, smoothed with a Gaussian filter (approximated by three successive box filters) and thresholded (Otsu's method¹ by default). The membrane mask is dilated to separate touching fibers. Connected regions outside the membrane (4-connectivity) are labeled as fibers, grown back into the dilated band to restore their outlines, and enclosed unlabeled pockets (for example around nuclei) are filled. A second pass with a smaller dilation (default 1 pixel) recovers small fibers erased by the first: its regions are added only where they overlap existing fibers by less than 10%, and pass the same filters. Regions are discarded if their area is outside the accepted range, if they touch the image border (regions that touch the border and exceed the maximum area are always treated as background outside the section), if their largest inscribed radius is below the set minimum (narrow gaps between fibers), if their solidity (area divided by convex-hull area) is below the set minimum (concave gaps and interstitium squeezed between round fibers), if their shape index (area divided by the area of the largest inscribed circle) exceeds the set maximum, or if nuclei cover more than the set fraction of their area (regions that are at least half marker-positive are exempt, to protect small regenerating fibers with central nuclei); the last two criteria reject interstitium that would otherwise be mistaken for fibers.

**3. Nuclear and marker masks.** DAPI and marker channels are background-subtracted, smoothed (σ = 1 pixel) and thresholded in the same way.

**4. Centrally nucleated fibers.** A chamfer (3–4) distance transform² is computed inside each fiber. The fiber core comprises pixels farther from the boundary than the core inset; for small fibers the inset is capped at 40% of the maximum inscribed distance. A fiber whose core contains at least the minimum nuclear area is classified as a CNF, which excludes normal subsarcolemmal nuclei.

**5. Marker-positive fibers.** A fiber is classified as marker-positive when the marker covers at least the set fraction of its area, optionally measured over the fiber plus a margin outside its outline (for marker signal concentrated at the fiber rim). Small marker-positive fibers missed by WGA segmentation are added automatically: marker-positive objects (thresholded by a second Otsu step among marker-positive pixels, with gaps in ring-shaped signal closed over about 1.5 µm) are accepted as fibers if they do not touch a detected fiber, fall within the set area range, have an inscribed radius of at least 2.5 µm and a shape index of at most 3, and have at most 70% of their area on the WGA membrane mask.

**6. Injured region.** The injured region is the union of all CNFs, optionally together with marker-positive fibers. Fiber-free areas of dense nuclear infiltration can be added, either outlined by hand or detected automatically as contiguous regions of high local nuclear coverage. Regions not accepted as fibers can also be counted as injured, by category (interstitium rejected for shape or nuclear content, oversized regions, small fragments, regions touching the image edge) or individually by clicking them. Regions connected to the background outside the section are never counted. Only pixels outside segmented fibers are added from these areas; fibers inside them keep their own classification.

**7. Primary outcome.** The marker-positive fraction of the injured region:

```
Marker+ fraction (%) = (marker+ area in injured fibers + marker+ area in fiber-free injured areas)
                       / (area of injured fibers + fiber-free injured area) × 100
```

Marker+ area is counted either as marker-positive pixels (default) or as the whole area of marker-positive fibers (selectable).

## Parameters

| Group | Parameter | Default | Notes |
| --- | --- | --- | --- |
| Image | Intensity scaling (16/32-bit) | Per-image stretch | *Fixed range* (raw minimum–maximum, default 0–65535) makes fixed thresholds comparable across images; use 0–4095 for 12-bit cameras |
| Scale | Original pixel size | 0.65 µm/pixel | Must match the acquisition |
| Scale | Downscale for processing | Auto | Auto keeps images at or below about 20 megapixels; *Common* rescales every image to the common working resolution |
| Scale | Common working resolution | 0.91 µm/pixel | Used with *Common*; choose the coarsest resolution in the batch |
| Fiber segmentation | Background radius | 40 µm | 0 disables background subtraction |
| Fiber segmentation | Smoothing σ | 1 pixel | |
| Fiber segmentation | Threshold | Otsu | A fixed value (0–255) can be set instead |
| Fiber segmentation | Membrane dilation | 3 pixels | Closes gaps in WGA rings up to about twice this width; about 4 µm is a good start. Fibers grow back by 2 × dilation + 1 pixels |
| Fiber segmentation | Fiber area range | 80–12,000 µm² | |
| Fiber segmentation | Exclude border fibers | On | |
| Fiber segmentation | Second-pass dilation | 1 pixel | Recovers small fibers; can be switched off |
| Separation | Min. solidity | 0.9 | Round or oval fibers are about 0.94–0.98; 0 disables |
| Separation | Min. inscribed radius | 2.5 µm | Rejects narrow gaps; lower for very small fibers; 0 disables |
| Separation | Max. shape index | 4 | 1 for a circle; 0 disables |
| Separation | Max. nuclear area in a fiber | 50% | 0 disables; marker+ regions exempt by default |
| Central nuclei | Nuclear background radius | 20 µm | |
| Central nuclei | Nuclear threshold | Otsu | |
| Central nuclei | Core inset | 4 µm | Capped at 40% of the inscribed radius |
| Central nuclei | Min. nuclear area in core | 6 µm² | |
| Marker | Background radius | 40 µm | |
| Marker | Threshold | Otsu | Check visually when signal is sparse |
| Marker | Area fraction for marker+ fiber | 20% | |
| Marker | Marker+ area method | Pixels | Alternative: whole marker+ fibers |
| Marker | Margin for marker+ call | 0 µm | 1–3 µm when signal lies at the fiber rim |
| Marker | Detect small marker+ fibers | On | Area range 40–600 µm²; detection threshold auto (second Otsu) |
| Marker | Count marker+ fibers as injured | Off | |
| Fiber-free areas | Auto-detect DAPI-dense areas | Off | Manual outlining is always available |
| Fiber-free areas | Density radius | 15 µm | |
| Fiber-free areas | Nuclear coverage threshold | 25% | |
| Fiber-free areas | Min. region area | 1,500 µm² | |
| Fiber-free areas | Undetected regions counted as injured | None | Categories: interstitium, oversized, small fragments, edge; each region can also be toggled by clicking it |

After each run, a segmentation check lists undetected regions by reason and suggests parameter changes, for example when membrane dilation is likely to erase small fibers.

Use the same parameters for every image in an experiment. All parameters are written to the exported CSV.

## Manual correction

Click any fiber, or a row in the per-fiber table, to see its measurements. The following corrections are available, by button or keyboard shortcut:

| Action | Shortcut | Effect |
| --- | --- | --- |
| Toggle central nucleation | C | Changes the CNF call and therefore injured-region membership |
| Toggle marker positivity | R | A fiber marked positive counts with its whole area; one marked negative counts as zero |
| Exclude or restore fiber | X | Removes the fiber from all counts, for example a merged fiber or an artefact |
| Reset to automatic | Button | Clears all manual calls for the fiber |

Regions that were not accepted as fibers are shaded grey (*Undetected regions*). Click one to see why it was rejected, set it to *Injured*, *Non-injured* or *By category*, or *Convert to fiber* if it is actually a fiber (shortcuts I, N, F). The reasons are: below the minimum area, above the maximum area (usually fibers merged through membrane gaps), irregular shape, high nuclear content, touching the image edge, or connected to the background outside the section. Increasing membrane dilation (about 4 µm) or lowering the WGA threshold usually recovers fibers with incomplete membranes.

Three drawing tools add what the automatic analysis missed:

| Tool | Effect |
| --- | --- |
| **Draw injured area** | Fiber-free pixels inside the outline are added to the injured region |
| **Draw fiber** | Pixels inside the outline that do not belong to another fiber form a new fiber, which is classified by the same rules and can be corrected like any other |
| **Draw red+** | Pixels inside the outline are counted as marker-positive |

Trace missed fibers along their inner edge so that the membrane is not included. **Undo** removes drawings in reverse order and **Clear** removes all of them; drawings are re-applied automatically when the analysis is re-run. Every manual correction and drawing is recorded in the CSV.

## Output

**Summary on screen:** marker+ fraction of the injured region; number of fibers; number and percentage of CNFs; injured area (with the fiber-free part shown separately); marker+ area; number and percentage of marker+ fibers in the injured region; injured fibers as a share of total fiber area; mean ± SD and median area of injured, non-injured and marker+ injured fibers.

**CSV export** (UTF-8 with byte-order mark, opens directly in Excel) in four blocks:

1. Summary values.
2. Fiber area statistics (n, mean, SD, median) for injured, non-injured, marker+ injured and all fibers.
3. Parameters, including tool version, analysis time, image name, intensity scaling and the raw range applied to each channel, thresholds actually applied and the number of manual corrections.
4. One row per fiber: ID; area; core area; nuclear area in core; marker fraction; marker+ area counted; automatic and final CNF call; automatic and final marker call; injured; manual-correction flags; drawn fiber; marker-detected fiber; excluded; centroid coordinates.

**PNG export:** the current overlay, including fiber IDs if displayed, for documentation.

Areas are reported in µm²; centroids in pixels of the working resolution.

## Validation

Automated results should be validated against manual quantification before use in a study. We recommend that two blinded raters count CNFs and marker+ fibers and outline the injured region on a random subset of sections, and that agreement be reported as intraclass correlation coefficients and Bland–Altman plots. Validation results for the accompanying study are reported in [Supplementary Fig. x] of the article.

## Limitations

- Segmentation depends on continuous WGA membrane staining. Torn membranes, folds or strong interstitial staining can merge or split fibers; these should be corrected or excluded.
- Fibers whose WGA ring is incomplete merge with the interstitium or the background and are not detected. Check the *Undetected regions* overlay and adjust membrane dilation or the WGA threshold.
- Large infiltrated areas without membranes can be segmented as a single large "fiber" if their area falls within the accepted range. Exclude them and outline them as fiber-free injured areas instead.
- The marker threshold strongly affects the result. In one test image, the marker+ fraction of the injured area was 25.9% with the automatic threshold (26), 11.3% at 40 and 3.8% at 60. Set a fixed marker threshold for the whole experiment, chosen so that secondary-only controls are essentially negative. For 16-bit or 32-bit images, also set *Intensity scaling* to *Fixed range*; with per-image stretch, a fixed threshold does not correspond to the same raw intensity in every image.
- Otsu thresholds are computed per image. When marker signal is sparse, the automatic threshold may be too low; inspect the *Red+ pixels* overlay and set a fixed threshold if needed.
- The tool analyzes one image at a time.

## How to cite

If you use FiberQuant, please cite the article above and the archived software version:

> [Authors]. FiberQuant: browser-based quantification of muscle injury and regeneration (v1.11.0). *Zenodo* https://doi.org/[DOI] ([year]).

Citation metadata are provided in `CITATION.cff`.

## Use of AI tools

The source code was generated with the assistance of a large language model (Claude, Anthropic). The authors specified the analysis procedure, reviewed the code, and validated its output against manual quantification. The authors take full responsibility for the code.

## License

FiberQuant is released under the MIT License (see `LICENSE`). Third-party libraries loaded at run time are listed in `THIRD_PARTY_NOTICES.md`.

## Contact

[Name], [Institution], [email]. Please report problems through the GitHub issue tracker.

## References

1. Otsu, N. A threshold selection method from gray-level histograms. *IEEE Trans. Syst. Man Cybern.* **9**, 62–66 (1979).
2. Borgefors, G. Distance transformations in digital images. *Comput. Vis. Graph. Image Process.* **34**, 344–371 (1986).
