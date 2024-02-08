
def code(user_input):
    x = ""
    data = [[0, '0x20'], [1, '0x21'], [2, '0x22'], [3, '0x23'], [4, '0x24'], [5, '0x25'],
 [6, '0x26'], [7, '0x27'], [8, '0x28'], [9, '0x29'], [10, '0x2a'], [11, '0x2b'],
 [12, '0x2c'], [13, '0x2d'], [14, '0x2e'], [15, '0x2f'], [16, '0x30'], [17, '0x31'],
 [18, '0x32'], [19, '0x33'], [20, '0x34'], [21, '0x35'], [22, '0x36'], [23, '0x37'],
 [24, '0x38'], [25, '0x39'], [26, '0x3a'], [27, '0x3b'], [28, '0x3c'], [29, '0x3d'],
 [30, '0x3e'], [31, '0x3f'], [32, '0x60'], [33, '0x61'], [34, '0x62'], [35, '0x63'],
 [36, '0x64'], [37, '0x65'], [38, '0x66'], [39, '0x67'], [40, '0x68'], [41, '0x69'],
 [42, '0x6a'], [43, '0x6b'], [44, '0x6c'], [45, '0x6d'], [46, '0x6e'], [47, '0x6f'],
 [48, '0x70'], [49, '0x71'], [50, '0x72'], [51, '0x73'], [52, '0x74'], [53, '0x75'],
 [54, '0x76'], [55, '0x77'], [56, '0x78'], [57, '0x79'], [58, '0x7a'], [59, '0x7b'],
 [60, '0x7c'], [61, '0x7d'], [62, '0x7e'], [63, '0x7f']]

    # Eingabe der Zahl zwischen 0 und 63
    user_input = int(user_input)

# Überprüfe, ob die Eingabe im gültigen Bereich liegt
    if 0 <= user_input <= 63:
    # Rufe den passenden Code aus dem Array ab
        hex_value, decimal_value = data[int(user_input)]
        print(f"Hexadezimalwert: {hex_value}, Dezimalwert: {decimal_value}")
    else:
        print("Die Eingabe muss zwischen 0 und 63 liegen.")

code(63)
