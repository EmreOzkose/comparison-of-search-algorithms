import cv2
from astar import GraphAstart
from dfs import GraphDfs
from bfs import GraphBfs
from ucs import GraphUcs
import numpy as np
import os
import time
import sys


# Flags
flag_print_number_of_edge_node = True
flag_print_path = False


def read_map(path):
    """

    :param path: map path
    :return: map as grayscale image
    """
    img = cv2.imread(path, 0)
    return img


def color_visited_pixels(graph, map, visited_pixel_dict, title="image", start_pixel=None, goal_pixel=None, save_path="outputs/"):
    """
    :param map:
    :param visited_pixel_list:
    :return:
    """

    if flag_print_path:
        graph.result_path = []
        graph.print_path(traced_path, "{}-{}".format(goal_pixel[0], goal_pixel[1]))
        print()

    visited_pixel_list = visited_pixel_dict.keys()

    map = cv2.cvtColor(np.transpose(map), cv2.COLOR_GRAY2RGB)

    for pixels in visited_pixel_list:
        try:
            x, y = [int(i) for i in pixels.split("-")]
            map[x,y] = (255, 0, 0)
        except ValueError:
            continue
        except AttributeError:
            continue

    radius = 20
    thickness = 2
    if start_pixel is not None:
        color = (0, 255, 0)
        center = (start_pixel[1], start_pixel[0])
        map = cv2.circle(map, center, radius, color, thickness)

    if goal_pixel is not None:
        color = (0, 0, 255)
        center = (goal_pixel[1], goal_pixel[0])
        map = cv2.circle(map, center, radius, color, thickness)

    if flag_print_path:
        for pixels in graph.result_path:
            x, y = [int(i) for i in pixels.split("-")]
            map = cv2.circle(map, (y,x), 3, (255, 0, 255), 1)

    cv2.imwrite(os.path.join(save_path, "{}.png".format(title)), np.transpose(map, (1, 0, 2)))



def create_graph(map, method):
    if method == "dfs":
        graph = GraphDfs(directed=False)
    elif method == "bfs":
        graph = GraphBfs(directed=False)
    elif method == "ucs":
        graph = GraphUcs(directed=False)
    else:
        graph = GraphAstart(directed=False)

    map = np.transpose(map)
    count_edge = 0
    node_set = set()
    for x_i in range(width):
        for y_i in range(height):
            pixel_value = int(map[x_i, y_i])
            node_key = "{}-{}".format(x_i, y_i)

            if pixel_value != 0:
                node_set.add(node_key)
                index_list = [[x_i + 1, y_i],
                              [x_i, y_i + 1],
                              [x_i + 1, y_i + 1],
                              [x_i - 1, y_i],
                              [x_i, y_i - 1],
                              [x_i - 1, y_i - 1],
                              [x_i + 1, y_i - 1],
                              [x_i - 1, y_i + 1],
                              ]

                for i, j in index_list:
                    try:
                        if (map[i, j] != 0):
                            graph.add_edge(node_key, "{}-{}".format(i, j))
                            count_edge += 1
                    except IndexError:
                        continue
    if flag_print_number_of_edge_node:
        print("number of edge: {}".format(count_edge))
        print("number of node: {}".format(len(node_set)))

    return graph


if __name__ == "__main__":
    sys.setrecursionlimit(4500)

    path = "data/maps/hacettepe map binary.png"
    map = read_map(path)

    scale_percent = 300  # percent of original size
    width = int(map.shape[1] * scale_percent / 100)
    height = int(map.shape[0] * scale_percent / 100)
    dim = (width, height)
    map = cv2.resize(map, dim, interpolation=cv2.INTER_NEAREST)

    print(map.shape)
    width, height = map.shape

    # thresholding
    map[map>250] = 255
    map[map<=250] = 0

    start_pixel = [350, 636]
    goal_pixel = [686, 640]

    start_pixel = [713, 1276]
    goal_pixel = [1400, 1280]

    start_pixel = [1065, 1915]
    goal_pixel = [2100, 1919]

    for method in ["dfs", "bfs", "ucs", "astar"]:
        print(method, end=" ")
        print("="*20)

        graph = create_graph(map, method)
        graph.start_pixel = start_pixel
        graph.goal_pixel = goal_pixel

        if method == "astar":
            start = time.time()
            traced_path, total_cost = graph.a_star_search()
            print("Elsapsed time: {:5f}".format(time.time()-start))
            print("number pf visited node: {}".format(len(set(traced_path.keys()))))
            title = "path_result_astar"
        elif method == "dfs":
            start = time.time()
            traced_path = graph.depth_first_search()
            print("Elsapsed time: {:5f}".format(time.time()-start))
            print("number pf visited node: {}".format(len(set(traced_path.keys()))))
            title = "path_result_dfs"
        elif method == "bfs":
            start = time.time()
            traced_path = graph.breadth_first_search()
            print("Elsapsed time: {:5f}".format(time.time()-start))
            print("number pf visited node: {}".format(len(set(traced_path.keys()))))
            title = "path_result_bfs"
        elif method == "ucs":
            start = time.time()
            traced_path, total_cost = graph.uniform_cost_search()
            print("Elsapsed time: {:5f}".format(time.time()-start))
            print("number pf visited node: {}".format(len(set(traced_path.keys()))))
            title = "path_result_ucs"

        color_visited_pixels(graph, map, traced_path, title=title, start_pixel=start_pixel, goal_pixel=goal_pixel)
