# encoding: utf-8

# Multi-dimensional Form Array Parser by Herman Schaaf (@ironzeb)
# http://www.ironzebra.com/code/23
def parse_html_array(post, name):
    dictionary = {}

    for key in post.keys():
        if key.startswith(name):
            rest = key[len(name):]

            # Split the string into different components
            parts = [p[:-1] for p in rest.split('[')][1:]

            # Prevent parsing non integer array keys (such as tmp)
            try:
                id = int(parts[0])
            except ValueError:
                continue

            # Add a new dictionary if it doesn't exist yet
            if id not in dictionary:
                dictionary[id] = {}

            # Add the information to the dictionary
            dictionary[id][parts[1]] = post.get(key)

    return dictionary

