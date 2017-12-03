# coding: utf-8
# Author Santiago Chávez Novaro
from pyparsing import (Literal, CaselessLiteral, Word, Combine, Group, Optional,
                       ZeroOrMore, Forward, nums, alphas, oneOf)
import operator,math
# from scipy import constants
import re
import mpmath as mp
mp.mp.dps = 10000 # max: 100,000

class NumericStringParser(object):

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
        phy = CaselessLiteral("PH")
        expr = Forward()
        atom = ((Optional(oneOf("- +")) +
                 (ident + lpar + expr + rpar | pi | phy | e | fnumber).setParseAction(self.pushFirst))
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
        self.opn = {"+": mp.mp.fadd,
                    "-": mp.mp.fsub,
                    "*": mp.mp.fmul,
                    "/": mp.mp.fdiv,
                    "^": mp.power}
        self.fn = {"sqrt": mp.sqrt,
                   "sin": mp.sin,
                   "cos": mp.cos,
                   "tan": mp.tan,
                   "exp": mp.exp,
                   "abs": abs,
                   "trunc": lambda a: int(a),
                   "round": round,
                   "sgn": lambda a: abs(a) > epsilon and cmp(a, 0) or 0}

    def evaluateStack(self, s):
        op = s.pop()
        if op == 'unary -':
            # print "X1\n"
            return -self.evaluateStack(s)
        if op in "+-*/^":
            op2 = self.evaluateStack(s)
            op1 = self.evaluateStack(s)
            # print "X2\n"
            # print "op1:",type(op1),op1
            # print "op2:",type(op2),op2
            # HACK
            if isinstance(op1, tuple):
                op1 = op1[1]
            if isinstance(op2, tuple):
                op2 = op2[1]
            # print "op1:",type(op1),op1
            # print "op2:",type(op2),op2

            return self.opn[op](op1, op2)
        elif op == "PI":
            # print "X3\n"
            # print math.pi
            return mp.pi  # 3.1415926535...
        elif op == "E":
            # print "X4\n"
            # print math.e
            return mp.e  # 2.718281828...
        elif op == "PH":
            # print "X5\n"
            # print "PH:", mp.phi
            return mp.phi  # 1.61803398875...
        elif op in self.fn:
            # print "X6\n"
            return self.fn[op](self.evaluateStack(s))
        elif op[0].isalpha():
            # print "X7\n"
            return 0
        else:
            # print "X8\n"
            # return '{:.20f}'.format(float(op))
            return float(op)

    def eval(self, num_string, parseAll=True):
        num_string = num_string.replace('×','*').replace('e','E').replace('π','PI').replace('φ','PH')
        num_string = re.sub(r'√','sqrt',num_string)
        self.exprStack = []
        try:
            results = self.bnf.parseString(num_string, parseAll)
        except Exception as e:
            return 'ERROR'
        results = self.bnf.parseString(num_string, parseAll)
        val = self.evaluateStack(self.exprStack[:])
        return val