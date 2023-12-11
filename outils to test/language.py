import requests

def get_language_by_country_code(country_code):
    try:
        url = f"https://restcountries.com/v2/alpha/{str(country_code)}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            languages = data.get("languages", [])
            
            if languages:
                print(languages[0].get("name", "English")) 
                return languages[0].get("name", "English")
            else:
                return "English"
        else:
            return "English"
    except Exception as e:
        return "English"

# Beispielaufruf
country_code_de = "IT"
language_de = get_language_by_country_code(country_code_de)
print(f"Die Amtssprache von {country_code_de} ist {language_de}.")

country_code_gb = "GB"
language_gb = get_language_by_country_code(country_code_gb)
print(f"Die Amtssprache von {country_code_gb} ist {language_gb}.")
