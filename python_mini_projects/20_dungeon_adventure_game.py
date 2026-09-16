"""Dungeon Adventure Game: Object-Oriented text adventure game with rooms, items, and inventory management."""


class Item:
    """Represents an interactable or collectible item in the dungeon."""

    def __init__(self, name, description, item_type="general", effect_value=0):
        self.name = name.strip()
        self.description = description.strip()
        self.item_type = item_type
        self.effect_value = effect_value

    def __str__(self):
        return f"{self.name}: {self.description}"


class Room:
    """Represents a location in the dungeon map with exits and items."""

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.exits = {}
        self.items = []
        self.locked_exit = None
        self.required_key = None
        self.hazard_damage = 0
        self.hazard_description = None

    def add_exit(self, direction, target_room):
        """Link this room to an adjacent room in given direction."""
        self.exits[direction.lower()] = target_room

    def lock_exit(self, direction, key_name):
        """Lock an exit requiring a specific item key to open."""
        self.locked_exit = direction.lower()
        self.required_key = key_name.lower()

    def unlock_exit(self):
        """Unlock previously locked exit."""
        self.locked_exit = None
        self.required_key = None

    def set_hazard(self, damage, description):
        """Set an environmental hazard that deals damage upon first entry."""
        self.hazard_damage = damage
        self.hazard_description = description


class Player:
    """Tracks player status, health, inventory, and location."""

    def __init__(self, name, starting_room):
        self.name = name
        self.hp = 100
        self.max_hp = 100
        self.inventory = []
        self.current_room = starting_room
        self.has_won = False

    def heal(self, amount):
        """Restore player health points up to max_hp."""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        gained = self.hp - old_hp
        return gained

    def take_damage(self, amount):
        """Deduct health points and return whether player remains alive."""
        self.hp = max(0, self.hp - amount)
        return self.hp > 0

    def add_item(self, item):
        """Add item to inventory."""
        self.inventory.append(item)

    def find_item_in_inventory(self, item_name):
        """Find an item in inventory by case-insensitive name."""
        name_lower = item_name.lower()
        for item in self.inventory:
            if item.name.lower() == name_lower:
                return item
        return None

    def remove_item(self, item):
        """Remove item from inventory."""
        if item in self.inventory:
            self.inventory.remove(item)


def build_dungeon():
    """Construct the dungeon rooms and item network."""
    entrance = Room(
        "Dungeon Entrance",
        "Stone walls dripping with moisture. Faint sunlight filters through a rusted grate above."
    )
    hallway = Room(
        "Echoing Hallway",
        "A long corridor with flickering wall torches. Cold air blows from the north."
    )
    armory = Room(
        "Ruined Armory",
        "Cobwebs drape over splintered weapon racks and shattered shields."
    )
    alchemy = Room(
        "Alchemist Lab",
        "Broken glass flasks and mysterious powders litter stone tables."
    )
    crypt = Room(
        "Forgotten Crypt",
        "Ancient stone sarcophagi line the chamber. Floor tiles are cracked and hazardous."
    )
    sanctuary = Room(
        "Inner Sanctuary",
        "A glowing chamber bathed in golden luminescence. An ancient pedestal stands in the center."
    )

    # Connect rooms
    entrance.add_exit("north", hallway)
    hallway.add_exit("south", entrance)

    hallway.add_exit("west", armory)
    armory.add_exit("east", hallway)

    hallway.add_exit("east", alchemy)
    alchemy.add_exit("west", hallway)

    hallway.add_exit("north", crypt)
    crypt.add_exit("south", hallway)

    crypt.add_exit("north", sanctuary)
    sanctuary.add_exit("south", crypt)

    # Lock crypt north door requiring Golden Key
    crypt.lock_exit("north", "golden key")

    # Set crypt trap hazard
    crypt.set_hazard(20, "Spike trap triggered on loose floor stones! You take 20 damage.")

    # Populate items
    armory.items.append(
        Item("Iron Sword", "A sharp steel blade, standard issue for dungeon guards.", "weapon")
    )
    alchemy.items.append(
        Item("Health Potion", "A crimson elixir that restores 35 Health Points.", "potion", effect_value=35)
    )
    alchemy.items.append(
        Item("Golden Key", "An ornate brass key engraved with an owl crest.", "key")
    )
    sanctuary.items.append(
        Item("Ancient Relic", "The legendary artifact of power. Your mission is complete!", "relic")
    )

    return entrance


def describe_current_location(player):
    """Print detailed status of current room, visible items, and exits."""
    room = player.current_room
    print("\n" + "=" * 65)
    print(f"LOCATION: {room.name.upper()} | HP: {player.hp}/{player.max_hp}")
    print("=" * 65)
    print(room.description)

    # Check for uncollected items
    if room.items:
        print("\nVisible Items:")
        for itm in room.items:
            print(f"  * {itm.name} : {itm.description}")

    # Available Exits
    exit_list = []
    for d in sorted(room.exits.keys()):
        if room.locked_exit == d:
            exit_list.append(f"{d} [LOCKED with {room.required_key}]")
        else:
            exit_list.append(d)
    print(f"\nExits: {', '.join(exit_list)}")
    print("=" * 65)


def handle_move(player, direction):
    """Process moving the player in specified direction."""
    room = player.current_room
    d = direction.lower()

    if d not in room.exits:
        print(f"\nYou cannot go '{direction}'. There is no path that way.")
        return

    # Check if locked
    if room.locked_exit == d:
        print(f"\nThe path '{d}' is locked! You need the {room.required_key} to proceed.")
        return

    target = room.exits[d]
    player.current_room = target

    # Handle hazards upon entry
    if target.hazard_damage > 0:
        print(f"\n[Warning] {target.hazard_description}")
        alive = player.take_damage(target.hazard_damage)
        target.hazard_damage = 0  # Disarm once triggered
        if not alive:
            print("\nYou have succumbed to dungeon hazards. GAME OVER.")
            return

    describe_current_location(player)


def handle_take(player, item_name):
    """Pick up an item from the current room."""
    room = player.current_room
    target = None
    for itm in room.items:
        if itm.name.lower() == item_name.lower():
            target = itm
            break

    if not target:
        print(f"\nNo item named '{item_name}' found here.")
        return

    room.items.remove(target)
    player.add_item(target)
    print(f"\nYou picked up: {target.name}")

    if target.item_type == "relic":
        print("\n" + "*" * 65)
        print("CONGRATULATIONS! YOU HAVE ACQUIRED THE ANCIENT RELIC!")
        print("YOU ESCAPED THE DUNGEON VICTORIOUS!")
        print("*" * 65)
        player.has_won = True


def handle_use(player, item_name):
    """Use an item from the inventory."""
    item = player.find_item_in_inventory(item_name)
    if not item:
        print(f"\nYou do not have '{item_name}' in your inventory.")
        return

    room = player.current_room

    # Case 1: Potion
    if item.item_type == "potion":
        gained = player.heal(item.effect_value)
        player.remove_item(item)
        print(f"\nYou consumed {item.name} and recovered {gained} HP! Current HP: {player.hp}/{player.max_hp}")
        return

    # Case 2: Key
    if item.item_type == "key":
        if room.locked_exit and room.required_key == item.name.lower():
            direction = room.locked_exit
            room.unlock_exit()
            print(f"\nYou turned the {item.name} in the lock. The door to the '{direction}' swings open!")
            return
        else:
            print(f"\nThe {item.name} doesn't fit any lock here.")
            return

    print(f"\nYou inspect {item.name}: {item.description}")


def show_inventory(player):
    """Display items currently carried by player."""
    print("\n=== Player Inventory ===")
    if not player.inventory:
        print("Your satchel is empty.")
    else:
        for itm in player.inventory:
            print(f"  * {itm.name} [{itm.item_type}] : {itm.description}")
    print()


def print_help():
    """Print available game commands."""
    print("\n=== Available Commands ===")
    print("  go <direction>  : Move (north, south, east, west)")
    print("  take <item>     : Pick up an item from the room")
    print("  use <item>      : Use an item (potions, keys)")
    print("  inventory / inv : View inventory")
    print("  look            : Re-examine the current room")
    print("  help            : Show this instructions menu")
    print("  quit            : Exit the game\n")


def main():
    print("=" * 60)
    print("       WELCOME TO THE DUNGEON ADVENTURE (OOP)")
    print("=" * 60)
    name = input("Enter adventurer name: ").strip()
    if not name:
        name = "Adventurer"

    start_room = build_dungeon()
    player = Player(name, start_room)

    print(f"\nWelcome, {player.name}! Find the Ancient Relic and escape alive.")
    print_help()
    describe_current_location(player)

    while True:
        if player.hp <= 0 or player.has_won:
            break

        cmd_raw = input("\n[Command] > ").strip()
        if not cmd_raw:
            continue

        parts = cmd_raw.split(maxsplit=1)
        action = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if action == "go":
            if not arg:
                print("Specify a direction: go north, go south, go east, go west.")
            else:
                handle_move(player, arg)
        elif action in ("north", "south", "east", "west"):
            handle_move(player, action)
        elif action in ("take", "get", "grab"):
            if not arg:
                print("Specify an item to take: take <item name>")
            else:
                handle_take(player, arg)
        elif action == "use":
            if not arg:
                print("Specify an item to use: use <item name>")
            else:
                handle_use(player, arg)
        elif action in ("inventory", "inv", "i"):
            show_inventory(player)
        elif action in ("look", "l"):
            describe_current_location(player)
        elif action == "help":
            print_help()
        elif action == "quit":
            print(f"\nFarewell, {player.name}. Thanks for playing!")
            break
        else:
            print(f"Unknown command '{action}'. Type 'help' to see valid commands.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
