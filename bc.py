import re
import sys
from typing import Any, List, Union

if len(sys.argv) != 2:
    print("Usage: python3 program_name.py [input_file]")
    sys.exit()


class Node:
    def __init__(self, value: Any, children: List = None):
        self.value = value
        self.children = children if children else []


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
        while self.tokens:
            children.append(self.parse_statement())
        return Node("statement_list", children)

    def parse_statement(self) -> Node:
        token = self.peek_next_token()
        if token == "print":
            node = self.parse_print_statement()
        elif re.match(r'\w+', token):
            var = self.get_next_token()
            if self.peek_next_token() == "=":
                self.get_next_token()
                node = Node("assignment", [Node(var), self.parse_expression()])
            else:
                node = Node("expression", [Node(var)])
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
            right = self.parse_unary_expression()
            left = Node(op, [left, right])

        return left

    def parse_unary_expression(self) -> Node:
        if self.peek_next_token() == "-":
            op = self.get_next_token()
            right = self.parse_primary_expression()
            return Node(op, [right])
        else:
            return self.parse_primary_expression()

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
        elif node.value == "print_statement":
            for expr in node.children:
                try:
                    print(self.evaluate(expr), end=' ')
                except DivideByZeroError:
                    print("divide by zero", end=' ')
            print()
        elif node.value == "expression":
            return self.evaluate(node.children[0])
        elif node.value in ["+", "-", "*", "/", "%", "^"]:
            left = self.evaluate(node.children[0])
            right = self.evaluate(node.children[1])
            if node.value == "+":
                return left + right
            elif node.value == "-":
                return left - right
            elif node.value == "*":
                return left * right
            elif node.value == "/":
                if right == 0:
                    raise DivideByZeroError()
                return left / right
            elif node.value == "%":
                return left % right
            elif node.value == "^":
                return left ** right
        elif isinstance(node.value, float):
            return node.value
        else:
            return self.variables.get(node.value, 0.0)


def main():
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

    # print 2 ^ 2 ^ 2

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

    # """

    filename = sys.argv[1]
    with open(str(filename), 'r') as f:
        input_str = f.read()
    parser = Parser(input_str)

    try:
        ast = parser.parse()
        parser.evaluate(ast)
    except ParseError as e:
        print("parse error")


if __name__ == "__main__":
    main()
