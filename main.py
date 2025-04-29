def tokenize(pattern):
    l = []
    for c in pattern:
        if c == '+':
            l.append(('PLUS', '+'))
        elif c == '*':
            l.append(('STAR','*'))
        elif c == '|':
            l.append(('ALT', '|'))
        elif c == '?':
            l.append(('QMARK', '?'))
        elif c.isalnum():
            l.append(('CHAR', c))
        elif c == "(":
            l.append(('LPAREN', '('))
        elif c == ")":
            l.append(('RPAREN', ')'))
    l.append(('END', ''))
    return l
class Node:
    pass
class Char(Node):
    def __init__(self, c):
        self.c = c
class Alt(Node):
    def __init__(self, left, right):
        self.left, self.right = left, right
class Star(Node):
    def __init__(self, expr):
        self.expr = expr
class Plus(Node):
    def __init__(self, expr):
        self.expr = expr
class QMark(Node):
    def __init__(self, expr):
        self.expr = expr
class Concat(Node):
    def __init__(self, left, right):
        self.left, self.right = left, right
def fold_concatenation(atoms):
    node = atoms[0]
    for n in atoms[1:]:
        node = Concat(node, n)
    return node
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    def peek(self):
        return self.tokens[self.pos][0]
    def eat(self, kind=None):
        t = self.tokens[self.pos]
        if kind and t[0] != kind:
            raise SyntaxError(t[0])
        self.pos += 1
        return t
    def parse(self):
        node = self.parse_alt()
        if self.peek() != 'END':
            raise SyntaxError("Extrainput")
        return node
    def parse_alt(self):
        node = self.parse_concat()
        while self.peek() == 'ALT':
            self.eat("ALT")
            right = self.parse_concat()
            node = Alt(node, right)
        return node
    def parse_concat(self):
        atoms = []
        while self.peek() in ('CHAR', 'DOT', 'LPAREN'):
            atoms.append(self.parse_repeat())
        if not atoms:
            raise SyntaxError("expected atom")
        return fold_concatenation(atoms)
    def parse_repeat (self):
        node = self.parse_atom()
        while self.peek() in ('STAR', 'PLUS', 'QMARK'):
            kind, val = self.eat()
            if kind == 'STAR':
                node = Star(node)
            elif kind == 'PLUS':
                node = Plus(node)
            else:
                node = QMark(node)
        return node
    def parse_atom(self):
        t = self.peek()
        if t == 'CHAR':
            _, c = self.eat('CHAR')
            return Char(c)
        if t == 'DOT':
            self.eat('DOT')
            return Char('.')
        if t == 'LPAREN':
            self.eat('LPAREN')
            node = self.parse_alt()
            self.eat('RPAREN')
            return node
        raise SyntaxError("Unexpected {t}")

WILDCARD = object()
class State:
    def __init__(self): self.edges=[]
    def add(self, s, st): self.edges.append((s,st))
def compile_node (n):
    if isinstance(n, Char):
        s, e = State(), State()
        s.add (n.c, e)
        return s, e
    if isinstance(n, Alt):
        s, e = State(), State()
        s1, e1 = compile_node(n.left)
        s2, e2 = compile_node(n.right)
        s.add(None, s1)
        s.add(None, s2)
        e1.add(None, e)
        e2.add(None, e)
        return s, e
    if isinstance(n,Concat):
        s1,e1=compile_node(n.left); s2,e2=compile_node(n.right)
        e1.add(None,s2); return s1,e2
    if isinstance(n,Star):
        s,e=State(),State(); s1,e1=compile_node(n.expr)
        s.add(None,s1); s.add(None,e)
        e1.add(None,s1); e1.add(None,e)
        return s,e
    if isinstance(n,Plus):
        s1,e1=compile_node(n.expr); s2,e2=compile_node(Star(n.expr))
        e1.add(None,s2); return s1,e2
    if isinstance(n,QMark):
        s,e=State(),State(); s1,e1=compile_node(n.expr)
        s.add(None,s1); s.add(None,e); e1.add(None,e)
        return s,e
    raise ValueError("Bad node")
def nfa_to_dfa(nfa_start, nfa_end):
    def epsilon_closure(states):
        if not isinstance(states, set):
            states = {states}
        
        closure = set(states)
        stack = list(states)
        
        while stack:
            state = stack.pop()
            for symbol, next_state in state.edges:
                if symbol is None and next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        
        return frozenset(closure)
    alphabet = set()
    all_states = set()
    states_to_process = [nfa_start]
    
    while states_to_process:
        state = states_to_process.pop()
        if state in all_states:
            continue
        all_states.add(state)
        
        for symbol, next_state in state.edges:
            if symbol is not None:
                alphabet.add(symbol)
            if next_state not in all_states:
                states_to_process.append(next_state)
    
    dfa_states_map = {}
    
    start_closure = epsilon_closure(nfa_start)
    dfa_start = State()
    dfa_states_map[start_closure] = dfa_start
    
    unprocessed = [start_closure]
    processed = set()
    
    while unprocessed:
        current_closure = unprocessed.pop(0)
        processed.add(current_closure)
        current_dfa = dfa_states_map[current_closure]
        
        for symbol in alphabet:
            next_states = set()
            for nfa_state in current_closure:
                for edge_symbol, next_nfa_state in nfa_state.edges:
                    if edge_symbol == symbol:
                        next_states.add(next_nfa_state)
            
            if next_states:
                next_closure = epsilon_closure(next_states)
                
                if next_closure not in dfa_states_map:
                    dfa_states_map[next_closure] = State()
                    
                    if next_closure not in processed:
                        unprocessed.append(next_closure)
                
                current_dfa.add(symbol, dfa_states_map[next_closure])
    
    accepting_states = set()
    for nfa_set, dfa_state in dfa_states_map.items():
        if nfa_end in nfa_set:
            accepting_states.add(dfa_state)
    
    return dfa_start, accepting_states
def compile_regex_to_dfa(pattern):
    tokens = tokenize(pattern)
    parser = Parser(tokens)
    ast = parser.parse()
    nfa_start, nfa_end = compile_node(ast)
    dfa_start, accepting_states = nfa_to_dfa(nfa_start, nfa_end)
    return dfa_start, accepting_states
def match_with_dfa(dfa_start, accepting_states, input_string):
    current = dfa_start
    
    for char in input_string:
        next_state = None
        for symbol, state in current.edges:
            if symbol == char:
                next_state = state
                break
        
        if next_state is None:
            return False
        
        current = next_state
    
    return current in accepting_states
test_failed = 0
def test_regex(pattern, test_cases):
    print(f"\nTesting pattern: '{pattern}'")
    dfa_start, accepting_states = compile_regex_to_dfa(pattern)   
    all_passed = True
    for string, expected in test_cases:
        result = match_with_dfa(dfa_start, accepting_states, string)
        passed = result == expected
        status = "+" if passed else "-"
        print(f"  {status} '{string}': {'Matched' if result else 'Not matched'} (Expected: {expected})")
        if not passed:
            all_passed = False
    if all_passed:
        print ("All tests passed!")
    else:
        print("Some tests failed!")
        test_failed += 1
import json

def run_tests():
    try:
        with open("tests.json", "r") as f:
            test_cases_json = json.load(f)
        
        print(f"Loaded {len(test_cases_json)} test cases from tests.json")
        for test_case in test_cases_json:
            name = test_case["name"]
            pattern = test_case["regex"]
            cases = [(ts["input"], ts["expected"]) for ts in test_case["test_strings"]]
            
            print(f"\nTesting {name}: '{pattern}'")
            test_regex(pattern, cases)
        if test_failed == 0:
            print ("Everything is fine!")
        else:
            print(f"{test_failed} test failed.")
    except FileNotFoundError:
        print("Error: tests.json file not found")
    except json.JSONDecodeError:
        print("Error: tests.json contains invalid JSON")
    except Exception as e:
        print(f"Unexpected error: {e}")
if __name__ == "__main__":
    run_tests()