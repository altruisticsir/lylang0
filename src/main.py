from lark import Lark, Transformer
from rich import print
from dataclasses import dataclass

from manager import Symbols, Procedures, Math, Control, Builtins, Post, log

parser = Lark.open("assets/grammar.lark", parser="lalr", lexer="contextual")
input_extension, output_extension = ("ll", "cpp")


@dataclass
class Class:
    name: str
    method: str
    type: str


class Converter(Transformer, Symbols, Procedures, Math, Control, Builtins, Post):
    def __init__(self, visit_tokens=True):
        super().__init__(visit_tokens=visit_tokens)
        self.symbols = {}
        self.procs = {}
        self.classes = {}

        self.headers = '#include "lib/LyLang.h"\n'

        self.main_found = False

        self.compile_timeClasses = ["digital"]
        self.assign_allClasses()

    def create_symbol(self, content, args):
        nested = False
        nested_args = []
        for arg in args:
            if "args" in arg:
                nested = True
                nested_args.append(arg["args"])
        symbol = {"content": content, "args": args if nested == False else nested_args}

        if f"!{content}" not in self.symbols:
            log(f"===> Created symbol with value {content}", "magenta")

        # !x represents a symbol that is not manually assigned to, e.g. literals like numbers
        self.symbols[f"!{content}"] = symbol
        return symbol

    def create_procedure(self, name, raw_params, raw_body):
        # just saves the proc's data like name, params and body(code)
        # which can be modified and accessed later
        name = str(name)
        params = [(param[0], "Unknown") for param in raw_params]

        self.procs[name] = {
            "name": name,
            "params": params,
            "body": raw_body,
        }

    def modify_procedureParam(self, name, parameter, species):
        # modifies a specific proc's parameter type; this is
        # often used during a proc call where the type is
        # pinned down and determined definitively
        if name in self.procs:
            procedure = self.procs[name]
            params = procedure["params"]
            param_name = params[parameter][0]
            params[parameter] = (param_name, species)

    # register all classes, yes one class has one return type.
    # it's usually always int so this degree of freedom is a little too much,
    # honestly.
    def assign_allClasses(self):
        class_list = [
            Class("digital", "Digital", "INT"),
            Class("delay", "Delay", "INT"),
        ]
        for entry in class_list:
            self.create_class(entry.name, entry.method, entry.type)

    # adds a class to the list
    def create_class(self, name, method, species):
        structure = Class(name, method, species)
        self.classes[name] = structure

    def add_header(self, content):
        self.headers += content

    # typically when deducing the types of symbols their types
    # are stored as C types, so we need to convert them to something
    # deduce_type can understand
    def c_typeTo_Python(self, value):
        if value == "const char*":
            return "STRING"
        if value == "float":
            return "FLOAT"
        return "INT"

    # opposite of the above function ^^
    def python_typeTo_C(self, value):
        if value == "STRING":
            return "const char*"
        if value == "FLOAT":
            return "float"
        return "int"

    # based on an array of types, it'll determine the
    # type based on priority
    def deduce_type(self, all_types):
        # an array of all the types
        complete = []
        for entry in all_types:
            name, species = entry
            # if the species of the entry isn't a symbol(var),
            # then just go ahead and add it
            if species != "SYMBOL":
                complete.append(species)
            else:
                # otherwise, it's a mystery what the real species
                # is so we need to check and add it.
                if name in self.symbols:
                    # extracted name isn't needed
                    _, species = self.symbols[name]
                    complete.append(self.c_typeTo_Python(species))
                else:
                    return f"__param_type_{name}__"

        # string > float > int
        if "STRING" in complete:
            return "const char*"
        if "FLOAT" in complete:
            return "float"
        if "INT" in complete:
            return "int"
        return "int"


# filepaths; no file extensions to be provided
def process(input, output):
    in_path = f"{input}.{input_extension}"
    out_path = f"{output}.{output_extension}"

    with open(in_path, "r") as file:
        code = file.read()
    tree = parser.parse(code)

    log(f"Starting compilation ({in_path} => {out_path})", "bold blue")

    converter = Converter()

    result = converter.transform(tree)

    log(f"=> {len(converter.symbols)} symbols generated", "green")
    log(f"=> {len(converter.procs)} procedures generated", "green")

    if converter.main_found == False:
        print("[bold red]No main function was detected; compilation aborted[/bold red]")
        return

    with open(out_path, "w") as file:
        file.write(result)
        log(f"Success!", "bold blue")


process("main", "main")
