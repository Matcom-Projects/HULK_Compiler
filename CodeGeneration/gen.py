from .ast_visitor import HulkToCVisitor, Auxiliar
from .decls_context import DefsInC


class GenCode:
  def __call__(self, ast, context):
      with open('CodeGeneration/template.c') as template:
          return template.read() + "\n\n" + self.generate_code(ast, context)

  @staticmethod
  def generate_code(ast, context):

    aux = Auxiliar()
    ast_visitor = HulkToCVisitor(context)
    decl = DefInC(context)

    code = ""
    objects = ""
    methods = ""
    funcs = ""

    main = "\nint main() {\n"
    main += "   srand(time(NULL));\n\n"
    main += aux.formated(ast_visitor.visit(ast.expression)) + ";"
    main += "\n   return 0; \n}"

    blocks = [
            ast_visitor.blocks_decl,
            ast_visitor.blocks_let_in,
            ast_visitor.blocks_if_else,
            ast_visitor.blocks_loop,
            ast_visitor.blocks_method_call,
            ast_visitor.create_blocks,
            ast_visitor.vector_comp,
            ast_visitor.vector_selector,
            ast_visitor.expr_blocks
        ]

    blocks_code = "\n\n".join("\n\n".join(block) for block in blocks)


    for type in context.types.values():
      if type.name not in ["Number", "Boolean", "String", "Object", "Range"]:
        current_def = decl.objects_def[type.name]
        code += current_def[0] + ";\n"
        if type.name in method_defs:
          for method_def, method_name, method in decl.method_defs[type.name]:
              code += method_def + ";\n"
              methods += method_def + " {\n"
              methods += "   if(self == NULL)\n"
              methods += "       throwError(\"Null Reference\");\n\n"
              methods += aux.formated(ast_visitor.visit(method.node), "ret") + "\n"
              methods += "}\n\n"
        code += "\n"

        objects += current_def[0] + " {\n"
        objects += "   Object* obj = create_object();\n\n"

        for param in current_def[1]:
          objects += "   add_attr(obj, \"" + param + "\", " + param + ");\n"

        objects += "\n"

        current = type
        index = 0
        while current is not None:
          objects += "   add_attr(obj, \"parent_type" + str(
              index) + "\", \"" + current.name + "\");\n"

          if current.name in decl.method_defs:
            for method in method_defs[current.name]:
              objects += "   add_attr(obj, \"" + method[1] + "\", *" + method[1] + ");\n"

          current = current.parent
          index += 1

        objects += "\n"
        index = 0

        for protocol in delc.protocols[type.name]:
          objects += "   add_attr(obj, \"conforms_protocol" + str(
            index) + "\", \"" + protocol.name + "\");\n"
          index += 1

        objects += "   return obj;\n"
        objects += "}\n\n"

    for function_def, function_name, function in decl.function_defs:
      code += function_def + ";\n"
      funcs += function_def + " {\n"
      funcs += aux.formated(ast_visitor.visit(function.node), True) + "\n"
      funcs += "}\n\n"



    return (
        code +
        objects +
        blocks_code +
        methods +
        funcs +
        main
    )
