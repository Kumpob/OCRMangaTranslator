import os
from PIL import Image

# Folder containing images
input_folder = "test"
# Folder to save converted png images
output_folder = "test/png"

# Supported input formats
supported_formats = (".jpg", ".jpeg", ".bmp", ".tiff", ".webp", ".gif")

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through all files in the input folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith(supported_formats):
        input_path = os.path.join(input_folder, filename)
        png_filename = os.path.splitext(filename)[0] + ".png"
        output_path = os.path.join(output_folder, png_filename)

        # Open image and convert to PNG
        with Image.open(input_path) as img:
            # Convert mode if needed (some images like GIFs may need conversion)
            if img.mode in ("P", "RGBA", "LA"):
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")
            img.save(output_path, "PNG")
        
        print(f"Converted: {filename} -> {png_filename}")

print("All supported images have been converted to PNG.")