#    Copyright 2019 Atikur Rahman Chitholian
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from heapq import heappop, heappush
from math import inf, sqrt


class GraphAstart:
    def __init__(self, directed=True):
        self.edges = {}
        self.huristics = {}
        self.directed = directed
        self.start_pixel = []
        self.goal_pixel = []
        self.result_path = []

    def add_edge(self, node1, node2, cost=1, __reversed=False):
        try: neighbors = self.edges[node1]
        except KeyError: neighbors = {}
        neighbors[node2] = cost
        self.edges[node1] = neighbors
        if not self.directed and not __reversed: self.add_edge(node2, node1, cost, True)

    def set_huristics(self, huristics={}):
        self.huristics = huristics

    def get_huristic(self, node_key):
        node_key_int = [int(i) for i in node_key.split("-")];
        return self.euclidean_distance(node_key_int, self.goal_pixel)

    def euclidean_distance(self, point1, point2):
        return sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

    def neighbors(self, node):
        try: return self.edges[node]
        except KeyError: return []

    def cost(self, node1, node2):
        try:
            return self.edges[node1][node2]
        except:
            return inf

    def get_start(self):
        return "{}-{}".format(self.start_pixel[0], self.start_pixel[1])

    def get_goal(self):
        return "{}-{}".format(self.goal_pixel[0], self.goal_pixel[1])

    def a_star_search(self):
        start = self.get_start()
        goal = self.get_goal()

        found, fringe, visited, came_from, cost_so_far = False, [(self.get_huristic(start), start)], set([start]), {start: None}, {start: 0}
        #print('{:11s} | {}'.format('Expand Node', 'Fringe'))
        #print('--------------------')
        #print('{:11s} | {}'.format('-', str(fringe[0])))

        while not found and len(fringe):
            _, current = heappop(fringe)
            #print('{:11s}'.format(current), end=' | ')

            if current == goal: found = True; break

            for node in self.neighbors(current):
                new_cost = cost_so_far[current] + self.cost(current, node)
                if node not in visited or cost_so_far[node] > new_cost:
                    visited.add(node); came_from[node] = current; cost_so_far[node] = new_cost
                    heappush(fringe, (new_cost + self.get_huristic(node), node))
            #print(', '.join([str(n) for n in fringe]))
        if found: print(); return came_from, cost_so_far[goal]
        else: print('No path from {} to {}'.format(start, goal)); return None, inf

    def print_path(self, came_from, goal):
        parent = came_from[goal]
        if parent:
            GraphAstart.print_path(self, came_from, parent)
        else: print(goal, end='');return
        print(' =>', goal, end='')
        self.result_path.append(goal)

    def __str__(self):
        return str(self.edges)
