import ollama
import json
import random

class Character:
    """Represents a D&D character with basic stats."""
    def __init__(self, name, strength, dexterity, constitution, intelligence, wisdom, charisma):
        self.name = name
        self.stats = {
            "Strength": strength,
            "Dexterity": dexterity,
            "Constitution": constitution,
            "Intelligence": intelligence,
            "Wisdom": wisdom,
            "Charisma": charisma
        }
        self.inventory = []
        self.hp = 10 + (constitution // 2 - 5) # Simple HP calculation

    def to_dict(self):
        """Converts character data to a dictionary for prompts."""
        return {
            "name": self.name,
            "stats": self.stats,
            "inventory": self.inventory,
            "hp": self.hp
        }

class DungeonMaster:
    """Manages the game state and interacts with the Ollama LLM."""
    def __init__(self, model="gemma3:12b"):
        self.model = model
        self.history = []

    def get_dm_response(self, player_action, character_data):
        """Sends a prompt to the LLM and gets the DM's response."""

        # Build the prompt with instructions, history, character data, and action
        prompt = f"""
        You are a Dungeon Master for a Dungeons and Dragons game.
        Your role is to describe the world, the challenges, and the non-player characters.
        You must remember and use the player's character stats when determining outcomes.
        Never forget the character's stats.
        Describe events vividly. Be fair but challenging.
        Keep your responses to a few paragraphs.

        Here is the character information:
        {json.dumps(character_data, indent=2)}

        Here is the recent history of events:
        {' '.join(self.history[-5:])} # Include the last 5 events

        The player's action is: "{player_action}"

        What happens next? Describe the scene and the results of the action.
        If a skill check seems appropriate, describe the attempt and outcome based on their stats
        (e.g., high Dexterity helps with sneaking, high Strength with breaking doors).
        You can introduce simple challenges or NPCs.
        """

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            dm_text = response['message']['content']
            self.history.append(f"Player: {player_action}\nDM: {dm_text}\n")
            return dm_text
        except Exception as e:
            return f"An error occurred with the Dungeon Master: {e}"

def create_character():
    """Guides the player through character creation."""
    print("Let's create your character!")
    name = input("Enter your character's name: ")

    print("\nRoll for your stats (4d6 drop lowest):")
    stats = {}
    stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    for stat_name in stat_names:
        rolls = sorted([random.randint(1, 6) for _ in range(4)])
        score = sum(rolls[1:])
        print(f"{stat_name}: {score}")
        stats[stat_name.lower()] = score # Use lowercase keys

    return Character(name, **stats)

def game_loop():
    """The main loop for the D&D game."""
    dm = DungeonMaster()
    player = create_character()

    print("\nYour adventure begins!")
    # Initial scenario from the DM
    initial_prompt = "You find yourself standing at the entrance of a dark, moss-covered cave. The air is damp and smells of earth and something vaguely unsettling. A faint, chilly breeze issues from the cave mouth. What do you do?"
    print(f"\nDM: {initial_prompt}")
    dm.history.append(f"DM: {initial_prompt}\n")


    while True:
        action = input("\nWhat do you do? > ")
        if action.lower() in ["quit", "exit"]:
            print("Your adventure ends here. Farewell!")
            break

        dm_response = dm.get_dm_response(action, player.to_dict())
        print(f"\nDM: {dm_response}")

if __name__ == "__main__":
    game_loop()