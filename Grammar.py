from cmp.pycompiler import Symbol, NonTerminal, Terminal, Sentence, SentenceList, Epsilon, Production, Grammar, EOF

G = Grammar()

# no terminales
Program = G.NonTerminal('Program', True)
Expr = G.NonTerminal('Expr')
Term = G.NonTerminal('Term')
Factor = G.NonTerminal('Factor')
Primary = G.NonTerminal('Primary')
LetDecl = G.NonTerminal('LetDecl')
FuncDecl = G.NonTerminal('FuncDecl')
TypeDecl = G.NonTerminal('TypeDecl')
Block = G.NonTerminal('Block')
Statement = G.NonTerminal('Statement')
Assign = G.NonTerminal('Assign')
Cond = G.NonTerminal('Cond')
While = G.NonTerminal('While')
For = G.NonTerminal('For')
Params = G.NonTerminal('Params')
Args = G.NonTerminal('Args')
Type = G.NonTerminal('Type')
FuncCall = G.NonTerminal('FuncCall')
ObjectCreation = G.NonTerminal('ObjectCreation')

# terminales
plus, minus, star, div, power = G.Terminals('+ - * / ^')
number, string, true, false = G.Terminals('number string true false')
id, lpar, rpar, lbrace, rbrace = G.Terminals('id ( ) { }')
let, in_kw, assign = G.Terminals('let in :=')
if_kw, else_kw = G.Terminals('if else')
while_kw, for_kw = G.Terminals('while for')
function, type_kw, new, inherits = G.Terminals('function type new inherits')
semicolon, comma = G.Terminals('; ,')
arrow = G.Terminal('=>')

# reglas de producción
Program %= Block

Block %= Statement + Block | G.Epsilon

FuncDecl %= Sentence(function, id, lpar, Params, rpar, lbrace, Block, rbrace) | \
            Sentence(function, id, lpar, Params, rpar, arrow, Expr, semicolon)

Statement %= LetDecl | Sentence(FuncDecl) | TypeDecl | Assign | Cond | While | For | Sentence(Expr, semicolon)

LetDecl %= let + id + assign + Expr + in_kw + Block

TypeDecl %= type_kw + id + lbrace + Block + rbrace

Assign %= id + assign + Expr + semicolon

Cond %= Sentence(if_kw, lpar, Expr, rpar, Block) + (Sentence(else_kw, Block)) | Sentence(G.Epsilon)

While %= while_kw + lpar + Expr + rpar + Block

For %= for_kw + lpar + id + in_kw + Expr + rpar + Block

Expr %= (Expr + plus + Term) | (Expr + minus + Term) | Term

Term %= (Term + star + Factor) | (Term + div + Factor) | Factor

Factor %= (Primary + power + Factor) | Primary

Primary %= Sentence(number) | Sentence(string) | Sentence(true) | Sentence(false) | Sentence(id) | Sentence(lpar + Expr + rpar) | Sentence(FuncCall) | Sentence(ObjectCreation)

FuncCall %= id + lpar + Args + rpar

ObjectCreation %= new + id + lpar + Args + rpar

Params %= id + comma + Params | id | G.Epsilon

Args %= Expr + comma + Args | Expr | G.Epsilon


print(G)
