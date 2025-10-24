cache = {}

class Stanje():
    def __init__(self, prijelaz: dict,accept: bool = False):
        self.prijelazi: dict = prijelaz
        self.accept: bool = accept
        self.index = None
    
    def __repr__(self):
        return f'{self.index}'
    
    def __str__(self):

        if self.accept:
            return f"{self.index} Accept"

        return f'{self.index} {self.prijelazi}'

class Automat():
    def __init__(self):
        self.start: Stanje
        self.indexed: bool = False
        self.node_list: list[Stanje] = []

    def _automat_dfs(self, node: Stanje):
        if node in self.node_list:
            return

        self.node_list.append(node)

        if node.accept:
            return

        for key in node.prijelazi:
            next = node.prijelazi[key]
            
            for n in next:
                self._automat_dfs(n)

    def traverse_automat(self) -> list[Stanje]:
        self.node_list = []

        self._automat_dfs(self.start)
        return self.node_list
    
    def get_accept_state(self) -> Stanje:
        nodes = self.traverse_automat()

        for node in nodes:
            if node.accept:
                return node
        
        print("Accept node not found!")
        return None

    def add_indexes(self):
        if self.indexed:
            return

        for i, node in enumerate(self.traverse_automat()):
            node.index = i

    def concat(self, other: "Automat") -> "Automat":
        # create new start node
        start = Stanje({"$":[self.start]})
        # create new end node
        end = Stanje({},True)
        # connect with middle
        last = self.get_accept_state()
        last.accept = False
        middle = Stanje({"$": [other.start]})
        last.prijelazi["$"] = [middle]

        # connect to end node
        last = other.get_accept_state()
        last.accept = False
        last.prijelazi["$"] = [end]

        # connect start node
        self.start = start

        return self


    def union(self, other: "Automat") -> "Automat":
        # create new start node
        start = Stanje({"$":[self.start,other.start]})
        # create new end node
        end = Stanje({},True)

        a_last = self.get_accept_state()
        b_last = other.get_accept_state()

        a_last.prijelazi["$"] = [end]
        b_last.prijelazi["$"] = [end]
        a_last.accept = False
        b_last.accept = False

        self.start = start

        return self

    def kleen(self) -> "Automat":
        # create new start node
        start = Stanje({"$":[self.start]})
        # create new end node
        end = Stanje({"$":[start]},True)

        last = self.get_accept_state()
        last.accept = False
        last.prijelazi["$"] = [start,end]

        start.prijelazi["$"].append(end) # might be wrong, but needed (double link)
        self.start = start

        return self

    def __str__(self):
        r = []
        self.add_indexes()
        for node in self.node_list:
            r.append(f'{node}')
        
        return "\n".join(r)

class Compiled_Automat():
    def __init__(self, a: Automat):
        self.stanja = []
        self.simboli = []
        self.accept = []
        self.start = None
        self.prelazi = {}

        a.add_indexes()
        self.start = a.start.index

        for node in a.node_list:
            self.stanja.append(node.index)

            if node.accept:
                self.accept.append(node.index)

            if node.index not in self.prelazi:
                self.prelazi[node.index] = {}

            for symb in node.prijelazi:

                if symb not in self.prelazi[node.index]:
                    self.prelazi[node.index][symb] = []

                for next_node in node.prijelazi[symb]:
                    self.prelazi[node.index][symb].append(next_node.index)

                if symb == "$":
                    continue

                if symb not in self.simboli:
                    self.simboli.append(symb)

    def __str__(self):
        r = f"""{",".join(map(str,self.stanja))}\n{",".join(map(str,self.simboli))}\n{",".join(map(str,self.accept))}\n{self.start}\n"""
        
        d = []
        for state in self.prelazi:
            for symb in self.prelazi[state]:
                d.append(f'{state},{symb}->{",".join(map(str,self.prelazi[state][symb]))}')

        r += "\n".join(d)

        return r

def simple_Automat(symb: str) -> Automat:
    a = Automat()
    end = Stanje({},True)
    s1 = Stanje({symb:[end]},False)
    a.start = s1

    return a

def regex_to_postfix(regex) -> str:
    """Shunting Yard algorithm"""
    priority = {'*': 3, '.': 2, '|': 1}
    output = []
    stack = []
    prev = None

    new_regex = []
    for c in regex:
        if prev and (str(prev) not in '(|' and str(c) not in '|)*'):
            new_regex.append('.')
        new_regex.append(c)
        prev = c

    for c in new_regex:
        if c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        elif c in priority:
            while stack and stack[-1] in priority and priority[stack[-1]] >= priority[c]:
                output.append(stack.pop())
            stack.append(c)
        else:
            output.append(c)

    while stack:
        output.append(stack.pop())

    return output

def regex_to_ascii(regex: str) -> str:
    """Converts regex string to a list of ascii ints of chars, and operators, also escapes things"""
    # regex = regex.encode('utf-8').decode('unicode_escape')

    operators = "|*()$"
    magic = {
        "n": 10,
        "t": 9,
        "\\": 92
    }
    ignore = False
    r = []


    for i, c in enumerate(regex):

        next = regex[i+1] if i+1 < len(regex) else None

        if ignore and c in magic and next != "\\":
            r.append(magic[c])
            ignore = False
            continue
        elif ignore:
            r.append(ord(c))
            ignore = False
            continue

        

        if c == "\\":
            # next symbol is escaped
            ignore = True
        elif c in operators:
            r.append(c)
        else:
            r.append(ord(c))

    # print(r)

    return r

def regex_to_automat(regex: str) -> Compiled_Automat:

    if regex in cache:
        return cache[regex]

    ascii_regex = regex_to_ascii(regex)
    postfix = regex_to_postfix(ascii_regex)

    stack = [Automat]
    for c in postfix:
        if c == ".":
            b = stack.pop()
            a = stack.pop()
            stack.append(a.concat(b))
        elif c == "|":
            b = stack.pop()
            a = stack.pop()
            stack.append(a.union(b))
        elif c == "*":
            a = stack.pop()
            stack.append(a.kleen())
        else:
            stack.append(simple_Automat(c))

    a = stack.pop()
    r = Compiled_Automat(a)

    cache[regex] = r

    return r