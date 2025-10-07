
class ParserData:
    def __init__(self, stanja, jedinke, prijelazi):
        self.stanja = stanja
        self.jedinke = jedinke
        self.prijelazi = prijelazi

reg_definicije = {}

def ispis_reg_def() -> None:
    for k in reg_definicije:
        print(f'{k:40}\t{"".join(reg_definicije[k])}')

def convert_2_pattern(pattern: str) -> str:
    """converts the given regex pattern to python applicable format""" 
    for key in reg_definicije:
        key2 = "{" + key + "}"
        if key2+"|" in pattern: # ne moramo enkapsulirati
            pattern = pattern.replace(key2,f'{reg_definicije[key]}')
        elif key2 in pattern:   # moramo
            pattern = pattern.replace(key2,f'({reg_definicije[key]})')
    pattern = pattern.replace("(","[").replace(")","]") # python regex uses [] insted of ()
    if not (pattern.startswith('[') and pattern.endswith(']') or pattern.endswith('*')) : pattern = f'[{pattern}]'      # mora biti enkapsulirano sa [], ako vec nije
    return pattern

def parse(filepath: str) -> ParserData: 

    pravila_txt = open(filepath, "r", encoding="utf-8").readlines()

    for i, line in enumerate(pravila_txt):

        line = line.strip()

        if line.startswith("%"):
            break

        key, value = line.split(" ")
        key = key[1:-1]

        reg_definicije[key] = value

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
        ulaz = convert_2_pattern(ulaz)
        # print(stanje,ulaz,akcija)

        if stanje not in prijelazi:
            prijelazi[stanje] = {}
        
        if ulaz not in prijelazi[stanje]:
            prijelazi[stanje][ulaz] = []

        prijelazi[stanje][ulaz] = akcija

    return ParserData(stanja, jedinke, prijelazi)

