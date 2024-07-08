from Grammar import G
from cmp.evaluation import evaluate_reverse_parse
from ParserLR1.Parser_LR1 import LR1Parser
from CodeGeneration.gen import GenCode
import sys
import dill
import os
import subprocess

def load_src():
    route = os.getcwd()
    try:
        # with open(os.path.join(route, 'lexer.pkl'), 'rb') as lexer_file:
        #     lexer = dill.load(lexer_file)

        with open(os.path.join(route, 'parser.pkl'), 'rb') as parser_file:
            parser = dill.load(parser_file)

        return parser
    except:
        # lexer =
        parser = LR1Parser(G)

        # with open(os.path.join(route, 'lexer.pkl'), 'wb') as lexer_file:
        #     dill.dump(lexer, lexer_file)

        with open(os.path.join(route, 'parser.pkl'), 'wb') as parser_file:
            dill.dump(parser, parser_file)

        return parser #, lexer

def run_cpp(text):
    with open('temp.cpp', 'w') as file:
        file.write(text)

    compilation = subprocess.Popen(["g++", "temp.cpp", "-o", "temp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = compilation.communicate()

    execution = subprocess.Popen("temp", stdout=subprocess.PIPE)
    output, _ = execution.communicate()
    print(output.decode())

def exec_file():
    parser = load_src()
    print(parser)
    with open(sys.argv[1]) as opened_file:
        text = opened_file.read()
    tokens = lexer(text)
    parse, operations = parser([token.token_type for token in tokens], True)
    ast = evaluate_reverse_parse(parse,operations,tokens)
    # errors = []
    # collector = Collector(errors)
    # collector.visit(ast)
    # context = collector.context
    # builder = TypeBuilder(context, errors)
    # builder.visit(ast)
    # checker = TypeChecker(context, errors)
    # scope = checker.visit(ast)
    text = GenCode(ast, context)
    run_cpp(text)

if __name__ == "__main__":
    if len(sys.argv) != 1:
        exec_file()
    else:
        print("Must provide a file to compile and run.")