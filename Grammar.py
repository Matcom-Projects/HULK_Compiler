from cmp.pycompiler import Grammar
from ParserLR1.Parser_LR1 import LR1Parser
from hulk_ast.ast_nodes import *

G = Grammar()

program = G.NonTerminal('program', startSymbol=True)

decl_list, decl, func_decl, type_decl, prot_decl = G.NonTerminals('decl_list decl func_decl type_decl prot_decl')
stat, expr, simple_expr, expr_block, stat_list, elif_branch = G.NonTerminals('stat expr simple_expr expr_block stat_list elif_branch')
arith_expr, disj, conj, neg, dyn_test, comp, num_expr, term, factorx, sign, atom = G.NonTerminals('arith_expr disj conj neg dyn_test comp num_expr term factorx sign atom')
expr_list, expr_tail, assign_list, var_decl, arg_list, arg_tail, feature_list, prot_methods, fully_type_args, fully_type_tail, type_list, body = G.NonTerminals('expr_list expr_tail assign_list var_decl arg_list arg_tail feature_list prot_methods fully_type_args fully_type_tail type_list body')

num, strx, boolx, const, idx, type_idx = G.Terminals('num str bool const id type_id')
letx, inx, ifx, elifx, elsex, whilex, forx, asx, isx, newx, function, typex, inherits, protocol, extends = G.Terminals('let in if elif else while for as is new function type inherits protocol extends')
plus, minus, star, div, mod, powx, starstar, eq, coloneq, eqeq, noteq, less, greater, leq, geq, andx, orx, notx, orxorx = G.Terminals('+ - * / % ^ ** = := == != < > <= >= & | ! ||')
dot, comma, colon, at, atat, arrow, opar, cpar, obrack, cbrack, obrace, cbrace, semi = G.Terminals('. , : @ @@ => ( ) [ ] { } ;')


program %= decl_list + stat, lambda h,s: ProgramNode(s[1], s[2])

# Declarations
decl_list %= decl + decl_list, lambda h,s: [s[1]] + s[2]
decl_list %= G.Epsilon, lambda h,s: []

decl %= func_decl, lambda h,s: s[1]
decl %= type_decl, lambda h,s: s[1]
decl %= prot_decl, lambda h,s: s[1]

# Statments
stat_list %= stat, lambda h,s: [s[1]]
stat_list %= stat + stat_list, lambda h,s: [s[1]] + s[2]

stat %= simple_expr + semi, lambda h,s: s[1]
stat %= expr_block, lambda h,s: s[1]
stat %= expr_block + semi, lambda h,s: s[1]

# Assigments
assign_list %= var_decl + eq + expr, lambda h,s: [AssignNode(s[1], s[3])]
assign_list %= var_decl + eq + expr + comma + assign_list, lambda h,s: [AssignNode(s[1], s[3])] + s[5]

var_decl %= idx, lambda h,s: VarDefNode(s[1])
var_decl %= idx + colon + type_idx, lambda h,s: VarDefNode(s[1], s[3])

# Expressions
expr %= simple_expr, lambda h,s: s[1]
expr %= expr_block, lambda h,s: s[1]

# Arithmetic expression
arith_expr %= disj, lambda h,s: s[1]
arith_expr %= arith_expr + at + disj, lambda h,s: ConcatNode(s[1], s[3])
arith_expr %= arith_expr + atat + disj, lambda h,s: ConcatWithSpaceNode(s[1], s[3])

disj %= conj, lambda h,s: s[1]
disj %= disj + orx + conj, lambda h,s: OrNode(s[1], s[3])

conj %= neg, lambda h,s: s[1]
conj %= conj + andx + neg, lambda h,s: AndNode(s[1], s[3])

neg %= dyn_test, lambda h,s: s[1]
neg %= notx + dyn_test, lambda h,s: NotNode(s[2])

dyn_test %= comp, lambda h,s: s[1]
dyn_test %= comp + isx + type_idx, lambda h,s: DynTestNode(s[1], s[3])

comp %= num_expr, lambda h,s: s[1]
comp %= num_expr + eqeq + num_expr, lambda h,s: EqualNode(s[1], s[3])
comp %= num_expr + noteq + num_expr, lambda h,s: NotEqualNode(s[1], s[3])
comp %= num_expr + less + num_expr, lambda h,s: LessNode(s[1], s[3])
comp %= num_expr + greater + num_expr, lambda h,s: GreaterNode(s[1], s[3])
comp %= num_expr + leq + num_expr, lambda h,s: LeqNode(s[1], s[3])
comp %= num_expr + geq + num_expr, lambda h,s: GeqNode(s[1], s[3])

num_expr %= term, lambda h,s: s[1]
num_expr %= num_expr + plus + term, lambda h,s: PlusNode(s[1], s[3])
num_expr %= num_expr + minus + term, lambda h,s: MinusNode(s[1], s[3])

term %= factorx, lambda h,s: s[1]
term %= term + star + factorx, lambda h,s: StarNode(s[1], s[3])
term %= term + div + factorx, lambda h,s: DivNode(s[1], s[3])
term %= term + mod + factorx, lambda h,s: ModNode(s[1], s[3])

factorx %= sign, lambda h,s: s[1]
factorx %= sign + powx + factorx, lambda h,s: PowNode(s[1], s[3])
factorx %= sign + starstar + factorx, lambda h,s: PowNode(s[1], s[3])

sign %= atom, lambda h,s: s[1]
sign %= minus + atom, lambda h,s: NegNode(s[2])

simple_expr %= letx + assign_list + inx + simple_expr, lambda h,s: LetNode(s[2], s[4])
simple_expr %= ifx + opar + expr + cpar + expr + elif_branch + elsex + simple_expr, lambda h,s: IfNode(s[3], s[5], s[6], s[8])
simple_expr %= whilex + opar + expr + cpar + simple_expr, lambda h,s: WhileNode(s[3], s[5])
simple_expr %= forx + opar + idx + inx + expr + cpar + simple_expr, lambda h,s: ForNode(s[3], s[5], s[7])
simple_expr %= idx + coloneq + simple_expr, lambda h,s: DestrAssign(s[1], s[3])
simple_expr %= idx + dot + idx + coloneq + simple_expr, lambda h,s: DestrAssign(s[3], s[5], True)
simple_expr %= arith_expr, lambda h,s: s[1]

expr_block %= obrace + stat_list + cbrace, lambda h,s: ExprBlockNode(s[2])
expr_block %= letx + assign_list + inx + expr_block, lambda h,s: LetNode(s[2], s[4])
expr_block %= ifx + opar + expr + cpar + expr + elif_branch + elsex + expr_block, lambda h,s: IfNode(s[3], s[5], s[6], s[8])
expr_block %= whilex + opar + expr + cpar + expr_block, lambda h,s: WhileNode(s[3], s[5])
expr_block %= forx + opar + idx + inx + expr + cpar + expr_block, lambda h,s: ForNode(s[3], s[5], s[7])
expr_block %= idx + coloneq + expr_block, lambda h,s: DestrAssign(s[1], s[3])
expr_block %= idx + dot + idx + coloneq + expr_block, lambda h,s: DestrAssign(s[3], s[5], True)

expr_list %= expr + expr_tail, lambda h,s: [s[1]] + s[2]
expr_list %= G.Epsilon, lambda h,s: []

expr_tail %= comma + expr + expr_tail, lambda h,s: [s[2]] + s[3]
expr_tail %= G.Epsilon, lambda h,s: []

# Functions
func_decl %= function + idx + opar + arg_list + cpar + body, lambda h,s: FuncDeclNode(s[2], s[4], s[6])
func_decl %= function + idx + opar + arg_list + cpar + colon + type_idx + body, lambda h,s: FuncDeclNode(s[2], s[4], s[8], s[7])

body %= arrow + stat, lambda h,s: s[2]
body %= obrace + stat_list + cbrace, lambda h,s: s[2]

arg_list %= var_decl + arg_tail, lambda h,s: [s[1]] + s[2]
arg_list %= G.Epsilon, lambda h,s: []

arg_tail %= comma + var_decl + arg_tail, lambda h,s: [s[2]] + s[3]
arg_tail %= G.Epsilon, lambda h,s: []

# Literals and Variables
atom %= num, lambda h,s: LiteralNumNode(s[1])
atom %= strx, lambda h,s: LiteralStrNode(s[1])
atom %= boolx, lambda h,s: LiteralBoolNode(s[1])
atom %= const, lambda h,s: ConstantNode(s[1])
atom %= idx, lambda h,s: VarNode(s[1])

# Conditionals
elif_branch %= elifx + opar + expr + cpar + expr + elif_branch, lambda h,s: [(s[3], s[5])] + s[6]
elif_branch %= G.Epsilon, lambda h,s: []

# Types
type_decl %= typex + type_idx + obrace + feature_list + cbrace, lambda h,s: TypeDeclNode(s[2], s[4])
type_decl %= typex + type_idx + opar + arg_list + cpar + obrace + feature_list + cbrace, lambda h,s: TypeDeclNode(s[2], s[7], s[4])
type_decl %= typex + type_idx + inherits + type_idx + obrace + feature_list + cbrace, lambda h,s: TypeDeclNode(s[2], s[6], None, s[4])
type_decl %= typex + type_idx + opar + arg_list + cpar + inherits + type_idx + opar + expr_list + cpar + obrace + feature_list + cbrace, lambda h,s: TypeDeclNode(s[2], s[12], s[4], s[7], s[9])

feature_list %= var_decl + eq + stat + feature_list, lambda h,s: [AssignNode(s[1], s[3])] + s[4]
feature_list %= idx + opar + arg_list + cpar + body + feature_list, lambda h,s: [MethodNode(s[1], s[3], s[5])] + s[6]
feature_list %= idx + opar + arg_list + cpar + colon + type_idx + body + feature_list, lambda h,s: [MethodNode(s[1], s[3], s[7], s[6])] + s[8]
feature_list %= G.Epsilon, lambda h,s: []

fully_type_args %= idx + colon + type_idx + fully_type_tail, lambda h,s: [VarDefNode(s[1], s[3])] + s[4]
fully_type_args %= G.Epsilon, lambda h,s: []

fully_type_tail %= comma + idx + colon + type_idx + fully_type_tail, lambda h,s: [VarDefNode(s[2], s[4])] + s[5]
fully_type_tail %= G.Epsilon, lambda h,s: []

type_list %= type_idx, lambda h,s: [s[1]]
type_list %= type_idx + comma + type_list, lambda h,s: [s[1]] + s[3]

# Protocols
prot_decl %= protocol + type_idx + obrace + prot_methods + cbrace, lambda h,s: ProtDeclNode(s[2], s[4])
prot_decl %= protocol + type_idx + extends + type_list + obrace + prot_methods + cbrace, lambda h,s: ProtDeclNode(s[2], s[6], s[4])

prot_methods %= idx + opar + fully_type_args + cpar + colon + type_idx + semi + prot_methods, lambda h,s: [ProtMethodNode(s[1], s[3], s[6])] + s[8]
prot_methods %= G.Epsilon, lambda h,s: []

# Vectors
atom %= obrack + expr_list + cbrack, lambda h,s: VectorNode(s[2])
atom %= obrack + expr + orxorx + idx + inx + expr + cbrack, lambda h,s: ImplicitVector(s[2], s[4], s[6])
atom %= opar + expr + cpar, lambda h,s: s[2]
atom %= newx + type_idx + opar + expr_list + cpar, lambda h,s: InstantiateNode(s[2], s[4])
atom %= idx + opar + expr_list + cpar, lambda h,s: FuncCallNode(s[1], s[3])
atom %= atom + asx + type_idx, lambda h,s: DowncastNode(s[1], s[3])
atom %= atom + obrack + expr + cbrack, lambda h,s: IndexingNode(s[1], s[3])
atom %= idx + dot + idx + opar + expr_list + cpar, lambda h,s: MethodCallNode(s[1], s[3], s[5])
atom %= idx + dot + idx, lambda h,s: AttrrCallNode(s[1], s[3])
