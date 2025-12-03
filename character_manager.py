"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code

Name: Robert ingle
AI Usage: ai used to fix error in code

This module handles character creation, loading, and saving.
"""

import os
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ============================================================================
# CHARACTER MANAGEMENT FUNCTIONS
# ============================================================================

def create_character(name, character_class):
    """
    Create a new character with stats based on class
    """
    valid_classes = {
        "Warrior": {"health": 120, "strength": 15, "magic": 5},
        "Mage": {"health": 80, "strength": 8, "magic": 20},
        "Rogue": {"health": 90, "strength": 12, "magic": 10},
        "Cleric": {"health": 100, "strength": 10, "magic": 15}
    }

    if character_class not in valid_classes:
        raise InvalidCharacterClassError(f"Invalid class: {character_class}")

    base = valid_classes[character_class]

    return {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": base["health"],
        "max_health": base["health"],
        "strength": base["strength"],
        "magic": base["magic"],
        "experience": 0,
        "gold": 100,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }


def save_character(character, save_directory="data/save_games"):
    """
    Save character to file
    """
    if not os.path.exists(save_directory):
        try:
            os.makedirs(save_directory)
        except Exception:
            raise IOError("Unable to create save directory")

    filename = os.path.join(save_directory, f"{character['name']}_save.txt")

    try:
        with open(filename, "w") as file:
            for key, value in character.items():
                if isinstance(value, list):
                    value = ",".join(value)
                file.write(f"{key.upper()}: {value}\n")
    except Exception as e:
        raise IOError(f"Save error: {e}")

    return True


def load_character(character_name, save_directory="data/save_games"):
    """
    Load character from save file
    """
    filename = os.path.join(save_directory, f"{character_name}_save.txt")

    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"No save file found for {character_name}")

    try:
        with open(filename, "r") as file:
            lines = file.readlines()
    except Exception:
        raise SaveFileCorruptedError("Could not read save file")

    character = {}

    try:
        for line in lines:
            if ":" not in line:
                raise InvalidSaveDataError("Invalid line format")

            key, raw_value = line.strip().split(":", 1)
            key = key.lower()
            raw_value = raw_value.strip()

            # Parse lists
            if key in ("inventory", "active_quests", "completed_quests"):
                character[key] = raw_value.split(",") if raw_value else []
            # Parse ints
            elif key in ("level", "health", "max_health", "strength",
                         "magic", "experience", "gold"):
                character[key] = int(raw_value)
            else:
                character[key] = raw_value

        validate_character_data(character)
    except Exception as e:
        if isinstance(e, InvalidSaveDataError):
            raise
        raise InvalidSaveDataError(f"Save data invalid: {e}")

    return character


def list_saved_characters(save_directory="data/save_games"):
    """
    Return list of saved character names
    """
    if not os.path.exists(save_directory):
        return []

    names = []
    for file in os.listdir(save_directory):
        if file.endswith("_save.txt"):
            names.append(file.replace("_save.txt", ""))

    return names


def delete_character(character_name, save_directory="data/save_games"):
    """
    Delete a character's save file
    """
    filename = os.path.join(save_directory, f"{character_name}_save.txt")

    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"No save file found for {character_name}")

    try:
        os.remove(filename)
    except Exception:
        raise IOError("Unable to delete save file")

    return True

# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

def gain_experience(character, xp_amount):
    """
    Add experience to character and handle level ups
    """
    if character["health"] <= 0:
        raise CharacterDeadError("Cannot gain EXP while dead")

    character["experience"] += xp_amount

    while character["experience"] >= character["level"] * 100:
        character["experience"] -= character["level"] * 100
        character["level"] += 1
        character["max_health"] += 10
        character["strength"] += 2
        character["magic"] += 2
        character["health"] = character["max_health"]

    return character


def add_gold(character, amount):
    """
    Add (or subtract) gold
    """
    new_total = character["gold"] + amount
    if new_total < 0:
        raise ValueError("Gold cannot go negative")

    character["gold"] = new_total
    return new_total


def heal_character(character, amount):
    """
    Heal the character
    """
    max_heal = character["max_health"] - character["health"]
    actual_heal = min(amount, max_heal)
    character["health"] += actual_heal
    return actual_heal


def is_character_dead(character):
    return character["health"] <= 0


def revive_character(character):
    if not is_character_dead(character):
        return False

    character["health"] = max(1, character["max_health"] // 2)
    return True

# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(character):
    required = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]

    for key in required:
        if key not in character:
            raise InvalidSaveDataError(f"Missing field: {key}")

    numeric_fields = ["level", "health", "max_health", "strength",
                      "magic", "experience", "gold"]
    for key in numeric_fields:
        if not isinstance(character[key], int):
            raise InvalidSaveDataError(f"{key} must be an integer")

    list_fields = ["inventory", "active_quests", "completed_quests"]
    for key in list_fields:
        if not isinstance(character[key], list):
            raise InvalidSaveDataError(f"{key} must be a list")

    return True


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")
    
    # Test character creation
    # try:
    #     char = create_character("TestHero", "Warrior")
    #     print(f"Created: {char['name']} the {char['class']}")
    #     print(f"Stats: HP={char['health']}, STR={char['strength']}, MAG={char['magic']}")
    # except InvalidCharacterClassError as e:
    #     print(f"Invalid class: {e}")
    
    # Test saving
    # try:
    #     save_character(char)
    #     print("Character saved successfully")
    # except Exception as e:
    #     print(f"Save error: {e}")
    
    # Test loading
    # try:
    #     loaded = load_character("TestHero")
    #     print(f"Loaded: {loaded['name']}")
    # except CharacterNotFoundError:
    #     print("Character not found")
    # except SaveFileCorruptedError:
    #     print("Save file corrupted")

