import requests
import re
import json
import os

URLS = {
    "buttons": "https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/buttons.hpp",
    "client": "https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.hpp",
    "offsets": "https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.hpp"
}


def download(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.text


# regex que funciona para qualquer tipo
OFFSET_REGEX = re.compile(
    r"constexpr\s+[a-zA-Z0-9_:<>]+\s+([a-zA-Z0-9_]+)\s*=\s*(0x[0-9A-Fa-f]+)"
)

NAMESPACE_REGEX = re.compile(r"namespace\s+([a-zA-Z0-9_]+)")


def parse_hpp(text):

    result = {}
    namespace_stack = []

    for line in text.splitlines():

        line = line.strip()

        # detect namespace
        ns = NAMESPACE_REGEX.search(line)
        if ns:
            namespace_stack.append(ns.group(1))
            continue

        # detect namespace end
        if line.startswith("}"):
            if namespace_stack:
                namespace_stack.pop()
            continue

        # detect offset
        match = OFFSET_REGEX.search(line)
        if match:

            name = match.group(1)
            value = match.group(2)

            key = "_".join(namespace_stack)

            if key not in result:
                result[key] = {}

            result[key][name] = value

    return result


def main():

    final = {}

    for name, url in URLS.items():

        print("Downloading:", name)

        text = download(url)

        parsed = parse_hpp(text)

        final.update(parsed)

    os.makedirs("output", exist_ok=True)

    with open("output/offsets.json", "w") as f:
        json.dump(final, f, indent=4)

    print("Offsets JSON updated.")


if __name__ == "__main__":
    main()
