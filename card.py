import random

def make_deck():
  deck = []
  for i in range(4):
    suit = ""
    if i == 0:
      suit = "♦️"
    elif i == 1:
      suit = "♣️"
    elif i == 2:
      suit = "♥️"
    else:
      suit = "♠️"
    for x in range(13):
      num = ""
      if x == 0:
        num = "A"
      elif x == 10:
        num = "J"
      elif x == 11:
        num = "Q"
      elif x == 12:
        num = "K"
      else:
        num = f"{x+1}"
      
      deck.append(f"{num}{suit}")
  return deck

def shuffle(deck):
  for i in range(len(deck)-1, 0, -1):
      
    # Pick a random index from 0 to i 
    j = random.randint(0, i + 1) 
    
    # Swap arr[i] with the element at random index 
    deck[i], deck[j] = deck[j], deck[i] 