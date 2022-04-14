from Pokemon import *
import Pokemon
from bs4 import BeautifulSoup
from fast_moves import *
from charged_moves import *

class info_pokemon():
    def __init__(self, name, number, photo):
        self.name= name
        self.number = number
        self.photo = photo
        self.url = f'https://pokemon.gameinfo.io/en/pokemon/{number}-{name}'
        self.response = requests.get(self.url)
        self.soup = BeautifulSoup(self.response.text, 'lxml')
        
        self.weaknesses_weak_type, self.weaknesses_weak_damage = self.weaknesses('weaknesses weak')
        self.weaknesses_res_type, self.weaknesses_res_damage = self.weaknesses('weaknesses res')
        self.poke_type = self.pokemon_type('large-type')
        self.poke_quick_move = self.pokemon_move('quickmove')
        self.quick_move_statistics = self.attack_statistics('quick')
        self.poke_main_move = self.pokemon_move('mainmove')
        self.main_move_statistics = self.attack_statistics('main')
        
    def remove_values_from_list_weaknesses(self, the_list, val1, val2):
        type_attack = list()
        damage_attack = list()
        for i in the_list:
            if val1 in i:
                type_attack.append(i[i.find(val1) + len(val1):])
            elif val2 in i:
                damage_attack.append(i[i.find('">') + 2:i.find('</span>')])
        return type_attack, damage_attack

    def weaknesses(self, class_):
        quotes = self.soup.find_all('table', class_=class_)
        x = str(quotes).split()
        val1 = 'POKEMON_TYPE_'
        val2 = 'class="_'
        type_attack, damage_attack = self.remove_values_from_list_weaknesses(x, val1, val2)
        return type_attack, damage_attack

    def remove_values_from_list_pokemon_type(self, the_list, val1):
        type_attack = list()
        for i in the_list:
            if val1 in i:
                type_attack.append(i[i.find('">') + 2:i.find('</div>')])
        return type_attack
    
    def pokemon_type(self, class_):
        quotes = self.soup.find_all('div', class_=class_)
        x = str(quotes).split()
        val1 = 'POKEMON_TYPE_'
        type_attack = self.remove_values_from_list_pokemon_type(x, val1)
        return type_attack
    
    def remove_values_from_list_pokemon_move(self, the_list, val1):
        type_attack = list()
        for i in the_list:
            if val1 in i:
                type_attack.append(i[i.find('">') + 2:i.find('</option>')])
        return type_attack
    
    def pokemon_move(self, class_):
        quotes = self.soup.find_all('select', class_=class_)
        x = str(quotes).split('\n')
        val1 = 'value="'
        type_attack = self.remove_values_from_list_pokemon_move(x, val1)
        return type_attack
    
    def attack_statistics(self, type_move):
        statistics_list = list()
        if type_move == 'quick':
            for i in self.poke_quick_move:
                if '(' in i:
                    i = i[:i.find('(') - 1]
                if 'Mud-Slap' in i or 'Lock-On' in i:
                    i = i.replace('-', ' ')
                statistics_list.append(fast_moves_dict[i].info())
        elif type_move == 'main':
            for i in self.poke_main_move:
                if '(' in i:
                    i = i[:i.find('(') - 1]
                if 'Weather Ball Normal' in i:
                    i = 'Weather Ball (Normal)'
                elif 'Weather Ball' in i:
                    quotes = str(self.soup.find_all('select', class_='mainmove'))
                    quotes = int(quotes[quotes.find('Weather Ball') - 5:quotes.find('Weather Ball') - 2])
                    if quotes == 292:
                        i = 'Weather Ball (Fire)'
                    elif quotes == 293:
                        i = 'Weather Ball (Ice)'
                    elif quotes == 352:
                        i = 'Weather Ball (Normal)'
                    elif quotes == 294:
                        i = 'Weather Ball (Rock)'
                    elif quotes == 295:
                        i = 'Weather Ball (Water)'
                elif 'V-create' in i:
                    i = 'V-Create'

                statistics_list.append(charged_moves_dict[i].info())
        return statistics_list
    
def pokemon_input(input_data):
    name, number, photo = Pokemon.get_name_number_photo(input_data)

    if name == -1:
        return -1
    else:
        pokemon = info_pokemon(name, number, photo)
        #print(pokemon.soup)        
        return [pokemon.name, pokemon.number, pokemon.photo, pokemon.poke_type, 
                pokemon.weaknesses_weak_type, pokemon.weaknesses_weak_damage, 
                pokemon.weaknesses_res_type, pokemon.weaknesses_res_damage,
                pokemon.poke_quick_move, pokemon.quick_move_statistics,
                pokemon.poke_main_move, pokemon.main_move_statistics]