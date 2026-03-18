#!/usr/bin/env python3
"""Simple plant tracker CLI — log plants, watering dates, and notes."""

import json
import os
import sys
from datetime import date, datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "plants.json")


def load_plants():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE) as f:
        return json.load(f)


def save_plants(plants):
    with open(DATA_FILE, "w") as f:
        json.dump(plants, f, indent=2)


def add_plant(name, watered, notes):
    plants = load_plants()
    key = name.lower()
    if key in plants:
        print(f"Plant '{name}' already exists. Use 'water' or 'note' to update it.")
        return
    plants[key] = {"name": name, "last_watered": watered, "notes": notes}
    save_plants(plants)
    print(f"Added '{name}'.")


def water_plant(name, watered):
    plants = load_plants()
    key = name.lower()
    if key not in plants:
        print(f"Plant '{name}' not found. Add it first with 'add'.")
        return
    plants[key]["last_watered"] = watered
    save_plants(plants)
    print(f"Updated watering date for '{plants[key]['name']}' to {watered}.")


def add_note(name, note):
    plants = load_plants()
    key = name.lower()
    if key not in plants:
        print(f"Plant '{name}' not found. Add it first with 'add'.")
        return
    plants[key]["notes"] = note
    save_plants(plants)
    print(f"Updated notes for '{plants[key]['name']}'.")


def remove_plant(name):
    plants = load_plants()
    key = name.lower()
    if key not in plants:
        print(f"Plant '{name}' not found.")
        return
    display = plants.pop(key)["name"]
    save_plants(plants)
    print(f"Removed '{display}'.")


def list_plants():
    plants = load_plants()
    if not plants:
        print("No plants tracked yet. Use 'add' to get started.")
        return
    today = date.today()
    print(f"{'Name':<20} {'Last Watered':<14} {'Days Ago':<10} Notes")
    print("-" * 70)
    for entry in sorted(plants.values(), key=lambda p: p["name"].lower()):
        name = entry["name"]
        watered = entry["last_watered"]
        notes = entry.get("notes", "")
        try:
            delta = (today - datetime.strptime(watered, "%Y-%m-%d").date()).days
            days_ago = f"{delta}d ago"
        except ValueError:
            days_ago = "?"
        print(f"{name:<20} {watered:<14} {days_ago:<10} {notes}")


def show_help():
    print("""Usage: plants.py <command> [args]

Commands:
  add <name> [--watered YYYY-MM-DD] [--notes "..."]
      Add a new plant. Watered date defaults to today.
  water <name> [YYYY-MM-DD]
      Update the last watered date (defaults to today).
  note <name> "notes text"
      Update notes for a plant.
  remove <name>
      Remove a plant from the tracker.
  list
      List all tracked plants.
  help
      Show this help message.
""")


def parse_add(args):
    if not args:
        print("Error: provide a plant name.")
        sys.exit(1)
    name = args[0]
    watered = date.today().isoformat()
    notes = ""
    i = 1
    while i < len(args):
        if args[i] == "--watered" and i + 1 < len(args):
            watered = args[i + 1]
            i += 2
        elif args[i] == "--notes" and i + 1 < len(args):
            notes = args[i + 1]
            i += 2
        else:
            i += 1
    add_plant(name, watered, notes)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("help", "--help", "-h"):
        show_help()
        return

    cmd = args[0].lower()
    rest = args[1:]

    if cmd == "add":
        parse_add(rest)
    elif cmd == "water":
        if not rest:
            print("Error: provide a plant name.")
            sys.exit(1)
        watered = rest[1] if len(rest) > 1 else date.today().isoformat()
        water_plant(rest[0], watered)
    elif cmd == "note":
        if len(rest) < 2:
            print("Error: provide a plant name and notes text.")
            sys.exit(1)
        add_note(rest[0], rest[1])
    elif cmd == "remove":
        if not rest:
            print("Error: provide a plant name.")
            sys.exit(1)
        remove_plant(rest[0])
    elif cmd == "list":
        list_plants()
    else:
        print(f"Unknown command '{cmd}'. Run 'plants.py help' for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
