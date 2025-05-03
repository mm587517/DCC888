"""
This file implements a parser: a function that reads a text file, and returns
a control-flow graph of instructions plus an environment mapping variables to
integer values.
"""

from lang import *


def line2env(line):
    """
    Maps a string (the line) to a dictionary in python. This function will be
    useful to read the first line of the text file. This line contains the
    initial environment of the program that will be created. If you don't like
    the function, feel free to drop it off.

    Example
        >>> line2env('{"zero": 0, "one": 1, "three": 3, "iter": 9}').get('one')
        1
    """
    import json

    env_dict = json.loads(line)
    env_lang = Env()
    for k, v in env_dict.items():
        env_lang.set(k, v)
    return env_lang


def file2cfg_and_env(lines):
    """
    Builds a control-flow graph representation for the strings stored in
    `lines`. The first string represents the environment. The other strings
    represent instructions.

    Example:
        >>> l0 = '{"a": 0, "b": 3}'
        >>> l1 = 'bt a 1'
        >>> l2 = 'x = add a b'
        >>> env, prog = file2cfg_and_env([l0, l1, l2])
        >>> interp(prog[0], env).get("x")
        3

        >>> l0 = '{"a": 1, "b": 3, "x": 42, "z": 0}'
        >>> l1 = 'bt a 2'
        >>> l2 = 'x = add a b'
        >>> l3 = 'x = add x z'
        >>> env, prog = file2cfg_and_env([l0, l1, l2, l3])
        >>> interp(prog[0], env).get("x")
        42

        >>> l0 = '{"a": 1, "b": 3, "c": 5}'
        >>> l1 = 'x = add a b'
        >>> l2 = 'x = add x c'
        >>> env, prog = file2cfg_and_env([l0, l1, l2])
        >>> interp(prog[0], env).get("x")
        9
    """
    # TODO: Imlement this method.
    operations = {"add": Add, "mul": Mul, "bt": Bt, "geq": Geq, "lth": Lth}

    def parser(line: str):
        words = line.strip().split()
        if "=" in words:
            # Assignment format: x = op a b
            return {"op": words[2], "dst": words[0], "arg1": words[3], "arg2": words[4]}
        else:
            # Branch format: bt x i0 i1
            return {
                "op": words[0],
                "arg1": words[1],
                "arg2": int(words[2]),
            }

    env = line2env(lines[0])
    insts = []
    bt_fix = []

    for line in lines[1:]:
        result = parser(line)
        op = result["op"]
        cls = operations[op]

        if op == "bt":
            insts.append(None)
            bt_fix.append((len(insts) - 1, result["arg1"], result["arg2"]))
        else:
            # Binary operation: dst = op arg1 arg2
            insts.append(cls(result["dst"], result["arg1"], result["arg2"]))

    for idx, cond, target in bt_fix:
        insts[idx] = Bt(cond, insts[target], insts[idx + 1])

    for inst, next_inst in zip(insts, insts[1:]):
        if not isinstance(inst, Bt):
            inst.add_next(next_inst)

    return env, insts
