import re
import sys
from typing import Any, List, Union


class Node:
    def __init__(self, value: Any, children: List = None):
        self.value = value
        self.children = children if children else []

    def __str__(self) -> str:
        print('VAL', self.value)
        # print(self.children)
        for node in self.children:
            print('CHIL', node.value)
        return ''


class ParseError(Exception):
    pass


class DivideByZeroError(Exception):
    pass


class Parser:
    def __init__(self, input_str: str):
        input_str = self.remove_comments(input_str)
        self.tokens = list(
            reversed(re.findall(r'[a-zA-Z_]\w*|\d+\.?\d*|[+\-*/%=^()]|\S+|\n', input_str)))

        self.variables = {}
        self.pre_variables = {}
        self.post_variables = {}

    def __str__(self):
        print(self.tokens)
        print(self.variables)
        return ""

    def remove_comments(self, input_str: str) -> str:
        # Remove multi-line comments
        input_str = re.sub(r'/\*.*?\*/', '', input_str, flags=re.DOTALL)
        # Remove single-line comments
        input_str = re.sub(r'#.*', '', input_str)
        return input_str

    def get_next_token(self) -> str:
        return self.tokens.pop() if self.tokens else None

    def peek_next_token(self) -> str:
        return self.tokens[-1] if self.tokens else None

    def parse(self) -> Node:
        return self.parse_statement_list()

    def parse_statement_list(self) -> Node:
        children = []
        self.main_list = Node("statement_list", children)
        while self.tokens:
            self.main_list.children.append(self.parse_statement())
        return self.main_list

    def parse_statement(self) -> Node:
        token = self.peek_next_token()
        if token == "print":
            node = self.parse_print_statement()
        elif re.match(r'\w+', token):
            var = self.get_next_token()
            # print('VAR', var)
            if self.peek_next_token() == "=":
                self.get_next_token()
                node = Node("assignment", [Node(var), self.parse_expression()])
            else:
                node = Node(self.get_next_token(), [
                            Node(var), self.parse_expression()])
        elif token == "\n":
            self.get_next_token()
            node = Node("empty_statement")
        else:
            node = Node("expression", [self.parse_expression()])

        if self.peek_next_token() == "\n":

            self.get_next_token()

        return node

    def parse_print_statement(self) -> Node:
        self.get_next_token()
        expressions = []

        while self.peek_next_token() not in ("\n", None):
            expressions.append(self.parse_expression())
            if self.peek_next_token() == ",":
                self.get_next_token()

        return Node("print_statement", expressions)

    def parse_expression(self) -> Node:
        return self.parse_additive_expression()

    def parse_additive_expression(self) -> Node:
        left = self.parse_multiplicative_expression()

        while self.peek_next_token() in ("+", "-"):
            op = self.get_next_token()
            right = self.parse_multiplicative_expression()
            left = Node(op, [left, right])

        return left

    def parse_multiplicative_expression(self) -> Node:
        left = self.parse_exponential_expression()

        while self.peek_next_token() in ("*", "/", "%"):
            op = self.get_next_token()
            right = self.parse_exponential_expression()
            left = Node(op, [left, right])

        return left

    def parse_exponential_expression(self) -> Node:
        left = self.parse_unary_expression()

        while self.peek_next_token() == "^":
            op = self.get_next_token()
            # right = self.parse_unary_expression()
            left = Node(op, [left, self.parse_exponential_expression()])

        return left

    def parse_unary_expression(self) -> Node:
        left = self.parse_prepostfix_expression()
        if not left:
            if self.peek_next_token() == "-":
                op = self.get_next_token()
                right = self.parse_primary_expression()
                return Node(op, [right])
            else:
                node = self.parse_prepostfix_expression(left)
                return self.parse_primary_expression()
        return left

    def create_increment_expression(self, var) -> Node:
        # print('HERE', self.peek_next_token())
        node2 = Node("+", [var, Node(float(1))])
        node1 = Node("assignment", [var, node2])
        return node1

    def create_decrement_expression(self, var) -> Node:
        node2 = Node("-", [var, Node(float(1))])
        node1 = Node("assignment", [var, node2])
        return node1

    def parse_prepostfix_expression(self, var=None) -> Node:
        if ''.join(self.tokens[-2:]) == '++':
            self.tokens.pop()
            self.tokens.pop()
            if not var:
                var = self.parse_primary_expression()
            if type(var.value) == float:
                raise ParseError(f"Unexpected token: {var.value}")
            # self.variables[var.value] += 1
            node = self.create_increment_expression(var)
            # self.main_list.children.append(node)
            return node
            # var = Node(float(self.variables[var.value]))
        elif ''.join(self.tokens[-2:]) == '--':
            self.tokens.pop()
            self.tokens.pop()
            if not var:
                var = self.parse_primary_expression()
            if type(var.value) == float:
                raise ParseError(f"Unexpected token: {var.value}")
            # self.variables[var.value] -= 1
            node = self.create_decrement_expression(var)
            # self.main_list.children.append(node)
            return node
            # var = Node(float(self.variables[var.value]))
        return None

    def parse_primary_expression(self) -> Node:
        token = self.peek_next_token()
        if token == "(":
            self.get_next_token()
            expr = self.parse_expression()
            if self.get_next_token() != ")":
                raise ParseError("Unbalanced parentheses")
            return expr
        elif token.isnumeric() or token.replace(".", "", 1).isnumeric():
            return Node(float(self.get_next_token()))
        elif re.match(r'\w+', token):
            return Node(self.get_next_token())
        else:
            raise ParseError(f"Unexpected token: {token}")

    # ... evaluation functions ...
    def evaluate(self, node: Node) -> Union[float, None]:
        if node.value == "statement_list":
            for child in node.children:
                self.evaluate(child)
        elif node.value == "empty_statement":
            return None
        elif node.value == "assignment":
            var = node.children[0].value
            self.variables[var] = self.evaluate(node.children[1])
            if len(node.children) > 2:
                self.evaluate(node.children[2])
            return self.variables[var]
        elif node.value == "print_statement":
            print_vals = []
            for expr in node.children:
                try:
                    print_vals.append(str(self.evaluate(expr)))
                    # print(self.evaluate(expr))
                except DivideByZeroError:
                    print_vals.append("divide by zero")
                    # print("divide by zero", end=' ')
            # print('HERE', print_vals)
            print(" ".join(print_vals))
        elif node.value == "expression":
            return self.evaluate(node.children[0])
        elif node.value in ["+", "-", "*", "/", "%", "^"]:
            left = self.evaluate(node.children[0])
            right = None
            if len(node.children) >= 2:
                right = self.evaluate(node.children[1])
            if node.value == "+":
                return left + right
            elif node.value == "-":
                return left - right if right else -left
            elif node.value == "*":
                return left * right
            elif node.value == "/":
                if right == 0:
                    raise DivideByZeroError()
                return left / right
            elif node.value == "%":
                return left % right
            elif node.value == "^":
                # print('POWER', left, right)
                return left ** right
        elif isinstance(node.value, float):
            return node.value
        else:
            return self.variables.get(node.value, 0.0)


def main():
    input_str = sys.stdin.read()
    # input_str = """
    #             # first example
    # x=2
    # z = 3
    # y= --x + z + --x
    # print y
    #     """
    # """#TC-2
    #     x  = 3
    #     y  = 5
    #     z  = 2 + x * y
    #     z2 = (2 + x) * y
    #     print x, y, z, z2
    #     """
    # input_str = """

    # # first example
    # x=3
    # y=5
    # z =2+x*y
    # z2 = (2 + x) * y
    # print x, y, z, z2

    # # second example
    # pi = 3.14159
    # r=2
    # area = pi * r^2
    # print area

    # #third example

    # x = 1

    # print x

    # # Fourth example

    # print 5 - 1 - 1 - 1

    # # Fifth example

    # print ((5 - 1) - 1) - 1

    # # Sixth example

    # print 2 ^ 3 ^ 2

    # # Seventh Example

    # print 1
    # print 2

    # # Eight Example - Extension ( comments feature)

    # x = 1
    # /*
    # x = 2
    # y = 3
    # */
    # y = 4
    # # print 0
    # print x, y

    # # Ninth Example

    # print 0 / 1, 1 / 0

    # x=2
    # z = 3
    # y= ++x + z + --x
    # print y

    # 1/0
    # """

    # input_str = "1/0"

    parser = Parser(input_str)
    # print(parser)
    try:
        ast = parser.parse()
        # print(ast)
    except ParseError as e:
        print("parse error")
        return
    try:
        parser.evaluate(ast)
    except DivideByZeroError as e:
        print('divide by zero')


if __name__ == "__main__":
    main()
