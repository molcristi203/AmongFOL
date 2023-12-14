import random

CREWMATES = 4
IMPOSTERS = 1
COLORS = ["Red", "Black", "Green", "White", "Blue"]

class Location:
    def __init__(self, name, tasks):
        self.tasks = tasks
        self.name = name
    
    def is_task_there(self, task):
        return task in self.tasks

class Map:
    def __init__(self, locations, all_tasks) -> None:
        self.locations = locations
        self.all_tasks = all_tasks

class GameScenario:
    def __init__(self) -> None:
        pass

    

def generate_players():
    players = {}
    roles = []

    roles = CREWMATES * ["Crewmate"] + IMPOSTERS * ["Imposter"] 

    random.shuffle(roles)
    colors = random.sample(COLORS, len(COLORS))

    for i in range(CREWMATES + IMPOSTERS):
        players[colors[i]] = roles[i]

    return players

def print_players(players):
    for p in players:
        print(p + " ", end="")
        print("")

def number_of_players_remaining(players):
    imposters = list(players.values()).count("Imposter")
    crewmates = list(players.values()).count("Crewmate")

    return imposters, crewmates

def run_game():
    players = generate_players()

    stop = False

    while not stop:
        print("Remaining players: ")
        print_players(players)
        vote = input("\nVote a player or skip: ")
        while (vote not in players.keys()) and (vote.lower != "skip"):
            vote = input("Not a player. Try again: ")

        if vote.lower() != "skip":
            ejected = players.pop(vote)
            if ejected == "Crewmate":
                print(vote + " was not an imposter")
            else:
                print(vote + " was an imposter")

        imposters, crewmates = number_of_players_remaining(players)

        if imposters == 0:
            print("Crewmates won")
            stop = True

        if crewmates == 0:
            print("Imposters won")
            stop = True


if __name__ == '__main__':
    


    run_game()
    pass

