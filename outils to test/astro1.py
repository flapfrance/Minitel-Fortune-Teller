
from kerykeion import Report, AstrologicalSubject


def signs(sign, ascd):
    signdata = [["Can","Cancer"],["Leo", "Lion"],["Vir", "Virgo"], ["Lib", "Libra"],
                ["Sco", "Scorpio"], ["Sag", "Saggitarius"], ["Cap", "Capricorn"],
                ["Aqu", "Aquarius"], ["Pis", "Pisces"], ["Ari", "Aries"],
                ["Tau", "Taurus"], ["Gem", "Gemini"]
                ]
    search1 = sign
    search2 = ascd

    for i, sign in enumerate(signdata):
        if search1 in sign[0]:
            x= sign[1]
            print(x)
            #signdata[i][1] = replacement_term
    for i, ascd in enumerate(signdata):
        if search2 in ascd[0]:
            y= ascd[1]
            print(y)
            #signdata[i][1] = replacement_term
    return (x,y)


dat_all = ["Karl", 1967, 11, 5, 16, 45, "Rome", "IT"] 

kanye = AstrologicalSubject(*dat_all) #The asterisk is a need to use the array

report = Report(kanye)
print(report)

print(kanye)
# Sternzeichen
print("Signe: ", kanye.sun['sign'])

# Get information about the first house / Ascendant:
print("Asc: ", kanye.first_house['sign'])

# Get element of the Sun- & moon sign:
print('Sonnenelement: ',kanye.sun.element)
print('Mondelement: ', kanye.moon.element)

mysign, myascd = signs(kanye.sun['sign'],kanye.first_house['sign'])
print( mysign, myascd)
