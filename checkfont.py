import os

# Path to Windows fonts folder
fonts_dir = "C:/Windows/Fonts"

# List all files in the fonts directory
for font_file in os.listdir(fonts_dir):
    # Check if the file is a font file
    if font_file.lower().endswith((".ttf", ".otf", ".ttc")):
        print(font_file)