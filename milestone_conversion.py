import argparse

from lxml import etree
from lxml.builder import ElementMaker


NAMESPACES = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace",
}
SKIPPABLE_MILESTONE_UNITS = (
    "para",
    "pg_l",
    None,
)

TEI_NS = "{http://www.tei-c.org/ns/1.0}"

E = ElementMaker(
    namespace="http://www.tei-c.org/ns/1.0", nsmap={None: "http://www.tei-c.org/ns/1.0"}
)
APP = E.app
DATE = E.date
DIV = E.div
LEM = E.lem


def convert(tree):
    refsDecls = tree.find(".//tei:refsDecl[@n='CTS']", namespaces=NAMESPACES)

    refable_units = []

    for cRefPattern in refsDecls.iterfind(".//tei:cRefPattern", namespaces=NAMESPACES):
        refable_units.append(cRefPattern.get("n"))

    refable_units = refable_units
    for milestone in tree.iterfind(f".//{TEI_NS}milestone"):
        current_unit = milestone.get("unit")

        if (
            current_unit in SKIPPABLE_MILESTONE_UNITS
            # or current_unit not in refable_units
        ):
            continue

        siblings = []

        for sibling in milestone.itersiblings():
            if (
                sibling.tag == f"{TEI_NS}milestone"
                and sibling.get("unit") == current_unit
            ):
                break
            siblings.append(sibling)

        if len(siblings) == 0:
            continue

        div = DIV(
            type=current_unit,
            n=milestone.get("n", ""),
            *siblings,
        )
        parent = milestone.getparent()
        parent.replace(milestone, div)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="milestone conversion")
    parser.add_argument("filename", help="the name of the file to convert")

    args = parser.parse_args()

    tree = etree.parse(args.filename)

    convert(tree)

    with open(args.filename, "wb") as f:
        etree.indent(tree, space="\t")
        f.write(etree.tostring(tree, encoding="utf-8", xml_declaration=True))
