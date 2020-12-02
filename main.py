"""
Usage:
from boolparser import *
p = BooleanParser('<expression text>')
p.evaluate(variable_dict) # variable_dict is a dictionary providing values for variables that appear in <expression text>
"""
from itertools import product


class TokenType:
    BOOL, VAR, AND, OR, LP, RP = range(6)


class TreeNode:
    tokenType = None
    value = None
    left = None
    right = None

    def __init__(self, tokenType):
        self.tokenType = tokenType


class Tokenizer:
    def __init__(self, exp):
        self.expression = exp
        self.tokens = None
        self.tokenTypes = None
        self.vars = set()
        self.i = 0

    def next(self):
        self.i += 1
        return self.tokens[self.i - 1]

    def peek(self):
        return self.tokens[self.i]

    def hasNext(self):
        return self.i < len(self.tokens)

    def nextTokenType(self):
        return self.tokenTypes[self.i]

    def nextTokenTypeIsOperator(self):
        t = self.tokenTypes[self.i]
        return t == TokenType.AND or t == TokenType.OR

    def tokenize(self):
        import re
        reg = re.compile(r'(\bTRUE\b|\bFALSE\b|\bAND\b|\bOR\b|\(|\))')
        self.tokens = reg.split(self.expression)
        self.tokens = [t.strip() for t in self.tokens if t.strip() != '']

        self.tokenTypes = []
        for t in self.tokens:
            if t == 'AND':
                self.tokenTypes.append(TokenType.AND)
            elif t == 'OR':
                self.tokenTypes.append(TokenType.OR)
            elif t == '(':
                self.tokenTypes.append(TokenType.LP)
            elif t == ')':
                self.tokenTypes.append(TokenType.RP)
            elif t == "TRUE" or t == "FALSE":
                self.tokenTypes.append(TokenType.BOOL)
            else:
                if re.search('^[a-zA-Z_]+$', t):
                    self.vars.add(t)
                    self.tokenTypes.append(TokenType.VAR)
                else:
                    self.tokenTypes.append(None)

    def get_vars(self):
        return set(self.vars)


class BooleanParser:
    def __init__(self, exp):
        self.tokenizer = Tokenizer(exp)
        self.tokenizer.tokenize()
        self.vars = self.tokenizer.get_vars()
        self.parse()

    def parse(self):
        self.root = self.parseExpression()
        self.check_correctness()

    def parseExpression(self):
        if self.tokenizer.hasNext() and self.tokenizer.nextTokenType() == TokenType.LP:
            self.tokenizer.next()
            expression = self.parseExpression()
            if self.tokenizer.hasNext() and self.tokenizer.nextTokenType() == TokenType.RP:
                self.tokenizer.next()
                if self.tokenizer.hasNext() and self.tokenizer.nextTokenTypeIsOperator():
                    tokenType = self.tokenizer.nextTokenType()
                    self.tokenizer.next()
                    expression2 = self.parseExpression()
                    n = TreeNode(tokenType)
                    n.left = expression
                    n.right = expression2
                    return n
                return expression
            else:
                if self.tokenizer.hasNext():
                    raise Exception("Closing ) expected, but got " + self.tokenizer.next())
                else:
                    raise Exception("Closing ) expected, but got the end of the expression")

        terminal1 = self.parseTerminal()
        if self.tokenizer.hasNext() and self.tokenizer.nextTokenTypeIsOperator():
            condition = TreeNode(self.tokenizer.nextTokenType())
            self.tokenizer.next()
            # terminal2 = self.parseTerminal()
            expression2 = self.parseExpression()
            condition.left = terminal1
            # condition.right = terminal2
            condition.right = expression2
            return condition
        else:
            return terminal1

    def parseTerminal(self):
        if self.tokenizer.hasNext():
            tokenType = self.tokenizer.nextTokenType()
            if tokenType == TokenType.BOOL:
                n = TreeNode(tokenType)
                value = self.tokenizer.next()
                n.value = True if value == "TRUE" else False
                return n
            elif tokenType == TokenType.VAR:
                n = TreeNode(tokenType)
                n.value = self.tokenizer.next()
                return n
            else:
                raise Exception('BOOL or VAR expected, but got ' + self.tokenizer.next())

        else:
            raise Exception('BOOL or VAR expected, but got ' + self.tokenizer.next())

    def check_correctness(self):
        if self.tokenizer.hasNext():
            if self.tokenizer.nextTokenType() == TokenType.RP:
                raise Exception("Unexpected )")
            elif self.tokenizer.nextTokenType() == TokenType.LP:
                raise Exception("Unexpected (")
            elif self.tokenizer.nextTokenType() == TokenType.BOOL:
                raise Exception("Unexpected operand")
            elif self.tokenizer.nextTokenType() == TokenType.AND:
                raise Exception("Unexpected AND")
            elif self.tokenizer.nextTokenType() == TokenType.OR:
                raise Exception("Unexpected OR")

    def evaluate(self, variable_dict):
        return self.evaluateRecursive(self.root, variable_dict)

    def evaluateRecursive(self, treeNode, variable_dict):
        if treeNode.tokenType == TokenType.BOOL:
            return treeNode.value
        if treeNode.tokenType == TokenType.VAR:
            return variable_dict.get(treeNode.value)

        left = self.evaluateRecursive(treeNode.left, variable_dict)
        right = self.evaluateRecursive(treeNode.right, variable_dict)
        if treeNode.tokenType == TokenType.AND:
            return left and right
        elif treeNode.tokenType == TokenType.OR:
            return left or right
        else:
            raise Exception('Unexpected type ' + str(treeNode.tokenType))

    def get_vars(self):
        return self.vars


class Solver:
    def __init__(self, phrase1, phrase2):
        self.phrase1 = phrase1
        self.phrase2 = phrase2

    def check_equivalence(self):
        vars1 = self.phrase1.get_vars()
        vars2 = self.phrase2.get_vars()

        print(vars1)
        print(vars2)
        if vars1 != vars2:
            return False

        nrof_vars = len(vars1)
        for values in product([True, False], repeat=nrof_vars):
            print(values)
            variable_dict = dict(zip(vars1, values))

            if self.phrase1.evaluate(variable_dict) != self.phrase2.evaluate(variable_dict):
                return False

        return True


if __name__ == "__main__":
    try:
        # p1 = BooleanParser('(((FALSE OR b) AND FALSE) OR a)')
        # p2 = BooleanParser('(a OR (FALSE AND b) OR TRUE)')
        p1 = BooleanParser('(a AND (b OR c))')
        p2 = BooleanParser('((a AND b) OR (a AND c))')
        # variable_dict = {'a': False, 'b': True}
        # print(p1.get_vars())
        # print(p1.evaluate(variable_dict))
        solver = Solver(p1, p2)
        if solver.check_equivalence():
            print("Expressions are equivalent!")
        else:
            print("Expressions are not equivalent!")
    except Exception as e:
        print(e)
