from flask import Flask, request, jsonify, render_template
import re
import heapq

app = Flask(__name__)

# Campus map with locations and connections
campus_map = {
    "MAIN_GATE": {"ADMIN_BLOCK": 2, "LIBRARY": 3},
    "ADMIN_BLOCK": {"MAIN_GATE": 2, "CANTEEN": 1, "PHARMACY_BLOCK": 2},
    "CANTEEN": {"ADMIN_BLOCK": 1, "TERESA_A": 3, "PHARMACY_BLOCK": 2},
    "PHARMACY_BLOCK": {"ADMIN_BLOCK": 2, "CANTEEN": 2, "ENGINEERING_BLOCK": 4},
    "ENGINEERING_BLOCK": {"PHARMACY_BLOCK": 4, "TERESA_D": 3, "LIBRARY": 2},
    "LIBRARY": {"MAIN_GATE": 3, "ENGINEERING_BLOCK": 2},
    "TERESA_A": {"CANTEEN": 3, "TERESA_D": 4},
    "TERESA_D": {"ENGINEERING_BLOCK": 3, "TERESA_A": 4, "MEDICAL_BLOCK": 5, "ATAL_A": 2},
    "MEDICAL_BLOCK": {"TERESA_D": 5, "SPORTS_COMPLEX": 3, "SARDAR_B": 3},
    "SPORTS_COMPLEX": {"MEDICAL_BLOCK": 3, "LIBRARY": 6},
    "ATAL_A": {"TERESA_D": 2, "SARDAR_B": 3},
    "SARDAR_B": {"MEDICAL_BLOCK": 3, "ATAL_A": 3}
}

def dijkstra(graph, start, end):
    """
    Implements Dijkstra's algorithm for finding shortest path between two points.
    """
    queue = [(0, start, [])]
    visited = set()

    while queue:
        (cost, node, path) = heapq.heappop(queue)
        if node not in visited:
            path = path + [node]
            visited.add(node)

            if node == end:
                return (cost, path)

            for adjacent, weight in graph.get(node, {}).items():
                if adjacent not in visited:
                    heapq.heappush(queue, (cost + weight, adjacent, path))

    return (float("inf"), [])

def format_path(path):
    """
    Formats the path list into a readable string.
    """
    return " -> ".join(path)

def normalize_location(location):
    """
    Normalizes location names to match the graph keys.
    """
    location = location.upper().replace(" ", "_")
    return location

def handle_greeting(message):
    """
    Handles greeting messages.
    """
    greetings = ["hi", "hello", "hey", "hii"]
    return message.lower() in greetings

def get_path_response(start, end):
    """
    Generates response for path queries.
    """
    start = normalize_location(start)
    end = normalize_location(end)

    if start not in campus_map or end not in campus_map:
        return "Sorry, I don't recognize one or both of these locations. Please check the location names and try again."

    cost, path = dijkstra(campus_map, start, end)
    if path:
        formatted_path = format_path(path)
        return f"Path from {start.replace('_', ' ')} to {end.replace('_', ' ')} is: {formatted_path} with a total cost of {cost}."
    else:
        return "Sorry, I couldn't find a path between these locations."

@app.route('/')
def index():
    """Renders the main page."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handles chat requests and generates responses.
    """
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'response': 'Please enter a message.'})

    # Handle greetings
    if handle_greeting(user_message):
        return jsonify({'response': 'Hello! How can I help you today? You can ask me about paths between campus locations.'})

    # Handle path queries
    path_match = re.search(r"path from (.+?) to (.+)", user_message, re.IGNORECASE)
    if path_match:
        start, end = path_match.groups()
        response = get_path_response(start, end)
        return jsonify({'response': response})

    return jsonify({'response': 'I can help you find paths between campus locations. Please ask something like "path from Main Gate to Teresa A"'})

if __name__ == '__main__':
    app.run(debug=True)