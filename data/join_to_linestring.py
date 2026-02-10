import json

INPUT_FILE = "./nelson-mandela-road.json"
OUTPUT_FILE = INPUT_FILE.replace(".json", "-multilinestring.json")

lines = []

with open(INPUT_FILE, "r") as f:
    data = json.load(f)

for element in data.get("elements", []):
    if element.get("type") == "way" and "geometry" in element:
        coords = []
        for point in element["geometry"]:
            lon = point["lon"]
            lat = point["lat"]
            coords.append(f"{lon} {lat}")

        # only keep valid LineStrings (>= 2 points)
        if len(coords) >= 2:
            lines.append(f"({', '.join(coords)})")

multilinestring = f"MULTILINESTRING({', '.join(lines)})"

output = {"geometry": multilinestring}

with open(OUTPUT_FILE, "w") as f:
    json.dump(output, f, indent=2)

print(multilinestring)
