from cmp.pycompiler import EOF
from ParserLR1.Parser_LR1 import ShiftReduceParser

def evaluate_reverse_parse(right_parse, operations, tokens, complete_token=False):
    if not right_parse or not operations or not tokens:
        return

    right_parse = iter(right_parse)
    tokens = iter(tokens)
    stack = []
    for operation in operations:
        if operation == ShiftReduceParser.SHIFT:
            token = next(tokens)
            if complete_token:
                stack.append(token)
            else:
                stack.append(token.lex)
        elif operation == ShiftReduceParser.REDUCE:
            production = next(right_parse)
            head, body = production
            attributes = production.attributes
            assert all(rule is None for rule in attributes[1:]), 'There must be only synteticed attributes.'
            rule = attributes[0]

            if len(body):
                synteticed = [None] + stack[-len(body):]
                value = rule(None, synteticed)
                stack[-len(body):] = [value]
            else:
                stack.append(rule(None, None))
        elif operation == ShiftReduceParser.OK:
            break
        else:
            raise Exception('Invalid action!!!')

    assert len(stack) == 1
    assert isinstance(next(tokens).token_type, EOF)
    return stack[0]