"""Run native SVG tracing outside the Django process (Python 3.13 runtime)."""

import sys

import vtracer


def main():
    source, destination, quality_value = sys.argv[1:]
    quality = int(quality_value)
    vtracer.convert_image_to_svg_py(
        source, destination, colormode="color", mode="spline",
        filter_speckle=max(1, round(8 - quality * .07)),
        color_precision=min(8, 3 + round(quality * .05)),
        path_precision=2 + round(quality * .02),
    )


if __name__ == "__main__":
    main()
