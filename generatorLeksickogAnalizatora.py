import re

pravila_txt = open("./data/c-leksik-pravila.txt", "r", encoding="utf-8").readlines()

reg_definicije = {}

def ispis_reg_def() -> None:
    for k in reg_definicije:
        print(f'{k:40}\t{"".join(reg_definicije[k])}')

cut = 0
for i, line in enumerate(pravila_txt):

    line = line.strip()

    if line.startswith("%"):
        cut = i
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

x = "e+100"

for definicija in reg_definicije:
    pattern = f'{reg_definicije[definicija]}'
    for key in reg_definicije:
        key2 = "{" + key + "}"
        if key2+"|" in pattern: # ne moramo enkapsulirati
            pattern = pattern.replace(key2,f'{reg_definicije[key]}')
        elif key2 in pattern:   # moramo
            pattern = pattern.replace(key2,f'({reg_definicije[key]})')
    pattern = pattern.replace("(","[").replace(")","]") # python regex uses [] insted of ()
    if not (pattern.startswith('[') and pattern.endswith(']') or pattern.endswith('*')) : pattern = f'[{pattern}]'      # mora biti enkapsulirano sa [], ako vec nije
    print(f'{definicija:50}\t{re.fullmatch(pattern,x) is not None}')


