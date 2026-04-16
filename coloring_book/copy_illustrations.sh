#!/bin/bash
set -e
ILLUS_DIR="/Users/michaelprice/Desktop/lauralai/250proud_landing/coloring_book/illustrations"
mkdir -p "$ILLUS_DIR"
BRAIN="/Users/michaelprice/.gemini/antigravity/brain/e27ee9ab-c901-487c-86ad-b0d38010b88a"

cp "$BRAIN/page_3_declaration_1776282861548.png" "$ILLUS_DIR/page_03.png"
cp "$BRAIN/page_4_washington_1776282875375.png" "$ILLUS_DIR/page_04.png"
cp "$BRAIN/page_5_capitol_1776282887204.png" "$ILLUS_DIR/page_05.png"
cp "$BRAIN/page_6_lewis_clark_v2_1776286461478.png" "$ILLUS_DIR/page_06.png"
cp "$BRAIN/page_7_sequoyah_v2_1776286474876.png" "$ILLUS_DIR/page_07.png"
cp "$BRAIN/page_8_tubman_v2_1776286487266.png" "$ILLUS_DIR/page_08.png"
cp "$BRAIN/page_9_lincoln_1776282939361.png" "$ILLUS_DIR/page_09.png"
cp "$BRAIN/page_10_railroad_1776282950730.png" "$ILLUS_DIR/page_10.png"
cp "$BRAIN/page_11_edison_v2_1776286500152.png" "$ILLUS_DIR/page_11.png"
cp "$BRAIN/page_12_wright_1776282981502.png" "$ILLUS_DIR/page_12.png"
cp "$BRAIN/page_13_suffrage_v3_1776287199122.png" "$ILLUS_DIR/page_13.png"
cp "$BRAIN/page_14_mustang_1776283007830.png" "$ILLUS_DIR/page_14.png"
cp "$BRAIN/page_15_rosie_1776283022044.png" "$ILLUS_DIR/page_15.png"
cp "$BRAIN/page_16_highway_v2_1776286527127.png" "$ILLUS_DIR/page_16.png"
cp "$BRAIN/page_17_moon_v2_1776286540689.png" "$ILLUS_DIR/page_17.png"
cp "$BRAIN/page_18_bridge_1776283061947.png" "$ILLUS_DIR/page_18.png"
cp "$BRAIN/page_19_mlk_v2_1776286553680.png" "$ILLUS_DIR/page_19.png"
cp "$BRAIN/page_20_arpanet_v3_1776287211185.png" "$ILLUS_DIR/page_20.png"
cp "$BRAIN/page_21_webb_1776283097597.png" "$ILLUS_DIR/page_21.png"
cp "$BRAIN/page_22_finale_v2_1776286577771.png" "$ILLUS_DIR/page_22.png"

echo "Copied images to illustrations directory."

cd /Users/michaelprice/Desktop/lauralai/250proud_landing/coloring_book
python3 build_book.py
python3 build_book_print.py
