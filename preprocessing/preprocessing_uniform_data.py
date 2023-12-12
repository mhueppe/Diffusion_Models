import os
import shutil
from PIL import Image
import cv2
import numpy as np
import ntpath


def overwrite(img, image_path, jpg_path):
    if jpg_path is not None:
        img.save(image_path, "PNG")  # and save the new one
        os.remove(jpg_path)  # remove the original image
    else:
        try:
            os.remove(image_path)  # remove the original image
            img.save(image_path, "PNG")  # and save the new one
        except:
            img.save(image_path, "PNG")


# uniform mode and size
def resize_and_convert(image_path, image_width = 64, image_height = 64):
    img = Image.open(image_path)

    if img.mode != "RGB":
        img = img.convert("RGBA")  # convert image to "RGBA" to paste it with a white background
        background = Image.new("RGB", img.size, (255, 255, 255))
        img.load()  # required for png.split()
        background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
        background = background.resize((image_height, image_width))  # resize to 64,64,3
        os.remove(image_path)  # remove the original image
        background.save(image_path, 'PNG')  # save the new image
    else:
        img = img.resize((image_height, image_width))  # resize to 64,64,3
        os.remove(image_path)  # remove the original image
        img.save(image_path, 'PNG')  # save the new image


def resize_and_save(image_path = None, image_width = 64, image_height = 64):
    img = Image.open(image_path)

    if img.size != (image_height, image_width):
        img = img.resize((image_height, image_width))  # resize to 64,64,3
        os.remove(image_path)  # remove the original image
        img.save(image_path, 'PNG')  # save the new image

def resize(img = None,image_path = None, image_width = 64, image_height = 64):
    if img is None:
        img = Image.open(image_path)
    if img.size != (image_height, image_width):
        img = img.resize((image_height, image_width))  # resize to 64,64,3
    return img


# uniform file type
def make_png(image_path):
    # removing any non png and converting it into png (jpeg, jpg)
    img = Image.open(image_path)
    if ".png" in image_path: return img
    if ".jpg" in image_path:
        fp = image_path.replace(".jpg", ".png")
        img.save(fp, "PNG")
        os.remove(image_path)
        return Image.open(fp)
    if ".jpeg" in image_path:
        fp = image_path.replace(".jpeg", ".png")
        img.save(fp, "PNG")
        os.remove(image_path)
        return Image.open(fp)


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


# check for white background
def uniform_background(img, r=0, g=0, b=0):
    cv_img = cv2.imread(img)

    number_of_white_pix = np.sum(cv_img == (255, 255, 255))
    number_of_other_pix = np.sum(cv_img == (r, g, b))
    img = Image.open(image_path)

    # if there are more black/green/red/blue pixels than white change them to white
    # the background has a very distinct color (126 for the respective color channel)
    # which is only used as a background because of resizing the there are also very few
    # complete black pixel (rather really dark grey but 0,0,0 is only used in the background)
    if number_of_white_pix < number_of_other_pix:
        img2 = make_white(img)  # make the background white
        return img2
    return img


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


def convert_pil_to_cv(img):
    # use numpy to convert the pil_image into a numpy array
    numpy_image = np.array(img)

    # convert to a openCV2 image, notice the COLOR_RGB2BGR which means that
    # the color is converted from RGB to BGR format
    opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
    return opencv_image


def convert_cv_to_pil(img):
    # convert from openCV2 to PIL. Notice the COLOR_BGR2RGB which means that
    # the color is converted from BGR to RGB
    color_converted = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(color_converted)
    return pil_image


def center_focus(image_path, tol=255, border=4):
    """
    Removes unnecessary white borders of image (makes the entire image to its focal point)
    :param image_path: str - path to the images.
    :param tol: background color or border color to be removed
    :param border: remaining border of the image
    """

    img = cv2.imread(image_path)
    mask = img < tol
    if img.ndim == 3:
        mask = mask.all(2)
    m, n = mask.shape
    mask0, mask1 = mask.any(0), mask.any(1)
    col_start, col_end = mask0.argmax(), n - mask0[::-1].argmax()
    row_start, row_end = mask1.argmax(), m - mask1[::-1].argmax()
    img1 = pad_to_square(img[row_start - border:row_end + border, col_start - border:col_end + border])
    # You may need to convert the color.
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
    img1 = Image.fromarray(img1)
    n_pixels = img1.size[0] * img1.size[1] * 3
    if np.sum(convert_pil_to_cv(img1) == (255, 255, 255)) > n_pixels*0.9:
        print(f"{Path(image_path).name} would have been destroyed")
        return img
    else:
        return img1


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def uniform(image_path, image_height=64, image_width=64):
    # uniform the filetype
    img = make_png(image_path)
    img = uniform_background(img)
    img = center_focus(img)
    try:
        # uniform the size and the transparency
        resize_and_convert(image_path, image_height, image_width)
    except:
        resize_and_save(image_path)
    # uniform the backgrounds


if __name__ == "__main__":
    # get all the needed paths
    current = os.getcwd()
    images = os.listdir("./images")

    for image in images:
        image_path = os.path.join("./images", image)
        uniform(image_path, 64, 64)
    print("Done")
