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
        ('Study', 10, 'left'),
        ('Lounge', 20, 'diagonally forward and left'),
        ('Dining Room', 20, 'diagonally forward and right'),
        ('Bathroom', 10, 'right'),
        ('Bedroom 1', 30, 'forward'),
        ('Bedroom 2', 40, 'forward')
    ],
    'Study': [
        ('Hall', 10, 'right')
    ],
    'Lounge': [
        ('Hall', 10, 'diagonally right and back'),
        ('Dining Room', 10, 'right')
    ],
    'Dining Room': [
        ('Hall', 10, 'diagonally left and back'),
        ('Lounge', 10, 'left'),
        ('Utility Room', 10, 'forward'),
        ('Kitchen', 10, 'right')
    ],
    'Bathroom': [
        ('Hall', 10, 'left')
    ],
    'Utility Room': [
        ('Dining Room', 10, 'back')
    ],
    'Kitchen': [
        ('Dining Room', 10, 'left')
    ],
    'Bedroom 1': [
        ('Hall', 30, 'back'),
        ('Bedroom 2', 10, 'right')
    ],
    'Bedroom 2': [
        ('Hall', 40, 'back'),
        ('Bedroom 1', 10, 'left')
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

        for neighbor, cost, direction in graph.get(current_node, []):
            if neighbor in closed_set:
                continue
            tentative_g_score = g_score + cost
            tentative_f_score = tentative_g_score + h[neighbor]
            new_path = path + [(neighbor, direction)]
            heapq.heappush(open_set, (tentative_f_score, tentative_g_score, neighbor, new_path))

    return None, float('inf')

