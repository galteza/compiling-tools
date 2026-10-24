import argparse
import os
from PIL import Image

## Page size definitions at 300dpi
A4 = (3508, 2480)  # Width and height in points for A4 size 300dpi
B4 = (3508, 4961)  # Width and height in points for B4 size 300dpi
B5 = (2480, 1748)  # Width and height in points for B5 size 300dpi

parser = argparse.ArgumentParser(description="Compile a PDF file")
parser.add_argument("i", help="Input PDF file")
parser.add_argument("size", help="PDF page size")
parser.add_argument("mode", help="Compilation mode")

args = parser.parse_args()

input_folder = args.i
size = args.size
mode = args.mode

def _prep_image(input_folder, size):
    # Prepare the images by resizing to specified size

    for filename in os.listdir(input_folder):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)
            img = img.resize(size)
            img.save(img_path)


def compile_pdf_normal(input_folder):


def compile_pdf_twopage(input_folder):




if mode == "normal":
    compile_pdf_normal(input_folder)
elif mode == "twopage":
    compile_pdf_twopage(input_folder)

pdf.compile(args.input, args.output)
