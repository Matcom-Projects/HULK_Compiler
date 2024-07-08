from cmp.ast import *
from cmp.semantic import Type,Context,SemanticError,Method

# Nodo para representar el programa completo
class ProgramNode(Node):
    def __init__(self, decl_list, expr):
        self.decl_list = decl_list
        self.expr = expr

# Nivel 1: Tipos de datos básicos que heredan de ObjectType o directamente de Type
class ObjectType(Type):
    def __init__(self):
        Type.__init__(self, 'Object')
    def __eq__(self, other):
        return other.name == self.name or isinstance(other, NumType) or isinstance(other, StringType) or isinstance(other, BoolType) or isinstance(other, ObjectType)

class NoneType(Type):
    def __init__(self):
        Type.__init__(self, 'None')

class NumType(ObjectType):
    def __init__(self):
        Type.__init__(self, 'Number')
    def __eq__(self, other):
        return other.name == self.name or isinstance(other, NumType) or isinstance(other, ObjectType)

class StringType(ObjectType):
    def __init__(self):
        Type.__init__(self,'String')
    def __eq__(self, other):
        return other.name == self.name or isinstance(other, StringType) or isinstance(other, ObjectType)

class BoolType(ObjectType):
    def __init__(self):
        Type.__init__(self,'Bool')
    def __eq__(self, other):
        return other.name == self.name or isinstance(other, BoolType) or isinstance(other, ObjectType)

# Nodos atómicos para literales y variables
class LiteralNumNode(AtomicNode):
    def __init__(self, lex):
        AtomicNode.__init__(self,lex)
        self.inferred_type= NumType()

class LiteralBoolNode(AtomicNode):
    def __init__(self, lex):
        AtomicNode.__init__(self,lex)
        self.inferred_type= BoolType()

class LiteralStrNode(AtomicNode):
    def __init__(self, lex):
        AtomicNode.__init__(self,lex)
        self.inferred_type= StringType()

class ConstantNode(AtomicNode):
    def __init__(self, lex):
        AtomicNode.__init__(self,lex)
        self.inferred_type= NumType()

class VarNode(AtomicNode):
    pass

# Nivel 2: Nodos de expresiones y declaraciones básicas
class ExprNode(Node):
    pass

class DeclNode(Node):
    pass

class ExprBlockNode(ExprNode):
    def __init__(self, expr_list) -> None:
        self.expr_list = expr_list

class LetNode(ExprNode):
    def __init__(self, assign_list, expr) -> None:
        self.assign_list = assign_list
        self.expr = expr

class IfNode(ExprNode):
    def __init__(self, cond, if_expr, elif_branches, else_expr) -> None:
        self.cond = cond
        self.if_expr = if_expr
        self.elif_branches = elif_branches
        self.else_expr = else_expr

class WhileNode(ExprNode):
    def __init__(self, cond, body) -> None:
        self.cond = cond
        self.body = body

class ForNode(ExprNode):
    def __init__(self, id, iterable, body) -> None:
        self.id = id
        self.iterable = iterable
        self.body = body

class DestrAssign(ExprNode):
    def __init__(self, id, expr, is_attr = False) -> None:
        self.id = id
        self.expr = expr
        self.is_attr = is_attr

class AssignNode(Node):
    def __init__(self, var, expr) -> None:
        self.var = var
        self.expr = expr

class VarDefNode(Node):
    def __init__(self, id, type = None) -> None:
        self.id = id
        self.type = type

# Nodos para operaciones binarias
class ConcatNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return str(lvalue) + str(rvalue)

class ConcatWithSpaceNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return str(lvalue) + " " + str(rvalue)

class OrNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return lvalue or rvalue

class AndNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return lvalue and rvalue

# Nodo para operación unaria NOT
class NotNode(UnaryNode):
    @staticmethod
    def operate(value):
        return not value

class DynTestNode(ExprNode):
    def __init__(self, expr, type) -> None:
        self.expr = expr
        self.type = type

# Nodos para comparaciones binarias
class EqualNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return lvalue == rvalue

class NotEqualNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return lvalue != rvalue

class LessNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return lvalue < rvalue

class GreaterNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return lvalue > rvalue

class LeqNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return lvalue <= rvalue

class GeqNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return lvalue >= rvalue

# Nodos para operaciones aritméticas binarias
class PlusNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return lvalue + rvalue

class MinusNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return lvalue - rvalue

class StarNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return lvalue * rvalue

class DivNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return lvalue / rvalue

class ModNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return lvalue % rvalue

class PowNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return lvalue ** rvalue

# Nodo para operación unaria Neg
class NegNode(UnaryNode):
    @staticmethod
    def operate(value):
        return - value


# Nivel 3: Nodos de expresiones y declaraciones más complejas
class VectorNode(ExprNode):
    def __init__(self, expr_list) -> None:
        self.expr_list = expr_list

class ImplicitVector(ExprNode):
    def __init__(self, expr, id, iterable) -> None:
        self.expr = expr
        self.id = id
        self.iterable = iterable

class IndexingNode(ExprNode):
    def __init__(self, vector, index):
        self.vector = vector
        self.expr = index

class InstantiateNode(ExprNode):
    def __init__(self, type, expr_list) -> None:
        self.type = type
        self.expr_list = expr_list

class DowncastNode(ExprNode):
    def __init__(self, obj, type) -> None:
        self.obj = obj
        self.type = type

class FuncCallNode(ExprNode):
    def __init__(self, id, args):
        self.id = id
        self.args = args

class MethodCallNode(ExprNode):
    def __init__(self, obj, id, args):
        self.obj = obj
        self.id = id
        self.args = args

class AttrrCallNode(ExprNode):
    def __init__(self, obj, id) -> None:
        self.obj = obj
        self.id = id

# Nodos para declaraciones de funciones, tipos y métodos
class FuncDeclNode(DeclNode):
    def __init__(self, id, args, body, return_type = None) -> None:
        self.id = id
        self.args = args
        self.return_type = return_type
        self.body = body

class TypeDeclNode(DeclNode):
    def __init__(self, id, features, args = None, parent = None, parent_constructor_args = None) -> None:
        self.id = id
        self.features = features
        self.args = args
        self.parent = parent
        self.parent_constructor_args = parent_constructor_args

class MethodNode(Node):
    def __init__(self, id, args, body, return_type = None) -> None:
        self.id = id
        self.args = args
        self.return_type = return_type
        self.body = body

class ProtDeclNode(DeclNode):
    def __init__(self, id, methods, parents=None) -> None:
        self.id = id
        self.methods = methods
        self.parents = parents

class ProtMethodNode(Node):
    def __init__(self, id, args: list[VarDefNode], return_type) -> None:
        self.id = id
        self.args = args
        self.return_type = return_type
