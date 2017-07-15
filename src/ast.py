"""
transform a concrete syntax tree(CST) to a abstract syntax tree(AST)

[AST structure form](http://www.cs.xu.edu/csci310/09s/ast.html)
"""

from .parser import ParseNode
from .token import Token
from .exceptions import TransformException


class SourceRoot(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        ast_node = cls("source root")

        if cst_node.symbol == "translation Unit":
            for node in cst_node.child:
                ast_node.child.append(ExternalDecl.transform(node))
        else:
            raise TransformException("expect a translation Unit node as the root of AST.")

        return cst_node


class ExternalDecl(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        ast_node = cls("external declaration")

        ast_node.child.append(cst_node.child[0])
        if cst_node.child[1].symbol == "init declarator list":
            ast_node.child.append(InitDeclaratorList.transform(cst_node.child[1]))
        else:
            ast_node.child.append(FunctionDefinition.transform(cst_node.child[1]))

        return cst_node


class InitDeclaratorList(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        ast_node = cls("init declarator list")

        for node in cst_node.child:
            if len(node.child) != 1:
                ast_node.child.append(AsignmentExp.transform(node))
            else:
                ast_node.child.append(node.child[0])

        return ast_node


class FunctionDefinition(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        ast_node = cls("function definition")

        ast_node.child.append(cst_node.child[0])
        for node in ast_node.child[1:]:
            if node.symbol == "param list":
                ast_node.child.append(ParamList.transform(node))
            elif node.symbol == "compound statement":
                ast_node.child.append(CompoundStat.transform(node))

        return ast_node


class ParamList(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        ast_node = cls("param list")
        
        for node in ast_node.child:
            if node.symbol == "param decl":
                ast_node.child.append(ParamDecl.transform(node))

        return ast_node


class ParamDecl(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        ast_node = cls("param decl")

        for node in cst_node.child:
            ast_node.child.append(node)

        return ast_node


class CompoundStat(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        ast_node = cls("compound statement")

        for node in cst_node.child:
            if node.symbol == "declaration list":
                ast_node.child.append(LocalDeclList.transform(node))
            elif node.symbol == "statement list":
                ast_node.child.append(StatList.transform(node))

        return ast_node


class LocalDeclList(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        ast_node = cls("declaration list")

        for node in cst_node.child:
            ast_node.child.append(node.child[0])
            ast_node.child.append(InitDeclaratorList.transform(node.child[1]))

        return ast_node


class StatList(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        ast_node = cls("statement list")

        for node in cst_node.child:
            ast_node.child.append(Statement.transform(node))

        return ast_node


class Statement(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        if cst_node.child[0].symbol == "labeled statement":
            return LabeledStat.transform(cst_node.child[0])
        elif cst_node.child[0].symbol == "expression statement":
            return ExpStat.transform(cst_node.child[0])
        elif cst_node.child[0].symbol == "compound statement":
            return CompoundStat.transform(cst_node.child[0])
        elif cst_node.child[0].symbol == "selection statement":
            return SelectionStat.transform(cst_node.child[0])
        elif cst_node.child[0].symbol == "iteration statement":
            return IterationStat.transform(cst_node.child[0])
        elif cst_node.child[0].symbol == "jump statement":
            return JumpStat.transform(cst_node.child[0])


class LabeledStat(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        ast_node = None

        if isinstance(cst_node.child[0].symbol, Token) and cst_node.child[0].symbol.value == "case":
            ast_node = cls(cst_node.child[0].symbol)
            ast_node.child.append(Expression.transform(cst_node.child[1]))
            ast_node.child.append(Statement.transform(cst_node.child[1]))
        elif isinstance(cst_node.child[0].symbol, Token) and cst_node.child[0].symbol.value == "default":
            ast_node = cls(cst_node.child[0].symbol)
            ast_node.child.append(Statement.transform(cst_node.child[1]))

        return ast_node


class ExpStat(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        ast_node = cls("expression statement")

        if cst_node.child[0].symbol == "expression":
            ast_node.child.append(Expression.transform(cst_node.child[0]))

        return ast_node


class SelectionStat(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        ast_node = None

        if isinstance(cst_node.child[0].symbol, Token) and cst_node.child[0].symbol.value == "if":
            ast_node = cls("if then else")
            for node in cst_node[1:]:
                if node.symbol == "expression":
                    ast_node.child.append(Expression.transform(node))
                elif node.symbol == "statement":
                    ast_node.child.append(Statement.transform(node))
                elif isinstance(node.symbol, Token) and node.symbol.value == "else":
                    ast_node.child.append(Statement.transform(node))
        else:
            ast_node = cls("switch")
            for node in cst_node[1:]:
                if node.symbol == "expression":
                    ast_node.child.append(Expression.transform(node))
                elif node.symbol == "statement":
                    ast_node.child.append(Statement.transform(node))

        return ast_node


class IterationStat(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        ast_node = None

        if isinstance(cst_node.child[0].symbol, Token) and cst_node.child[0].symbol.value == "do":
            ast_node = cls("do while")
        else:
            ast_node = cls("while do")
        for node in cst_node[1:]:
            if node.symbol == "expression":
                ast_node.child.append(Expression.transform(node))
            elif node.symbol == "statement":
                ast_node.child.append(Statement.transform(node))

        return ast_node


class JumpStat(ParseNode):

    # TODO: Do I need check if there are semantic error.
    @classmethod
    def transform(cls, cst_node):
        ast_node = cls(cst_node.child[0].symbol)
        if isinstance(cst_node.child[1].symbol, str) and cst_node.child[1] == "expression":
            ast_node.child.append(Expression.transform(ast_node.child[1]))

        return ast_node


class Expression(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        pass


class AsignmentExp(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        if len(cst_node.child) > 1:
            if cst_node.child[1].symbol.value == '=':
                ast_node = cls(cst_node.child.pop(1).symbol)
                ast_node.child.append(UnaryExp.transform(cst_node.child.pop(0)))
                ast_node.child.append(cls.transform(cst_node))
            else:
                ast_node = cls('=')
                ast_node.child.append(UnaryExp.transform(cst_node.child[0]))
                ast_node.child.append(cst_node.child.pop(1).symbol.value[0])
                ast_node.child[1].child.append(UnaryExp.transform(cst_node.child.pop(0)))
                ast_node.child[1].child.append(cls.transform(cst_node))
        else:
            return LogicalOrExp.transform(cst_node.child[0])

        return ast_node


class LogicalOrExp(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        if len(cst_node.child) > 1:
            ast_node = cls(cst_node.child.pop(1).symbol)
            ast_node.child.append(LogicalAndExp.transform(cst_node.child.pop(0)))
            ast_node.child.append(LogicalAndExp.transform(cst_node))
        else:
            return LogicalAndExp.transform(cst_node)

        return ast_node


class LogicalAndExp(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        if len(cst_node.child) > 1:
            ast_node = cls(cst_node.child.pop(1).symbol)
            ast_node.child.append(EqualityExp.transform(cst_node.child.pop(0)))
            ast_node.child.append(EqualityExp.transform(cst_node))
        else:
            return EqualityExp.transform(cst_node)

        return ast_node


class EqualityExp(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        if len(cst_node.child) > 1:
            ast_node = cls(cst_node.child.pop(1).symbol)
            ast_node.child.append(RelationalExp.transform(cst_node.child.pop(0)))
            ast_node.child.append(RelationalExp.transform(cst_node))
        else:
            return RelationalExp.transform(cst_node)

        return ast_node


class RelationalExp(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        if len(cst_node.child) > 1:
            ast_node = cls(cst_node.child.pop(1).symbol)
            ast_node.child.append(AdditiveExp.transform(cst_node.child.pop(0)))
            ast_node.child.append(AdditiveExp.transform(cst_node))
        else:
            return AdditiveExp.transform(cst_node)

        return ast_node


class AdditiveExp(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        if len(cst_node.child) > 1:
            ast_node = cls(cst_node.child.pop(1).symbol)
            ast_node.child.append(MultExp.transform(cst_node.child.pop(0)))
            ast_node.child.append(MultExp.transform(cst_node))
        else:
            return MultExp.transform(cst_node)

        return ast_node


class MultExp(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        if len(cst_node.child) > 1:
            ast_node = cls(cst_node.child.pop(1).symbol)
            ast_node.child.append(CastExp.transform(cst_node.child.pop(0)))
            ast_node.child.append(CastExp.transform(cst_node))
        else:
            return CastExp.transform(cst_node)

        return ast_node


class CastExp(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        if isinstance(cst_node.child[0], Token) and  cst_node.child[0].symbol.value == '(':
            ast_node = cls(cst_node.child.pop(1).symbol)
            cst_node.child.pop(0)
            cst_node.child.pop(0)
            ast_node.child.append(UnaryExp.transform(cst_node))
        else:
            return UnaryExp.transform(cst_node)


class UnaryExp(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        if isinstance(cst_node.child[0], Token) and  cst_node.child[0].symbol.value in ('++', '--'):
            ast_node = cls(cst_node.child[0].symbol)
            if cst_node.child[1].symbol.value in ('+', '-', '!'):
                raise TransformException("semantic error")
            else:
                ast_node.child.append(PostfixExp.transform(cst_node.child[1]))
        else:
            if cst_node.child[0].symbol.value in ('+', '-', '!'):
                ast_node = cls(cst_node.child[0].symbol)
                ast_node.child.append(cst_node.child[1].symbol.value)
            else:
                return CastExp.transform(cst_node.child[0])

        return ast_node


class PostfixExp(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        pass


class PrimaryExp(ParseNode):

    @classmethod
    def transform(cls, cst_node):
        pass
