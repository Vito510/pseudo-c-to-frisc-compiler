from NKaGenerator import regex_to_automat

cache = {}

def match(pattern: str, text: str):
    a = regex_to_automat(pattern)
    text = [ord(i) for i in text]

    stanja = a.stanja
    simboli = a.simboli
    accept = a.accept
    start = a.start

    if a in cache:
        prelazi = cache[a]
    else:
        prelazi = a.prelazi
        # izgradi epsilon
        for state in prelazi:
            if '$' in prelazi[state]:
                for i in prelazi:
                    for j in prelazi[i]:
                        if state in prelazi[i][j]:
                            prelazi[i][j].extend(prelazi[state]['$'])
                            prelazi[i][j] = list(set(prelazi[i][j]))
        cache[a] = prelazi


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