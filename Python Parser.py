class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.type == other.type and self.value == other.value
        return False

    def __repr__(self):
        return f'Token({self.type}, {self.value})'


class Lexer:
    def __init__(self, input):
        self.input = input
        self.position = 0

    #helper function for tokenize
    def whitespace(self):
        while self.position < len(self.input) and self.input[self.position].isspace():
            self.position += 1

    def tokenize(self):
        #declare list tokens
        tokens = []
        #loop as long as position is less than the len of input
        while self.position < len(self.input):
            char = self.input[self.position]
            #if char is whitespace, call helper function whitespace and increment position by 1
            if char.isspace():
                self.whitespace()
                continue #use continue built in to reject all other cases if this case is true
            #handle alphabetic chars
            if char.isalpha():
                start_pos = self.position
                while self.position < len(self.input) and self.input[self.position].isalpha():
                    self.position += 1
                tokens.append(Token("VARIABLE", self.input[start_pos:self.position]))
                continue
            #handle digit cases
            if char.isdigit():
                start_pos = self.position
                while self.position < len(self.input) and self.input[self.position].isdigit():
                    self.position += 1
                tokens.append(Token("INTEGER", int(self.input[start_pos:self.position]))) 
                continue
            #create new dictionary with keys as tokens and their values as the types
            token_dict = {'+': "OPERATOR",'-': "OPERATOR", '*': "OPERATOR", '/': "OPERATOR",'=': "ASSIGN",';': "SEMICOLON",'(': "PARENTHESIS",')': "PARENTHESIS"
            }
            if char in token_dict:
                tokens.append(Token(token_dict[char], char))
                self.position += 1
                continue
            #raise exception if char is invalid at a given
            raise Exception(f"Invalid character '{char}' at position {self.position}.")  # Modified error message
        #return list of tokens
        return tokens 

class Node:
    def __init__(self, type, value=None, children=None):
        self.type = type
        self.value = value
        self.children = children if children is not None else []

    def __str__(self, level=0):
        ret = "\t" * level + f'{self.type}: {self.value}\n'
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def consume(self, expected_type=None):
        #first check if there are more tokens to consume
        if self.position >= len(self.tokens):
            #if there arent, raise an exception
            raise Exception("Syntax error: unexpected end of input")
        #check if a token matches the expected type that defaults to none
        if expected_type and self.tokens[self.position].type != expected_type:
            raise Exception(f"Syntax error: Expected token type {expected_type} but got {self.tokens[self.position].type}")
        
        #retrieve current token and increment the position
        current_token = self.tokens[self.position]
        self.position += 1
        return current_token 

    def peek(self):

        if self.position >= len(self.tokens):
            raise Exception("Syntax error: unexpected end of input")
        return self.tokens[self.position]

    #call helper function to begin parsing through the list nodes 
    def parse(self):
        return self.parse_statement_helper() 
    
    #helper for parse
    #creates list nodes and loops through nodes as long as positon is less than len of the tokens
    def parse_statement_helper(self):
        nodes = []
        while self.position < len(self.tokens):
            nodes.append(self.parse_statement())
        return Node('Program', children=nodes)


    def parse_statement(self):
        return self.parse_assignment() 

    def parse_assignment(self):
        #parse through an assignment
        variable_token = self.peek()
        if variable_token.type != "VARIABLE":
            raise Exception(f"Syntax error: Unexpected token {variable_token.type}. Expected VARIABLE.")
        self.consume("VARIABLE")
        
        self.consume("ASSIGN")

        expression_node = self.parse_expression()
        self.consume("SEMICOLON")
        return Node('Assignment', value=variable_token.value, children=[expression_node]) 

    def parse_expression(self):
        term_node = self.parse_term()
        #check operators after parsing a term
        while self.position < len(self.tokens) and self.tokens[self.position].type == "OPERATOR":
            operator_token = self.consume("OPERATOR")
            next_term_node = self.parse_term()
            term_node = Node('Expression', value=operator_token.value, children=[term_node, next_term_node])

        return term_node

    #takes no input
    def parse_term(self):
        #set current token to peek method

        current_token = self.peek()
        #parse different expressions
        if current_token.type == "INTEGER":
            return Node('Term', value=self.consume("INTEGER").value)

        #if we reach a certain variable, call consume and return a new term node
        if current_token.type == "VARIABLE":
            return Node('Term', value=self.consume("VARIABLE").value)

        #we have found opening parathensis, which means we have reach an enclosed expression
        if current_token.type == "PARENTHESIS" and current_token.value == "(":
            self.consume("PARENTHESIS")
            expression_node = self.parse_expression()

            #after parsing, there ust be closing parenthesis
            if self.peek().type != "PARENTHESIS":
                raise Exception(f"Syntax error: Expected closing parenthesis but found {self.peek().type}")
            self.consume("PARENTHESIS")
            return expression_node
        
        #if a given token doesnt match any of the above cases raise an exception
        raise Exception(f"Syntax error: Unexpected token {current_token.type} at position {self.position}")  


