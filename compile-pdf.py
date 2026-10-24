import argparse
import os
from PIL import Image

## Page size definitions at 300dpi
A4 = (3508, 2480)  # Width and height in points for A4 size 300dpi
B4 = (3508, 4961)  # Width and height in points for B4 size 300dpi
B5 = (2480, 1748)  # Width and height in points for B5 size 300dpi

def _prep_image(input_folder: str, size: str):
    # Prepare the images by resizing to specified size

    for filename in os.listdir(input_folder):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)
            img = img.resize(eval(size))
            img.save(img_path)


def _compile_pdf_normal(input_folder, output_pdf):
    output_images = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)
            output_images.append(img)
    if output_images:
        output_images[0].save(output_pdf, "PDF", resolution=300.0, save_all=True, append_images=output_images[1:])

def _compile_pdf_twopage(input_folder, output_pdf, size):
    output_images = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)
            output_images.append(img)
    if output_images:
        output_images[0].save(output_pdf, "PDF", resolution=300.0, save_all=True, append_images=output_images[1:])

def compile_pdf(input_folder, size, mode, output_pdf=f"outputs/{input_folder}.pdf"):
    _prep_image(input_folder, size)
    if mode == "normal":
        _compile_pdf_normal(input_folder, output_pdf)
    elif mode == "twopage":
        _compile_pdf_twopage(input_folder, output_pdf, size)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Compile a PDF file")
    parser.add_argument("input_folder", help="Input folder containing images")
    parser.add_argument("size", help="PDF page size")
    parser.add_argument("mode", help="Compilation mode")
    parser.add_argument("output_pdf", help="Output PDF file", nargs="?", default=f"untitled.pdf")

    args = parser.parse_args()

    input_folder = args.input_folder
    size = args.size
    mode = args.mode
    output_pdf = args.output_pdf
    compile_pdf(input_folder, size, mode, output_pdf=output_pdf)
