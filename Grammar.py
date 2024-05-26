from cmp.pycompiler import Grammar

G = Grammar()

Program = G.NonTerminal('Program', True)
DeclList, Decl, Stat, Expr, SimpleExpr = G.NonTerminals('DeclList Decl Stat Expr SimpleExpr')
ArithExpr, Disj, Conj, Neg, DynTest, Comp, NumExpr, Term, Factor, Sign, Atom = G.NonTerminals('ArithExpr Disj Conj Neg DynTest Comp NumExpr Term Factor Sign Atom')
ExprBlock, StatList, ExprList, ExprTail, AssignList, VarDecl, ElifBranch = G.NonTerminals('ExprBlock StatList ExprList ExprTail AssignList VarDecl ElifBranch')
FuncDecl, Body, ArgList, ArgTail, TypeDecl, FeatureList = G.NonTerminals('FuncDecl Body ArgList ArgTail TypeDecl FeatureList')
ProtDecl, ProtMethods, FullyTypedArgs, FullyTypedTail, TypeList = G.NonTerminals('ProtDecl ProtMethods FullyTypedArgs FullyTypedTail TypeList')

num, str, bool, const, id, type_id = G.Terminals('num str bool const id type_id')
leT, iN, iF, eliF, elsE, whilE, foR, aS, iS, neW = G.Terminals('let in if elif else while for as is new')
function, type, inherits, protocol, extends = G.Terminals('function type inherits protocol extends')
plus, minus, star, div, mod, pow, starstar = G.Terminals('+ - * / % ^ **')
eq, coloneq, eqeq, noteq, less, greater, leq, geq = G.Terminals('= := == != < > <= >=')
anD, oR, noT, oror = G.Terminals('& | ! ||')
dot, comma, colon, semi, at, atat, arrow = G.Terminals('. , : ; @ @@ =>')
opar, cpar, obrack, cbrack, obrace, cbrace = G.Terminals('( ) [ ] { }')


Program %= DeclList + Stat, lambda ctx: ctx.NonTerminal(1).propagate_attributes(ctx[2])

DeclList %= Decl + DeclList, lambda ctx: ctx.NonTerminal(1).merge_with(ctx[2])
DeclList %= G.Epsilon, lambda ctx: []

Decl %= FuncDecl, lambda ctx: ctx[1]
Decl %= TypeDecl, lambda ctx: ctx[1]
Decl %= ProtDecl, lambda ctx: ctx[1]

Stat %= SimpleExpr + semi, lambda ctx: ctx[1]
Stat %= ExprBlock, lambda ctx: ctx[1]
Stat %= ExprBlock + semi, lambda ctx: ctx[1]

Expr %= SimpleExpr, lambda ctx: ctx[1]
Expr %= ExprBlock, lambda ctx: ctx[1]

SimpleExpr %= leT + AssignList + iN + SimpleExpr, lambda ctx: ctx[1].assign(ctx[2], ctx[4])
SimpleExpr %= iF + opar + Expr + cpar + Expr + ElifBranch + elsE + SimpleExpr, lambda ctx: ctx[1].conditional(ctx[3], ctx[5], ctx[6], ctx[8])
SimpleExpr %= whilE + opar + Expr + cpar + SimpleExpr, lambda ctx: ctx[1].loop(ctx[3], ctx[5])
SimpleExpr %= foR + opar + id + iN + Expr + cpar + SimpleExpr, lambda ctx: ctx[1].loop(ctx[3], ctx[5], ctx[7])
SimpleExpr %= id + coloneq + SimpleExpr, lambda ctx: ctx[1].assign(ctx[3])
SimpleExpr %= id + dot + id + coloneq + SimpleExpr, lambda ctx: ctx[1].attribute_assign(ctx[3], ctx[5])
SimpleExpr %= ArithExpr, lambda ctx: ctx[1]

ExprBlock %= obrace + StatList + cbrace, lambda ctx: ctx[2]
ExprBlock %= leT + AssignList + iN + ExprBlock, lambda ctx: ctx[1].assign_block(ctx[2], ctx[4])
ExprBlock %= iF + opar + Expr + cpar + Expr + ElifBranch + elsE + ExprBlock, lambda ctx: IfElseBlock(ctx[3], ctx[5], ctx[7], ctx[8])
ExprBlock %= whilE + opar + Expr + cpar + ExprBlock, lambda ctx: ctx[1].while_loop(ctx[3], ctx[5])
ExprBlock %= foR + opar + id + iN + Expr + cpar + ExprBlock, lambda ctx: ctx[1].for_loop(ctx[3], ctx[5], ctx[7])
ExprBlock %= id + coloneq + ExprBlock, lambda ctx: ctx[1].assign(ctx[3])
ExprBlock %= id + dot + id + coloneq + ExprBlock, lambda ctx: ctx[1].attribute_assign(ctx[3], ctx[5])

StatList %= Stat + StatList, lambda ctx: [ctx[1]] + ctx[2]
StatList %= G.Epsilon, lambda ctx: []

ExprList %= Expr + ExprTail, lambda ctx: [ctx[1]] + ctx[2]
ExprList %= G.Epsilon, lambda ctx: []

ExprTail %= comma + Expr + ExprTail, lambda ctx: [ctx[2]] + ctx[3]
ExprTail %= G.Epsilon, lambda ctx: []

AssignList %= VarDecl + eq + Expr, lambda ctx: [ctx[1].assign(ctx[3])]
AssignList %= VarDecl + eq + Expr + comma + AssignList, lambda ctx: [ctx[1].assign(ctx[3])] + ctx[5]

VarDecl %= id, lambda ctx: VariableDeclaration(ctx[1])
VarDecl %= id + colon + type_id, lambda ctx: TypedVariableDeclaration(ctx[1], ctx[3])

ElifBranch %= eliF + opar + Expr + cpar + Expr + ElifBranch, lambda ctx: [ctx[1].elif_clause(ctx[3], ctx[5])] + ctx[6]
ElifBranch %= G.Epsilon, lambda ctx: []

FuncDecl %= function + id + opar + ArgList + cpar + Body, lambda ctx: FunctionDeclaration(ctx[2], ctx[4], ctx[6])
FuncDecl %= function + id + opar + ArgList + cpar + colon + type_id + Body, lambda ctx: TypedFunctionDeclaration(ctx[2], ctx[4], ctx[7], ctx[8])

Body %= arrow + Stat, lambda ctx: ctx[2]
Body %= obrace + StatList + cbrace, lambda ctx: ctx[2]

ArgList %= VarDecl + ArgTail, lambda ctx: [ctx[1]] + ctx[2]
ArgList %= G.Epsilon, lambda ctx: []

ArgTail %= comma + VarDecl + ArgTail, lambda ctx: [ctx[2]] + ctx[3]
ArgTail %= G.Epsilon, lambda ctx: []

TypeDecl %= type + type_id + obrace + FeatureList + cbrace, lambda ctx: TypeDeclaration(ctx[2], ctx[4])
TypeDecl %= type + type_id + opar + ArgList + cpar + obrace + FeatureList + cbrace, lambda ctx: FunctionTypeDeclaration(ctx[2], ctx[4], ctx[7])
TypeDecl %= type + type_id + inherits + type_id + obrace + FeatureList + cbrace, lambda ctx: InheritedTypeDeclaration(ctx[2], ctx[6], ctx[4])
TypeDecl %= type + type_id + opar + ArgList + cpar + inherits + type_id + opar + ExprList + cpar + obrace + FeatureList + cbrace, lambda ctx: ComplexTypeDeclaration(ctx[2], ctx[4], ctx[7], ctx[9], ctx[12])

FeatureList %= VarDecl + eq + Stat + FeatureList, lambda ctx: [ctx[1].initialize(ctx[3])] + ctx[4]
FeatureList %= id + opar + ArgList + cpar + Body + FeatureList, lambda ctx: [ctx[1].method(ctx[3], ctx[5])] + ctx[6]
FeatureList %= id + opar + ArgList + cpar + colon + type_id + Body + FeatureList, lambda ctx: [ctx[1].typed_method(ctx[3], ctx[6], ctx[7])] + ctx[8]
FeatureList %= G.Epsilon, lambda ctx: []

ProtDecl %= protocol + type_id + obrace + ProtMethods + cbrace, lambda ctx: ProtocolDeclaration(ctx[2], ctx[4])
ProtDecl %= protocol + type_id + extends + TypeList + obrace + ProtMethods + cbrace, lambda ctx: ExtendedProtocolDeclaration(ctx[2], ctx[4], ctx[6])

ProtMethods %= id + opar + FullyTypedArgs + cpar + colon + type_id + semi + ProtMethods, lambda ctx: [ctx[1].define_method(ctx[3], ctx[6])] + ctx[8]
ProtMethods %= G.Epsilon, lambda ctx: []

FullyTypedArgs %= id + colon + type_id + FullyTypedTail, lambda ctx: [TypedParameter(ctx[1], ctx[3])] + ctx[4]
FullyTypedArgs %= G.Epsilon, lambda ctx: []

FullyTypedTail %= comma + id + colon + type_id + FullyTypedTail, lambda ctx: [TypedParameter(ctx[2], ctx[4])] + ctx[5]
FullyTypedTail %= G.Epsilon, lambda ctx: []

TypeList %= type_id + (comma + TypeList | G.Epsilon), lambda ctx: [ctx[1]] + (ctx[2] if len(ctx) > 2 else [])
