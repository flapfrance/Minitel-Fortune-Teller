
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
dat_str = ["Sebastian"]
dat_str.append("Hamm")
dat_str.append("DE")
print(dat_str)
#dat_str = ["Sebastian","Bielefeld", "DE"]
dat_num = [1966, 12, 27, 16, 45 ]
dat_all = ["Sebastian", 1966, 12, 27, 16, 45, "Rome"] 
#kanye = AstrologicalSubject("Sebastian", 1966, 12, 27, 16, 45, "Bielefeld") #, nation = "FR")
 #lng=1.35,   lat=44.0167, tz_str="Europe/Paris", 
#kanye = AstrologicalSubject("Sebastian", 1966, 12, 27, 17, 45, nation = "DE", city="Bielefeld")
#print(dat_str[0], dat_num[0],dat_num[1],dat_num[2],dat_num[3],dat_num[4], dat_str[1])
#kanye = AstrologicalSubject(dat_str[0], dat_num[0],dat_num[1],dat_num[2],dat_num[3],dat_num[4], dat_str[1], dat_str[2])

print(dat_all[0], dat_all[1], dat_all[2], dat_all[3], dat_all[4], dat_all[5], dat_all[6])#), dat_all[7])
kanye = AstrologicalSubject(dat_all[0], dat_all[1], dat_all[2], dat_all[3], dat_all[4], dat_all[5], dat_all[6])#, dat_all[7])
report = Report(kanye)
print(report)

#report.print_report()

# Get the information about the sun in the chart:
# (The position of the planets always starts at 0)
#> {'name': 'Sun', 'quality': 'Mutable', 'element': 'Air', 'sign': 'Gem', 'sign_num': 2, 'pos': 17.598992059774275, 'abs_pos': 77.59899205977428, 'emoji': '♊️', 'house': '12th House', 'retrograde': False}
#> {'name': 'First_House', 'quality': 'Cardinal', 'element': 'Water', 'sign': 'Can', 'sign_num': 3, 'pos': 17.995779673209114, 'abs_pos': 107.99577967320911, 'emoji': '♋️'}
print(kanye)
# Sternzeichen
print("Signe: ", kanye.sun['sign'])
#print("Mondzeichen: ",kanye.moon['sign'])
# Get information about the first house / Ascendant:
print("Asc: ", kanye.first_house['sign'])

# Get element of the Sun- & moon sign:
print('Sonnenelement: ',kanye.sun.element)
print('Mondelement: ', kanye.moon.element)

mysign, myascd = signs(kanye.sun['sign'],kanye.first_house['sign'])
print( mysign, myascd)
