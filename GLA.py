import sys
import json

class ParserData:
    def __init__(self, stanja, jedinke, prijelazi):
        self.stanja = stanja
        self.jedinke = jedinke
        self.prijelazi = prijelazi

# def ispis_reg_def() -> None:
#     for k in reg_definicije:
#         print(f'{k:40}\t{"".join(reg_definicije[k])}')
_reg_definicije = {}

def _convert_2_pattern(pattern: str, reg_definicije: dict = {}):
    """converts the given regex pattern to python applicable format""" 
    for key in reg_definicije:
        key2 = "{" + key + "}"
    
        if key2+"|" in pattern or "|"+key2 in pattern: # ne moramo enkapsulirati
            pattern = pattern.replace(key2,f'{reg_definicije[key]}')
        elif key2 in pattern:   # moramo
            pattern = pattern.replace(key2,f'({reg_definicije[key]})')
    
    # escape = ["^", "[", "+", "-", "$", "]","?","."]
    # for item in escape:
    #     pattern = pattern.replace(item,"\\"+item)
    pattern = pattern.replace("\\_"," ")
    
    return pattern

def parse():
    global _reg_definicije
    pravila_txt = [line + "\n" for line in sys.stdin.read().split("\n")[:-1]]
    # print(len(pravila_txt))

    for i, line in enumerate(pravila_txt):

        line = line.strip()

        if line.startswith("%"):
            break

        key, value = line.split(" ")
        key = key[1:-1]

        for k in _reg_definicije:
            key2 = "{" + k + "}"
        
            if key2+"|" in value: # ne moramo enkapsulirati
                value = value.replace(key2,f'{_reg_definicije[k]}')
            elif key2 in value:   # moramo
                value = value.replace(key2,f'({_reg_definicije[k]})')
        
        _reg_definicije[key] = value

    pravila_txt = pravila_txt[i:]

    stanja = pravila_txt.pop(0).strip().split(" ")[1:]
    jedinke = pravila_txt.pop(0).strip().split(" ")[1:]

    # print(stanja,jedinke,sep="\n")
    # ispis_reg_def()
    # print(reg_definicije)

    # x = "e+100"
    # print(re.fullmatch(convert_2_pattern(reg_definicije["eksponent"]),x))

    prijelazi = {}

    for prijelaz in "".join(pravila_txt).strip()[1:-1].split("}\n<"):

        if prijelaz == "\n":
            continue

        stanje,r = prijelaz.split(">",maxsplit=1)
        ulaz, akcija = map(str.strip,r.rsplit("{",maxsplit=1))
        akcija = list(filter(lambda x: x != "-", akcija.split("\n")))
        ulaz = _convert_2_pattern(ulaz, _reg_definicije)
        # print(stanje,ulaz,akcija)

        if stanje not in prijelazi:
            prijelazi[stanje] = {}
        
        if ulaz not in prijelazi[stanje]:
            prijelazi[stanje][ulaz] = []
            prijelazi[stanje][ulaz] = akcija
        else:
            continue

    return ParserData(stanja, jedinke, prijelazi)

if __name__ == "__main__":

    data = parse()
    out = {
        "jedinke": data.jedinke,
        "stanja": data.stanja,
        "prijelazi": data.prijelazi
    }

    with open("./analizator/tablice.json", "w") as f:
        json.dump(out, f)