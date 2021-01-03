import argparse
import glob
import os
import numpy as np
from pathlib import Path

import skimage
from skimage import io, transform

example_usage = '''example:
  python shrink_images.py "data-raw/**/*jpg" data/mass512
  python shrink_images.py "data-raw/**/*jpg" data/mass256 -r 256
'''

parser = argparse.ArgumentParser(epilog=example_usage, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("input", help="glob with which to look look for files. Must be enclosed in quotes.", type=str)
parser.add_argument("output", help="directory to output", type=Path)
parser.add_argument("-r", "--resolution", default=512, help="resolution of output images. Defaults to 512.",type=int)
args = parser.parse_args()

if os.path.isdir(args.output):
    raise argparse.ArgumentTypeError("Output directory already exists! Will not overwrite.")
else:
    os.makedirs(args.output)

def load_convert(f):
    i = io.imread(f)
    return (transform.resize(i, output_shape = (args.resolution, args.resolution), anti_aliasing=True)*255).astype(np.uint8)

filenames = glob.glob(args.input)
collection = io.ImageCollection(filenames, load_func = load_convert)

for i, im in enumerate(collection):
    io.imsave(os.path.join(args.output, f'mass{i}.jpg'), im)
    