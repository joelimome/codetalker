#!/usr/bin/env python

from tokens import Token
import types
import inspect
from nodes import AstNode

from errors import CodeTalkerException

class TranslatorException(CodeTalkerException):
    pass

class Scope:
    pass

class Translator:
    def __init__(self, grammar):
        self.grammar = grammar
        self.register = {}

    def translates(self, what):
        if inspect.isclass(what):
            if issubclass(what, Token) and what in self.grammar.tokens:
                what = -(self.grammar.tokens.index(what) + 1)
            elif issubclass(what, AstNode):
                pass
            else:
                raise TranslatorException('Unexpected translation target: %s' % what)
        else:
            raise TranslatorException('Unexpected translation target: %s' % what)
        def meta(func):
            self.register[what] = func
        return meta

    def translate(self, tree, scope):
        if isinstance(tree, Token):
            which = -(self.grammar.tokens.index(tree.__class__) + 1)
        else:
            which = tree.__class__
        if which not in self.register:
            if which >= 0:
                raise TranslatorException('unknown rule to translate (%s)' % self.grammar.rule_names[which])
            else:
                raise TranslatorException('unknown token to translate (%s)' % self.grammar.tokens[-(which + 1)])
        return self.register[which](tree, scope)

    def from_string(self, text, **args):
        tree = self.grammar.to_ast(self.grammar.process(text))
        return self.from_ast(tree, **args)

    def from_ast(self, tree, **args):
        Scope = type('Scope', (), {'__slots__': tuple(args.keys())})
        scope = Scope()
        for k,v in args.iteritems():
            setattr(scope, k, v)
        return self.translate(tree, scope)

# vim: et sw=4 sts=4