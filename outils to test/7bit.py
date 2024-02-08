def decimal_to_7bit_binary(decimal_number):
    # Binärdarstellung erhalten und das Präfix "0b" entfernen
    binary_representation = bin(decimal_number)[2:]

    # Auf 7 Bits beschränken oder Nullen hinzufügen
    if len(binary_representation) < 7:
        # Führende Nullen hinzufügen, falls notwendig
        binary_representation = '0' * (7 - len(binary_representation)) + binary_representation
    elif len(binary_representation) > 7:
        # Auf 7 Bits beschränken, indem die führenden Bits entfernt werden
        binary_representation = binary_representation[-7:]

    return binary_representation

def binary_to_ascii(binary_code):
    # Binärcode in Dezimalzahl umwandeln und dann in ASCII-Code
    decimal_number = int(binary_code, 2)
    ascii_character = chr(decimal_number)
    return ascii_character

# Beispiel: Dezimalzahl 25 in 7-Bit-Binärcode und dann in ASCII-Code umwandeln
decimal_number = 30
hexa_num = hex(decimal_number)
binary_code = decimal_to_7bit_binary(decimal_number)
ascii_code = binary_to_ascii(binary_code)

print(f'Dezimalzahl: {decimal_number}')
print(f'Hexazahl: {hexa_num}')
print(f'7-Bit-Binärcode: {binary_code}')
print(f'ASCII-Code: {ascii_code}')
