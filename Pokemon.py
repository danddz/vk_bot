import matplotlib.pyplot as plt
import pandas as pd
import requests

class Pokemon:
    def __init__(self, name = None, number = None):
        if name and number:
            self.name = name
            self.number = number
            self.url = "https://pokeapi.co/api/v2/pokemon/" + name
        elif name:
            self.name = name
            self.url = "https://pokeapi.co/api/v2/pokemon/" + name
            self.number = requests.get(self.url).json()["id"]
        elif number:
            self.number = number
            self.url = "https://pokeapi.co/api/v2/pokemon/" + str(number)
            self.name = requests.get(self.url).json()["name"]
            self.url = "https://pokeapi.co/api/v2/pokemon/" + self.name

    def keys(self):
        return requests.get(self.url).json().keys()

    def values(self):
        return requests.get(self.url).json().values()

    def items(self):
        return requests.get(self.url).json().items()

    def abilities(self):
        return requests.get(self.url).json()["abilities"]

    def ability_names(self):
        return [d["ability"]["name"] for d in requests.get(self.url).json()["abilities"]]

    def base_experience(self):
        return requests.get(self.url).json()["base_experience"]

    def forms(self):
        return requests.get(self.url).json()["forms"]

    def game_indices(self):
        return requests.get(self.url).json()["game_indices"]

    def held_items(self):
        return requests.get(self.url).json()["held_items"]

    def height(self):
        return requests.get(self.url).json()["height"]
        
    @property
    def id(self):
        return requests.get(self.url).json()["id"]

    def is_default(self):
        return requests.get(self.url).json()["is_default"]

    def location_area_encounters(self):
        return requests.get(self.url).json()["location_area_encounters"]

    def moves(self):
        return requests.get(self.url).json()["moves"]

    def get_move_by_number(self, number: str):
        return requests.get(self.url.replace("pokemon", "move").replace(self.name, str(number))).json()

    def get_move_names(self, numbers):
        return [move["name"] for move in [self.get_move_by_number(n) for n in numbers]]

    def get_move_by_name(self, name):
        return {d["move"]["name"]: d["move"] for d in requests.get(self.url).json()["moves"]}[name]

    def plot_move_powers(self, numbers, ascending = True):
        pd.DataFrame({move["name"]: move["power"] for move in [self.get_move_by_number(n) for n in numbers]}, index=[self.name]).melt(var_name="move", value_name="power").sort_values(by="power", ascending=ascending).set_index("move").plot.barh(legend=False)
        plt.suptitle(f"Power values for {self.name}")
        plt.title(f"Obtained from {self.url}")
        plt.show()

    def order(self):
        return requests.get(self.url).json()["order"]

    def species(self):
        return requests.get(self.url).json()["species"]

    def sprites(self):
        return requests.get(self.url).json()["sprites"]

    def sprite_options(self):
        return requests.get(self.url).json()["sprites"].keys()

    def stats(self):
        return requests.get(self.url).json()["stats"]

    def types(self):
        return requests.get(self.url).json()["types"]

    def weight(self):
        return requests.get(self.url).json()["weight"]

    def get_ability(self, name):
        return {d["ability"]["name"]: d["ability"] for d in requests.get(self.url).json()["abilities"]}[name]

    def show_sprite(self, option = "front_default"):
        plt.imshow(plt.imread(requests.get(self.url).json()["sprites"][option]))
        print(requests.get(self.url).json()["sprites"][option])

    def image(self):
        number = self.id
        if number < 10:
            number = f'00{number}'
        elif number < 100:
            number = f'0{number}'
        return f'https://assets.pokemon.com/assets/cms2/img/pokedex/full/{number}.png'

def get_name_number_photo(input_data):
    try:
        if input_data.isdigit():
            p = Pokemon(number=input_data)
        else:
            p = Pokemon(name=input_data)
        return p.name, p.number, p.image()
    except ValueError:
        return -1, -1, -1
