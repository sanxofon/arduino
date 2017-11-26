# coding: utf-8
from __future__ import division
from pyparsing import (Literal, CaselessLiteral, Word, Combine, Group, Optional,
                       ZeroOrMore, Forward, nums, alphas, oneOf)
import math
import operator

from decimal import *
import readchar
import os,sys

#####################################################################
#####################################################################
class NumericStringParser(object):
    '''
    Most of this code comes from the fourFn.py pyparsing example

    '''

    def pushFirst(self, strg, loc, toks):
        self.exprStack.append(toks[0])

    def pushUMinus(self, strg, loc, toks):
        if toks and toks[0] == '-':
            self.exprStack.append('unary -')

    def __init__(self):
        """
        expop   :: '^'
        multop  :: '*' | '/'
        addop   :: '+' | '-'
        integer :: ['+' | '-'] '0'..'9'+
        atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
        factor  :: atom [ expop factor ]*
        term    :: factor [ multop factor ]*
        expr    :: term [ addop term ]*
        """
        point = Literal(".")
        e = CaselessLiteral("E")
        fnumber = Combine(Word("+-" + nums, nums) +
                          Optional(point + Optional(Word(nums))) +
                          Optional(e + Word("+-" + nums, nums)))
        ident = Word(alphas, alphas + nums + "_$")
        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("*")
        div = Literal("/")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")
        pi = CaselessLiteral("PI")
        expr = Forward()
        atom = ((Optional(oneOf("- +")) +
                 (ident + lpar + expr + rpar | pi | e | fnumber).setParseAction(self.pushFirst))
                | Optional(oneOf("- +")) + Group(lpar + expr + rpar)
                ).setParseAction(self.pushUMinus)
        # by defining exponentiation as "atom [ ^ factor ]..." instead of
        # "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-right
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + \
            ZeroOrMore((expop + factor).setParseAction(self.pushFirst))
        term = factor + \
            ZeroOrMore((multop + factor).setParseAction(self.pushFirst))
        expr << term + \
            ZeroOrMore((addop + term).setParseAction(self.pushFirst))
        # addop_term = ( addop + term ).setParseAction( self.pushFirst )
        # general_term = term + ZeroOrMore( addop_term ) | OneOrMore( addop_term)
        # expr <<  general_term
        self.bnf = expr
        # map operator symbols to corresponding arithmetic operations
        epsilon = 1e-12
        self.opn = {"+": operator.add,
                    "-": operator.sub,
                    "*": operator.mul,
                    "/": operator.truediv,
                    "^": operator.pow}
        self.fn = {"sin": math.sin,
                   "cos": math.cos,
                   "tan": math.tan,
                   "exp": math.exp,
                   "abs": abs,
                   "trunc": lambda a: int(a),
                   "round": round,
                   "sgn": lambda a: abs(a) > epsilon and cmp(a, 0) or 0}

    def evaluateStack(self, s):
        op = s.pop()
        if op == 'unary -':
            return -self.evaluateStack(s)
        if op in "+-*/^":
            op2 = self.evaluateStack(s)
            op1 = self.evaluateStack(s)
            return self.opn[op](op1, op2)
        elif op == "PI":
            return math.pi  # 3.1415926535
        elif op == "E":
            return math.e  # 2.718281828
        elif op in self.fn:
            return self.fn[op](self.evaluateStack(s))
        elif op[0].isalpha():
            return 0
        else:
            return float(op)

    def eval(self, num_string, parseAll=True):
        self.exprStack = []
        results = self.bnf.parseString(num_string, parseAll)
        val = self.evaluateStack(self.exprStack[:])
        return val
#####################################################################
#####################################################################


# Calcula la descomposicion en primos de un numero
# regresa una lista con los factores primos y sus exponentes
def primed(a):
    p, expo = 2, 0
    div = [[]]
    tmp = 0
    it = 0
    while p <= a:

        if a % p == 0:
            tmp = 1
            expo += 1
            a = a / p
            div[it] = [p,expo]
        else:

            if tmp ==1:
                it +=1
                div.append([ ])
                tmp = 0
            p += 1
            expo = 0
    return div

# multiplica con exponentes la lista y regresa el numero
def multi(L):
    res = 1
    for a in L:
        res = res*a[0]**a[1]
    return res

#Regresa el minimo comun multiplo de dos numeros
#Si el resultado es [1,1] son primos relativos
def mcm (a,b):
    A, B = primed(a), primed(b)
    mcc = []
    for a in A:
        for b in B:
            if a[0] == b[0]:
                mcc.append([a[0], min(a[1],b[1])])
    if mcc == []:
        mcc = [1,1]
    return mcc


# Aqui determina el periodo del denominador, si no tiene factores de 5 o de 2

def mpl (q):
    if q%5 == 0 or q%2==0:
        return -1
    k = 0
    stop = True
    while stop:
        k +=1
        if (10**k-1) % q == 0:

            stop = False
    return k        

## Determina el periodo de una fraccion y lo comprueba
def Periodo (q):
    # regresa: (i,j), donde i son los primeros y el periodo es j
    freQ, norep = [], [1]
    primeQ = primed(q)
    for a in primeQ:
        # OJO >> REVISAR SALIDA CUANDO NO HAY PUNTO FLOTANTE !!EXCEPCIÓN
        if len(a)<=0:
            return [0,0]
        if a[0]==2 or a[0]==5:
            norep.append(a[1])
        else:
            freQ.append(a)
    return [max(norep), mpl(multi(freQ))]

def confirma(p,q):
    rat = Decimal(p)/(Decimal(q) )
    print rat
    PL = Periodo(q)
    nrp, pl = PL[0], PL[1]
    cad = str(str(rat).split('.')[1])
    print cad[0:nrp]
    print "a: "+cad[nrp:pl+nrp ]
    print "b: "+cad[pl+nrp :pl+nrp +pl ]
    print nrp,pl


####################################################################
######## CAMBIOS DEL SANX ##########################################
def recibeChar(cadena='',dondestoy='p',p='',q=''):
    if (dondestoy=='q' and cadena=='1'):
        cadena = ''
    while 1:
        c = readchar.readchar()
        # print(c,ord(c))
        
        # SALIDAS
        if ord(c) == 27: # [ESC]
            # reiniciar programa
            return '','REINICIAR'
            break
        elif ord(c) == 3: # [CLTRL]+C
            # salir del programa
            return '','SALIR'
            break

        # IGUAL A
        elif ord(c)==10 or ord(c)==13 or ord(c)==61: # [ENTER] o [=] > Salto de línea o igual: '\n' ó '\r' ó '='
            # imprimir cadena RESULTADO
            return cadena,'RESULTADO'
            break

        # ESCRITURA NORMAL
        elif ord(c) == 8: # BACKSPACE
            # recortar cadena un digito
            if (len(cadena)>=1):
                cadena = cadena[:-1]
        elif (ord(c)>=48 and ord(c)<=57): # NUMEROS 0-9
            # incrementa la cadena con c
            cadena = cadena+c
        elif ord(c)==44 or ord(c)==46: # NUMEROS 0-9, COMA o PUNTO
            if ord(c)==44 or ord(c)==46:
                c='.' # Siempre usa punto
            # incrementa la cadena con c
            cadena = cadena+c

        # NUMEROS ESPECIALES e y pi
        elif (ord(c)==101):    # e => 101
            # Euler's number => 'e'
            c = 'E'
            # incrementa la cadena con c
            cadena = cadena+c
        elif (ord(c)==104):    # h => 104
            # PI => 'h'
            c = 'PI'
            # incrementa la cadena con c
            cadena = cadena+c
        
        # OPERACIONES SIMPLES: * + - /
        elif (ord(c)==42): # * => 42
            # incrementa la cadena con c
            cadena = cadena+c
        elif (ord(c)==43):    # + => 43
            # incrementa la cadena con c
            cadena = cadena+c
        elif (ord(c)==45):    # - => 45
            # incrementa la cadena con c
            cadena = cadena+c
        elif (ord(c)==47):    # / => 47
            # OPCION 1: incrementa la cadena con c ???
            # cadena = cadena+c
            # OPCION 2: Debe enviar al valor q sólo si no estamos ahí !!!???
            if (dondestoy!='q'):
                return cadena, 'SETQ'
                break

        # DENOMINADORES P, Q
        elif (ord(c)==112):    # p => 112
            # Debe enviar al valor p sólo si no estamos ahí
            if (dondestoy!='p'):
                return cadena, 'SETP'
                break
        elif (ord(c)==113):    # q => 113
            # Debe enviar al valor q sólo si no estamos ahí
            if (dondestoy!='q'):
                return cadena, 'SETQ'
                break

        if (dondestoy=='p'):
            p = cadena
        if (dondestoy=='q'):
            q = cadena
        if (q==''):
            q = '1'
        operacion(p,q)


    return cadena,'OK'

def pausa():
    while 1:
        c = readchar.readchar()
        if c!='':
            break


def calculadora(cadena='',p='',q='',dondestoy='p'):
    cadena,estado = recibeChar(cadena,dondestoy,p,q)
    # print(estado,cadena)
    if (estado=='RESULTADO'):
        if (dondestoy=='p'):
            p = cadena
        if (dondestoy=='q'):
            q = cadena
        if (q==''):
            q='1'
        nsp = NumericStringParser()
        res = nsp.eval(p+'/'+q)
        res = str(res)
        if (res[-2:]=='.0'):
            res=res[:-2]
        # res = p+'/'+q
        resultado(p,q, res)
        # pausa()
        calculadora(cadena,p,q,dondestoy)
    if (estado=='REINICIAR'):
        printhead()
        operacion(p='',q=1)
        calculadora()
    if (estado=='SALIR'):
        return
    if (estado=='SETP'):
        q = cadena
        dondestoy = 'p'
        calculadora(p,p,q,dondestoy)
    if (estado=='SETQ'):
        p = cadena
        dondestoy = 'q'
        calculadora(q,p,q,dondestoy)

def maxlen(p,q):
    maxlen = len(str(p))
    if (len(str(q))>maxlen):
        maxlen = len(str(q))
    lp = len(str(p))
    lq = len(str(q))
    return maxlen,lp,lq

def printhead():
    os.system('cls' if os.name == 'nt' else 'clear')
    print (' _____________________________________________ ')
    print ('|                                             |')
    print ('|               La calculadora                |')
    print ('|_____________________________________________|')
    print ('                                               ')

def printfoot():
    print (' ______________________________________________')
    print ('|                                              |')
    print ('|  TECLAS ACEPTADAS:                           |')
    print ('|      0-9  => Numeros                         |')
    print ('|        e  => Euler                           |')
    print ('|        h  => Pi                              |')
    print ('|        *  => Multiplicar                     |')
    print ('|        +  => Sumar                           |')
    print ('|        -  => Restar                          |')
    print ('|        /  => Dividir (Establecer divisor)    |')
    print ('|        p  => Establecer dividendo            |')
    print ('|        q  => Establecer divisor              |')
    print ('|   [ENTER] => Igual a                         |')
    print ('|     [ESC] => Reiniciar                       |')
    print ('|   [CTRL]+C => Salir del programa             |')
    print ('|______________________________________________|')


def operacion(p='',q=1):
    printhead()
    ml,lp,lq = maxlen(p,q)
    print ('       P      ' + (' '*(ml-lp)) + str(p))
    print ('     _____ =  '+('_'*ml))
    print (' ')
    print ('       Q      ' + (' '*(ml-lq)) + str(q))
    printfoot() # Imprime instructivo

def resultado(p,q, res):
    printhead()
    ml,lp,lq = maxlen(p,q)
    print ('       P      ' + (' '*(ml-lp)) + str(p))
    print ('     _____ =  ' + ('_'*ml) + ' = ' + str(res))
    print (' ')
    print ('       Q      ' + (' '*(ml-lq)) + str(q))
    print (' ')

    ################################################
    # Calcula p y q numericamente a floats
    nsp = NumericStringParser()
    fp = int(nsp.eval(p))
    fq = int(nsp.eval(q))

    ################################################
    ####### AQUÍ VAN LOS CALCULOS DE PERIODO #######

    PL = Periodo(fq)
    prec = (PL[0]+2)*(PL[1]+5)
    getcontext().prec = prec

    res = Decimal(fp)/Decimal(fq)
    # print 'res:',res

    nrp, pl = PL[0], PL[1]
    cad = str(res).split('.')
    if len(cad)>1:
        precad = cad[0]
        cad = str(str(res).split('.')[1])
        repite = cad[nrp-1:pl+nrp-1]
    else: # No tiene decimales
        precad = ''
        cad = ''
        repite = ''

    # IMPRIME LOS DETALLES DEL PERIODO
    print 'LONGITUD DEL PERIODO: '+str(PL[1])
    print 'PERIODO: '+str(repite)
    print 'ANTES DEL PERIODO: '+precad+'. '+str(cad[0:nrp-1])
    print 'PRECISION: '+str(prec)
    print 'RESULTADO: '+str(res)

    ################################################
    printfoot() # Imprime instructivo

####################################################
### START DEMO #####################################
printhead()
operacion(p='',q=1)
calculadora()