import heapq

# Define locations heuristic h(n)
h = {
    'Charging Station': 0,
    'Hall': 1,
    'Study': 2,
    'Bathroom': 2,
    'Dining Room': 2,
    'Kitchen': 3,
    'Utility Room': 3,
    'Bedroom 1': 3,
    'Bedroom 2': 3,
    'Lounge': 2,
    'Washing Machine': 4,
    'Tumble Dryer': 4,
    'Ironing Board': 4
}

# Define the graph with directions
graph = {
    'Hall': [
        ('Charging Station', 1, 'diagonally back and right'),
        ('Study', 5, 'left'),
        ('Lounge', 10, 'diagonally forward and left'),
        ('Dining Room', 10, 'diagonally forward and right'),
        ('Bathroom', 5, 'right'),
        ('Bedroom 1', 15, 'forward'),
        ('Bedroom 2', 15, 'forward')
    ],
    'Charging Station': [
    ('Hall', 1, 'diagonally forward and left')
    ],
    'Study': [
        ('Hall', 5, 'right')
    ],
    'Lounge': [
        ('Hall', 5, 'diagonally back and right')
    ],
    'Dining Room': [
        ('Hall', 5, 'diagonally back and left'),
        ('Utility Room', 5, 'forward'),
        ('Kitchen', 5, 'right')
    ],
    'Bathroom': [
        ('Hall', 5, 'left')
    ],
    'Utility Room': [
        ('Dining Room', 5, 'back'),
        ('Washing Machine', 1, 'right'),
        ('Tumble Dryer', 1, 'left'),
        ('Ironing Board', 1, 'forward')
    ],
    'Washing Machine': [
        ('Utility Room', 1, 'left'),
        ('Tumble Dryer', 2, 'left'),
        ('Ironing Board', 2, 'diagonally forward and left')
    ],
    'Tumble Dryer': [
        ('Utility Room', 1, 'right'),
        ('Washing Machine', 2, 'right'),
        ('Ironing Board', 2, 'diagonally forward and right')
    ],
    'Ironing Board': [
        ('Utility Room', 1, 'back'),
        ('Washing Machine', 2, 'diagonally back and right'),
        ('Tumble Dryer', 2, 'diagonally back and left')
    ],
    'Kitchen': [
        ('Dining Room', 5, 'left')
    ],
    'Bedroom 1': [
        ('Hall', 15, 'back'),
        ('Bedroom 2', 5, 'right')
    ],
    'Bedroom 2': [
        ('Hall', 15, 'back'),
        ('Bedroom 1', 5, 'left')
    ],
}

# Define actions
actions = {
    'Pick up the dirty laundry',
    'Put the dirty laundry in the washing machine',
    'Put the laundry in the tumble dryer',
    'Hang up the washing',
    'Iron these clothes',
    'Neatly fold this laundry',
    'Put this clean laundry away',
    'Sort this laundry by washing cycle type',
    'Sort this clean laundry according to where it belongs'
}

# Implementation of A* search to return list of rooms to pass through
async def a_star_search(graph, start, goal, h):
    open_set = []
    heapq.heappush(open_set, (h[start], 0, start, [(start, None)]))  # (f_score, g_score, current_node, path)
    closed_set = set()

    while open_set:
        f_score, g_score, current_node, path = heapq.heappop(open_set)
        if current_node == goal:
            return path[1:]  # Exclude the initial None direction
        if current_node in closed_set:
            continue
        closed_set.add(current_node)

        for neighbour, cost, direction in graph.get(current_node, []):
            if neighbour in closed_set:
                continue
            tentative_g_score = g_score + cost
            tentative_f_score = tentative_g_score + h[neighbour] # A* calculation of cost f(n) = g(n) + h(n)
            new_path = path + [(neighbour)]
            heapq.heappush(open_set, (tentative_f_score, tentative_g_score, neighbour, new_path))

    return None
