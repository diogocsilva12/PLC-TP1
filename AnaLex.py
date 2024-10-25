import ply.lex as lex
import sys

# Define os tokens da linguagem
tokens = (
    'PAL',          # Identificadores
    'VIRG',         # Vírgula ,
    'MENOR',        # Símbolo menor <
    'MAIOR',        # Símbolo maior >
    'INTERROGA',    # Interrogação ?
    'PONTO',        # Ponto final .
    'DOISPONTOS',   # Dois pontos :
    'PONTOEVIRG',   # Ponto e vírgula ;
    'EXCLAMACAO',   # Exclamação !
    'INTEIRO',      # Número inteiro
    'REAL',         # Número decimal
    'STRING',       # Strings entre aspas
    'OPERADOR',     # Operadores aritméticos (+, -, *, /)
    'OPERADOR_LOGICO', # Operadores lógicos (and, or, not)
    'ATRIBUICAO',   # Atribuição =
    'PARENTESES_ESQ', # Parênteses esquerdo (
    'PARENTESES_DIR'  # Parênteses direito )
)

# Número decimal
def t_REAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

# Número inteiro
def t_INTEIRO(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Regras para tokens específicos
t_VIRG = r','
t_MENOR = r'<'
t_MAIOR = r'>'
t_INTERROGA = r'\?'
t_PONTO = r'\.'
t_DOISPONTOS = r':'
t_PONTOEVIRG = r';'
t_EXCLAMACAO = r'!'
t_OPERADOR = r'[\+\-\*/]'   # Operadores aritméticos
t_OPERADOR_LOGICO = r'\b(and|or|not)\b'
t_ATRIBUICAO = r'='
t_PARENTESES_ESQ = r'\('
t_PARENTESES_DIR = r'\)'

# Palavras alfanuméricas iniciadas por letra
t_PAL = r'[A-Za-z]\w*'      

# Strings entre aspas duplas
def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'  
    t.value = t.value[1:-1] # Remove as aspas
    return t

# Ignora espaços, tabs e quebras de linha
t_ignore = ' \r\n\t'

# Função para tratar erros de caracteres ilegais
def t_error(t):
    print('Carácter ilegal: ' + t.value[0])
    t.lexer.skip(1)

# Construção do Analisador Léxico
lexer = lex.lex()

# Programa principal para leitura da entrada
for linha in sys.stdin:
    lexer.input(linha)
    simb = lexer.token()
    while simb:
        print(simb)
        simb = lexer.token()
