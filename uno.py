from typing import List
import card
import discord
from discord.ext import commands
import formatter

class uno_deck():
    def __init__(self):
        self.deck = []
        self.create_deck()

    def create_deck(self):
        deck = []
        for c in range(8):
            color = ""
            for n in range(14):
                if n == 13:
                    color = "W"
                else:
                    if c < 4:
                        if c == 0:
                            color = "R"
                        elif c == 1:
                            color = "B"
                        elif c == 2:
                            color = "G"
                        elif c == 3:
                            color = "Y"
                    else:
                        if c-4 == 0:
                            color = "R"
                        elif c-4 == 1:
                            color = "B"
                        elif c-4 == 2:
                            color = "G"
                        elif c-4 == 3:
                            color = "Y"
                if n > 9:
                    if n == 10:
                        num = "S"
                    elif n == 11:
                        num = "R"
                    elif n == 12:
                        num = "D2"
                    elif n == 13:
                        if c > 3:
                            num = "D4"
                        else:
                            num = ""
                else:
                    num = f"{n}"

                deck.append(f"{color}{num}")
        self.deck = deck
        self.shuffle()

    def draw(self):
        if len(self.deck) == 0:
            self.create_deck()
            self.shuffle()
        return self.deck.pop()

    def shuffle(self):
        for i in range(3):
            card.shuffle(self.deck)

class uno_player():
    def __init__(self, _id):
        self.called_uno = False
        self.hand = []
        self._id = _id
    
    def draw(self, deck:uno_deck):
        self.hand.append(deck.draw())
        self.called_uno = False

    def has_draws(self):
        for c in self.hand:
            if c[1] == "D":
                return True
        return False
    
    def has_valid(self, card):
        for c in self.hand:
            if c.startswith(card[0]):
                return True
            elif len(card) > 1:
                if c[1:].startswith(card[1:]):
                    return True
        return False

    def input_valid(self, inputs:List[str]):
        pass

class uno():
    def __init__(self, bot:commands.bot, players:List[uno_player], uno_deck:uno_deck, bet, stacking):
        self.uno_deck = uno_deck
        self.players = players
        self.bet = bet
        self.bot = bot
        self.turn = 0
        self.reversed = False
        self.discard = ""
        self.stacking = False

    def next_turn(self):
        if reversed:
            self.turn -= 1
        else:
            self.turn += 1

        if self.turn >= len(self.players):
            self.turn = 0
        elif self.turn < 0:
            self.turn = (len(self.players) - 1)

    def reverse(self):
        self.reverse = True
        self.next_turn()
    
    def skip(self):
        self.next_turn()
        self.next_turn()

    def start(self):
        for x in range(7):
            for i in range(len(self.players)):
                self.players[i].draw(self.uno_deck)
        self.discard = self.uno_deck.draw()

def start_uno():
    pass