import subprocess, sys, re
from rich import print

high_detail = False


def log(content, visual):
    if high_detail == False and "===>" in content:
        return
    print(f"[{visual}]{content}[/{visual}]")


# all literals(numbers, strings) aka primaries are stored as symbols, prefixed with an exclamation mark (!).
# variables do not have an automatically appended prefix.
class Symbols:
    def primary(self, args):
        value = args[0]

        # this not only saves the raw value but
        # also saves the Token, which was info on type.
        return self.create_symbol(value, args)

    def set_var(self, args):
        name, value = args
        name = str(name)  # we dont want TOKEN names now do we
        all_types = (
            []
        )  # contains the types of each token that the variable is being assigned to

        found_assignment = False

        # check if it's a class assignment
        possible_class = "" if isinstance(value, str) == False else value.split(":")[0]
        for entry in self.classes:
            if self.classes[entry].method == possible_class:
                # add the class type to the mix
                all_types.append((possible_class, self.classes[entry].type))
                # mark it here
                found_assignment = True

        species = self.deduce_type(all_types)

        # check if it's a proc assignment
        possible_proc = value.split("(")[0] if isinstance(value, str) == True else ""
        if possible_proc in self.procs:
            # make it the proc placeholder so it gets replaced later
            species = f"__proc_type_{possible_proc}__"
            found_assignment = True
        if found_assignment == False:
            for arg in value["args"]:
                if hasattr(arg, "type"):
                    all_types.append((arg[0], arg.type))

        if "content" in value:
            content = value["content"]
        else:
            # probably class or proc assignment
            content = value.strip(";")

        log(
            f"===> Created variable named {name}, type {species} and value {content}",
            "yellow",
        )

        self.symbols[name] = (name, species)
        return f"{species} {name} = {content};\n"

    # So easy
    def reassign_var(self, args):
        name, value = args
        name = str(name)
        return f"{name} = {value};\n"


# procedures are functions, that's really it
class Procedures:
    def define_proc(self, args):
        name = args[0]
        params = args[1] if args[1] is not None else ""
        start = 2

        # this is a STRING that includes each parameter. since type is
        # unknown, we place __param_type_x__ until type is all figured
        # out by the end of the transpile process.
        placeholder_params = ", ".join(
            [f"__param_type_{param}__ {param}" for param in params]
        )

        body = args[start:]

        code = "".join(body)
        self.create_procedure(name, params, code)

        log(
            f"===> Created procedure named {name}",
            "blue",
        )

        return f"__proc_type_{name}__ {name}({placeholder_params}) {{\n{code}}}\n"

    def call_proc(self, args):
        name = args[0]
        arguments = args[1] if args[1] is not None else ""
        count = 0
        for arg in arguments:
            if hasattr(arg[0], "type"):
                self.modify_procedureParam(name, count, arg[0].type)
            count += 1
        arguments = ", ".join([arg[0] for arg in arguments])
        return f"{name}({arguments});\n"

    def return_call_proc(self, args):
        name = args[0]
        arguments = args[1] if args[1] is not None else ""
        count = 0
        for arg in arguments:
            if hasattr(arg[0], "type"):
                self.modify_procedureParam(name, count, arg[0].type)
            count += 1
        arguments = ", ".join([arg[0] for arg in arguments])
        return f"{name}({arguments})"

    def parameters(self, args):
        return args

    def arguments(self, args):
        return [arg["args"] for arg in args]

    def return_stmt(self, args):
        content = args[0]["content"]
        return f"return {content};\n"


# handles math, obviously
class Math:
    def __extract__(self, args):
        # because we're processing parsed primaries, we need
        # to extract their content values to properly structure
        # this.
        left = args[0]["content"]
        right = args[1]["content"]

        array = [arg["content"] for arg in args]

        return left, right, array

    def add(self, args):
        left, right, array = self.__extract__(args)
        return self.create_symbol(f"{left} + {right}", array)

    def sub(self, args):
        left, right, array = self.__extract__(args)
        return self.create_symbol(f"{left} - {right}", array)

    def mul(self, args):
        left, right, array = self.__extract__(args)
        return self.create_symbol(f"{left} * {right}", array)

    def div(self, args):
        left, right, array = self.__extract__(args)
        return self.create_symbol(f"{left} / {right}", array)

    def mod(self, args):
        left, right, array = self.__extract__(args)
        return self.create_symbol(f"{left} % {right}", array)

    def parentheses(self, args):
        content = args[0]["content"]
        return f"({content})"


class Control:
    def while_loop(self, args):
        cond = args[0]
        body = args[1:]
        code = "".join(body)
        return f"while ({cond}) {{\n{code}}}\n"

    def condition(self, args):
        left = args[0]
        if "content" in left:
            left = left["content"]
        if len(args) > 1:
            _, cond, right = args
            if "content" in right:
                right = right["content"]
            return f"{left} {cond} {right}"

        return left

    def comp(self, args):
        return args[0]


class Builtins:
    def builtin_call(self, args):
        label = args[0]
        func = args[1]
        arguments = args[2] if args[2] is not None else []

        if label in self.classes:
            method = self.classes[label].method
        else:
            method = label

        if label in self.compile_timeClasses:
            compile_time = arguments[0][0]
            arguments.pop(0)
            arguments = ", ".join([arg[0] for arg in arguments])
            return f"{method}::{func}<{compile_time}>({arguments});\n"
        else:
            arguments = ", ".join([arg[0] for arg in arguments])
            return f"{method}::{func}({arguments});\n"


# after everything is processed, we need to structure the code, clear
# placeholders, and return a usable string of C++ code
class Post:
    def start(self, instructions):
        try:
            joined = "\n".join(instructions)
            joined = f'#include "lib/LyLang.h"\n\n{joined}'

            for proc in self.procs:
                body = self.procs[proc]["body"]
                params = self.procs[proc]["params"]

                # if the current procedure is MAIN, then we
                # need to adjust the function type and return
                # appropriately.
                if proc == "main":
                    self.main_found = True
                    joined = joined.replace(f"__proc_type_{proc}__", "int")
                    if "return" in body:
                        continue
                    new_body = body + "return 0;\n"
                    joined = joined.replace(body, new_body)
                    body = new_body

                # the proc has a return statement. we will access the first one
                # we find and extract its type. it doesn't matter which statement
                # we choose, because C/C++ demands consistent return types regardless
                # of the path the function goes.
                if "return" in body:
                    position = body.find("return")
                    next = position + len("return")
                    remainder = body[next:].strip()

                    # separate based on +-*/%;
                    regex = r"[+*/;% -]+"

                    tokens = re.split(regex, remainder)
                    clean_tokens = [token.strip() for token in tokens if token.strip()]

                    word = re.split(regex, remainder)[0] if remainder else None

                    # go through each parameter; if it matches the first token of the
                    # return statement then we need to replace the placeholder with its
                    # type (species; type is a "reserved keyword" :/)
                    for param in params:
                        if param[0] == word.strip():
                            joined = joined.replace(
                                f"__proc_type_{proc}__", self.python_typeTo_C(param[1])
                            )

                    # if it is a VARIABLE; no ! prefix then get the type
                    # and replace
                    if word in self.symbols:
                        joined = joined.replace(
                            f"__proc_type_{proc}__", self.symbols[word][1]
                        )

                    # if it is a number or anything else
                    all_types = []
                    # get ALL tokens, find their types and append.
                    for token in clean_tokens:
                        tag = f"!{token}"
                        if tag in self.symbols:
                            if "args" in tag:
                                all_types.append(
                                    (tag, self.symbols[tag]["args"][0].type)
                                )
                    if len(all_types) > 0:
                        species = self.deduce_type(all_types)

                # if there are any placeholders left for this specific proc
                # then it's probably void
                joined = joined.replace(f"__proc_type_{proc}__", "void")

                for param in params:
                    name, species = param
                    joined = joined.replace(
                        f"__param_type_{name}__", self.python_typeTo_C(species)
                    )

            return joined
        except Exception as e:
            print(f"[bold red]Compilation failed. ==> {e}[/bold red]")
            return "// Compilation failed //"


# the incorrect file was run, so run the main
# correct file instead. Sometimes running this
# file is just more convenient! :)
if __name__ == "__main__":
    subprocess.run([sys.executable, "src/lylang.py"])
