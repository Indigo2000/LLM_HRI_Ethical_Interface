import heapq

# Define the heuristic h(n)
h = {
    'Hall': 0,
    'Study': 1,
    'Bathroom': 1,
    'Dining Room': 1,
    'Kitchen': 2,
    'Utility Room': 2,
    'Bedroom 1': 3,
    'Bedroom 2': 3,
    'Lounge': 1
}

# Define the graph with directions
graph = {
    'Hall': [
        ('Study', 5, 'left'),
        ('Lounge', 10, 'diagonally forward and left'),
        ('Dining Room', 10, 'diagonally forward and right'),
        ('Bathroom', 5, 'right'),
        ('Bedroom 1', 15, 'forward'),
        ('Bedroom 2', 20, 'forward')
    ],
    'Study': [
        ('Hall', 5, 'right')
    ],
    'Lounge': [
        ('Hall', 5, 'diagonally right and back'),
        ('Dining Room', 5, 'right')
    ],
    'Dining Room': [
        ('Hall', 5, 'diagonally left and back'),
        ('Lounge', 5, 'left'),
        ('Utility Room', 5, 'forward'),
        ('Kitchen', 5, 'right')
    ],
    'Bathroom': [
        ('Hall', 5, 'left')
    ],
    'Utility Room': [
        ('Dining Room', 5, 'back')
    ],
    'Kitchen': [
        ('Dining Room', 5, 'left')
    ],
    'Bedroom 1': [
        ('Hall', 15, 'back'),
        ('Bedroom 2', 5, 'right')
    ],
    'Bedroom 2': [
        ('Hall', 20, 'back'),
        ('Bedroom 1', 5, 'left')
    ],
}


def a_star_search(graph, start, goal, h):
    open_set = []
    heapq.heappush(open_set, (h[start], 0, start, [(start, None)]))  # (f_score, g_score, current_node, path)

    closed_set = set()

    while open_set:
        f_score, g_score, current_node, path = heapq.heappop(open_set)

        if current_node == goal:
            return path[1:], g_score  # Exclude the initial None direction

        if current_node in closed_set:
            continue

        closed_set.add(current_node)

        for neighbour, cost, direction in graph.get(current_node, []):
            if neighbour in closed_set:
                continue
            tentative_g_score = g_score + cost
            tentative_f_score = tentative_g_score + h[neighbour]
            new_path = path + [(neighbour, direction)]
            heapq.heappush(open_set, (tentative_f_score, tentative_g_score, neighbour, new_path))

    return None, float('inf')


