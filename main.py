from tournament import Tournament
from headers import *

t = Tournament(player_type.random, player_type.random, 1000)
t.start()
t.print_results()