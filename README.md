# valid_multimodel
Video Aspect Ratio Finder & Same-Video Detector
This API provides a solution for processing multiple video uploads to extract metadata and identify duplicate content across different aspect ratios.

Public URL

Features
Metadata Extraction: Automatically identifies video width, height, and aspect ratio using ffprobe.
Canonical Bucketing: Groups videos into standard buckets (9:16, 1:1, 4:5, 16:9) with a $\pm1\%$ tolerance.
Same-Video Detection: Uses perceptual video hashing to match content even if it has been resized or slightly modified.
In-Memory Storage: Efficiently handles data without the need for an external database.