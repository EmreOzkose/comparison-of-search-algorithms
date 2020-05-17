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

from collections import deque


class GraphBfs:
    def __init__(self, directed=True):
        self.edges = {}
        self.directed = directed
        self.start_pixel = []
        self.goal_pixel = []
        self.result_path = []

    def add_edge(self, node1, node2, __reversed=False):
        try: neighbors = self.edges[node1]
        except KeyError: neighbors = set()
        neighbors.add(node2)
        self.edges[node1] = neighbors
        if not self.directed and not __reversed: self.add_edge(node2, node1, True)

    def get_start(self):
        return "{}-{}".format(self.start_pixel[0], self.start_pixel[1])

    def get_goal(self):
        return "{}-{}".format(self.goal_pixel[0], self.goal_pixel[1])

    def neighbors(self, node):
        try: return self.edges[node]
        except KeyError: return []

    def breadth_first_search(self):
        start = self.get_start()
        goal = self.get_goal()

        found, fringe, visited, came_from = False, deque([start]), set([start]), {start: None}
        print('{:11s} | {}'.format('Expand Node', 'Fringe'))
        print('--------------------')
        print('{:11s} | {}'.format('-', start))
        while not found and len(fringe):
            current = fringe.pop()
            #print('{:11s}'.format(current), end=' | ')
            if current == goal: found = True; break
            for node in self.neighbors(current):
                if node not in visited: visited.add(node); fringe.appendleft(node); came_from[node] = current
            #print(', '.join(fringe))
        if found: print(); return came_from
        else: print('No path from {} to {}'.format(start, goal))

    def print_path(self, came_from, goal):
        parent = came_from[goal]
        if parent:
            GraphBfs.print_path(self, came_from, parent)
        else: print(goal, end='');return
        print(' =>', goal, end='')
        self.result_path.append(goal)

    def __str__(self):
        return str(self.edges)
