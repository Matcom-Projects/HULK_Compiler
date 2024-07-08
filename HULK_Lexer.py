from Lexer.lexer import Lexer

class lex_error:
    def __init__(self,token):
        self.token= token

    def __str__(self):
        return f'({self.token.line},{self.token.line}) Lexicographical error : {self.token.lex}'
    
class hulk_lexer:
    def __init__(self, eof):
        nonzero_digits = '|'.join(str(n) for n in range(1,10))
        letters = '|'.join(chr(n) for n in range(ord('a'),ord('z')+1))
        upper_letters= '|'.join(chr(n) for n in range(ord('A'),ord('Z')+1))
        num1=f'({nonzero_digits})(0|{nonzero_digits})*.(0|{nonzero_digits})(0|{nonzero_digits})*'
        num2=f'({nonzero_digits})(0|{nonzero_digits})*'
        num3=f'0.(0|{nonzero_digits})(0|{nonzero_digits})*'
        number = '|'.join(n for n in [num1,num2,num3,'0'])   
        symbols='!|@|%|^|&|_|+|-|:|;|<|>|=|,|.|?|~|`|[|]|{|}|#|¿|¡|º|ª|¬'
        string= f'(")({symbols}|0| |{nonzero_digits}|{letters}|{upper_letters})*(")' 
        const='PI|E'
        bool= 'true|false'
        self.lexer = Lexer([
            ('for' , 'for'),
            ('let','let'),
            ('in','in'),
            ('if','if'),
            ('elif','elif'),
            ('else','else'),
            ('while','while'),
            ('as','as'),
            ('is','is'),
            ('new','new'),
            ('function','function'),
            ('type','type'),
            ('inherits','inherits'),
            ('protocol','protocol'),
            ('extends','extends'),
            ('+','+'),
            ('-','-'), 
            ('*','*'), 
            ('/','/'), 
            ('%','%'), 
            ('^','^'), 
            ('**','**'), 
            ('=','='), 
            (':=',':='), 
            ('==','=='), 
            ('!=','!='), 
            ('<','<'), 
            ('>','>'), 
            ('<=','<='), 
            ('>=','>='), 
            ('&','&'), 
            ('|','|'), 
            ('!','!'), 
            ('||','||'),
            ('.','.'), 
            (',',','), 
            (':',':'), 
            ('@','@'), 
            ('@@','@@'), 
            ('=>','=>'), 
            ('(','('), 
            (')',')'), 
            ('[','['), 
            (']',']'), 
            ('{','{'), 
            ('}','}'), 
            (';',';'),
            ('str', string),
            ('num',f'({number})'),
            ('bool',f'({bool})'),
            ('const',f'({const})'),
            ('space', '  *'),
            ('id', f'({letters})({letters}|0|{nonzero_digits}|{upper_letters})*'),
            ('type_id',f'({upper_letters})({letters}|0|{nonzero_digits}|{upper_letters})*')
        ], eof)
        self.eof = eof

    def __call__(self, text):
        tokens = self.lexer(text)
        tokens_return=[]
        unknowntokens =[]
        for tk in tokens:
            if tk.token_type == 'space':
                continue
            elif tk.is_valid:
                tokens_return.append(tk)
            else:
                unknowntokens.append(lex_error(tk))

        if len(unknowntokens)>0:
            return tokens_return,unknowntokens
        return tokens_return,None
    

