import pygraphviz as pgv
import pandas as pd
import clingo.ast as ast


def extract_rel(file_add):
    prg = []
    ast.parse_files(file_add, lambda x: prg.append(x))
    result = []

    minted_rules = []
    rule_no = 0
    for i, dd in enumerate(prg):
        # print(i,str(x))
        head = []
        body = []
        is_disjunction = 0
        try:
            if str(dd.head.ast_type) == "ASTType.Disjunction":
                for det in dd.head.elements:
                    head.append(
                        "{name}/{arity}".format(
                            name=det.literal.atom.symbol.name,
                            arity=len(det.literal.atom.symbol.arguments),
                        )
                    )
                is_disjunction = 1
            else:
                for h in dd.head.atom.values():
                    try:
                        head.append(
                            "{name}/{arity}".format(name=h.name,
                                                    arity=len(h.arguments))
                        )
                    except BaseException as ex:
                        print("head err:", ex, str(dd))
                        head.append("{name}".format(name=h.name))
                        pass
            for b in dd.body:
                try:
                    body.append(
                        (
                            "{name}/{arity}".format(
                                name=b.atom.values()[0].name,
                                arity=len(b.atom.symbol.values()[2]),
                            ),
                            b.sign,
                        )
                    )
                except BaseException as ex:
                    print("body err:", ex, str(dd), str(b.atom))
                    body.append(("{name}".format(name=b.atom.values()[0].name),
                                b.sign))
                    pass

            for h in head:
                for comp in body:
                    result.append(
                        [
                            comp[0],
                            h,
                            rule_no,
                            "not" if comp[1] == 1 else "",
                            is_disjunction,
                        ]
                    )
        except BaseException as ex:
            print("err:", ex, str(dd))
            pass
        minted_rules.append((rule_no, str(dd)))
        rule_no += 1

    return (result, minted_rules, prg)


def rule_vis(file_add):

    file_add = [file_add]
    G = pgv.AGraph(overlap=False, directed=True, rankdir="BT")
    lst, mint_rl, prg = extract_rel(file_add)

    df = pd.DataFrame(
        lst, columns=["body", "head", "rule_no", "negation", "is_disjunction"]
    )

    for row_no in range(len(df)):
        rule_no = df.loc[row_no, "rule_no"]

        if df.loc[row_no, "is_disjunction"] == 1:
            rule_color = "#CCFFFF"
        else:
            rule_color = "#CCFFCC"

        G.add_node(
            df.loc[row_no, "body"],
            shape="box",
            style="rounded,filled",
            fillcolor="#FFFFCC",
            peripheries=1,
            fontname="Helvetica",
        )
        G.add_node(
            df.loc[row_no, "head"],
            shape="box",
            style="rounded,filled",
            fillcolor="#FFFFCC",
            peripheries=1,
            fontname="Helvetica",
        )
        G.add_node(
            "R" + str(rule_no),
            shape="circle",
            style="filled",
            fillcolor=rule_color,
            peripheries=1,
            fontname="Helvetica",
            tooltip=mint_rl[rule_no],
        )

        if str(df.loc[row_no, "negation"]) != "not":
            G.add_edge(
                df.loc[row_no, "body"],
                "R" + str(rule_no),
                label=df.loc[row_no, "negation"],
                weight=14,
                color="#b26e37",
                fontname="Palatino-Italic",
            )
        else:
            G.add_edge(
                df.loc[row_no, "body"],
                "R" + str(rule_no),
                label=df.loc[row_no, "negation"],
                weight=14,
                color="red3",
                fontcolor="red3",
                style="dashed",
                penwidth="1.8",
                fontname="Palatino-Italic",
            )
        G.add_edge(
            "R" + str(rule_no), df.loc[row_no, "head"],
            weight=14, color="#b26e37"
        )

    # save pdf
    file = "output"
    G.draw("{}.pdf".format(file), prog="dot")
    # save png for display
    G.draw("{}.png".format(file), prog="dot")
    # save svg
    G.draw("{}.svg".format(file), prog="dot")
    # save dot for rendering on web with tooltip
    with open("{}.dot".format(file), "w") as file:
        file.write(G.to_string())
