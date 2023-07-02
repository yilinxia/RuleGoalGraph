import pygraphviz as pgv
import pandas as pd
import clingo.ast as ast
import os


def extract_rel(file_name):
    # store the programs including program base and rules
    prg = []
    ast.parse_files(file_name, lambda x: prg.append(x))

    result = []
    minted_rules = []
    rule_no = 0

    # for every single line of scripts including rule_id and rule_content
    for rule_id, rule_content in enumerate(prg):
        head = []
        body = []
        # default settings
        is_disjunction = 0
        # skip #program base
        if rule_id > 0:
            try:
                # ===============head part===================
                # the processed rule head is disjunction
                if str(rule_content.head.ast_type) == "ASTType.Disjunction":
                    # literals in the head

                    for disjunctive_literal in rule_content.head.elements:
                        arity = len(disjunctive_literal.literal.atom.symbol.arguments)
                        temp_variable_ls = []
                        for variable_id in range(arity):
                            temp_variable_ls.append(
                                disjunctive_literal.literal.atom.symbol.arguments[
                                    variable_id
                                ].values()[1]
                            )
                        head.append(
                            "{literal_name}/{arity_names}".format(
                                # relationship name
                                literal_name=disjunctive_literal.literal.atom.symbol.name,
                                # number of variables
                                arity_names=temp_variable_ls,
                            )
                        )
                    is_disjunction = 1

                # the processed rule head is not disjunction
                else:
                    arity = len(rule_content.head.atom.symbol.arguments)
                    temp_variable_ls = []
                    for variable_id in range(arity):
                        temp_variable_ls.append(
                            rule_content.head.atom.symbol.arguments[variable_id].values()[1]
                        )
                    try:
                        head.append(
                            "{literal_name}/{arity_names}".format(
                                literal_name=rule_content.head.atom.symbol.name,
                                arity_names=temp_variable_ls,
                            )
                        )
                    except BaseException as ex:
                        print(
                            "head err:",
                            ex,
                            str(rule_content),
                        )
                        head.append("{name}".format(name=rule_content.head.atom.symbol.name))
                        pass
                # ===============body part===================
                # start to process body part
                for body_literal in rule_content.body:
                    try:
                        #
                        if str(body_literal.atom.ast_type) == "ASTType.SymbolicAtom":
                            arity = len(body_literal.atom.symbol.arguments)
                            temp_arg_ls = []
                            for arg_id in range(arity):
                                temp_arg_ls.append(body_literal.atom.symbol.arguments[arg_id].name)
                            body.append(
                                (
                                    "{literal_name}/{arity_names}".format(
                                        literal_name=body_literal.atom.symbol.name,
                                        arity_names=temp_arg_ls,
                                    ),
                                    # sign indicate whether the literal is
                                    # positive (0) negative (1) or not not(2)
                                    body_literal.sign,
                                )
                            )
                        if str(body_literal.atom.ast_type) == "ASTType.Comparison":
                            continue

                    except BaseException as ex:
                        print(
                            "body err:",
                            ex,
                            str(body_literal.atom),
                        )
                        pass

                #
                for non_disjunctive_literal in head:
                    for comp in body:
                        if comp[1] == 0:
                            not_string = ""
                        elif comp[1] == 1:
                            not_string = "not"
                        elif comp[1] == 2:
                            not_string = "not not"
                        else:
                            not_string = ""  # Or some other default value

                        result.append(
                            [
                                comp[0],
                                non_disjunctive_literal,
                                rule_no,
                                not_string,
                                is_disjunction,
                            ]
                        )
            # if this an parse error, print the rule content
            except BaseException as ex:
                pass
                print("err:", ex, str(rule_content))

            minted_rules.append((rule_no, str(rule_content)))
            rule_no += 1

    return (result, minted_rules, prg)


# the main function to extract rules
def rule_vis(file_name):
    filename = [file_name]
    G = pgv.AGraph(overlap=False, directed=True, rankdir="BT")
    lst, mint_rl, prg = extract_rel(filename)

    df = pd.DataFrame(
        lst,
        columns=[
            "body",
            "head",
            "rule_no",
            "negation",
            "is_disjunction",
        ],
    )
    # print(df)

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
            "R" + str(rule_no),
            df.loc[row_no, "head"],
            weight=14,
            color="#b26e37",
        )

    dir_path = "output"
    # Check if the directory exists
    if not os.path.isdir(dir_path):
        # If it doesn't exist, create it
        os.makedirs(dir_path)

    # save pdf
    file = file_name.split("/")[-1].split(".")[0]
    G.draw("output/{}.pdf".format(file), prog="dot")
    # save png for display
    G.draw("output/{}.png".format(file), prog="dot")
    # save svg
    G.draw("output/{}.svg".format(file), prog="dot")
    # save dot for rendering on web with tooltip
    with open("output/{}.dot".format(file), "w") as file:
        file.write(G.to_string())
