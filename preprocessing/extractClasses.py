# import json
import json

from preprocessing_webscraping_all import distribute, get_pokemon, get_soup
from typing import List
from threading import Thread, Lock
from multiprocessing import Value
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
def get_bulbapedia_url(pokemondb_url, devider = "_"):
    pokemon = pokemondb_url.title().replace('-', devider)
    return f"https://bulbapedia.bulbagarden.net/wiki/{pokemon}_(Pok%C3%A9mon)"

def get_all_images(url):
    # Send an HTTP request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all image tags
        img_tags = soup.find_all('img')

        # Extract the src attribute from each image tag
        img_urls = [urljoin(url, img['src']) for img in img_tags if 'src' in img.attrs]

        return img_urls
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return []

def getBodyType(url):
    images = get_all_images(url)
    body_types = [f"Body{str(i).rjust(2,'0')}" for i in range(20)]

    for image in images:
        for body in body_types:
            if body in image:
                return body

def register_body_type(pokemons, association, association_lock, count, total):
    for pokemon in pokemons:
        pokemon_name = pokemon.replace("https://pokemondb.net/pokedex/", "")
        b_url = get_bulbapedia_url(pokemon_name)
        if association.get(pokemon_name, False):
            count.value = count.value + 1
            print(f"{count.value}/{total}")
            continue

        try:
            body_type = getBodyType(b_url)
            if not body_type:
                body_type = getBodyType(get_bulbapedia_url(pokemon_name, "-"))
            with association_lock:
                association[pokemon_name] = body_type
            count.value = count.value + 1
            print(f"{count.value}/{total}")
        except Exception as e:
            print(e)

if __name__ == '__main__':
    url = 'https://pokemondb.net/pokedex/national'
    pokemons = get_pokemon(url)[1:]

    pokemons_devided = distribute(pokemons, 10)
    loadingThreads = []
    # Define a shared integer variable
    pokemon_to_body = {}
    pokemon_to_body_lock = Lock()
    count = Value("i", 0)
    total = len(pokemons)

    # Specify the file path where you want to save the JSON file
    json_file_path = "pokemon_to_body.json"

    # Read the JSON file into a dictionary
    with open(json_file_path, 'r') as json_file:
        pokemon_to_body = json.load(json_file)

    for group in pokemons_devided:
        t = Thread(target=register_body_type, args=(group, pokemon_to_body, pokemon_to_body_lock, count, total))
        t.start()
        loadingThreads.append(t)

    for lt in loadingThreads:
        lt.join()

    # Write the dictionary into the JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(pokemon_to_body, json_file, indent=4)