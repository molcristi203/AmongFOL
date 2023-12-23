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

    def __eq__(self, __value: object) -> bool:
        return self.name == __value.name

class Player:
    def __init__(self, name) -> None:
        self.name = name
        self.location = None
        self.task = None

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
            case "didTask({player}, {task}) & task({location}, {task})":
                player = random.choice([p for p in game.players if not isinstance(p, Body)])
                return message.format(player = player.get_name(), task = player.task, location = player.location.name)
            case "deadAt({player}, {location})":
                player = [p for p in game.players if isinstance(p, Body)][0]
                return message.format(player = player.get_name(), location = player.location.name)
            case "-deadAt({player}, {location})":
                player = random.choice([p for p in game.players if not isinstance(p, Body)])
                return message.format(player = player.get_name(), location = player.location.name)
            case "vent({player}, {location})":
                player = random.choice([p for p in game.players if isinstance(p, Imposter)])
                return message.format(player = player.name, location = player.location.name)
            case "-vent({player}, {location})":
                player = random.choice([p for p in game.players if isinstance(p, Crewmate)])
                return message.format(player = player.name, location = player.location.name)
            case _:
                return ""

    def get_role(self):
        return "Crewmate"

class Imposter(Player):
    def __init__(self, name) -> None:
        super().__init__(name)

    def interpret_message(self, message):
        match message:
            case "crewmate({player})" | "imposter({player})" | "-crewmate({player})" | "-imposter({player})":
                return message.format(player = (random.choice([p for p in game.players if not isinstance(p, Body)])).get_name())
            case "didTask({player}, {task}) & task({location}, {task})":
                player = random.choice([p for p in game.players if not isinstance(p, Body)])
                return message.format(player = player.get_name(), task = random.choice(game.tasks), location = random.choice(game.locations).name)
            case "deadAt({player}, {location})" | "-deadAt({player}, {location})":
                return message.format(player = random.choice(game.players).name, location = random.choice(game.locations).name)
            case "vent({player}, {location})" | "-vent({player}, {location})":
                return message.format(player = random.choice(game.players).name, location = random.choice(game.locations).name)
            case _:
                return ""
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
        message = ""

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

        message += players_list1 + players_list2

        if hasattr(self, "locations"):
            locations_list1 = ""
            locations_list2 = ""
            task_list1 = ""
            for i in range(len(self.tasks)):
                task_list1 += "{task} = {v}".format(task = self.tasks[i], v = i)

                if i == len(self.tasks) - 1:
                    task_list1 += ".\n\t"
                else:
                    task_list1 += " & "

            message += task_list1

            for i in range(len(self.locations)):
                locations_list1 += "{location} = {v}".format(location = self.locations[i].name, v = i)
                locations_list2 += "location({location})".format(location = self.locations[i].name)
                if i == len(self.locations) - 1:
                    locations_list1 += ".\n\t"
                    locations_list2 += ".\n\t"
                else:
                    locations_list1 += " & "
                    locations_list2 += " | "

                task_list2 = ""

                for j in range(len(self.tasks)):
                    if self.tasks[j] in self.locations[i].tasks:
                        task_list2 += "task({location}, {task})".format(location = self.locations[i].name, task = self.tasks[j])
                    else:
                        task_list2 += "-task({location}, {task})".format(location = self.locations[i].name, task = self.tasks[j])

                    if j == len(self.tasks) - 1:
                        task_list2 += ".\n\t"
                    else:
                        task_list2 += " & "

                message += task_list2

            message += locations_list1 + locations_list2

        if hasattr(self, "dead_player"):
            for p in self.players:
                seen_messages = ""
                task_messages = ""
                for i in range(len(self.locations)):
                    seen_messages += "("
                    task_messages += "("
                    for j in range(len(self.locations)):
                        if self.locations[i] == self.locations[j]:
                            seen_messages += "seenAt({player}, {location})".format(player = p.name, location = self.locations[j].name)
                            task_messages += "didTask({player}, {location})".format(player = p.name, location = self.locations[j].name)
                        else:
                            seen_messages += "-seenAt({player}, {location})".format(player = p.name, location = self.locations[j].name)
                            task_messages += "-didTask({player}, {location})".format(player = p.name, location = self.locations[j].name)
                        if j != len(self.locations) - 1:
                            seen_messages += " & "
                            task_messages += " & "
                    seen_messages += ")"
                    task_messages += ")"
                    if i == len(self.locations) - 1:
                        seen_messages += ".\n\t"
                        task_messages += ".\n\t"
                    else:
                        seen_messages += " | "
                        task_messages += " | "
                message += seen_messages
                message += task_messages

            for p in self.players:
                seen_messages = ""
                dead_messages = ""
                for i in range(len(self.locations)):
                    loc = self.locations[i]

                    if p.location == loc:
                        seen_messages += "seenAt({player}, {location})".format(player = p.name, location = loc.name)
                    else:
                        seen_messages += "-seenAt({player}, {location})".format(player = p.name, location = loc.name)

                    if isinstance(p, Body) and p.location == loc:
                        dead_messages += "deadAt({player}, {location})".format(player = p.name, location = loc.name)
                    else:
                        dead_messages += "-deadAt({player}, {location})".format(player = p.name, location = loc.name)

                    if i == len(self.locations) - 1:
                        seen_messages += ".\n\t"
                        dead_messages += ".\n\t"
                    else:
                        seen_messages += " & "
                        dead_messages += " & "

                message += seen_messages
                message += dead_messages

        if hasattr(self, "vents"):
            for p in self.players:
                vent_messages = ""
                seen_messages = ""
                for i in range(len(self.locations)):
                    seen_messages += "seenVenting({player}, {location}) | -seenVenting({player}, {location})".format(player = p.name, location = self.locations[i].name)
                    vent_messages += "vent({player}, {location}) | -vent({player}, {location})".format(player = p.name, location = self.locations[i].name)

                    if i == len(self.locations) - 1:
                        seen_messages += ".\n\t"
                        vent_messages += ".\n\t"
                    else:
                        seen_messages += " | "
                        vent_messages += " | "

                message += seen_messages
                message += vent_messages

            for p in self.players:
                seen_messages = ""
                for i in range(len(self.locations)):
                    if isinstance(p, Imposter) and p.location.name == self.locations[i].name:
                        seen_messages += "seenVenting({player}, {location})".format(player = p.name, location = self.locations[i].name)
                    else:
                        seen_messages += "-seenVenting({player}, {location})".format(player = p.name, location = self.locations[i].name)    

        return message

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
            self.dead_player = True

        for i in range(len(players)):
            self.players.append(Crewmate(players.pop()))
        
        for p in self.players:
            if "locations" in data:
                location = random.choice(self.locations)
                task = random.choice(location.tasks)

                p.location = location
                p.task = task

        if data["vents"]:
            self.vents = True

        f = open(data["template"], "r")
        self.template = f.read()
        f.close()

    def run_game(self):
        print(TITLE)

        conditions = self.init_conditions()
        messages = ""

        for p in self.players:
            m = p.get_message()
            print(m)
            #print("{player} is {role}".format(player = p.get_name(), role = p.get_role()))
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
    game = Game("data5.json")

    game.run_game()