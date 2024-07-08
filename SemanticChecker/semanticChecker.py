from AST.ast import *
import cmp.visitor as visitor
from cmp.semantic import Scope
from cmp.semantic import SemanticError
from cmp.semantic import Attribute, VariableInfo

#Error messages
WRONG_SIGNATURE = 'Method "%s" already defined in "%s" with a different signature.'
SELF_IS_READONLY = 'Variable "self" is read-only.'
LOCAL_ALREADY_DEFINED = 'Variable "%s" is already defined in method "%s".'
INCOMPATIBLE_TYPES = 'Cannot convert "%s" into "%s".'
VARIABLE_NOT_DEFINED = 'Variable "%s" is not defined in "%s".'
INVALID_OPERATION = 'Operation is not defined between "%s" and "%s".'



class TypeCollector(object):
    def __init__(self, errors=[]):
        self.context = None
        self.errors = errors
    
    @visitor.on('node')
    def visit(self, node):
        pass
    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        self.context = Context()
        self.context.create_type("Object")
        self.context.create_type("Void")
        self.context.create_type("Number")
        self.context.create_type("Boolean")
        self.context.create_type("String")
        self.context.create_type("Function")
        vector=self.context.create_type("Vector")
        vector.define_method('next',[],[],self.context.get_type('Boolean'))
        vector.define_method('size',[],[],self.context.get_type('Number'))
        iterable_protocol=self.context.create_protocol('Iterable')
        iterable_protocol.define_method('next',[],[],self.context.get_type('Boolean'))
        iterable_protocol.define_method('current',[],[],self.context.get_type('Object'))
        
        for decl in node.decl_list:
            self.visit(decl)
        return self.context
        
    @visitor.when(TypeDeclNode)
    def visit(self, node: TypeDeclNode):
        try :
            self.context.create_type(node.id)
        except SemanticError as e:
            self.errors.append(e)
            
    @visitor.when(ProtDeclNode)
    def visit(self, node:ProtDeclNode):
        try :
            
            self.context.create_protocol(node.id)
        except SemanticError as e:
            self.errors.append(e)


class TypeBuilder:
    def __init__(self, context: Context, errors=[]):
        self.context = context
        self.current_type: Type = None
        self.errors = errors
    
    @visitor.on('node')
    def visit(self, node):
        pass
    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        for decl in node.decl_list:
            try:
                self.visit(decl)
            except SemanticError as error:
                self.errors.append(error)
    
    @visitor.when(TypeDeclNode)
    def visit(self, node: TypeDeclNode):
        self.current_type = self.context.get_type(node.id)
        self.current_type.set_parent(self.context.get_type(node.parent) if node.parent != None else self.context.get_type("Object"))
        type_args=[]

            
        for arg in node.args:
            actual_type=self.context.get_type(arg.type) if arg.type!=None else self.context.get_type('Object')
            type_args.append(VariableInfo(arg.id,actual_type))
        self.current_type.args=type_args
        

        for feature in node.features:
            self.visit(feature)
        
        self.current_type=None
    
    @visitor.when(AssignNode)
    def visit(self, node: AssignNode): 
        type_node = self.context.get_type(node.var.type) if node.var.type!=None else self.context.get_type("Object") 
        self.current_type.define_attribute(node.var.id,type_node)
        
    @visitor.when(MethodNode)
    def visit(self, node: MethodNode):
        type=self.context.get_type(node.return_type if node.return_type!=None else 'Object')
        param_names = []
        param_types = []
        for param in node.args:
            aux:VarDefNode=param
            param_names.append(aux.id)
            param_types.append(self.context.get_type(aux.type if aux.type != None else "Object"))
        self.current_type.define_method(node.id,param_names,param_types, type)
    
    @visitor.when(ProtDeclNode)
    def visit(self, node: ProtDeclNode):
        self.current_type= self.context.get_protocol(node.id)
        self.current_type.set_parent(self.context.get_type(node.parents) if node.parents!=None else self.context.get_type("Object"))
        for method in node.methods:
            self.visit(method)
    
    
    @visitor.when(ProtMethodNode)
    def visit(self, node: ProtMethodNode):
        type=self.context.get_type(node.return_type if node.return_type!=None else 'Object')
        param_names = []
        param_types = []
        for param in node.args:
            aux:VarDefNode=param
            param_names.append(aux.id)
            param_types.append(self.context.get_type(aux.type if aux.type != None else "Object"))
        self.current_type.define_method(node.id,param_names,param_types,type)
    
    @visitor.when(FuncDeclNode)
    def visit(self, node: FuncDeclNode):
        #las funciones seran metodos de tipo "Function"
        function_type : Type =self.context.get_type('Function')
        return_type=self.context.get_type(node.return_type if node.return_type!=None else 'Object')
        param_names = []
        param_types = []
        for param in node.args:
            aux:VarDefNode=param
            param_names.append(aux.id)
            param_types.append(self.context.get_type(aux.type if aux.type != None else "Object"))
        function_type.define_method(node.id,param_names,param_types,return_type)
            


class TypeChecker:
    def __init__(self, context: Context, errors=[]):
        self.context = context
        self.current_type: Type = None
        self.current_method:Method = None
        self.errors:list = errors

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, scope=None):
        newScope=Scope()
        for decl in node.decl_list:
            self.visit(decl,newScope)
   
    @visitor.when(TypeDeclNode)
    def visit(self, node: TypeDeclNode, scope:Scope):
        self.current_type=self.context.get_type(node.id)
        
        childScope=scope.create_child()
        childScope.define_variable('self',self.current_type)
        for arg in node.args:
            self.visit(arg,childScope)
        
        for feature in node.features:
            self.visit(feature,childScope)
        
        self.current_type=None
    
    @visitor.when(AssignNode)
    def visit(self, node: AssignNode, scope:Scope):
        
        type:Type=self.visit(node.var,scope)
        expr_type:Type=self.visit(node.expr,scope)
        
        if(not expr_type.conforms_to(type)):
            self.errors.append(SemanticError(INCOMPATIBLE_TYPES%(type.name,expr_type.name))) 
            raise
        
        if(self.current_method!=None and self.current_method==None):
            return
        

        return expr_type
        
    @visitor.when(MethodNode)
    def visit(self, node: MethodNode, scope:Scope):
        actual_method:Method=self.current_type.get_method(node.id)
        new_child=scope.create_child()
        
        #Declarando como variables los parametros de la funcion en el 
        #nuevo scope
        for i in range(0,len(actual_method.param_names)):
            new_child.define_variable(actual_method.param_names[i],
                                      actual_method.param_types[i])
        
        self.current_method=actual_method
        expr_type= self.visit(node.body,new_child)
        self.current_method=None
        
        if(not expr_type.conforms_to(node.return_type)):
            print(f'Problema con los tipos en metodo "{actual_method.name}"')
            self.errors.append(f'Problema con los tipos en metodo "{actual_method.name}"')
    
    @visitor.when(ExprBlockNode)
    def visit(self, node: ExprBlockNode, scope:Scope):
        expr_return_type=self.context.get_type('Object')
        for expr in node.expr_list:
            expr_return_type=self.visit(expr,scope)
        return expr_return_type
    
    @visitor.when(LetNode)
    def visit(self, node: LetNode, scope:Scope):
        new_scope=scope.create_child()
        for assign in node.assign_list:
            self.visit(assign,new_scope)
        type_expr=self.visit(node.expr,new_scope)
        return type_expr
    
    
    @visitor.when(WhileNode)
    def visit(self, node: WhileNode, scope:Scope):
        expr_type:Type=self.visit(node.cond,scope)
        if(not expr_type.name!='Boolean'):
            print(f'Tiene que haber una expresion booleana')
            self.errors.append(f'Tiene que haber una expresion booleana')
        new_scope=scope.create_child()
        while_block_type= self.visit(node.body,new_scope)
        return while_block_type
    
    @visitor.when(ForNode)
    def visit(self, node: ForNode, scope:Scope):
        
        #magia con la expresion para ver si iterable 
        
        new_scope =scope.create_child()
        expr_type:Type =self.visit(node.iterable,scope)
        
        #chequeando que implemente los metodos necesarios para ser iterable
        next_func:Method= expr_type.get_method('next')
        current_func:Method= expr_type.get_method('current')
        if(next_func.return_type.name!='Boolean'):
            self.errors.append(f'Ninguna no es iterable este for')    
        new_scope.define_variable( node.id, self.context.get_type('Number'))
        
        
        return self.visit(node.body,new_scope)
    
    @visitor.when(DestrAssign)
    def visit(self, node: DestrAssign, scope:Scope):
        
        
        variable_type=self.visit(node.id)
        type:Type=self.visit(node.expr,scope)
        if(not type.conforms_to(variable_type)):
            self.errors.append(INCOMPATIBLE_TYPES)
            raise
        return variable_type
    
    @visitor.when(MethodCallNode)
    def visit(self, node: MethodCallNode, scope:Scope):
        obj_type = self.visit(node.obj,scope)
        actual_method:Method=obj_type.get_method(node.id)
        args_types:list[Type]=[]
        for arg in node.args:
            actual_type=self.visit(arg,scope)
            args_types.append(actual_type)
        real_params_types:list[Type]=actual_method.param_types
        if(len(real_params_types)!=len(args_types)):
            self.errors.append(f'Cantidad de argumanetos erronea')
            raise
        for i in range(len(real_params_types)):
            if not args_types[i].conforms_to(real_params_types[i]):
                self.errors.append(f'Tipo de argumento erroneo')
                raise
        return actual_method.return_type
    
    @visitor.when(AttrrCallNode)
    def visit(self ,node : AttrrCallNode, scope:Scope):
        
        

        instance_type:Type = self.visit(node.obj,scope)
        atrribute_in_type:Attribute =instance_type.get_attribute(node.id)
        return atrribute_in_type.type
        
        
    
    @visitor.when(FuncCallNode)
    def visit(self ,node : FuncCallNode, scope:Scope):
        
        #tipo donde guardo las funciones globales
        function_type:Type =self.context.get_type('Function')
        actual_function:Method =function_type.get_method(node.id)
        args_types:list[Type]=[]
        for arg in node.args:
            actual_type=self.visit(arg,scope)
            args_types.append(actual_type)
        real_params_types:list[Type]=actual_function.param_types
        if(len(real_params_types)!=len(args_types)):
            self.errors.append(f'Cantidad de argumanetos erronea')
            raise
        for i in range(len(real_params_types)):
            if not args_types[i].conforms_to(real_params_types[i]):
                self.errors.append(f'Tipo de argumento erroneo')
                raise
        return actual_function.return_type
    
    @visitor.when(InstantiateNode)
    def visit(self ,node : InstantiateNode, scope:Scope):
        
        type:Type=self.context.get_type(node.type)
        args_types:list[Type]=[]
        for arg in node.expr_list:
            actual_type=self.visit(arg,scope)
            args_types.append(actual_type)
        
        if(len(args_types)!=len(type.args)):
            self.errors.append(f'Incongruencia en cantidad de argumentos')
        for i in range(len(type.args)):
           if not args_types[i].conforms_to(type.args[i].type):
               self.errors.append(f'Incongruencia en tipo de argumentos')
        return type
    
    @visitor.when(VectorNode)
    def visit(self ,node : VectorNode, scope:Scope):
        last_type:Type=self.context.get_type('Object');
        for i in range(len(node.expr_list)):
            current_type:Type=self.visit(node.expr_list[i],scope)
            if not current_type.conforms_to(last_type):
                self.errors.append(f'En un vector los elementos tienen qe ser del mismo tipo')
                raise
        vector_type:Type=self.context.get_type('Vector')
        vector_type.define_method('current',[],[],last_type)
        
        return vector_type
    
    @visitor.when(DowncastNode)
    def visit(self, node:DowncastNode, scope:Scope):
        
        cast_type=self.context.get_type(node.type)
        instance_type=self.visit(node.obj,scope)
        if(not instance_type.conforms_to(cast_type)):
            self.errors.append(f'Intento erroneo de casteo')
        return cast_type
    
    @visitor.when(IndexingNode)
    def visit(self, node:IndexingNode, scope:Scope):
        type:Type=self.visit(node.vector,scope)
        protocolo_iterable= self.context.get_protocol('Iterable')
        if not implements_protocol(protocolo_iterable,type):
            self.errors.append(f'No iterable el tipo {type.name}')
            raise
        method_to_get_type:Method=type.get_method('current')
        return method_to_get_type.return_type
    
    @visitor.when(VarNode)
    def visit(self, node:VarNode, scope:Scope):
        if not scope.is_defined(node.lex):
            self.errors.append(VARIABLE_NOT_DEFINED)
            raise
        var =scope.find_variable(node.lex)
        return var.type
    
    @visitor.when(VarDefNode)
    def visit(self, node:VarDefNode, scope:Scope):
        
        if scope.is_local(node.id):
            self.errors.append(f'Variable {node.id} ya definidia')
            raise
        var_type=self.context.get_type(node.type);
        scope.define_variable(node.id,var_type)
        return var_type
    
    
        
def implements_protocol(protocol:Type,tipo:Type):
    for method in list(protocol.all_methods()):
        try :tipo.get_method(method[0].name)
        except: return False
    return True
# tipo_prueba=Type('Pruebita')
# tipo_prueba_padre=Type('Pruebota')
# tipo_prueba_padre.define_method('next',[],[],Type('Boolean'))
# tipo_prueba_padre.define_method('current',[],[],Type('Boolean'))
# tipo_prueba.set_parent(tipo_prueba_padre)
# print(list(tipo_prueba.all_methods())[0][0].name)