import pynitel, serial, os, openai

#******Format to left and to right
def strformat(left='', right='', fill=' ', width=40):
    " formattage de texte "
    total = width-len(left+right)
    if total > 0:
        out = left + fill * total + right
    else:
        out = left+right
    print("'"+out+"'", width, total, len(out))
    return(out)
def strcenter(row = 0, pos=20, txt = ' ', width = 40, size = 0):
    out = pos - len(txt)//2
    if out < 1:
        out = 1
    m.pos(row,out)
    m.scale(size)
    m._print(txt)
    m.scale(1)
    return()
def split_string_into_lines(text, max_line_length=40):
    words = text.split()  # Teile den Text in Worte auf
    lines = []
    current_line = ""

    for word in words:
        # Wenn das Hinzufügen des aktuellen Wortes zur aktuellen Zeile die maximale Länge überschreiten würde, füge die Zeile zu den Zeilen hinzu und starte eine neue Zeile.
        if len(current_line) + len(word) + 1 <= max_line_length:
            if current_line:
                current_line += " "
            current_line += word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

# Function to send a message to the OpenAI chatbot model and return its response
def send_message(message_log):
    # Use OpenAI's ChatCompletion API to get the chatbot's response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # The name of the OpenAI chatbot model to use
        #model="gpt-4",
        messages=message_log,   # The conversation history up to this point, as a list of dictionaries
        max_tokens=500,        # The maximum number of tokens (words or subwords) in the generated response
        stop=None,              # The stopping sequence for the generated response, if any (not used here)
        temperature=0.9,        # The "creativity" of the generated response (higher temperature = more creative)
    )
    token_usage = response['usage']['total_tokens']            
    print("Anzahl der verwendeten Tokens:", token_usage)
    # Find the first response from the chatbot that has text in it (some responses may not have text)
    for choice in response.choices:
        if "text" in choice:
            return choice.text

    # If no response with text is found, return the first response's content (which may be empty)
    return response.choices[0].message.content

def chatbot():
    # Initialize the conversation history with a message from the chatbot
    message_log = [
        {"role": "system", "content": "Benutze die Sprache vom beginn der jeweils aktuellen Eingabe. Formuliere eine kurze Antwort die die Anzahl von 500 Tokens nicht überschreitet. "}
    ]

    # Set a flag to keep track of whether this is the first request in the conversation
    first_request = True

    # Start a loop that runs until the user types "quit"
    while True:
        if first_request:
            # If this is the first request, get the user's input and add it to the conversation history
            user_input = input("You: ")
            user_input = user_input #+ " (Bitte in lockerer, burnerorientierter Sprache abfassen. Die Sprache vom beginn der aktuellen Eingabe benutzen.)" 
            message_log.append({"role": "user", "content": user_input})

            # Send the conversation history to the chatbot and get its response
            response = send_message(message_log)

            # Add the chatbot's response to the conversation history and print it to the console
            message_log.append({"role": "assistant", "content": response})
            print(f"AI assistant: {response}")
            

            # Set the flag to False so that this branch is not executed again
            first_request = False
        else:
            # If this is not the first request, get the user's input and add it to the conversation history
            user_input = input("You: ")
            user_input = user_input# + " (Bitte in lockerer, burnerorientierter Sprache abfassen. Die Sprache vom beginn der aktuellen Eingabe benutzen.)"
            # If the user types "quit", end the loop and print a goodbye message
            if user_input.lower() == "quit":
                print("Goodbye!")
                break

            message_log.append({"role": "user", "content": user_input})

            # Send the conversation history to the chatbot and get its response
            response = send_message(message_log)

            # Add the chatbot's response to the conversation history and print it to the console
            message_log.append({"role": "assistant", "content": response})
            print(f"AI assistant: {response}")
            
        return response

     
def printout(message):
    #*****prepa array
    #with open("test.txt", "r") as file:
        #file_content = file.read()
    file_content = message
    lines = split_string_into_lines(file_content, max_line_length=39)
    print(len(lines)) #anzahl zeilen
    m.pos(1,1)
    page = 1    
    # plusieurs pages ?
    if len(lines) > 18:
         m.pos(0, 33)
         m._print(" "+str(int(abs(page)))+'/'+str(int((len(lines)+22)/23)))

    while True:
        
        if len(lines) > 0:  # affichage
                # entête sur 2 lignes + séparation
            m.home()
            m.pos(0)
            m._print("TEST3")#transl("p5t1"))
            if lines != '':
                #m.pos(0, 36)
                m.color(m.bleu)
                m._print(str(len(lines)))
            m.pos(2)
            m.color(m.bleu)
            m.plot('̶', 40)
                    
        # plusieurs pages ?
            if len(lines) > 18:
                m.pos(0, 33)
                m._print(" "+str(int(abs(page)))+'/'+str(int((len(lines)+17)/18)))
                m.pos(3)

                # première ligne de résultat
            y = 3
            m.pos(y)
            for a in range((page-1)*18, page*18, ):
            #for a in range( page*9,(page-1)*9, -1): # neu rückwärts
                print("Anzeige page:",(page-1)*18, "  ",page*18)
                y= y
                m.pos(y,1)
                if a < len(lines):
                    r = lines[a]
                    print(r, len(r))
                    m.color(m.blanc)                                                     
                    strcenter(row = y, pos = 20, txt = r, width = 40, size = 0)
                    #m._print(r)
                    y= y +1
                    m.pos(y,1)
                    m.color(m.vert)
                    m.color(m.bleu)
                    
                        
        # ligne finale
            m.pos(21)
            m.color(m.bleu)
            m.plot('̶', 40)

            if page > 1:
                if len(lines) > page*18:  # place pour le SUITE
                    m.pos(22, 20)
                else:
                    m.pos(22, 20)
                m.color(m.vert)
                m._print("test1")
                m.pos(22, 33)
                m.underline()
                m._print(' ')
                m.inverse()
                m.color(m.cyan)
                m._print('_RETOUR ' )
                        
            if len(lines) > page*18:
                m.pos(23, 21)
                m.color(m.vert)
                m._print("test2")
                m.pos(23, 34)
                m.underline()
                m._print(' ')
                m.inverse()
                m.color(m.cyan)
                m._print('_SUITE')

            m.pos(22, 1)
            m._print("test3")
            m.pos(23, 5)
            m._print("test4")

            m.underline()
            m._print(' ')
            m.inverse()
            m.color(m.cyan)
            m._print('_ENVOI ')
            m.pos(24, 1)
            m.color(m.vert)
            m._print("test6")
            m.pos(24, 11)
            m.inverse()
            m.color(m.cyan)
            m._print(' GUIDE')
            m.underline()
            m._print(' ')
            m.inverse()
            m.color(m.cyan)
            m.pos(24, 26)
            m.color(m.vert)
            m._print("test7")
            m.pos(24, 33)
            m.inverse()
            m.color(m.cyan)
            m._print("SOMMAIRE")
                
        elif db_num == 0:
                    
            print("0 Data... und raus")
            m.message(15, 7, 5,"message", bip=True)
            break
        else:
            page = abs(page)

            # attente saisie            
        (choix, touche) = m.input(23, 1, 3, sltime)
        #****** check for integer
        if not isinstance(choix,int):
            if not choix.isdigit():
                choix = 0
            choix = int(choix)
            m.clear
                
        if choix == "":
            choix = int(0)
                
        elif choix > len(lines):
            break
        else:
            choix = int(choix)
        m.cursor(False)
        if touche == m.suite:
            if page*18 < len(lines):
                page = page + 1
            else:
                m.bip()
        elif touche == m.retour:
            if page > 1:
                page = page - 1
            else:
                m.bip()
        elif touche == m.envoi:
            r = res[choix-1]                
            choix_lfd = r[0]
            break
        elif touche == m.annulation:
            break
        elif touche == m.guide:
            break
        elif touche == m.sommaire: 
            break
        elif touche == m.correction:  # retour saisie pour correction
            break
            #return(touche)
        elif touche != m.repetition:
            m.bip()
            page = -page  # pas de ré-affichage        
        #end while

#******* Code start***************

m = pynitel.Pynitel(serial.Serial('/dev/ttyUSB0', 1200, parity=serial.PARITY_EVEN, bytesize=7, timeout=2))
        #os.system("echo -en '\x1b\x3a\x6b\x64' > /dev/ttyUSB0")        
os.system("stty -F /dev/ttyUSB0 speed 1200")
speed = 4800

sltime = 60
if speed == 4800:
     os.system("echo -en '\x1b\x3a\x6b\x76' > /dev/ttyUSB0")
     m.end()      
     os.system("stty -F /dev/ttyUSB0 speed 4800")
     m = pynitel.Pynitel(serial.Serial('/dev/ttyUSB0', 4800, parity=serial.PARITY_EVEN, bytesize=7, timeout=2))
     print("Baudrate: ", speed)
else:# speed == 1200:            
     print("Baudrate: ", speed)
m.home()
os.system("echo -en '\x1b\x3a\x6A\x43' > /dev/ttyUSB0")
#m.step(1)# Set up OpenAI API key
api_key = "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"


m._print("Losgehts")
answer = chatbot()
printout(answer)
