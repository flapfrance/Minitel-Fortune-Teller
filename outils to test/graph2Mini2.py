# Annahme: data_hex ist deine Hexadezimal-Liste von Pixel-Daten
# Annahme: image_width ist die Bildbreite (z.B., 80)
# Annahme: image_height ist die Bildhöhe (z.B., 15)

data_hex = b'\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x01\x01\x00\x00\x00\x01\x01\x01\x00\x00\x00\x00\x01\x00\x00'
image_width = 8
image_height = 5

# Konvertiere Hexadezimaldaten in binäre Daten
#data_binary = bytearray.fromhex(data_hex.decode('utf-8'))
data_binary = bytearray(data_hex)

# Transformiere Daten in 2x3 Blöcke
transformed_data = []
for y in range(0, image_height, 3):
    for x in range(0, image_width, 2):
        block = [data_binary[i + j*image_width] for j in range(3) for i in range(2)]
        transformed_data.append(block)

# Betrachte die übrig gebliebenen Daten (5 Zeilen und 2 Spalten)
remaining_data = [data_binary[i] for i in range((image_height // 3) * 3 * image_width, image_height * image_width)]

# Ausgabe der transformierten Daten und der übrig gebliebenen Daten
print("Transformierte Daten:")
for block in transformed_data:
    print(block)

print("\nÜbrig gebliebene Daten:")
print(remaining_data)
