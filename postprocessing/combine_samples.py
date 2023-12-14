import matplotlib.pyplot as plt
from matplotlib import rcParams


import re

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation

import os
from pathlib import Path

def concatenate_and_get_columns(image_path, n):
    # Open the image
    original_image = Image.open(image_path)

    # Convert the image to a NumPy array for easier manipulation
    img_array = np.array(original_image)

    # Get the shape of the array
    height, width, c = img_array.shape

    # Ensure that n is not greater than the width of the original image

    # Split the image vertically in half
    upper_half = img_array[:height // 2, :]
    lower_half = img_array[height // 2:, :]

    # Concatenate the lower half to the right of the upper half
    concatenated_image_array = np.concatenate((upper_half, lower_half), axis=1)

    n = min(n, concatenated_image_array.shape[1])
    # Get the first n columns from the concatenated image
    new_image_array = concatenated_image_array[:, :n]

    return new_image_array

if __name__ == '__main__':
    # Set the font to be used
    rcParams['font.family'] = 'serif'  # Choose a font family (e.g., sans-serif, serif, monospace)

    use_ema = False
    use_file = lambda f: ("ema" in f if use_ema else "ema" not in f) and ".jpg" in f
    dir_path = r"C:\Users\mhueppe.LAPTOP-PKNG4OSF\MasterInformatik\Semester_1\ImageDiffusion\results\DDPM_conditional_cifar10_32"
    files = [os.path.join(dir_path, file) for file in os.listdir(dir_path) if use_file(file)]
    files.sort(key=lambda file: [int(x) if x.isdigit() else x for x in re.findall(r"[^0-9]|[0-9]+", Path(file).name)])

    image_size = 34
    n_classes = 10
    n_columns = ((image_size+1)*n_classes)-6  # Set the desired number of columns


    fig, (regular_ax, ema_ax) = plt.subplots(2)
    # fig.set_size_inches(15, 5)

    title = fig.suptitle("Results after 100 epochs")
    og_img = regular_ax.imshow(concatenate_and_get_columns(files[-1], n_columns))
    regular_ax.set_yticks([], [])
    regular_ax.set_xticks([i+image_size/2 for i in range(0, image_size*n_classes, image_size)], ["Airplane", "Car", "Bird", "Cat", "Deer", "Dog", "Frog", "Horse", "Ship", "Truck"])
    regular_ax.set_title("DDPM without EMA")

    use_ema = True
    use_file = lambda f: ("ema" in f if use_ema else "ema" not in f) and ".jpg" in f
    dir_path = r"C:\Users\mhueppe.LAPTOP-PKNG4OSF\MasterInformatik\Semester_1\ImageDiffusion\results\DDPM_conditional_cifar10_32"
    files = [os.path.join(dir_path, file) for file in os.listdir(dir_path) if use_file(file)]
    files.sort(key=lambda file: [int(x) if x.isdigit() else x for x in re.findall(r"[^0-9]|[0-9]+", Path(file).name)])

    og_img = ema_ax.imshow(concatenate_and_get_columns(files[-1], n_columns))
    ema_ax.set_yticks([], [])
    ema_ax.set_xticks([i+image_size/2 for i in range(0, image_size*n_classes, image_size)], ["Airplane", "Car", "Bird", "Cat", "Deer", "Dog", "Frog", "Horse", "Ship", "Truck"])
    ema_ax.set_title("DDPM with EMa")
    fig.tight_layout()
    # Save the plot as an SVG file
    plt.savefig(r'C:\Users\mhueppe.LAPTOP-PKNG4OSF\MasterInformatik\Semester_1\ImageDiffusion\Paper\src\Images\cifar10_results.svg', format='svg', dpi=300, bbox_inches='tight')

    plt.show()