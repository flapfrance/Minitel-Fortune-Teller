from itertools import permutations

# Die Zahlen, die du kombinieren möchtest
zahlen = [1, 2, 3, 4]

# Alle vierstelligen Permutationen der Zahlen
alle_permutationen = permutations(zahlen, 4)

# Umwandeln der Permutationen in Zahlen
alle_kombinationen = [''.join(map(str, perm)) for perm in alle_permutationen]

# Ausgabe der resultierenden Kombinationen
for kombination in alle_kombinationen:
    print(kombination)
