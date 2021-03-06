"""
Work of this module is to convert A parse tree to a Dot graph.

powered by pydot module
"""
import pydot
from src.parser import ParseNode, ParseTranslationUnit
from src.ast import SourceRoot
from src.lexer import Lexer
from src.source import FileSource
from src.token import TokenSource
# TODO: add CLI.


def convert_parse_tree_to_dot(graph: pydot.Dot, parse_node: ParseNode, father_node: pydot.Node):
    """function to convert parse tree to dot language."""
    node_label: str = str(parse_node.symbol if isinstance(
        parse_node.symbol, str) else parse_node.symbol.value) + " "
    node: pydot.Node = pydot.Node(
        name=str(id(parse_node)), label=node_label, shape="box")
    graph.add_node(node)
    if father_node:
        graph.add_edge(pydot.Edge(father_node, node))
    for child in parse_node.child:
        convert_parse_tree_to_dot(graph, child, node)


def generate_cst_dot(source_file: str, output_file: str):
    """parse and generate the dot file."""
    parse_tree_graph: pydot.Dot = pydot.Dot(graph_type='digraph')
    source: FileSource = FileSource(source_file)
    lexer: Lexer = Lexer(source)
    token_source = TokenSource(lexer.match())
    parse_tree = ParseTranslationUnit.parse(token_source)
    convert_parse_tree_to_dot(parse_tree_graph, parse_tree, None)
    parse_tree_graph.write(output_file)


def generate_ast_dot(source_file: str, output_file: str):
    """parse and generate the dot file."""
    ast_graph: pydot.Dot = pydot.Dot(graph_type='digraph')
    source: FileSource = FileSource(source_file)
    lexer: Lexer = Lexer(source)
    token_source = TokenSource(lexer.match())
    parse_tree = ParseTranslationUnit.parse(token_source)
    ast = SourceRoot.transform(parse_tree)
    convert_parse_tree_to_dot(ast_graph, ast, None)
    ast_graph.write(output_file)


if __name__ == '__main__':
    generate_ast_dot('test.tl', 'tree.dot')
