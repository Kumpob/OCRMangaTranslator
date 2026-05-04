import argparse
from draw import run_all_draw
from run_ocr import run_all_ocr
from translate import run_all_translate

def main(input_dir, ocr_output_dir, final_output_dir):
    # Step 1: OCR
    run_all_ocr(input_dir, ocr_output_dir)
    
    # Step 2: Translate
    run_all_translate(ocr_output_dir)
    
    # Step 3: Draw
    run_all_draw(ocr_output_dir, input_dir, final_output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process images with OCR, translation, and drawing.")
    parser.add_argument("--input", "-i", default="images", help="Input images directory")
    parser.add_argument("--ocr_output", "-o", default="output", help="OCR output directory")
    parser.add_argument("--final_output", "-f", default="final", help="Final output directory")
    
    args = parser.parse_args()
    
    main(args.input, args.ocr_output, args.final_output)