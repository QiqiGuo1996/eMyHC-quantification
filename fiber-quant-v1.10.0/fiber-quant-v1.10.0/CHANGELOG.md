# Changelog

All notable changes to FiberQuant are documented here. Versions follow [Semantic Versioning](https://semver.org/).

## [1.10.0] – [YYYY-MM-DD]

### Added
- Solidity filter (area ÷ convex-hull area, default minimum 0.9): rejects concave gaps and interstitium squeezed between round fibers, which were previously accepted as fibers and often counted as injured because they contain nuclei.
- Minimum inscribed radius filter (default 2.5 µm): rejects narrow gaps between neighboring fibers.

## [1.9.0] – [YYYY-MM-DD]

### Added
- Mean ± SD and median fiber area for injured, non-injured and marker+ injured fibers, shown in the summary and exported to CSV.

## [1.8.0] – [YYYY-MM-DD]

### Added
- Common working resolution: every image is rescaled from its own pixel size to a chosen resolution before analysis, so images saved at different pixel sizes (for example by Keyence's automatic downscaling of stitched images) are analyzed identically.
- CSV records the original pixel size and the rescaling mode.

## [1.7.0] – [YYYY-MM-DD]

### Added
- Pixel size is read automatically from Keyence TIFF metadata; a warning is shown when a file has none.
- Segmentation check after each run, with counts of undetected regions by reason and parameter suggestions.
- Regions that are at least half marker-positive are exempt from the nuclear-content filter (can be switched off).

## [1.6.0] – [YYYY-MM-DD]

### Added
- Second segmentation pass with a smaller membrane dilation to recover small fibers.
- Undetected regions: Injured / Non-injured / By category selector and Convert to fiber, with shortcuts I, N and F.
- CSV reports second-pass dilation and the number of fibers converted from undetected regions.

### Changed
- Marker-based small-fiber detection accepts objects with up to 70% overlap with the WGA membrane mask (previously 40%), so small fibers enclosed by thick WGA staining are detected.

## [1.5.0] – [YYYY-MM-DD]

### Added
- Automatic detection of small marker-positive fibers missed by WGA segmentation, using a stricter second-level threshold, ring closing, and size, roundness and membrane-overlap criteria.
- Margin for the marker+ call: the marker fraction can be measured over the fiber plus a band outside its outline.
- CSV records the detection settings, threshold and number of marker-detected fibers, plus a per-fiber "red-detected" flag.

### Changed
- The marker mask is computed before fiber segmentation.

## [1.4.0] – [YYYY-MM-DD]

### Added
- Undetected regions can be counted as injured area by category (interstitium, oversized regions, small fragments, regions touching the image edge) or individually from the region's info panel. Settings and the number of individually toggled regions are exported to CSV.

## [1.3.0] – [YYYY-MM-DD]

### Added
- Draw fiber: outline a missed fiber to add it; it is classified automatically and can be corrected.
- Draw red+: outline missed marker-positive signal to add it to the marker mask.
- Drawings are re-applied when the analysis is re-run, and counts of each drawing type and a per-fiber "drawn" flag are exported to CSV.

## [1.2.0] – [YYYY-MM-DD]

### Added
- Fiber–interstitium separation: regions are rejected when their shape index (area ÷ area of the largest inscribed circle) or nuclear area fraction exceeds a set maximum, so interstitium is no longer counted as fibers.
- Enclosed unlabeled pockets inside fibers are filled.

### Changed
- Grow-back after membrane dilation now runs 2 × dilation + 1 iterations, restoring full fiber outlines at larger dilations.
- Default membrane dilation increased from 1 to 3 pixels.
- Nuclear mask is computed before fiber segmentation.

## [1.1.0] – [YYYY-MM-DD]

### Added
- Undetected-regions overlay: regions not accepted as fibers are shaded, and clicking one explains why (below minimum area, above maximum area, touching the image edge, or connected to the background).

### Changed
- Automatic downscaling now starts above about 20 megapixels instead of 12, so stitched Keyence BZ-X images (about 12.5 megapixels) are analyzed at full resolution.

## [1.0.0] – [YYYY-MM-DD]

Version used for the analyses in [Authors], *[Journal]* ([year]).

### Added
- Fiber segmentation from WGA staining with background subtraction, Gaussian smoothing, Otsu or fixed thresholds, membrane dilation and region growing.
- Identification of centrally nucleated fibers from nuclear signal in a distance-transform-defined fiber core.
- Marker-positive fiber classification and two methods for marker-positive area (pixels or whole positive fibers).
- Injured region defined by centrally nucleated fibers, with optional addition of marker-positive fibers and fiber-free areas (manually outlined or automatically detected DAPI-dense regions).
- Manual correction of central nucleation and marker calls, fiber exclusion, keyboard shortcuts and per-fiber flags for every correction.
- Display of fiber IDs, overlays for injured, marker-positive and selected fibers, and zoom and pan.
- Reading of RGB PNG, JPG and TIFF, and multipage 8-bit, 16-bit and 32-bit float TIFF, including planar-configuration files.
- CSV export of summary values, all parameters (with tool version and analysis time) and per-fiber data; PNG export of the overlay.
- Bilingual (Chinese and English) interface.
