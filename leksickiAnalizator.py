import parserLeksickogAnalizatora

data = parserLeksickogAnalizatora.parse("./data/c-leksik-pravila.txt")

stanja = data.stanja
jedinke = data.jedinke
prijelazi = data.prijelazi

print(stanja,jedinke,prijelazi)