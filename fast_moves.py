class fast_moves():
    def __init__(self, type_move, damage, energy, turns):
        self.type_move = type_move
        self.damage = damage
        self.energy = energy
        self.turns = turns
        self.damage_per_turn = round(self.damage / self.turns, 2)
        self.energy_per_turn = round(self.energy / self.turns, 2)
        
    def __str__(self):
        return f'{self.type_move}, {self.damage}, {self.energy}, {self.turns}, {self.damage_per_turn}, {self.energy_per_turn}'
     
    def info(self):
        return [self.type_move, self.damage, self.energy, self.turns, self.damage_per_turn, self.energy_per_turn]
    
fast_moves_dict = {
    'Acid': fast_moves('poison', 6, 5, 2),
    'Air Slash': fast_moves('flying', 9, 9, 3),
    'Astonish': fast_moves('ghost', 5, 9, 3),
    'Bite': fast_moves('dark', 4, 2, 1),
    'Bubble': fast_moves('water', 7, 11, 3),
    'Bug Bite': fast_moves('bug', 3, 3, 1),
    'Bullet Punch': fast_moves('steel', 6, 7, 2),
    'Bullet Seed': fast_moves('grass', 5, 13, 3),
    'Charge Beam': fast_moves('electric', 5, 11, 3),
    'Charm': fast_moves('fairy', 16, 6, 3),
    'Confusion': fast_moves('psychic', 16, 12, 4),
    'Counter': fast_moves('fighting', 8, 7, 2),
    'Cut': fast_moves('normal', 3, 2, 1),
    'Dragon Breath': fast_moves('dragon', 4, 3, 1),
    'Dragon Tail': fast_moves('dragon', 13, 9, 3),
    'Ember': fast_moves('fire', 7, 6, 2),
    'Extrasensory': fast_moves('psychic', 8, 10, 3),
    'Feint Attack': fast_moves('dark', 6, 6, 2),
    'Fire Fang': fast_moves('fire', 8, 5, 2),
    'Fire Spin': fast_moves('fire', 9, 10, 3),
    'Frost Breath': fast_moves('ice', 7, 5, 2),
    'Fury Cutter': fast_moves('bug', 2, 4, 1),
    'Gust': fast_moves('flying', 16, 12, 4),
    'Hex': fast_moves('ghost', 6, 12, 3),
    'Hidden Power': fast_moves('normal', 9, 8, 3),
    'Ice Fang': fast_moves('ice', 8, 5, 2),
    'Ice Shard': fast_moves('ice', 9, 10, 3),
    'Incinerate': fast_moves('fire', 15, 20, 5),
    'Infestation': fast_moves('bug', 6, 12, 3),
    'Iron Tail': fast_moves('steel', 9, 6, 3),
    'Karate Chop': fast_moves('fighting', 5, 8, 2),
    'Lick': fast_moves('ghost', 3, 3, 1),
    'Lock On': fast_moves('normal', 1, 5, 1),
    'Low Kick': fast_moves('fighting', 4, 5, 2),
    'Metal Claw': fast_moves('steel', 5, 6, 2),
    'Mud Shot': fast_moves('ground', 3, 9, 2),
    'Mud Slap': fast_moves('ground', 11, 8, 3),
    'Peck': fast_moves('flying', 6, 5, 2),
    'Poison Jab': fast_moves('poison', 7, 7, 2),
    'Poison Sting': fast_moves('poison', 3, 9, 2),
    'Pound': fast_moves('normal', 5, 4, 2),
    'Powder Snow': fast_moves('ice', 5, 8, 2),
    'Present': fast_moves('normal', 3, 12, 3),
    'Psycho Cut': fast_moves('psychic', 3, 9, 2),
    'Quick Attack': fast_moves('normal', 5, 7, 2),
    'Razor Leaf': fast_moves('grass', 10, 4, 2),
    'Rock Smash': fast_moves('fighting', 9, 7, 3),
    'Rock Throw': fast_moves('rock', 8, 5, 2),
    'Scratch': fast_moves('normal', 4, 2, 1),
    'Shadow Claw': fast_moves('ghost', 6, 8, 2),
    'Smack Down': fast_moves('rock', 12, 8, 3),
    'Snarl': fast_moves('dark', 5, 13, 3),
    'Spark': fast_moves('electric', 4, 8, 2),
    'Splash': fast_moves('water', 0, 12, 4),
    'Steel Wing': fast_moves('steel', 7, 5, 2),
    'Struggle Bug': fast_moves('bug', 9, 8, 3),
    'Sucker Punch': fast_moves('dark', 5, 7, 2),
    'Tackle': fast_moves('normal', 3, 2, 1),
    'Take Down': fast_moves('normal', 5, 8, 3),
    'Thunder Fang': fast_moves('electric', 8, 5, 2),
    'Thunder Shock': fast_moves('electric', 3, 9, 2),
    'Transform': fast_moves('normal', 0, 0, 1),
    'Vine Whip': fast_moves('grass', 5, 8, 2),
    'Volt Switch': fast_moves('electric', 12, 16, 4),
    'Water Gun': fast_moves('water', 3, 3, 1),
    'Waterfall': fast_moves('water', 12, 8, 3),
    'Wing Attack': fast_moves('flying', 5, 7, 2),
    'Yawn': fast_moves('normal', 0, 12, 4),
    'Zen Headbutt': fast_moves('psychic', 8, 6, 3)
}