#!/usr/bin/env bash
set -euo pipefail

mkdir -p static/dist/css static/dist/js

for source in static/css/*.css; do
    [ -f "$source" ] || continue

    filename="$(basename "$source" .css)"

    ./node_modules/.bin/cleancss \
        --with-rebase "$source" \
        -o "static/dist/css/${filename}.min.css"
done

for source in static/js/*.js; do
    [ -f "$source" ] || continue

    filename="$(basename "$source" .js)"

    ./node_modules/.bin/terser "$source" \
        --compress \
        --mangle \
        --format comments=false \
        --output "static/dist/js/${filename}.min.js"
done

echo "Minification completed successfully."