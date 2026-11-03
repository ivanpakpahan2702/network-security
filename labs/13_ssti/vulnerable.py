import operator

from jinja2 import StrictUndefined, TemplateError, nodes
from jinja2.sandbox import SandboxedEnvironment


class LabSandbox(SandboxedEnvironment):
    intercepted_binops = frozenset({"+", "-", "*", "**", "/", "//", "%"})

    def is_safe_attribute(self, obj, attr, value):
        return False

    def is_safe_callable(self, obj):
        return False

    def call_binop(self, context, operator_name, left, right):
        if operator_name not in {"+", "-", "*"} or type(left) is not int or type(right) is not int:
            raise ValueError("Batas lab: operasi hanya +, -, * pada integer kecil.")
        if abs(left) > 1000 or abs(right) > 1000:
            raise ValueError("Batas lab: operand terlalu besar.")
        result = {"+": operator.add, "-": operator.sub, "*": operator.mul}[operator_name](left, right)
        if abs(result) > 10000:
            raise ValueError("Batas lab: hasil aritmetika terlalu besar.")
        return result


def run(db, data, context):
    source = data.get("template", "")[:2048]
    environment = LabSandbox(autoescape=True, undefined=StrictUndefined)
    environment.globals.clear()
    environment.filters.clear()
    environment.tests.clear()
    try:
        tree = environment.parse(source)
        allowed = (nodes.Template, nodes.Output, nodes.TemplateData, nodes.Name, nodes.Const, nodes.Add, nodes.Sub, nodes.Mul)
        for node in [tree, *tree.find_all(nodes.Node)]:
            if not isinstance(node, allowed):
                raise ValueError("Batas lab: hanya teks, variabel dan aritmetika sederhana diizinkan.")
            if isinstance(node, nodes.Const) and (type(node.value) not in {str, int} or
                    (type(node.value) is int and abs(node.value) > 1000)):
                raise ValueError("Batas lab: konstanta tidak didukung.")
        # RENTAN: input menjadi TEMPLATE SOURCE dan dapat membaca konteks secret.
        output = environment.from_string(source).render(secret="SECRET_TEMPLATE_DEMO_2026")
    except (TemplateError, RecursionError) as error:
        raise ValueError("Template ditolak oleh sandbox: " + str(error)[:200]) from error
    return dict(title="Template pengguna dievaluasi server", detail=output,
                trace="Template source:\n" + source + "\n\nHasil render:\n" + output)
