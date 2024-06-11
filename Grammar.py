from cmp.pycompiler import Grammar

G = Grammar()
Program = G.NonTerminal('Program', True)

DeclarationList, Declaration, Statement, Expression, SimpleExpression = G.NonTerminals('DeclarationList Declaration Statement Expression SimpleExpression')
ArithmeticExpression, Disjunction, Conjunction, Negation, DynamicTest, Comparison, NumericExpression, Term, Factor, Sign, Atom = G.NonTerminals('ArithmeticExpression Disjunction Conjunction Negation DynamicTest Comparison NumericExpression Term Factor Sign Atom')
ExpressionBlock, StatementList, ExpressionList, ExpressionTail, AssignmentList, VariableDeclaration, ElseIfBranch = G.NonTerminals('ExpressionBlock StatementList ExpressionList ExpressionTail AssignmentList VariableDeclaration ElseIfBranch')
FunctionDeclaration, Body, ArgumentList, ArgumentTail, TypeDeclaration, FeatureList = G.NonTerminals('FunctionDeclaration Body ArgumentList ArgumentTail TypeDeclaration FeatureList')
ProtocolDeclaration, ProtocolMethods, FullyTypedArguments, FullyTypedTail, TypeList = G.NonTerminals('ProtocolDeclaration ProtocolMethods FullyTypedArguments FullyTypedTail TypeList')


NUMBER, STRING, BOOLEAN, CONSTANT, IDENTIFIER, TYPE_IDENTIFIER = G.Terminals('NUMBER STRING BOOLEAN CONSTANT IDENTIFIER TYPE_IDENTIFIER')
LET, IN, IF, ELIF, ELSE, WHILE, FOR, AS, IS, NEW = G.Terminals('LET IN IF ELIF ELSE WHILE FOR AS IS NEW')
FUNCTION, TYPE, INHERITS, PROTOCOL, EXTENDS = G.Terminals('FUNCTION TYPE INHERITS PROTOCOL EXTENDS')
PLUS, MINUS, STAR, DIVIDE, MODULO, POW, POWER2 = G.Terminals('+ - * / % ^ **')
EQUAL, ASSIGN, EQUALS, NOT_EQUALS, LESS_THAN, GREATER_THAN, LESS_EQUAL, GREATER_EQUAL = G.Terminals('= := == != < > <= >=')
AND, OR, NOT, OR_OR = G.Terminals('& | ! ||')
DOT, COMMA, COLON, SEMICOLON, AT, AT_AT, ARROW = G.Terminals('. , : ; @ @@ =>')
OPEN_PAREN, CLOSE_PAREN, OPEN_BRACK, CLOSE_BRACK, OPEN_BRACE, CLOSE_BRACE = G.Terminals('( ) [ ] { }')

Program %= DeclarationList + Statement, lambda h, s: createProgramNode(s[1], s[2])

DeclarationList %= Declaration + DeclarationList, lambda h, s: [s[1]] + s[2]
DeclarationList %= G.Epsilon, lambda h, s: []

Declaration %= FunctionDeclaration, lambda h, s: s[1]
Declaration %= TypeDeclaration, lambda h, s: s[1]
Declaration %= ProtocolDeclaration, lambda h, s: s[1]

Statement %= SimpleExpression + SEMICOLON, lambda h, s: s[1]
Statement %= ExpressionBlock, lambda h, s: s[1]
Statement %= ExpressionBlock + SEMICOLON, lambda h, s: s[1]

Expression %= SimpleExpression, lambda h, s: s[1]
Expression %= ExpressionBlock, lambda h, s: s[1]

SimpleExpression %= LET + AssignmentList + IN + SimpleExpression, lambda h, s: constructLet(s[2], s[4])
SimpleExpression %= IF + OPEN_PAREN + Expression + CLOSE_PAREN + Expression + ElseIfBranch + ELSE + SimpleExpression, lambda h, s: constructIf(s[3], s[5], s[6], s[8])
SimpleExpression %= WHILE + OPEN_PAREN + Expression + CLOSE_PAREN + SimpleExpression, lambda h, s: constructWhile(s[3], s[5])
SimpleExpression %= FOR + OPEN_PAREN + IDENTIFIER + IN + Expression + CLOSE_PAREN + SimpleExpression, lambda h, s: constructFor(s[3], s[5], s[7])
SimpleExpression %= IDENTIFIER + ASSIGN + SimpleExpression, lambda h, s: assignDirect(s[1], s[3])
SimpleExpression %= IDENTIFIER + DOT + IDENTIFIER + ASSIGN + SimpleExpression, lambda h, s: assignDirect(s[3], s[5], True)
SimpleExpression %= ArithmeticExpression, lambda h, s: s[1]

ExpressionBlock %= OPEN_BRACE + StatementList + CLOSE_BRACE, lambda h, s: constructExpressionBlock(s[2])
ExpressionBlock %= LET + AssignmentList + IN + ExpressionBlock, lambda h, s: constructLet(s[2], s[4])
ExpressionBlock %= IF + OPEN_PAREN + Expression + CLOSE_PAREN + Expression + ElseIfBranch + ELSE + ExpressionBlock, lambda h, s: constructIf(s[3], s[5], s[6], s[8])
ExpressionBlock %= WHILE + OPEN_PAREN + Expression + CLOSE_PAREN + ExpressionBlock, lambda h, s: constructWhile(s[3], s[5])
ExpressionBlock %= FOR + OPEN_PAREN + IDENTIFIER + IN + Expression + CLOSE_PAREN + ExpressionBlock, lambda h, s: constructFor(s[3], s[5], s[7])
ExpressionBlock %= IDENTIFIER + ASSIGN + ExpressionBlock, lambda h, s: assignDirect(s[1], s[3])
ExpressionBlock %= IDENTIFIER + DOT + IDENTIFIER + ASSIGN + ExpressionBlock, lambda h, s: assignDirect(s[3], s[5], True)

StatementList %= Statement, lambda h, s: [s[1]]
StatementList %= Statement + StatementList, lambda h, s: [s[1]] + s[2]

ExpressionList %= Expression + ExpressionTail, lambda h, s: [s[1]] + s[2]
ExpressionList %= G.Epsilon, lambda h, s: []

ExpressionTail %= COMMA + Expression + ExpressionTail, lambda h, s: [s[2]] + s[3]
ExpressionTail %= G.Epsilon, lambda h, s: []

AssignmentList %= VariableDeclaration + EQUAL + Expression, lambda h, s: [assignNode(s[1], s[3])]
AssignmentList %= VariableDeclaration + EQUAL + Expression + COMMA + AssignmentList, lambda h, s: [assignNode(s[1], s[3])] + s[5]

VariableDeclaration %= IDENTIFIER, lambda h, s: defineVariable(s[1])
VariableDeclaration %= IDENTIFIER + COLON + TYPE_IDENTIFIER, lambda h, s: defineVariable(s[1], s[3])

ElifBranch %= ELIF + OPEN_PAREN + Expression + CLOSE_PAREN + Expression + ElifBranch, lambda h, s: [(s[3], s[5])] + s[6]
ElifBranch %= G.Epsilon, lambda h, s: []

ArithmeticExpression %= Disjunction, lambda h, s: s[1]
ArithmeticExpression %= ArithmeticExpression + AT + Disjunction, lambda h, s: concatenate(s[1], s[3])
ArithmeticExpression %= ArithmeticExpression + AT_AT + Disjunction, lambda h, s: concatenateWithSpace(s[1], s[3])

Disjunction %= Conjunction, lambda h, s: s[1]
Disjunction %= Disjunction + OR + Conjunction, lambda h, s: disjunctionOr(s[1], s[3])

Conjunction %= Negation, lambda h, s: s[1]
Conjunction %= Conjunction + AND + Negation, lambda h, s: conjunctionAnd(s[1], s[3])

Negation %= DynamicTest, lambda h, s: s[1]
Negation %= NOT + DynamicTest, lambda h, s: negateCondition(s[2])

DynamicTest %= Comparison, lambda h, s: s[1]
DynamicTest %= Comparison + IS + TYPE_IDENTIFIER, lambda h, s: dynamicTypeCheck(s[1], s[3])

Comparison %= NumericExpression, lambda h, s: s[1]
Comparison %= NumericExpression + EQUALS + NumericExpression, lambda h, s: compareEqual(s[1], s[3])
Comparison %= NumericExpression + NOT_EQUALS + NumericExpression, lambda h, s: compareNotEqual(s[1], s[3])
Comparison %= NumericExpression + LESS_THAN + NumericExpression, lambda h, s: compareLessThan(s[1], s[3])
Comparison %= NumericExpression + GREATER_THAN + NumericExpression, lambda h, s: compareGreaterThan(s[1], s[3])
Comparison %= NumericExpression + LESS_EQUAL + NumericExpression, lambda h, s: compareLessEqual(s[1], s[3])
Comparison %= NumericExpression + GREATER_EQUAL + NumericExpression, lambda h, s: compareGreaterEqual(s[1], s[3])

NumericExpression %= Term, lambda h, s: s[1]
NumericExpression %= NumericExpression + PLUS + Term, lambda h, s: addition(s[1], s[3])
NumericExpression %= NumericExpression + MINUS + Term, lambda h, s: subtraction(s[1], s[3])

Term %= Factor, lambda h, s: s[1]
Term %= Term + STAR + Factor, lambda h, s: multiply(s[1], s[3])
Term %= Term + DIVIDE + Factor, lambda h, s: divide(s[1], s[3])
Term %= Term + MODULO + Factor, lambda h, s: modulo(s[1], s[3])

Factor %= Sign, lambda h, s: s[1]
Factor %= Sign + POWER + Factor, lambda h, s: power(s[1], s[3])
Factor %= Sign + POWER2 + Factor, lambda h, s: power(s[1], s[3])

Sign %= Atom, lambda h, s: s[1]
Sign %= MINUS + Atom, lambda h, s: negativeSign(s[2])

Atom %= NUMBER, lambda h, s: literalNumber(s[1])
Atom %= STRING, lambda h, s: literalString(s[1])
Atom %= BOOLEAN, lambda h, s: literalBool(s[1])
Atom %= CONSTANT, lambda h, s: constantNode(s[1])
Atom %= IDENTIFIER, lambda h, s: variableNode(s[1])
Atom %= OPEN_BRACK + ExpressionList + CLOSE_BRACK, lambda h, s: createVector(s[2])
Atom %= OPEN_BRACK + Expression + OR_OR + IDENTIFIER + IN + Expression + CLOSE_BRACK, lambda h, s: implicitVectorConstruction(s[2], s[4], s[6])
Atom %= OPEN_PAREN + Expression + CLOSE_PAREN, lambda h, s: s[2]
Atom %= NEW + TYPE_IDENTIFIER + OPEN_PAREN + ExpressionList + CLOSE_PAREN, lambda h, s: instantiateType(s[2], s[4])
Atom %= IDENTIFIER + OPEN_PAREN + ExpressionList + CLOSE_PAREN, lambda h, s: functionCall(s[1], s[3])
Atom %= Atom + AS + TYPE_IDENTIFIER, lambda h, s: downcastType(s[1], s[3])
Atom %= Atom + OPEN_BRACK + Expression + CLOSE_BRACK, lambda h, s: indexAccess(s[1], s[3])
Atom %= IDENTIFIER + DOT + IDENTIFIER + OPEN_PAREN + ExpressionList + CLOSE_PAREN, lambda h, s: methodCall(s[1], s[3], s[5])
Atom %= IDENTIFIER + DOT + IDENTIFIER, lambda h, s: attributeAccess(s[1], s[3])

FunctionDeclaration %= FUNCTION + IDENTIFIER + OPEN_PAREN + ArgumentList + CLOSE_PAREN + Body, lambda h, s: declareFunction(s[2], s[4], s[6])
FunctionDeclaration %= FUNCTION + IDENTIFIER + OPEN_PAREN + ArgumentList + CLOSE_PAREN + COLON + TYPE_IDENTIFIER + Body, lambda h, s: declareFunction(s[2], s[4], s[8], return_type=s[7])

TypeDeclaration %= TYPE + TYPE_IDENTIFIER + OPEN_BRACE + FeatureList + CLOSE_BRACE, lambda h, s: declareType(s[2], s[4])
TypeDeclaration %= TYPE + TYPE_IDENTIFIER + OPEN_PAREN + ArgumentList + CLOSE_PAREN + OPEN_BRACE + FeatureList + CLOSE_BRACE, lambda h, s: declareType(s[2], s[7], s[4])
TypeDeclaration %= TYPE + TYPE_IDENTIFIER + INHERITS + TYPE_IDENTIFIER + OPEN_BRACE + FeatureList + CLOSE_BRACE, lambda h, s: declareType(s[2], s[6], base_type=s[4])
TypeDeclaration %= TYPE + TYPE_IDENTIFIER + OPEN_PAREN + ArgumentList + CLOSE_PAREN + INHERITS + TYPE_IDENTIFIER + OPEN_PAREN + ExpressionList + CLOSE_PAREN + OPEN_BRACE + FeatureList + CLOSE_BRACE, lambda h, s: declareType(s[2], s[12], s[4], s[7], s[9])

ProtocolDeclaration %= PROTOCOL + TYPE_IDENTIFIER + OPEN_BRACE + ProtocolMethods + CLOSE_BRACE, lambda h, s: declareProtocol(s[2], s[4])
ProtocolDeclaration %= PROTOCOL + TYPE_IDENTIFIER + EXTENDS + TypeList + OPEN_BRACE + ProtocolMethods + CLOSE_BRACE, lambda h, s: declareProtocol(s[2], s[6], s[4])

ArgumentList %= VariableDeclaration + ArgumentTail, lambda h, s: [s[1]] + s[2]
ArgumentList %= G.Epsilon, lambda h, s: []

ArgumentTail %= COMMA + VariableDeclaration + ArgumentTail, lambda h, s: [s[2]] + s[3]
ArgumentTail %= G.Epsilon, lambda h, s: []

FeatureList %= VariableDeclaration + EQUAL + Statement + FeatureList, lambda h, s: [defineFeature(s[1], s[3])] + s[4]
FeatureList %= IDENTIFIER + OPEN_PAREN + ArgumentList + CLOSE_PAREN + Body + FeatureList, lambda h, s: [defineMethod(s[1], s[3], s[5])] + s[6]
FeatureList %= IDENTIFIER + OPEN_PAREN + ArgumentList + CLOSE_PAREN + COLON + TYPE_IDENTIFIER + Body + FeatureList, lambda h, s: [defineMethod(s[1], s[3], s[7], return_type=s[6])] + s[8]
FeatureList %= G.Epsilon, lambda h, s: []

ProtocolMethods %= IDENTIFIER + OPEN_PAREN + FullyTypedArgs + CLOSE_PAREN + COLON + TYPE_IDENTIFIER + SEMICOLON + ProtocolMethods, lambda h, s: [declareProtocolMethod(s[1], s[3], s[6])] + s[8]
ProtocolMethods %= G.Epsilon, lambda h, s: []

FullyTypedArgs %= IDENTIFIER + COLON + TYPE_IDENTIFIER + FullyTypedTail, lambda h, s: [defineVariable(s[1], s[3])] + s[4]
FullyTypedArgs %= G.Epsilon, lambda h, s: []

FullyTypedTail %= COMMA + IDENTIFIER + COLON + TYPE_IDENTIFIER + FullyTypedTail, lambda h, s: [defineVariable(s[2], s[4])] + s[5]
FullyTypedTail %= G.Epsilon, lambda h, s: []

TypeList %= TYPE_IDENTIFIER, lambda h, s: [s[1]]
TypeList %= TYPE_IDENTIFIER + COMMA + TypeList, lambda h, s: [s[1]] + s[3]

Body %= ARROW + Stat, lambda h, s: s[2]
Body %= OPEN_BRACE + StatList + CLOSE_BRACE, lambda h, s: s[2]
