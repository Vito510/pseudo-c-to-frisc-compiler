def match(a: dict, text: str):
    text = [ord(i) for i in text]

    stanja = a['stanja']
    simboli = a['simboli']
    accept = a['accept']
    start = a['start']
    prelazi = a['prijelazi']

    longest_match = None
    next = [start]
    if '$' in prelazi[start]: next.extend(prelazi[start]['$'])
    # res = ",".join([stanja[i] for i in sorted(next)])
    for j, sim in enumerate(text):
        r = []
        temp = []
        for n in next:
            if n in prelazi and sim in prelazi[n]:
                temp.extend(prelazi[n][sim])

        next = list(set(temp))
        r.extend([stanja[i] for i in sorted(next)])
        
        if len(next) == 0:
            break

        # print(r)
        if accept[0] in next:
            longest_match = j + 1

    if longest_match:
        return "".join(map(chr,text[:longest_match]))
    else:
        return None