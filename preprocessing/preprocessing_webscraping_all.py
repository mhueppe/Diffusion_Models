# author: Michael Hüppe
# project: Pokemon Diffusion Image Generation

from typing import Tuple, List
from multiprocessing import Process, Lock, Value
import requests
from threading import Thread
from bs4 import BeautifulSoup
import os
from .preprocessing_uniform_data import uniform, center_focus, resize_and_save
import io
import PIL
from PIL import Image


# gets all the pokemon sites of their list
def get_pokemon(url: str, identifier: str = "pokedex") -> List[str]:
    """
    Parse the Pokedex for available pokemons
    :param url: Url of the identifier
    :param identifier:
    :return: List of links to their pokedex page
    """
    soup = get_soup(url)
    # find all the attributed tags (links that contain more information aka lead to
    # a different site here: the pokemon) from the website
    pokemon_urls = []
    for a in soup.find_all('a', href=True):
        # of all the attributed tags get only the ones that are pokemon (identifiable by the url (pokedex/sprites))
        if identifier in a['href']:
            # append this tag with the base link to form the complete link to the pokemon
            pokemon_urls.append('https://pokemondb.net' + a['href'])
    all_pokemon = list(set(pokemon_urls))
    all_pokemon.sort()
    return all_pokemon


def listed_sprites(soup: BeautifulSoup) -> List[str]:
    """
    Get all of the sprites for the pokemons
    :param soup:
    :return:
    """
    # find all images in the given parsed html file
    lists = soup.find_all('span')
    listed_pokemon = []
    # get all the lists
    for list in lists:
        # get all the href in each list
        listed_pokemon += [image['href'] for image in list.find_all('a', href=True)]

    return listed_pokemon


def listed_artwork(soup: BeautifulSoup) -> List:
    """
    Get all of the artwork
    :param soup:
    :return:
    """
    originals = [image['src'] for image in soup.find_all('img')]
    alternatives = [image['href'] for image in soup.find_all('a', href=True) if 'artwork' in image['href']]
    return originals + alternatives


def get_soup(url: str) -> BeautifulSoup:
    # request the given url
    r = requests.get(url)
    # parse it into a soup
    return BeautifulSoup(r.text, 'html.parser')


def download(images: str, save_path: str, n_retries: int = 5):
    """
    Download an image, process it and save it
    :param images:
    :param save_path:
    :return:
    """
    # for every image in the list make the filename valid and
    # and download it
    for image in images:
        name = image.replace('https://img.pokemondb.net/', '').replace(' ', '_').replace('-', '_').replace('/',
                                                                                                           '_').replace(
            '&', '_')
        if "design_header" in name:
            continue

        path = os.path.join(save_path, name)
        if os.path.exists(path):
            continue
        if '.gif' not in name:
            for i in range(n_retries):
                try:
                    with open(path, 'wb') as f:
                        im = requests.get(image)
                        f.write(im.content)
                        break
                except ConnectionError:
                    print("Reconnecting")
                except requests.exceptions.MissingSchema:
                    print(f"MissingSchema {image}")
            try:
                # make all the images uniform
                uniform(path, 64, 64)
            except PermissionError:
                print(f"{path} gave permission error")
            except:
                print(f"{path} didn't work")


def imagedown(url, folder):
    if not os.path.exists(folder):
        folder = os.path.join(os.getcwd(), folder)
        # making a directory by joining the current one with the given one
        os.makedirs(folder, exist_ok=True)
        # change to the given folder and request the given url and parse its html

    # get the soup of the pokemon for both its sprites and its artworks
    sprites_soup = get_soup(url.replace('pokedex', 'sprites'))
    artwork_soup = get_soup(url.replace('pokedex', 'artwork'))

    # find all images in the given parsed html file
    sprites = listed_sprites(sprites_soup)
    artworks = listed_artwork(artwork_soup)

    # download all the images in both of the lists
    # download(sprites)
    download(artworks, folder)
    download(sprites, folder)


def remove_corrupted_images(path: str):
    for file in os.listdir(path):
        try:
            with open(os.path.join(path, file), 'rb') as f:
                img = Image.open(io.BytesIO(f.read()))
        except PIL.UnidentifiedImageError as e:
            os.remove(os.path.join(path, file))
            print(f"Removed {file} because it is corrupted.")


def load_pokemons_thread(pokemons:list, shared_count:Value, total:int = 903):
    for pokemon in pokemons:
        shared_count.value = shared_count.value + 1
        print(
            f"{shared_count.value}/{total}. Current pokemon: {pokemon.replace('https://pokemondb.net/pokedex/', '')}")

        imagedown(pokemon, folder=r"data\raw")

def load_pokemons(pokemons: list, shared_count: Value, total: int = 903):
    """
    Load all the pokemons in the list.
    :param pokemons:
    :param total:
    :return:
    """
    print(f"Start loading pokemon: {pokemons}")
    pokemons_devided = distribute(pokemons, 5)
    loadingThreads = []
    # Define a shared integer variable
    for group in pokemons_devided:
        t = Thread(target=load_pokemons_thread, args=(group, shared_count, total))
        t.start()
        loadingThreads.append(t)

    for lt in loadingThreads:
        lt.join()



def distribute(original_list, n) -> List[List]:
    """
    Split a list into n sublists
    :param original_list:
    :param n: Number of lists to split into
    :return: List os Sublists
    """
    # Calculate the size of each sublist
    sublist_size = len(original_list) // n

    # Use list comprehension to create n sublists
    sublists = [original_list[i:i + sublist_size] for i in range(0, len(original_list), sublist_size)]

    # If there's a remainder, distribute the remaining elements among the sublists
    remainder = len(original_list) % n
    for i in range(remainder):
        sublists[i].append(original_list[-(i + 1)])
    return sublists


if __name__ == "__main__":
    # for every pokemon found in the first site (the national pokedex) find every possible sprite for it
    # and make a new folder with its name (or not)
    scrape = True
    if scrape:
        url = 'https://pokemondb.net/pokedex/national'
        pokemons = get_pokemon(url)[1:]

        # A lot of the time is spent waiting for a request.
        pokemons_devided = distribute(pokemons, 1)
        loadingThreads = []
        # Define a shared integer variable
        count = Value("i", 0)

        for group in pokemons_devided:
            t = Process(target=load_pokemons, args=(group, count, len(pokemons)))
            t.start()
            loadingThreads.append(t)

        for lt in loadingThreads:
            lt.join()
    save_path = "data/pokemon"
    images = os.listdir(save_path)

    # sometimes do to laggy internet it doesn't resize properly only do this if
    # if you can see that there are wrongly sized images in your data folder (checks before resizing but still)
    # n = len(images)
    # for c, image in enumerate(images):
    #     print(f"{c}/{n} {image}")
    #     image_path = os.path.join(save_path, image)
    #     if "artwork" in image:
    #         resize_and_save(image_path, 64, 64)
    #     try:
    #         if "artwork" not in image and "sprite" in image:
    #             center_focus(image_path)
    #     except Exception as e:
    #         print("Failed to center: ", image, "with exception", e)
    #
    # remove_corrupted_images(save_path)
