import os
import time

import numpy as np
import cv2
from PIL import Image
import PIL
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.animation as animation
def pad_to_square(img):
    # read image
    ht, wd, cc = img.shape
    # create new image of desired size and color (blue) for padding
    if ht > wd:
        ww = hh = ht
    else:
        ww = hh = wd
    color = (255, 255, 255)
    result = np.full((hh, ww, cc), color, dtype=np.uint8)

    # compute center offset
    xx = (ww - wd) // 2
    yy = (hh - ht) // 2

    # copy img image into center of result image
    result[yy:yy + ht, xx:xx + wd] = img
    return result

def resize(img = None,image_path = None, image_width = 64, image_height = 64):
    if img is None:
        img = Image.open(image_path)
    if img.size != (image_height, image_width):
        img = img.resize((image_height, image_width))  # resize to 64,64,3
    return img

def uniform_background(img, r=0, g=0, b=0):
    img_data = np.asarray(img.getdata())

    number_of_white_pix = np.sum(img_data == (255, 255, 255))
    number_of_other_pix = np.sum(img_data == (r, g, b))

    # if there are more black/green/red/blue pixels than white change them to white
    # the background has a very distinct color (126 for the respective color channel)
    # which is only used as a background because of resizing the there are also very few
    # complete black pixel (rather really dark grey but 0,0,0 is only used in the background)
    if number_of_white_pix < number_of_other_pix:
        img2 = make_white(img)  # make the background white
        return img2
    return img

def convert_pil_to_cv(img):
    # use numpy to convert the pil_image into a numpy array
    numpy_image = np.array(img)

    # convert to a openCV2 image, notice the COLOR_RGB2BGR which means that
    # the color is converted from RGB to BGR format
    opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
    return opencv_image

def center_focus(img: PIL.Image, tol=255, border=4) -> PIL.Image:
    """
    Removes unnecessary white borders of image (makes the entire image to its focal point)
    :param image_path: str - path to the images.
    :param tol: background color or border color to be removed
    :param border: remaining border of the image
    """

    img_data = convert_pil_to_cv(img)
    mask = img_data < tol
    if img_data.ndim == 3:
        mask = mask.all(2)
    m, n = mask.shape
    mask0, mask1 = mask.any(0), mask.any(1)
    col_start, col_end = mask0.argmax(), n - mask0[::-1].argmax()
    row_start, row_end = mask1.argmax(), m - mask1[::-1].argmax()
    img1 = pad_to_square(img_data[row_start - border:row_end + border, col_start - border:col_end + border])
    # You may need to convert the color.
    n_pixels = img1.shape[0] * img1.shape[1] * 3
    if np.sum(img1 == (255, 255, 255)) > n_pixels*0.9:
        print("Not Center")
        return img
    else:
        return Image.fromarray(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB))


# uniform the backgrounds
def make_white(img, b=0, g=0, r=0):
    pixel_data = img.getdata()
    new_data = []

    # check for every pixel if it is either complete black, red, green, blue
    # (the three backgrounds that occurred in the dataset)
    for item in pixel_data:
        if item[0] == r and item[1] == g and item[2] == b:  # black
            new_data.append((255, 255, 255))  # append a white pixel instead
        elif item[0] != r and item[1] == g and item[2] == b:  # red
            new_data.append((255, 255, 255))
        elif item[0] == r and item[1] != g and item[2] == b:  # green
            new_data.append((255, 255, 255))
        elif item[0] == r and item[1] == g and item[2] != b:  # blue
            new_data.append((255, 255, 255))
        else:
            new_data.append(item)  # if it is none of the one keep the pixel as it is

    img.putdata(new_data)  # encode the pixel data with the swapped pixels as an image
    return img


if __name__ == '__main__':
    path = r"C:\Users\mhueppe.LAPTOP-PKNG4OSF\MasterInformatik\Semester_1\ImageDiffusion\data\raw _small\Body01"

    files = [os.path.join(path, file) for file in os.listdir(path) if "sprite" in file]


    fig, (og_ax, uniform_ax) = plt.subplots(1, 2)
    fig.set_size_inches(5, 5)
    fig.tight_layout()
    og_img = og_ax.imshow(Image.open(files[0]))
    uniform_img = uniform_ax.imshow(Image.open(files[0]))
    title = fig.suptitle(Path(files[0]).name)

    og_ax.set_title("Previous")
    uniform_ax.set_title("After Preprocessing")
    def update(frame):
        file_path = files[frame]
        og_img.set_array(Image.open(file_path))
        fig.suptitle(Path(file_path).name)
        uniform_img.set_array(center_focus(uniform_background(Image.open(file_path))))
        return og_img, uniform_img

    ani = animation.FuncAnimation(fig, update, frames=len(files), interval =1000, blit=True)
    plt.show()