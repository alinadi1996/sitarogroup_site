#!/usr/bin/env bash
set -euo pipefail

mkdir -p static/dist/css static/dist/js

npx --yes \
    --package=clean-css-cli@5.6.3 \
    --package=terser@5.51.2 \
    --call '
        set -eu
        for source in static/css/*.css; do
            filename="$(basename "$source" .css)"
            cleancss --with-rebase "$source" -o "static/dist/css/${filename}.min.css"
        done
        for source in static/js/*.js; do
            filename="$(basename "$source" .js)"
            terser "$source" --compress --mangle --format comments=false \
                --output "static/dist/js/${filename}.min.js"
        done
    '
