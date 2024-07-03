from Lexer.lexer import Lexer



nonzero_digits = '|'.join(str(n) for n in range(1,10))
letters = '|'.join(chr(n) for n in range(ord('a'),ord('z')+1))


lexer = Lexer([
    ('num', f'({nonzero_digits})(0|{nonzero_digits})*'),
    ('for' , 'for'),
    ('foreach' , 'foreach'),
    ('space', '  *'),
    ('id', f'({letters})({letters}|0|{nonzero_digits})*')
], 'eof')


text = '5465 for 45foreach fore'

tokens = lexer(text)

print(tokens)
assert [t.token_type for t in tokens] == ['num', 'space', 'for', 'space', 'num', 'foreach', 'space', 'id', 'eof']
assert [t.lex for t in tokens] == ['5465', ' ', 'for', ' ', '45', 'foreach', ' ', 'fore', '$']

text = '4forense forforeach for4foreach foreach 4for'
print(f'\n>>> Tokenizando: "{text}"')
tokens = lexer(text)
print(tokens)
assert [t.token_type for t in tokens] == ['num', 'id', 'space', 'id', 'space', 'id', 'space', 'foreach', 'space', 'num', 'for', 'eof']
assert [t.lex for t in tokens] == ['4', 'forense', ' ', 'forforeach', ' ', 'for4foreach', ' ', 'foreach', ' ', '4', 'for', '$']