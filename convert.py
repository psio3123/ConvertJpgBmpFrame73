#encoding: utf-8

import sys
import os.path
from PIL import Image, ImagePalette, ImageOps
import argparse

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='Convert image or images in folder to BMP for Wafeshare Picture Frame 7.3')

# Add orientation parameter
parser.add_argument('path_or_file', type=str, help='Input image file or folder')
parser.add_argument('--dir', choices=['landscape', 'portrait'], help='Image direction (landscape or portrait)')
parser.add_argument('--mode', choices=['scale', 'cut'], default='scale', help='Image conversion mode (scale or cut)')
parser.add_argument('--dither', type=int, choices=[Image.NONE, Image.FLOYDSTEINBERG], default=Image.FLOYDSTEINBERG, help='Image dithering algorithm (NONE(0) or FLOYDSTEINBERG(3))')

# Parse command line arguments
args = parser.parse_args()

# Get input parameter
path_or_file = args.path_or_file
display_direction = args.dir
display_mode = args.mode
display_dither = Image.Dither(args.dither)

###############################################################################
# Conversion function
###############################################################################
def convert_image(input_filename, display_direction, display_mode, display_dither):
    # Check whether the input file exists

    # Read input image
    input_image = Image.open(input_filename)

    # Get the original image size
    width, height = input_image.size

    # Specified target size
    if display_direction:
        if display_direction == 'landscape':
            target_width, target_height = 800, 480
        else:
            target_width, target_height = 480, 800
    else:
        if  width > height:
            target_width, target_height = 800, 480
        else:
            target_width, target_height = 480, 800
        
    if display_mode == 'scale':
        # Computed scaling
        scale_ratio = max(target_width / width, target_height / height)

        # Calculate the size after scaling
        resized_width = int(width * scale_ratio)
        resized_height = int(height * scale_ratio)

        # Resize image
        output_image = input_image.resize((resized_width, resized_height))

        # Create the target image and center the resized image
        resized_image = Image.new('RGB', (target_width, target_height), (255, 255, 255))
        left = (target_width - resized_width) // 2
        top = (target_height - resized_height) // 2
        resized_image.paste(output_image, (left, top))
    elif display_mode == 'cut':
        # Calculate the fill size to add or the area to crop
        if width / height >= target_width / target_height:
            # The image aspect ratio is larger than the target aspect ratio, and padding needs to be added on the left and right
            delta_width = int(height * target_width / target_height - width)
            padding = (delta_width // 2, 0, delta_width - delta_width // 2, 0)
            box = (0, 0, width, height)
        else:
            # The image aspect ratio is smaller than the target aspect ratio and needs to be filled up and down
            delta_height = int(width * target_height / target_width - height)
            padding = (0, delta_height // 2, 0, delta_height - delta_height // 2)
            box = (0, 0, width, height)

        resized_image = ImageOps.pad(input_image.crop(box), size=(target_width, target_height), color=(255, 255, 255), centering=(0.5, 0.5))
    # Create a palette object
    pal_image = Image.new("P", (1,1))
    pal_image.putpalette( (0,0,0,  255,255,255,  255,255,0,  255,0,0,  0,0,0,  0,0,255,  0,255,0) + (0,0,0)*249)
    
    # The color quantization and dithering algorithms are performed, and the results are converted to RGB mode
    quantized_image = resized_image.quantize(dither=display_dither, palette=pal_image).convert('RGB')
    # Save output image
    output_filename = os.path.splitext(input_filename)[0] + '.bmp'  
    quantized_image.save(output_filename)
    print(f'Successfully converted {input_filename} to {output_filename}')

##############################################################################
# Main Program
##############################################################################

# Check if user wants to convert all images in the folder
if path_or_file:
    if os.path.isdir(path_or_file):
        print(f'Processing folder {path_or_file}')
        # we have a folder
        input_folder = os.path.abspath(path_or_file)
        for filename in os.listdir(input_folder):
            if not os.path.isdir(filename):
                if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    continue
                if filename.startswith('.'):
                    continue
                print(f'Processing file {filename}')
                convert_image( input_folder + '/' + filename, display_direction, display_mode, display_dither)
        sys.exit(0)
    else:
        filename = path_or_file
        print(f'Processing file {filename}')
        if not os.path.isfile(filename):
            print(f'Error: file {filename} does not exist')
            sys.exit(1)
        else:
            convert_image(os.path.abspath(filename), display_direction, display_mode, display_dither)
else:
    print(f'Error: missing parameter path_or_file')
    sys.exit(1)
