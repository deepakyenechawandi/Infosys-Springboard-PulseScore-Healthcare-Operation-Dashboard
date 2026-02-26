"""Extract structural_gaps.pyc bytecode details"""
import dis, marshal, types

with open('sections/__pycache__/structural_gaps.cpython-313.pyc', 'rb') as f:
    f.read(16)
    code = marshal.load(f)

def get_code_objects(code_obj, name='', depth=0):
    results = [(name or code_obj.co_name, code_obj, depth)]
    for const in code_obj.co_consts:
        if isinstance(const, types.CodeType):
            results.extend(get_code_objects(const, const.co_name, depth+1))
    return results

objs = get_code_objects(code)
for name, co, d in objs:
    indent = "  " * d
    args = co.co_varnames[:co.co_argcount]
    print(f'{indent}=== {name} (args: {args}) ===')
    print(f'{indent}  vars: {co.co_varnames}')
    print(f'{indent}  names: {co.co_names}')
    print()

# Full disassembly of the render function
for name, co, d in objs:
    if name == 'render_structural_gaps':
        print("=== FULL DISASSEMBLY ===")
        dis.dis(co)
