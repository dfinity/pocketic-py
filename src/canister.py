from ic.parser.DIDEmitter import *;
from antlr4 import *
from antlr4.InputStream import InputStream
from ic.candid import FuncClass, decode


class Canister:
    def __init__(self, ic, canister_id, candid=None) -> None:
        self.ic = ic
        self.canister_id = canister_id
        self.candid = candid
        
        input_stream = InputStream(candid)
        lexer = DIDLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = DIDParser(token_stream)
        tree = parser.program()

        emitter = DIDEmitter()
        walker =  ParseTreeWalker()
        walker.walk(emitter, tree)

        self.actor = emitter.getActor()

        for name, method in self.actor["methods"].items():
            assert type(method) == FuncClass
            anno = None if len(method.annotations) == 0 else method.annotations[0]
            setattr(self, name, PocketICCanisterMethod(self.ic, self.canister_id, name, method.argTypes, method.retTypes, anno))


class PocketICCanisterMethod:
    def __init__(self, ic, canister_id, name, args, rets, anno = None):
        self.ic = ic
        self.canister_id = canister_id
        self.name = name
        self.args = args
        self.rets = rets
        self.anno = anno

    def __call__(self, sender, *args, **kwargs):
        if len(args) != len(self.args):
            raise ValueError("Arguments length not match")
        arguments = []
        for i, arg in enumerate(args):
            arguments.append({"type": self.args[i], "value": arg})
        # effective_cansiter_id = args[0]['canister_id'] if self.canister_id == 'aaaaa-aa' and len(args) > 0 and type(args[0]) == dict and 'canister_id' in args[0] else self.canister_id
        if self.anno == 'query':
            res = self.ic.canister_query_call(sender, self.canister_id, self.name, arguments)
            res = decode(bytes(res), self.rets)
        else:
            res = self.ic.canister_update_call(sender, self.canister_id, self.name, arguments)
            res = decode(bytes(res), self.rets)
            
        if type(res) is not list:
            return res
        
        return list(map(lambda item: item["value"], res))
