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

    values = value.split("|")
    # rekurzija shi
    # for i, v in enumerate(values):
    #     if v[1:-1] in reg_definicije.keys():
    #         values[i] = reg_definicije[v[1:-1]]


    reg_definicije[key] = values.copy()

pravila_txt = pravila_txt[i:]

stanja = pravila_txt.pop(0).strip().split(" ")[1:]
jedinke = pravila_txt.pop(0).strip().split(" ")[1:]

print(stanja,jedinke,sep="\n")
# ispis_reg_def()
# print(reg_definicije)
