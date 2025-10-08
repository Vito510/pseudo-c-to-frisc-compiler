import re
import parserLeksickogAnalizatora

data = parserLeksickogAnalizatora.parse("./data/c-leksik-pravila.txt")

stanja = data.stanja
jedinke = data.jedinke
prijelazi = data.prijelazi


stanje = stanja[0] # pocetno stanje
c_file = open("./data/c-program.c", "r", encoding="utf-8").read()

buffer = []
carape = [0]*60


c_file = "0x1234 "
for s in c_file:
    # print(s)
    buffer.append(s)
    for i, ulaz in enumerate(prijelazi[stanje]):
        
        if re.fullmatch(ulaz, "".join(buffer)) is not None:
            carape[i] += 1
        else:
            carape[i] = 0


    print("".join(map(str,carape)))



for i in range(len(carape)):
    if carape[i] > 0:
        k = list(prijelazi[stanje].keys())[i]
        print(prijelazi[stanje][k],k)