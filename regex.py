def check():

    pat = "blud(e|a)*(0|1|2)"

    x = [i for i in "bludeaaaa0"]

    groups = list(filter(lambda x: not (len(x) == 1 and x[0] == ''),[i.split("|") for i in pat.replace(")","(").split("(")]))
    print(groups)
    for i in range(len(groups)):
        if len(x) == 0 and i < len(groups):
            return False
        elif len(x) == 0:
            break
        
        char = x.pop(0)
        g = groups[i]
        if "".join(g) == '*':
            g = groups[i-1]
            while len(x) and char in g:
                char = x.pop(0)
            
            if char not in g:
                x.insert(0,char)
                
            continue
        elif len(g) == 1 and len(g[0]) > 1:
            # constant
            while len(char) < len(g[0]):
                char += x.pop(0)
                
            if char != g[0]:
                return False
        
        if char not in g:
            print(char,g)
            return False
            
    return len(x) == 0

print(check())