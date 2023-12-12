import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os

def concatenate_and_get_columns(image_path, n):
    # Open the image
    original_image = Image.open(image_path)

    # Convert the image to a NumPy array for easier manipulation
    img_array = np.array(original_image)

    # Get the shape of the array
    height, width, c = img_array.shape

    # Ensure that n is not greater than the width of the original image
    n = min(n, width)

    # Split the image vertically in half
    upper_half = img_array[:height // 2, :]
    lower_half = img_array[height // 2:, :]

    # Concatenate the lower half to the right of the upper half
    concatenated_image_array = np.concatenate((upper_half, lower_half), axis=1)

    # Get the first n columns from the concatenated image
    new_image_array = concatenated_image_array[:, :n]

    return new_image_array

if __name__ == '__main__':
    dir_path = r"C:\Users\mhueppe.LAPTOP-PKNG4OSF\MasterInformatik\Semester_1\ImageDiffusion\results\DDPM_conditional_cifar10_32"
    images = os.listdir(dir_path)

    n_columns = (35*10)-6  # Set the desired number of columns

    fig, ax = plt.subplots()
    ims = []

    for image in images:
        image_path = os.path.join(dir_path, image)
        concatenated_image = concatenate_and_get_columns(image_path, n_columns)
        im = ax.imshow(concatenated_image)
        ims.append([im])

    ani = FuncAnimation(fig, ims, blit=False)
    plt.show()