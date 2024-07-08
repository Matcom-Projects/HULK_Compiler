from ast.ast import *
import cmp.visitor as visitor
from cmp.utils import Context
import hashlib

class Auxiliar:
    def __init__(self):
        self.generated_names = set()

    def generate_name(self, base_name):
        suffix = hashlib.sha1(base_name.encode()).hexdigest()[:8]
        unique_name = f"{base_name}_{suffix}"

        while unique_name in self.generated_names:
            suffix = hashlib.sha1((base_name + suffix).encode()).hexdigest()[:8]
            unique_name = f"{base_name}_{suffix}"

        self.generated_names.add(unique_name)
        return unique_name

    @staticmethod
    def formated(code: str, add_return = ""):
        lines = [line for line in code.split('\n') if line.strip()]
        if lines:
            if add_return == "ret":
                lines[-1] = f"   return {lines[-1].strip()};"
            elif add_return == "ret_obj":
                lines[-1] = f"   return_obj = {lines[-1].strip()};"
        formatted_lines = [f"   {line}" for line in lines]
        return '\n'.join(formatted_lines)

class HulkToCVisitor(object):

    def __init__(self, context) -> None:
        self.aux = Auxiliar()
        self.context: Context = context
        self.blocks_decl = []
        self.blocks_let_in = []
        self.blocks_if_else = []
        self.blocks_loop = []
        self.blocks_method_call = []
        self.create_blocks = []
        self.vector_comp = []
        self.vector_selector = []
        self.expr_blocks = []

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(VarDefNode)
    def visit(self, node: VarDefNode):
        return scope.find_variable(node.id).name_temp

    @visitor.when(AssignNode)
    def visit(self, node: AssignNode):
        var = self.aux.generate_name("v")
        scope.find_variable(node.var).set_temp_name(var)

        return "object* " + var + " = copy_object(" + self.visit(node.expr) + ");"

    @visitor.when(LiteralNumNode)
    def visit(self, node: LiteralNumNode):
        return f'create_number({node.lex})'

    @visitor.when(LiteralBoolNode)
    def visit(self, node: LiteralBoolNode):
        return f'create_boolean({node.lex})'

    @visitor.when(LiteralStrNode)
    def visit(self, node: LiteralStrNode):
        return f'create_string({node.lex})'

    @visitor.when(PlusNode)
    def visit(self, node: PlusNode):
        return f'perform_numeric_operation({self.visit(node.left)},{self.visit(node.right)},"plus")'

    @visitor.when(MinusNode)
    def visit(self, node: MinusNode):
        return f'perform_numeric_operation({self.visit(node.left)},{self.visit(node.right)},"minus")'

    @visitor.when(StarNode)
    def visit(self, node: StarNode):
        return f'perform_numeric_operation({self.visit(node.left)},{self.visit(node.right)},"star")'

    @visitor.when(DivNode)
    def visit(self, node: DivNode):
        return f'perform_numeric_operation({self.visit(node.left)},{self.visit(node.right)},"div")'

    @visitor.when(PowNode)
    def visit(self, node: PowNode):
        return f'perform_numeric_operation({self.visit(node.left)},{self.visit(node.right)},"pow")'

    @visitor.when(ModNode)
    def visit(self, node: ModNode):
        return f'perform_numeric_operation({self.visit(node.left)},{self.visit(node.right)},"mod")'

    @visitor.when(MethodNode)
    def visit(self, node: MethodNode):
        return self.visit(node.body)

    @visitor.when(FuncDeclNode)
    def visit(self, node: FuncDeclNode):
        return self.visit(node.body)

    @visitor.when(InstantiateNode)
    def visit(self, node: InstantiateNode):
        vars = scope.get_variables(True)
        params = ", ".join([var.name_temp for var in vars])
        objects = ", ".join([f"object* {var.name_temp}" for var in vars])

        name_temp = self.aux("block")
        create_block = f"object* {name_temp} ({objects});"
        self.blocks_decl.append(create_block)
        create_block += " {\n"
        block_vars = ""
        code = "   return create" + node.id + "("
        change = False

        typex = self.context.get_type(node.id)
        args = node.args

        while typex is not None and typex.name != "object":
            for i, param in enumerate(typex.params_names):
                var = self.aux.generate_name("v")
                block_vars += f"   object* {var} = {self.visit(args[i])};\n"
                typex.scope.children[0].find_variable(param).set_temp_name(var)

            for att in typex.attributes:
                code += f"copy_object({self.visit(att.node.expr)}), "
                change = True

            args = typex.node.parent_constructor_args
            typex = typex.parent

        if change:
            code = code[:-2]
        code += ");"

        create_block += block_vars + "\n" + code + "\n}"
        self.create_blocks.append(create_block)

        return f"{name_temp} ({params})"


    @visitor.when(ExprBlockNode)
    def visit(self, node: ExprBlockNode):
        vars = scope.get_variables(True)

        params = ", ".join([var.name_temp for var in vars])
        objects = ", ".join([f"object* {var.name_temp}" for var in vars])

        name_temp = self.aux("expr_block")
        create_block = f"object* {name_temp} ({objects});"
        self.blocks_decl.append(create_block)
        create_block += " {\n"
        block_expr = ""

        for expr in node.expr_list:
            block_expr += self.visit(expr) + ";\n"

        create_block += self.aux.formated(block_expr[:-2], "ret") + "\n}"
        self.expr_blocks.append(create_block)

        return f"{name_temp} ({params})"

    @visitor.when(LetNode)
    def visit(self, node: LetNode):
        vars = scope.get_variables(True)

        params = ", ".join([var.name_temp for var in vars])
        objects = ", ".join([f"object* {var.name_temp}" for var in vars])

        name_temp = self.aux("let")
        create_block = f"object* {name_temp} ({objects});"
        self.blocks_decl.append(create_block)
        create_block += " {\n"

        for assign in node.assign_list:
            create_block += "   " + self.visit(assign) + "\n"

        create_block += self.aux.formated(self.visit(node.body), "ret") + "\n}"
        self.blocks_let_in.append(create_block)

        return f"{name_temp} ({params})"

    @visitor.when(FuncCallNode)
    def visit(self, node: FuncCallNode):
        function = "func_" + node.id + "("
        for arg in node.args:
            function += "copy_object(" + self.visit(arg) + "), "
        if len(node.args) > 0:
            function = function[:-2]
        function += ")"

        return function

    @visitor.when(DowncastNode)
    def visit(self, node: DowncastNode):
        return self.visit(node.obj)

    @visitor.when(DynTestNode)
    def visit(self, node: DynTestNode):
        try:
            self.context.get_type(node.type)
            return "is_type(" + self.visit(node.expr) + ", \"" + node.type + "\")"
        except:
            return "is_protocol(" + self.visit(node.expr) + ", \"" + node.type + "\")"

    @visitor.when(AttrrCallNode)
    def visit(self, node: AttrrCallNode):
        obj = self.visit(node.obj)
        typex = scope.find_variable(obj).type
        if typex.name == "Self":
            typex = typex.referred_type

        return "get_attr_value(" + obj + ", \"" + typex.name + "_" + node.attribute + "\")"

    @visitor.when(MethodCallNode)
    def visit(self, node: MethodCallNode):
        obj = self.visit(node.obj)

        args = ','.join(["object*" for i in range(len(node.args))])

        if len(args) > 0:
            args = ',' + args

        if isinstance(node.obj, VarDefNode):
            code = "((object* (*)(object*" + args + "))" + \
                    "get_method(" + obj + ", \"" + node.id + "\", NULL)" + \
                    ")(" + obj
            for arg in node.args:
                code += ", copy_object(" + self.visit(arg) + ")"
            code += ")"
            return code

        else:
            vars = scope.get_variables(True)

            params = ", ".join([var.name_temp for var in vars])
            objects = ", ".join([f"object* {var.name_temp}" for var in vars])

            name_temp = self.aux("method_call_block")
            create_block = f"object* {name_temp} ({objects});"
            self.blocks_decl.append(create_block)
            create_block += " {\n"


            create_block += "   object* obj = " + obj + ";\n"
            create_block += "   return ((object* (*)(object*" + args + "))" + \
                    "get_method(obj, \"" + node.id + "\", NULL)" + \
                    ")(obj"

            for arg in node.args:
                create_block += ", copy_object(" + self.visit(arg) + ")"

            create_block += ");\n}"
            self.blocks_method_call.append(create_block)

            return f"{name_temp} ({params})"

    @visitor.when(IfNode)
    def visit(self, node: IfNode):
        vars = scope.get_variables(True)

        params = ", ".join([var.name_temp for var in vars])
        objects = ", ".join([f"object* {var.name_temp}" for var in vars])

        name_temp = self.aux("if_else")
        create_block = f"object* {name_temp} ({objects});"
        self.blocks_decl.append(create_block)
        create_block += " {\n"

        create_block += "   if(*((bool*)get_attr_value(" + self.visit(node.cond) + ", \"value\"))) {\n"
        create_block += self.aux.formated(self.aux.formated(self.visit(node.if_expr), "ret")) + "\n   }\n"

        for i in range(len(node.elif_branches)):
            create_block += "   else if(*((bool*)get_attr_value(" + self.visit(node.elif_branches[i][0]) + ", \"value\"))) {\n"
            create_block += self.aux.formated(self.aux.formated(self.visit(node.elif_branches[i][1]), "ret")) + "\n   }\n"


        create_block += "   else {\n"
        create_block += self.aux.formated(self.aux.formated(self.visit(node.else_expr), "ret")) + "\n   }\n"

        self.blocks_if_else.append(create_block)

        return f"{name_temp} ({params})"

    @visitor.when(GreaterNode)
    def visit(self, node: GreaterThanNode):
        return f'perform_boolean_comparison({self.visit(node.left)},{self.visit(node.right)},"greater_than")'

    @visitor.when(GeqNode)
    def visit(self, node: GreaterOrEqualNode):
        return f'perform_boolean_comparison({self.visit(node.left)},{self.visit(node.right)},"greater_or_eq")'

    @visitor.when(LessNode)
    def visit(self, node: LessThanNode):
        return f'perform_boolean_comparison({self.visit(node.left)},{self.visit(node.right)},"less_than")'

    @visitor.when(LeqNode)
    def visit(self, node: LessOrEqualNode):
        return f'perform_boolean_comparison({self.visit(node.left)},{self.visit(node.right)},"less_or_eq")'

    @visitor.when(OrNode)
    def visit(self, node: OrNode):
        return f"boolean_operation({self.visit(node.left)},{self.visit(node.right)},'|')"

    @visitor.when(AndNode)
    def visit(self, node: AndNode):
        return f"boolean_operation({self.visit(node.left)},{self.visit(node.right)},'&')"

    @visitor.when(ConcatNode)
    def visit(self, node: ConcatNode):
        return f"string_concat({self.visit(node.left)},{self.visit(node.right)}, false)"

    @visitor.when(ConcatWithSpaceNode)
    def visit(self, node: ConcatWithSpaceNode):
        return f"string_concat({self.visit(node.left)},{self.visit(node.right)}, true)"

    @visitor.when(EqualNode)
    def visit(self, node: EqualNode):
        left = self.visit(node.left)

        if isinstance(node.left, VarDefNode):
            code = "((object* (*)(object*, object*))" + \
                    "get_method(" + left + ", \"equals\", NULL)" + \
                    ")(" + left + ", " + self.visit(node.right) + ")"
            return code

        else:
            vars = scope.get_variables(True)

            params = ", ".join([var.name_temp for var in vars])
            objects = ", ".join([f"object* {var.name_temp}" for var in vars])

            name_temp = self.aux("method_call_block")
            create_block = f"object* {name_temp} ({objects});"
            self.blocks_decl.append(create_block)
            create_block += " {\n"

            create_block += "   object* obj = " + left + ";\n"
            create_block += "   return ((object* (*)(object*, object*))" + \
                    "get_method(obj, \"equals\", NULL)" + \
                    ")(obj, " + self.visit(node.right) + ");\n}"

            self.blocks_method_call.append(create_block)

            return f"{name_temp} ({params})"

    @visitor.when(NotEqualNode)
    def visit(self, node: NotEqualNode):
        left = self.visit(node.left)

        if isinstance(node.left, VarDefNode):
            code = "invert_boolean(((object* (*)(object*, object*))" + \
                    "get_method(" + left + ", \"equals\", NULL)" + \
                    ")(" + left + ", " + self.visit(node.right) + "))"

            return code

        else:
            vars = scope.get_variables(True)

            params = ", ".join([var.name_temp for var in vars])
            objects = ", ".join([f"object* {var.name_temp}" for var in vars])

            name_temp = self.aux("method_call_block")
            create_block = f"object* {name_temp} ({objects});"
            self.blocks_decl.append(create_block)
            create_block += " {\n"

            create_block += "   object* obj = " + left + ";\n"
            create_block += "   return invert_boolean(((object* (*)(object*, object*))" + \
                    "get_method(obj, \"equals\", NULL)" + \
                    ")(obj, " + self.visit(node.right) + "));"

            self.blocks_method_call.append(create_block)

        return f"{name_temp} ({params})"


    @visitor.when(WhileNode)
    def visit(self, node: WhileNode):
        vars = scope.get_variables(True)

        params = ", ".join([var.name_temp for var in vars])
        objects = ", ".join([f"object* {var.name_temp}" for var in vars])

        name_temp = self.aux("while")
        create_block = f"object* {name_temp} ({objects});"
        self.blocks_decl.append(create_block)
        create_block += " {\n"

        create_block += "   object* return_obj = NULL;\n"
        create_block += "   while(*((bool*)get_attr_value(" + self.visit(node.cond) + ", \"value\"))) {\n"

        create_block += self.aux.formated(self.aux.formated(self.visit(node.body), "ret_obj")) + "\n}\n"
        create_block += "   return return_obj;\n}"

        self.blocks_loop.append(create_block)

        return f"{name_temp} ({params})"


    @visitor.when(ForNode)
    def visit(self, node: ForNode):
        var_iter = self.aux("v")
        scope.children[0].find_variable(node.var).set_temp_name(var_iter)

        vars = scope.get_variables(True)

        params = ", ".join([var.name_temp for var in vars])
        objects = ", ".join([f"object* {var.name_temp}" for var in vars])

        name_temp = self.aux("for")
        code = f"object* {name_temp} ({objects});"
        self.blocks_decl.append(code)
        code += " {\n"

        code += "   object* return_obj = NULL;\n"
        code += "   object* " + var_iter + " = NULL;\n"
        code += "   object* iterable = " + self.visit(node.iterable) + ";\n"
        code += "   object*(*next)(object*) = get_method(iterable, \"next\", NULL);\n"
        code += "   object*(*current)(object*) = get_method(iterable, \"current\", NULL);\n\n"

        code += "   while(*(bool*)get_attr_value(next(iterable), \"value\")) {\n"
        code += "      " + var_iter + " = current(iterable);\n\n"
        code += self.aux.formated(self.aux.formated(self.visit(node.body), "ret_obj")) + "\n"
        code += "   }\n"

        code += "   return return_obj;\n}"

        self.blocks_loop.append(code)

        return f'{name_temp} ({params})'


    @visitor.when(DestrAssign)
    def visit(self, node: DestrAssign):
        return f"replace_object({self.visit(node.target)},{self.visit(node.expr)})"


    @visitor.when(VectorNode)
    def visit(self, node: VectorNode):
        return "create_vector(" + str(len(node.expr_list)) + ", " + ", ".join(
            [self.visit(expr) for expr in node.expr_list]) + ")"

    @visitor.when(ImplicitVector)
    def visit(self, node: ImplicitVector):
        var_iter = self.aux("v")
        scope.children[0].find_variable(node.var).set_temp_name(var_iter)

        objects = ", ".join([f"object* {var.name_temp}" for var in vars])

        name_temp_1 = self.aux("selector")
        selector = f"object* {name_temp_1} ({objects});"
        self.blocks_decl.append(selector)
        selector += " {\n"
        selector += self.aux.formated(self.visit(node.expr), "ret") + "\n}"

        self.implicit_vector.append(selector)

        objects_1 = ", ".join([f"object* {var.name_temp}" for var in vars])

        name_temp = self.aux("implicit_vector")
        implicit_vector = f"object* {name_temp} ({objects_1});"
        self.blocks_decl.append(implicit_vector)
        implicit_vector += " {\n"
        implicit_vector += "   object* iterable = " + self.visit(node.iterable) + ";\n"
        implicit_vector += "   object*(*next)(object*) = get_method(iterable, \"next\", NULL);\n"
        implicit_vector += "   object*(*current)(object*) = get_method(iterable, \"current\", NULL);\n\n"
        implicit_vector += "   int size = *(int*)get_attr_value(iterable, \"size\");\n\n"
        implicit_vector += "   object** new_list = malloc(size * sizeof(object*));\n\n"
        implicit_vector += "   for(int i = 0; i < size; i++) {\n"
        implicit_vector += "      next(iterable);\n"
        implicit_vector += "      new_list[i] = " + name_temp_1

        params = ", ".join([var.name_temp for var in vars])

        implicit_vector += "(" + params + "," + "current(iterable));\n"

        implicit_vector += "   }\n\n"
        implicit_vector += "   return create_vector_from_list(size, new_list);\n"
        implicit_vector += "}"

        self.vector_comp.append(vector_comp)

        return f'{name_temp} ({params})'

    @visitor.when(IndexingNode)
    def visit(self, node: IndexingNode):
        return "get_element_of_vector(" + self.visit(node.vector) + ", " + self.visit(node.index) + ")"
