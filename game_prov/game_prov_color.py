import clingo
import pandas as pd
import pygraphviz as pgv
import graphviz
from IPython.display import display
from collections import defaultdict
import subprocess

def find_win_pos(dict):
    dict_values = list(dict.values())
    # Transform each list into a set
    sets = [set(lst) for lst in dict_values]

    # Find the intersection across all sets
    win_pos = set.intersection(*sets)
    
    # Find the union across all sets
    all_items = set.union(*sets)

    # Subtract common_items from all_items to get not common items
    drawn_pos = all_items - win_pos

    return win_pos, drawn_pos

def find_lost_pos(input_set, win_pos, drawn_pos):
    # Find what is not included based on common_items and not_common_items
    lost_pos = input_set - win_pos - drawn_pos

    return lost_pos


def get_node_colors(dict, input_set):
    win_pos, drawn_pos = find_win_pos(dict)
    lost_pos = find_lost_pos(input_set, win_pos, drawn_pos)
    
    color_dict = {}
    
    for node in win_pos:
        color_dict[node] = '#dbfdda'
    for node in drawn_pos:
        color_dict[node] = '#fdff94'
    for node in lost_pos:
        color_dict[node] = '#f77580'
        
    return color_dict


def pos_label(file_add):
    with open(file_add) as plain_graph_lp:
        facts_graph = plain_graph_lp.read()

    ctl = clingo.Control()
    ctl.configuration.solve.models = 0
    ctl.add(
        "base",
        [],
        facts_graph
        + """
        pos(X):- move(X,_).
        pos(X):- move(_,X).
        win(X) :- move(X,Y), not win(Y).
        """,
    )
    ctl.ground([("base", [])])

    with ctl.solve(yield_=True) as handle:
        pws = {}
        pos_ls=[]
        pw_id = 1
        for model in handle:
            pw_data = []
            for literal in model.symbols(atoms=True):
                if (
                    literal.name == "win" ### filter literals
                ):  
                    pw_data.append(literal.arguments[0].name)
                if (
                    literal.name == "pos" ### filter literals
                ):  
                    pos_ls.append(literal.arguments[0].name)
            pws[pw_id] = pw_data
            pw_id = pw_id + 1

    return get_node_colors(pws, set(pos_ls))


def generate_graph(input_file):
    # Define colors for nodes
    node_colors = pos_label(input_file)  # Add more colors as needed

    # Parse file
    with open(input_file, "r") as file:
        lines = file.readlines()

    # Create a directed graph
    G = pgv.AGraph(directed=True)

    # Group nodes at the same rank
    ranks = defaultdict(list)
    ranks[0] = ['a', 'k']
    ranks[1] = ['b', 'c', 'l']
    ranks[2] = ['d', 'e', 'm']
    ranks[3] = ['f', 'g', 'h', 'n']

    # Add nodes and edges to the graph
    for line in lines:
        if ',' not in line: 
            continue
        stripped_line = line.strip().replace("move(", "").replace(").", "")
        start, end = stripped_line.split(',')
        G.add_edge(start, end)

    # Set same ranks for specified nodes
    for rank in ranks.values():
        G.add_subgraph(rank, rank='same')

    # Render the graph to a file (e.g., output_no_color.dot)
    output_file_no_color = input_file.split(".")[0] + "_no_color.dot"
    G.write(output_file_no_color)
    
    # Convert the no_color dot file to a png image
    image_file_no_color = output_file_no_color.replace(".dot", ".png")
    subprocess.run(["dot", "-Tpng", output_file_no_color, "-o", image_file_no_color])

    # Add colors to nodes in the graph
    for node in G.nodes():
        # Get the color for the node, if specified, otherwise use white
        node_color = node_colors.get(node, "white")
        node.attr['fillcolor'] = node_color
        node.attr['style'] = 'filled'

    # Render the graph to a file (e.g., output.dot)
    output_file = input_file.split(".")[0] + "_output.dot"
    G.write(output_file)
    
    # Convert the colored dot file to a png image
    image_file = output_file.replace(".dot", ".png")
    subprocess.run(["dot", "-Tpng", output_file, "-o", image_file])