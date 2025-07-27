#!/bin/bash

# Convert images to WebP format for better performance
# Requires: brew install webp (on macOS) or apt-get install webp (on Linux)

echo "Converting images to WebP format..."

# Check if cwebp is installed
if ! command -v cwebp &> /dev/null; then
    echo "cwebp command not found!"
    echo "Please install webp:"
    echo "  macOS: brew install webp"
    echo "  Linux: apt-get install webp"
    exit 1
fi

# Convert office.jpeg with quality optimization for LCP
echo "Converting office.jpeg..."
cwebp -q 85 assets/img/office.jpeg -o assets/img/office.webp

# Convert PNG files with lossless compression
echo "Converting pixel-nbb.png..."
cwebp -lossless assets/img/pixel-nbb.png -o assets/img/pixel-nbb.webp

echo "Converting pixel-rew.png..."
cwebp -lossless assets/img/pixel-rew.png -o assets/img/pixel-rew.webp

# List the created files
echo -e "\nCreated WebP files:"
ls -lh assets/img/*.webp

echo -e "\nConversion complete! Don't forget to update your HTML/CSS to use the new .webp files."