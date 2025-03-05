from tournament import Tournament
from headers import *

t = Tournament(player_type.random, player_type.random, 100_000)
t.start()
t.print_results()