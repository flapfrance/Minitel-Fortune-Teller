from PIL import Image
from itertools import permutations

# Lade die Bilder
image1 = Image.open('1.png').convert('RGBA')
image2 = Image.open('2.png').convert('RGBA')
image3 = Image.open('3.png').convert('RGBA')
image4 = Image.open('4.png').convert('RGBA')

# Die Zahlen, die du kombinieren möchtest
bilder = [image1, image2, image3, image4]

# Erzeuge alle vierstelligen Permutationen der Bilder
alle_permutationen = permutations(bilder)

# Iteriere durch alle Kombinationen
for i, kombination in enumerate(alle_permutationen, start=1):
    # Erstelle eine leere Bildfläche mit transparentem Hintergrund
    kombiniertes_bild = Image.new('RGBA', (280, image1.height), (0, 0, 0, 0))

    # Berechne die neue Breite für jedes Bild
    neue_breite = 280 // len(kombination)

    # Skaliere und füge die Bilder horizontal zusammen
    offset = 0
    for bild in kombination:
        skaliertes_bild = bild.resize((neue_breite, image1.height), Image.ANTIALIAS)
        kombiniertes_bild.paste(skaliertes_bild, (offset, 0), skaliertes_bild)
        offset += neue_breite

    # Speichere das kombinierte Bild als PNG
    kombiniertes_bild.save(f'code_{i}.png', format='PNG')

# Schließe die Originalbilder
image1.close()
image2.close()
image3.close()
image4.close()
