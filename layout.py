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
        ('Charging Station', 2, 'diagonally back and right'),
        ('Study', 2, 'left'),
        ('Lounge', 2, 'diagonally forward and left'),
        ('Dining Room', 2, 'diagonally forward and right'),
        ('Bathroom', 2, 'right'),
        ('Bedroom 1', 4, 'forward'),
        ('Bedroom 2', 4, 'forward')
    ],
    'Charging Station': [
    ('Hall', 2, 'diagonally forward and left')
    ],
    'Study': [
        ('Hall', 2, 'right')
    ],
    'Lounge': [
        ('Hall', 2, 'diagonally back and right')
    ],
    'Dining Room': [
        ('Hall', 2, 'diagonally back and left'),
        ('Utility Room', 2, 'forward'),
        ('Kitchen', 2, 'right')
    ],
    'Bathroom': [
        ('Hall', 2, 'left')
    ],
    'Utility Room': [
        ('Dining Room', 2, 'back'),
        ('Washing Machine', 2, 'right'),
        ('Tumble Dryer', 2, 'left'),
        ('Ironing Board', 2, 'forward')
    ],
    'Washing Machine': [
        ('Utility Room', 2, 'left')
    ],
    'Tumble Dryer': [
        ('Utility Room', 2, 'right')
    ],
    'Ironing Board': [
        ('Utility Room', 2, 'back')
    ],
    'Kitchen': [
        ('Dining Room', 2, 'left')
    ],
    'Bedroom 1': [
        ('Hall', 4, 'back')
    ],
    'Bedroom 2': [
        ('Hall', 4, 'back')
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
    open_set = [] # list for storing 'min heap' structure of the priority queue heapq

    # Set push the initial values passed to the function into the priority queue
    heapq.heappush(open_set, (h[start], 0, start, [(start, None)]))  # (f_score, g_score, current_node, path)
    closed_set = set() # For storing values already visited

    # Look through priority until we find the goal, if the goal does not exist or cannot be reached, return none.
    while open_set:
        f_score, g_score, current_node, path = heapq.heappop(open_set)
        # Return the path if the current node is the goal
        if current_node == goal:
            return path[1:]  # Exclude the initial None direction

        # If current node is already in the closed set, restart the while loop
        if current_node in closed_set:
            continue

        # Add the current node to the closed set
        closed_set.add(current_node)

        # Explore the neighbours of the current node
        for neighbour, cost, direction in graph.get(current_node, []):
            if neighbour in closed_set:
                continue
            # If neighbour not yet explored, calculate new f(n) and update path
            updated_g_score = g_score + cost
            updated_f_score = updated_g_score + h[neighbour] # A* calculation of cost f(n) = g(n) + h(n)
            new_path = path + [(neighbour)]
            # Push updated costs, and path to open set for this node (contained in variable neighbour)
            heapq.heappush(open_set, (updated_f_score, updated_g_score, neighbour, new_path))

    return None
