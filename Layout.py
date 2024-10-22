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
        ('Study', 1, 'left'),
        ('Lounge', 2, 'diagonally forward and left'),
        ('Dining Room', 2, 'diagonally forward and right'),
        ('Bathroom', 1, 'right'),
        ('Bedroom 1', 3, 'forward, forward and left'),
        ('Bedroom 2', 3, 'forward, forward and right')
    ],
    'Study': [
        ('Hall', 1, 'right')
    ],
    'Lounge': [
        ('Hall', 1, 'diagonally right and back'),
        ('Dining Room', 1, 'right')
    ],
    'Dining Room': [
        ('Hall', 1, 'diagonally left and back'),
        ('Lounge', 1, 'left'),
        ('Utility Room', 1, 'forward'),
        ('Kitchen', 1, 'right')
    ],
    'Bathroom': [
        ('Hall', 1, 'left')
    ],
    'Utility Room': [
        ('Dining Room', 1, 'back')
    ],
    'Kitchen': [
        ('Dining Room', 1, 'left')
    ],
    'Bedroom 1': [
        ('Hall', 3, 'right, back and back'),
        ('Bedroom 2', 1, 'right')
    ],
    'Bedroom 2': [
        ('Hall', 3, 'left, back and back'),
        ('Bedroom 1', 1, 'left')
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

# Example usage

