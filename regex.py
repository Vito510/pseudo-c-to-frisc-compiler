def to_ord(group: list):
    out = []
    for g in group:
        t = []
        for i in g:
            if len(i) == 1:
                t.append(ord(i))
            else:
                t.append("+".join([str(ord(j)) for j in i]))
        out.append(t)

    return out

rpl_map = {
    "\\(": "(",
    "\\)": ")", 
    "\\{": "{",
    "\\}": "}",
    "\\|": "|",
    "\\*": "*",
    "\\$": "$",
    "josip": "(",
    "damir": ")",
    "luka": "\\\""
}

def group_replace(group: list, rpl_map: dict):
    out = []
    for g in group:
        t = []
        for i in g:
            if i in rpl_map:
                i = rpl_map[i]
                
            t.append(i)

        out.append(t)

    return out

def remove_empty_elements(groups: list):
    out = []
    for g in groups:
        t = list(filter(lambda x: x != '', g))
        out.append(t)

    return out



def match(pat: str, text_in: str, silent: bool = True):
    pat = pat.replace("\\\\\"","luka").replace("\\(","josip").replace("\\)","damir")
    text = [i for i in text_in.replace('\\*','©')]
    pat = pat.encode('utf-8').decode('unicode_escape')
    groups = group_replace(remove_empty_elements(list(filter(lambda x: not (len(x) == 1 and x[0] == ''),[i.split("|") for i in pat.replace(")","(").split("(")]))),rpl_map)
    new = []
    for g in groups:
        # const npr. abc(1|2|3) abc dio
        if len(g) == 1 and len(g[0]) > 1:
            for item in [j for j in g[0]]:
                if item: new.append([item])
        else:
            new.append([j for j in g])

    groups = new.copy()

    # for kleen 
    new = []
    groups_r = []
    flag = 0
    for g in groups[::-1]:
        if g == ['*']:
            flag = 1
        else:
            new.insert(0,g)
            groups_r.insert(0,flag)
            flag = 0

    groups = group_replace(new,{"©": "*"})

    # print(groups, to_ord(groups),sep="\n")

    # for g in groups:
    #     print(g)

    group_idx = 0
    match_idx = 0
    capture = [0]*len(groups)

    while text and group_idx < len(groups):
        c = text.pop(0)

        # if not silent: print(f'{c}  {group_idx:2} {groups[group_idx]} {groups_r[group_idx]}\t')

        if groups_r[group_idx]:
            #repeating group

            if c not in groups[group_idx]:
                group_idx += 1
                text.insert(0,c)
            else:
                capture[group_idx] = 1
                match_idx += 1
        else:
            if c not in groups[group_idx]:
                if not silent: print('out', c)
                break
            else:
                capture[group_idx] = 1
                group_idx += 1
                match_idx += 1

    # are all groups hit
    # if not silent: print('end',groups,groups_r,group_idx)
    
    for i in range(len(capture)):
        capture[i] += groups_r[i]

    if sum(capture) < len(groups):
        if not silent: print("Missing groups", capture)
        return None

    if not silent: print("Found match:", text_in[:match_idx].strip(), [ord(i) for i in text_in[:match_idx]])
    return text_in[:match_idx]

if __name__ == "__main__":
    import re
    pat = "\"(\\(|\\)|\\{|\\}|\\||\\*|\\\\|\\$|\\t| |!|#|%|&|'|+|,|-|.|/|0|1|2|3|4|5|6|7|8|9|:|;|<|=|>|?|@|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|[|]|^|_|`|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|~|\\\\\")*\""
    x = r'"\"tes\"t2\"";'
    # print([ord(i) for i in x])
    print(x)
    # r1 = re.match(pat, x)
    r1 = None
    r2 = match(pat,x,False)

    # print(f'\n\nP:\t{pat}\nT:\t{x}\n')
    # print(f're:\t{r1}')
    print(f'my:\t{r2}')

    if (r1 is None and r2 is None or r1 and r1.group(0) == r2):
        print("\x1B[42mEQUAL\x1B[0m") 
    else:
        print("\x1B[41mFAIL\x1B[0m")