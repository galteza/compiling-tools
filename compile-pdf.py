import argparse
import os
from PIL import Image
import pymupdf
import io

## Page size definitions at 300dpi
SIZES_300DPI = {
    "A4": (3508, 2480),
    "B4": (3508, 4961),
    "B5": (1748, 2480),
}

DPI_OVER_PPI = 300.0 / 72.0

PAGE_SIZES_PT = {
    name: (dims[0] / DPI_OVER_PPI, dims[1] / DPI_OVER_PPI)
    for name, dims in SIZES_300DPI.items()
}

## IMAGE PREP FUNCTIONS

def _optimize_image_bytes(file_path, max_size=(3508, 3508), quality=85):
    # Optimize the image by reading its bytes and returning them
    # Convert transparent to white (detach alpha), optionally downscales, encodes to JPEG in-memory
    with Image.open(file_path) as img:
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            img = img.convert("RGBA") # Ensure image has an alpha channel for transparency handling
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        else:
            img = img.convert("RGB")

        # Downscaled if needed
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        with io.BytesIO() as output:
            img.save(output, format="JPEG", quality=quality, optimize=True)
            image_bytes = output.getvalue()
    return image_bytes

def _calculate_fit_rect(image_bytes, slot):
    # Calculate the fit rectangle for the image within the slot and return exactly the rectangle coordinates of the fitted image relative to the slot
    with Image.open(io.BytesIO(image_bytes)) as img:
        img_width, img_height = img.size
    
    slot_width = slot[2] - slot[0]
    slot_height = slot[3] - slot[1]

    scale = min(slot_width / img_width, slot_height / img_height)

    new_width = int(img_width * scale)
    new_height = int(img_height * scale)

    x_offset = slot[0] + (slot_width - new_width) // 2
    y_offset = slot[1] + (slot_height - new_height) // 2

    return pymupdf.Rect(x_offset, y_offset, x_offset + new_width, y_offset + new_height)

def _compile_pdf_normal(input_folder_path, output_pdf_path, size_pt: tuple, max_pixel_size):

    doc = pymupdf.open()
    file_paths = sorted([os.path.join(input_folder_path, f) for f in os.listdir(input_folder_path) if f.lower().endswith(".png") or f.lower().endswith(".jpg") or f.lower().endswith(".jpeg")])
    slot = (0,0,size_pt[0], size_pt[1])

    for i in range(0, len(file_paths)):
        page = doc.new_page(width=size_pt[0], height=size_pt[1])

        bytes = _optimize_image_bytes(file_paths[i], max_size=max_pixel_size, quality=85)
        rect = _calculate_fit_rect(bytes, slot)
        page.insert_image(rect, stream=bytes)

    doc.save(
        output_pdf_path,
        garbage=4,
        deflate=True,
        clean=True,
    )

    doc.close()
    print(f"Saved PDF to {output_pdf_path}")

def _compile_pdf_twopage(input_folder_path, output_pdf_path, size, max_pixel_size):
    doc = pymupdf.open()
    file_paths = sorted([os.path.join(input_folder_path, f) for f in os.listdir(input_folder_path) if f.lower().endswith(".png") or f.lower().endswith(".jpg") or f.lower().endswith(".jpeg")])
    left_slot = (0, 0, size[0], size[1])
    right_slot = (size[0], 0, size[0] * 2, size[1])

    for i in range(0, len(file_paths), 2):
        page = doc.new_page(width=size[0] * 2, height=size[1])

        bytes_left = _optimize_image_bytes(file_paths[i], max_size=max_pixel_size, quality=85)
        rect_left = _calculate_fit_rect(bytes_left, left_slot)
        page.insert_image(rect_left, stream=bytes_left)

        if i + 1 < len(file_paths):
            bytes_right = _optimize_image_bytes(file_paths[i + 1], max_size=max_pixel_size, quality=85)
            rect_right = _calculate_fit_rect(bytes_right, right_slot)
            page.insert_image(rect_right, stream=bytes_right)

    doc.save(
        output_pdf_path,
        garbage=4,
        deflate=True,
        clean=True,
    )

    doc.close()
    print(f"Saved PDF to {output_pdf_path}")

def compile_pdf(input_folder, size, mode, output_pdf_name):

    os.makedirs('output', exist_ok=True)
    if os.path.exists(os.path.join('output', f"{output_pdf_name}.pdf")):
        output_pdf_name = f"{output_pdf_name}_copy"

    size_pt = PAGE_SIZES_PT[size]
    max_pixel_size = SIZES_300DPI[size]
    
    output_pdf_path = os.path.join('output', f"{output_pdf_name}.pdf")
    input_folder_path = os.path.join('assets', input_folder)

    if mode == "normal":
        _compile_pdf_normal(input_folder_path, output_pdf_path, size_pt, max_pixel_size=max_pixel_size)
    elif mode == "twopage":
        _compile_pdf_twopage(input_folder_path, output_pdf_path, size_pt, max_pixel_size=max_pixel_size)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Compile a PDF file")
    parser.add_argument("input_folder", help="Input folder containing images")
    parser.add_argument("size", choices=["A4", "B4", "B5"], help="PDF page size")
    parser.add_argument("mode", choices=["normal", "twopage"], help="Compilation mode")
    parser.add_argument("output_pdf_name", help="Output PDF file", nargs="?", default="untitled")

    args = parser.parse_args()

    input_folder = args.input_folder
    size = args.size
    mode = args.mode
    output_pdf_name = args.output_pdf_name

    compile_pdf(input_folder, size.upper(), mode, output_pdf_name=output_pdf_name)
