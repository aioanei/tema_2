# Parser și Evaluator de Expresii Regulate

Acest proiect implementează un parser și evaluator de expresii regulate (regex) în Python, construit de la zero. Compilează expresiile regulate într-un automat finit determinist (DFA) prin intermediul unui automat finit nedeterminist (NFA), apoi utilizează DFA pentru a verifica șirurile.

## Caracteristici

- Analizează expresii regulate și le transformă într-un arbore sintactic abstract (AST)
- Suportă diverși operatori regex:
  - `.` (punct): Potrivește orice caracter
  - `*` (asterisc): Potrivește zero sau mai multe apariții
  - `+` (plus): Potrivește una sau mai multe apariții
  - `?` (semnul întrebării): Potrivește zero sau o apariție
  - `|` (alternativă): Potrivește fie expresia din stânga, fie cea din dreapta
  - Concatenare: Operație implicită între caractere
  - Paranteze pentru grupare
- Convertește AST în NFA
- Transformă NFA în DFA pentru o evaluare eficientă
- Include un cadru de testare pentru validarea expresiilor regulate

## Detalii de Implementare

Implementarea urmărește următorii pași:

1. **Tokenizare**: Șirul regex de intrare este împărțit în token-uri.
2. **Parsare**: Un parser recursiv descendant construiește un arbore sintactic abstract (AST).
3. **Construcția NFA**: AST-ul este convertit într-un automat finit nedeterminist.
4. **Conversia la DFA**: NFA este transformat într-un automat finit determinist pentru o evaluare eficientă.
5. **Verificarea șirurilor**: DFA este utilizat pentru a determina dacă un șir de intrare se potrivește cu modelul regex.

## Cum se utilizează

```python
from main import compile_regex_to_dfa, match_with_dfa

# Compilarea unei expresii regulate în DFA
dfa_start, accepting_states = compile_regex_to_dfa("a(b|c)*")

# Verificarea unui șir cu DFA
result = match_with_dfa(dfa_start, accepting_states, "abcbc")
print(f"Rezultatul potrivirii: {result}")  # True sau False
```

## Testare

Proiectul include un sistem de testare care citește cazuri de test dintr-un fișier `tests.json`. Fiecare caz de test include:
- Un nume
- Un model regex
- O listă de șiruri de testat, fiecare cu un rezultat așteptat

Exemplu de format pentru `tests.json`:

```json
[
  {
    "name": "Alternare Simplă",
    "regex": "a|b",
    "test_strings": [
      {"input": "a", "expected": true},
      {"input": "b", "expected": true},
      {"input": "c", "expected": false}
    ]
  }
]
```

Pentru a rula testele:

```bash
python main.py
```

Acest lucru va executa toate cazurile de test și va raporta dacă acestea au trecut sau nu.

Să luăm expresia regulată simplă: a(b|c)*d

Când compile_node procesează această expresie:

Se creează un NFA pentru litera a
Se creează un NFA pentru expresia (b|c)*
Se creează un NFA pentru litera d
Acestea sunt concatenate
Structura NFA-ului ar arăta astfel:

s_inițială ---a---> s1 ---ε---> s2 --ε--> s3 ---b---> s4 --ε--> s6
                               |              |                  |
                               |              v                  v
                               |             s5 ---c---> s6 --ε--> s7 --d--> s_finală
                               |              ^         |
                               |              |         |
                               +--ε-----------+--ε------+