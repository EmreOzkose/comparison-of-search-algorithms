import json
from glob import glob
from os.path import join as pjoin
from pathlib import Path
import spacy
import time
import os
import warnings

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network

from astar import GraphAstart
from dfs import GraphDfs
from bfs import GraphBfs
from ucs import GraphUcs

warnings.filterwarnings("ignore")

nlp = spacy.load("en_core_web_sm")


# noinspection find_similarity
def find_similarity(doc1, doc2):
    doc1 = nlp(doc1)
    doc2 = nlp(doc2)
    sim = doc1.similarity(doc2)

    return sim


def read_data(data_path):
    """

    :param data_path: folder path od data
    :return:
    """
    print("Reading json data ...", end=" ")

    data_dict = {}

    counter = 0
    for json_path in Path(data_path).rglob("*.json"):
        with open(json_path, 'r') as f:
            distros_dict = json.load(f)

            abstract_text = distros_dict["metadata"]["title"]

            body_text = ""
            for part in distros_dict["abstract"]:
                body_text += part["text"]

            if abstract_text == "" or body_text == "": continue # if there is not any abstract or body text info, skip paper
            data_dict[distros_dict["paper_id"]] = [abstract_text, body_text, counter]

        counter += 1
        if counter == 500:
            break
    print("DONE")
    return data_dict


def calculate_sims(data_dict, sim_path):
    print("Calculating similarities ...", end=" ")
    text_file = open(sim_path, "w")
    text_file.write("# paper_id_1;paper_id_2;pairwise abstract similarity;pairwise body similarity")

    t1 = time.time()
    for counter, paper1 in enumerate(data_dict.items()):
        print(counter)
        for paper2 in data_dict.items():
            if paper1[0] == paper2[0]: continue # diagonal value

            abstract_sim = find_similarity(paper1[1][0], paper2[1][0])
            body_sim = find_similarity(paper1[1][1], paper2[1][1])

            text_file.write("{};{};{};{}\n".format(paper1[0], paper2[0], abstract_sim, body_sim))

    text_file.close()
    print("DONE")

    print(time.time()-t1)


def create_graph(sim_path, method):
    if method == "dfs":
        graph = GraphDfs(directed=False)
    elif method == "bfs":
        graph = GraphBfs(directed=False)
    elif method == "ucs":
        graph = GraphUcs(directed=False)
    else:
        graph = GraphAstart(directed=False)

    file = open(sim_path, "r")

    for line in  file.readlines():
        if line[0] == "#": continue
        paper_id_1, paper_id_2, title_sim, abstract_sim = line.rstrip("\n").split(";")

        if float(title_sim) > 0.75:
            graph.add_edge(paper_id_1, paper_id_2)

    return graph


def get_heuristics(sim_path, goal_id):
    file = open(sim_path, "r")

    heuristics = {}
    heuristics[goal_id] = 0.0

    for line in file.readlines():
        if line[0] == "#": continue
        paper_id_1, paper_id_2, title_sim, abstract_sim = line.rstrip("\n").split(";")

        if paper_id_1 == goal_id: heuristics[paper_id_2] = 1 - float(abstract_sim)
        elif paper_id_2 == goal_id: heuristics[paper_id_1] = 1 - float(abstract_sim)

    return heuristics


def visualize(graph, id_to_counter):
    # Build a dataframe with 4 connections
    from_list = []
    to_list = []
    for k, v in graph.edges.items():
        for v_i in v.keys():
            from_list.append(id_to_counter[k])
            to_list.append(id_to_counter[v_i])

    df = pd.DataFrame({'from': from_list, 'to': to_list})
    print(df)

    # Build your graph
    G = nx.from_pandas_edgelist(df, 'from', 'to')

    # Plot it
    # nx.draw(G, with_labels=True)
    nx.draw(G, with_labels=True, node_size=150, font_size=8, node_color="skyblue", pos=nx.fruchterman_reingold_layout(G))

    plt.show()


def visualize_online(graph, id_to_counter, start, goal, traced_path=None, method=None, flag_show_graph=False):
    got_net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")

    # set the physics layout of the network
    got_net.barnes_hut()

    if traced_path is not None:
        traced_path_nodes = list(traced_path.keys()) + list(traced_path.values())
    else:
        traced_path_nodes = []

    if method == "dfs" or method == "bfs":
        for k, v in graph.edges.items():
            for v_i in v:
                n1 = id_to_counter[k]
                n2 = id_to_counter[v_i]

                color_1 = "blue"; color_2 = "blue"
                if k in traced_path_nodes and v_i in traced_path_nodes: color_1 = "red"; color_2 = "red"

                if k == start: color_1 = "yellow"
                elif v_i == start: color_2 = "yellow"

                if k == goal: color_1 = "purple"
                elif v_i == goal: color_2 = "purple"

                got_net.add_node(n1, n1, color=color_1, title=str(n1))
                got_net.add_node(n2, n2, color=color_2, title=str(n2))
                got_net.add_edge(n1, n2, value=1)
    else: # ucs or astar
        for k, v in graph.edges.items():
            for v_i in v.keys():
                n1 = id_to_counter[k]
                n2 = id_to_counter[v_i]

                color_1 = "blue"; color_2 = "blue"
                if k in traced_path_nodes and v_i in traced_path_nodes: color_1 = "red"; color_2 = "red"

                if k == start: color_1 = "yellow"
                elif v_i == start: color_2 = "yellow"

                if k == goal: color_1 = "purple"
                elif v_i == goal: color_2 = "purple"

                got_net.add_node(n1, n1, color=color_1, title=str(n1))
                got_net.add_node(n2, n2, color=color_2, title=str(n2))
                got_net.add_edge(n1, n2, value=1)

    if traced_path is not None:
        for k, v in traced_path.items():
            got_net.add_edge(n1, n2, color="#00ff1e", value=1)

    if flag_show_graph:
        got_net.show_buttons(filter_=['physics'])
        got_net.show("paper_graph_{}_1.html".format(method))


if __name__ == "__main__":
    data_path = "data/papers/arxiv"
    sim_path = "similarities_100.txt"
    data_dict = read_data(data_path)

    flag_visualize = False
    flag_show_graph = False
    flag_count_edge = True

    id_to_counter = {}
    for k, v in data_dict.items(): id_to_counter[k] = v[-1]; print("{} - {} ({})".format(v[-1], v[0], k))

    # calculate_sims(data_dict, sim_path)

    for method in ["dfs", "bfs", "ucs", "astar"]:
        print(method, end=" "); print("="*20)
        graph = create_graph(sim_path, method)

        if flag_count_edge:
            coun = 0
            for k, v in graph.edges.items():
                coun += len(v)
            print("number of edge: {}".format(coun / 2))
            exit(0)

        start_id = "ec6bafda5f55a297074c0a4b2fb497d33dd2353d"
        goal_id = "4717c3506f166d2f39a1a9829e408e7d9a2539ae"

        if method == "astar":
            heuristics = get_heuristics(sim_path, goal_id)
            graph.set_heuristics(heuristics)
            time_start = time.time()
            traced_path, total_cost = graph.a_star_search(start_id, goal_id)
            print("Total Time: {:.5f}".format(time.time() - time_start))
        elif method == "bfs":
            time_start = time.time()
            traced_path = graph.breadth_first_search(start_id, goal_id)
            print("Total Time: {:.5f}".format(time.time() - time_start))
        elif method == "ucs":
            time_start = time.time()
            traced_path, total_cost = graph.uniform_cost_search(start_id, goal_id)
            print("Total Time: {:.5f}".format(time.time() - time_start))
        else:
            time_start = time.time()
            traced_path = graph.depth_first_search(start_id, goal_id)
            print("Total Time: {:.5f}".format(time.time() - time_start))

        print("Number of visited node : {}".format(len(traced_path.keys())))
        if flag_visualize:
            visualize_online(graph, id_to_counter, start_id, goal_id, traced_path=traced_path, method=method, flag_show_graph=flag_show_graph)

    print("Program ... DONE")
