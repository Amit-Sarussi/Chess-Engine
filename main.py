from tournament import Tournament
from headers import *

t = Tournament(player_type.heuristics, player_type.random, 1)
t.start()
t.print_results()