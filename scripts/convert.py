import requests
import re
import json
from collections import defaultdict

URLS = {
    "buttons": "https://raw.githubusercontent.com/a2x/cs2-dumper/refs/heads/main/output/buttons.hpp",
    "client": "https://raw.githubusercontent.com/a2x/cs2-dumper/refs/heads/main/output/client_dll.hpp",
    "offsets": "https://raw.githubusercontent.com/a2x/cs2-dumper/refs/heads/main/output/offsets.hpp"
}

def download(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.text


def parse_buttons(text):
    result = {}
    
    pattern = re.compile(r"constexpr\s+auto\s+(\w+)\s*=\s*(0x[0-9A-Fa-f]+)")
    
    for name, value in pattern.findall(text):
        result[name] = value
        
    return result


def parse_structs(text):
    data = defaultdict(dict)

    struct = None

    struct_pattern = re.compile(r"struct\s+(\w+)")
    field_pattern = re.compile(r"constexpr\s+auto\s+(\w+)\s*=\s*(0x[0-9A-Fa-f]+)")

    for line in text.splitlines():

        s = struct_pattern.search(line)
        if s:
            struct = s.group(1)
            continue

        f = field_pattern.search(line)
        if f and struct:
            name, value = f.groups()
            data[struct][name] = value

    return data


def main():

    buttons_text = download(URLS["buttons"])
    client_text = download(URLS["client"])
    offsets_text = download(URLS["offsets"])

    output = {}

    output["buttons"] = parse_buttons(buttons_text)

    structs_client = parse_structs(client_text)
    structs_offsets = parse_structs(offsets_text)

    output.update(structs_client)
    output.update(structs_offsets)

    with open("output/offsets.json", "w") as f:
        json.dump(output, f, indent=4)

    print("JSON atualizado!")


if __name__ == "__main__":
    main()
