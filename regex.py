def match(pat: str, text_in: str, silent: bool = True):
    text = [i for i in text_in]
    groups = list(filter(lambda x: not (len(x) == 1 and x[0] == ''),[i.split("|") for i in pat.replace(")","(").split("(")]))

    dont = {"\\n": "\n"}

    new = []
    for g in groups:
        # const npr. abc(1|2|3) abc dio
        if g[0] in dont:
            new.append([dont[g[0]]])
        elif len(g) == 1 and len(g[0]) > 1:
            for item in [j for j in g[0]]:
                item = item.replace("\\","")
                if item: new.append([item])
        else:
            new.append([j.replace("\\","") for j in g])

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

    groups = new


    group_idx = 0
    match_idx = 0
    capture = [0]*len(groups)

    if not silent: print(f'{'-'*20}\nP: {pat}\tG: {groups}')

    while text and group_idx < len(groups):
        c = text.pop(0)

        if not silent: print(f'{c}  {group_idx:2} {groups[group_idx]} {groups_r[group_idx]}\t')

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
    if not silent: print('end',groups,groups_r,group_idx)
    
    for i in range(len(capture)):
        capture[i] += groups_r[i]

    if sum(capture) != len(groups):
        if not silent: print("Missing groups", capture)
        return None

    if not silent: print("Found match:", text_in[:match_idx])
    return text_in[:match_idx]

if __name__ == "__main__":
    import re
    pat = "\\n"
    # pat = "(e|E)(\\$|\\+|-)(1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*"

    # pat = "(a|b)*"
    x = "\n"

    r1 = re.match(pat, x)
    r2 = match(pat,x,False)

    print(f'\n\nP:\t{pat}\nT:\t{x}\n')
    print(f're:\t{r1}')
    print(f'my:\t{r2}')

    if (r1 is None and r2 is None or r1 and r1.group(0) == r2):
        print("\x1B[42mEQUAL\x1B[0m") 
    else:
        print("\x1B[41mFAIL\x1B[0m")