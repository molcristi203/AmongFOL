import random
import json
import subprocess
import re

TITLE = """                                                         
 _____ __  __ _____ ____   ____ _____ _   _  ______   __ 
| ____|  \\/  | ____|  _ \\ / ___| ____| \\ | |/ ___\\ \\ / / 
|  _| | |\\/| |  _| | |_) | |  _|  _| |  \\| | |    \\ V /  
| |___| |  | | |___|  _ <| |_| | |___| |\\  | |___  | |   
|_____|_|  |_|_____|_| \\_\\\\____|_____|_| \\_|\\____| |_|   
                                                         
                                                         
 __  __ _____ _____ _____ ___ _   _  ____                
|  \\/  | ____| ____|_   _|_ _| \\ | |/ ___|               
| |\\/| |  _| |  _|   | |  | ||  \\| | |  _                
| |  | | |___| |___  | |  | || |\\  | |_| |               
|_|  |_|_____|_____| |_| |___|_| \\_|\\____|               
"""

CREWMATES_WIN = """
  ____ ____  _______        ____  __    _  _____ _____ ____   __        _____ _   _ 
 / ___|  _ \| ____\ \      / |  \/  |  / \|_   _| ____/ ___|  \ \      / |_ _| \ | |
| |   | |_) |  _|  \ \ /\ / /| |\/| | / _ \ | | |  _| \___ \   \ \ /\ / / | ||  \| |
| |___|  _ <| |___  \ V  V / | |  | |/ ___ \| | | |___ ___) |   \ V  V /  | || |\  |
 \____|_| \_|_____|  \_/\_/  |_|  |_/_/   \_|_| |_____|____/     \_/\_/  |___|_| \_|
"""

IMPOSTER_WINS = """
 ___ __  __ ____   ___  ____ _____ _____ ____   __        _____ _   _ ____  
|_ _|  \/  |  _ \ / _ \/ ___|_   _| ____|  _ \  \ \      / |_ _| \ | / ___| 
 | || |\/| | |_) | | | \___ \ | | |  _| | |_) |  \ \ /\ / / | ||  \| \___ \ 
 | || |  | |  __/| |_| |___) || | | |___|  _ <    \ V  V /  | || |\  |___) |
|___|_|  |_|_|    \___/|____/ |_| |_____|_| \_\    \_/\_/  |___|_| \_|____/ 
"""

game = None

class Location:
    def __init__(self, name, tasks) -> None:
        self.name = name
        self.tasks = tasks

class Player:
    def __init__(self, name) -> None:
        self.name = name

    def get_name(self):
        return self.name
    
    def get_message(self):
        final_message = "message({player})<->".format(player = self.name)
        global game

        messages = random.sample(game.get_messages(), random.randint(1, min(4, len(game.get_messages()))))

        for i in range(len(messages)):
            final_message += self.interpret_message(messages[i])

            if i == len(messages) - 1:
                final_message += ".\n\t"
            else:
                final_message += " & "

        return final_message
    
    def interpret_message(self, message):
        return ""
    
    def get_role(self):
        return ""

class Crewmate(Player):
    def __init__(self, name) -> None:
        super().__init__(name)

    def interpret_message(self, message):
        match message:
            case "crewmate({player})" | "-imposter({player})":
                return message.format(player = (random.choice([p for p in game.players if isinstance(p, Crewmate)])).get_name())
            case "imposter({player})" | "-crewmate({player})":
                return message.format(player = (random.choice([p for p in game.players if isinstance(p, Imposter)])).get_name())

    def get_role(self):
        return "Crewmate"

class Imposter(Player):
    def __init__(self, name) -> None:
        super().__init__(name)

    def interpret_message(self, message):
        match message:
            case "crewmate({player})" | "imposter({player})" | "-crewmate({player})" | "-imposter({player})":
                return message.format(player = (random.choice([p for p in game.players if not isinstance(p, Body)])).get_name())
            # case "crewmate({player})" | "-imposter({player})":
            #     return message.format(player = (random.choice([p for p in game.players if isinstance(p, Imposter)])).get_name())
            # case "imposter({player})" | "-crewmate({player})":
            #     return message.format(player = (random.choice([p for p in game.players if isinstance(p, Crewmate)])).get_name())


    def get_role(self):
        return "Imposter"

class Body(Player):
    def __init__(self, name) -> None:
        super().__init__(name)

    def get_message(self):
        return ""

class Game:
    def __init__(self, path) -> None:
        self.load_data(path)

    def init_conditions(self):
        players_list1 = ""
        players_list2 = ""
        
        for i in range(len(self.players)):
            players_list1 += "player({p_name})".format(p_name = self.players[i].get_name())
            players_list2 += "{p_name} = {v}".format(p_name = self.players[i].get_name(), v = i)

            if i == len(self.players) - 1:
                players_list1 += ".\n\t"
                players_list2 += ".\n\t"
            else:
                players_list1 += " & "
                players_list2 += " & "

        return players_list1 + players_list2

    def get_messages(self):
        return self.messages

    def print_players(self, percentages):
        for i in range(len(self.players)):
            print("{p_name}: {percent}% to be imposter".format(p_name = self.players[i].get_name().capitalize(), percent=percentages[i]))

    def load_data(self, path):
        f = open(path)
        data = json.load(f)
        f.close()

        self.max_models = data["max_models"]

        if "tasks" in data:
            self.tasks = data["tasks"]

        if "locations" in data:
            self.locations = []
            for loc in data["locations"]:
                new_loc = Location(loc["name"], loc["tasks"])
                self.locations.append(new_loc)

        players = random.sample(data["players"], len(data["players"]))

        self.messages = data["messages"]

        self.players = []

        self.players.append(Imposter(players.pop()))
        
        if data["dead_player"]:
            self.players.append(Body(players.pop()))

        for _ in players:
            self.players.append(Crewmate(players.pop()))
        
        f = open(data["template"], "r")
        self.template = f.read()
        f.close()

    def run_game(self):
        print(TITLE)

        conditions = self.init_conditions()
        messages = ""

        for p in self.players:
            m = p.get_message()
            print("{player} is {role}".format(player = p.get_name(), role = p.get_role()))
            messages += m

        self.template = self.template.format(max_models = self.max_models, domain_size = len(self.players), game = conditions, messages = messages)

        f = open("out.in", "w")
        f.write(self.template)
        f.close()

        result = run_mace4()

        game.print_players(result)

        vote = input("Vote who you think is the imposter: ")
        while vote.lower() not in [player.get_name() for player in game.players]:
             vote = input("Not a player. Try again: ")

        game.players = [player for player in game.players if player.get_name() != vote.lower()]

        if any(isinstance(player, Imposter) for player in game.players):
            print(IMPOSTER_WINS)
        else:
            print(CREWMATES_WIN)
        
def run_mace4():
    result = subprocess.run(["mace4 | interpformat standard"], input=game.template, text=True, capture_output=True, shell=True)

    output = result.stdout

    line_imposter_regex = "relation\(imposter\(_\), \[(?:\d+,)+\d\]\)"
    array_regex = "\[\d+(?:,\d+)*\]"

    lines = re.findall(line_imposter_regex, output)
    result = [0] * len(game.players)

    for line in lines:
        array = eval(re.findall(array_regex, line)[0])
        result = [elem1 + elem2 for elem1, elem2 in zip(result, array)]

    result = [v * 100 / len(lines) for v in result]

    return result  

if __name__ == "__main__":
    game = Game("data1.json")

    game.run_game()