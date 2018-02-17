# Create an AST from a boolean expression. AST is a tuple
# consisting of an operator and a list of operands.
#
# Note: NOT is not supported.

# Example:
#   given a AND b
#   returns ('AND', ['a','b'])
#
# Copyright 2006, by Paul McGuir
# Modified: 02/2011 for csci1580
# Modified: 02/2018 for data2040

from typing import Union

import pyparsing


class BoolOperand(object):
    reprsymbol = None

    def __init__(self, t):
        self.args = t[0][0::2]

    def __str__(self):
        sep = " %s " % self.reprsymbol
        return "(" + sep.join(map(str, self.args)) + ")"

    def eval_expr(self):
        raise NotImplementedError


class BoolAnd(BoolOperand):
    reprsymbol = 'AND'

    def eval_expr(self):
        lst = []
        for arg in self.args:
            if not isinstance(arg, BoolOperand):
                elem = arg
            else:
                elem = arg.eval_expr()
            lst.append(elem)
        return self.reprsymbol, lst


class BoolOr(BoolOperand):
    reprsymbol = 'OR'

    def eval_expr(self):
        lst = []
        for arg in self.args:
            if not isinstance(arg, BoolOperand):
                elem = arg
            else:
                elem = arg.eval_expr()
            lst.append(elem)
        return self.reprsymbol, lst


BOOL_OPERAND = pyparsing.Word(pyparsing.alphanums +
                              "!#$%&'*+,-./:;<=>?@[]^_`{|}~\\")
OP_LIST = [("AND", 2, pyparsing.opAssoc.LEFT, BoolAnd),
           ("OR", 2, pyparsing.opAssoc.LEFT, BoolOr)]
BOOL_EXPR = pyparsing.operatorPrecedence(BOOL_OPERAND, OP_LIST)


def bool_expr_ast(expr: str) -> Union[str, tuple]:
    expr = expr.strip()
    parsed_expr = BOOL_EXPR.parseString(expr)[0]
    if not isinstance(parsed_expr, BoolOperand):
        return expr
    return parsed_expr.eval_expr()
