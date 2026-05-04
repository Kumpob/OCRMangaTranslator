from paddleocr import PaddleOCRVL
import os

os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

ocr = PaddleOCRVL()


def save_to_json(image_path, output_dir):
    print(f"Running OCR on {image_path}")
    result = ocr.predict(image_path)
    for res in result:
        res.print()
        res.save_to_json(output_dir)
        print(f"Saved OCR result for {image_path} to {output_dir}")


def run_all_ocr(image_dir, output_dir):
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created directory: {os.path.abspath(output_dir)}")
        except Exception as e:
            print(f"Error creating directory: {e}")
    for file in os.listdir(image_dir):
        if file.endswith(".png"):
            file_name= file.split(".")[0]
            print(f"Processing {file_name}...")
            if os.path.exists(f"{output_dir}/{file_name}_res.json"):
                print(f"OCR result for {file} already exists, skipping.")
                continue
            save_to_json(f"{image_dir}/{file}", output_dir)
