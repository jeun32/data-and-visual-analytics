######################################################## DO NOT EDIT ########################################################
import csv
import json
import http.client
#############################################################################################################################

class Graph:

    # Do not modify
    def __init__(self):
        """
        Initialize an empty graph.
        self.nodes is a list of tuples: (iata, name)
        self.edges is a list of tuples: (iata_a, iata_b)
        """
        self.nodes = []
        self.edges = []


    def add_node(self, iata: str, name: str) -> None:
        """
        Add a tuple (iata, name) to self.nodes if a node with that iata does not already exist.
        Duplicate nodes must be ignored.

        :param iata: str - the IATA code of the airport (e.g. 'HKG')
        :param name: str - the name of the airport (e.g. 'Hong Kong International Airport')
        """

        for existing_iata, _ in self.nodes:
            if existing_iata == iata:
                return
        self.nodes.append((iata, name))


    def add_edge(self, iata_a: str, iata_b: str) -> None:
        """
        Add a tuple (iata_a, iata_b) to self.edges if this edge does not already exist.
        The graph is undirected: (iata_a, iata_b) and (iata_b, iata_a) are the same edge.
        Duplicate edges must be ignored.

        :param iata_a: str - IATA code of one airport in the flight path
        :param iata_b: str - IATA code of the other airport in the flight path
        """

        for u, v in self.edges:
            if (u == iata_a and v == iata_b) or (u == iata_b and v == iata_a):
                return
        self.edges.append((iata_a, iata_b))


    def degree_centrality(self) -> dict:
        """
        Compute normalized degree centrality for every node in the graph.

        The degree d(v) of a node v is the number of edges attached to a node v.

        A node v with degree d(v) has a normalized degree centrality equal to

                    degree_centrality(v) = d(v)/(N−1)

        where N is the number of airports added to the graph with add_node().

        Return a score for every airport that appears in the graph — including airports with degree 0,
        and any airport that appears only as an endpoint of an edge.

        Use Python's round() function to round outputs to 6 decimal places.
        
        Do NOT use networkx or any external library.

        :rtype: dict - keys are IATA codes (str), values are centrality
                       scores (float) rounded to 6 decimal places using
                       Python's round() function.
                       e.g., {'HKG': 0.022774, 'ADD': 0.011387, ...}

        Note these examples are not the true centrality scores for those airports.
        """

        N = len(self.nodes)

        degrees = {}
        for iata, name in self.nodes:
            degrees[iata] = 0

        for u, v in self.edges:
            if u not in degrees:
                degrees[u] = 0
            if v not in degrees:
                degrees[v] = 0

        for u, v in self.edges:
            degrees[u] += 1
            degrees[v] += 1

        centrality = {}
        denom = N - 1 if N > 1 else 1

        for node, d in degrees.items():
            if N <= 1:
                score = 0.0
            else:
                score = d / denom
            centrality[node] = round(score, 6)

        return centrality


def get_data(endpoint: str, host: str = 'localhost', port: int = 3000) -> list:
    """
    Make a GET request to the specified endpoint of the API.

    You may only use packages in the Python Standard Library or Requests.

    :param endpoint: str - the API endpoint to call e.g. '/airports', '/flights', or '/iwt_flights'
    :param host:     str - the API host (e.g. 'localhost')
    :param port:     int - the API port (e.g. 3000)
    :rtype: list
    """

    conn = http.client.HTTPConnection(host, port)
    conn.request("GET", endpoint)
    response = conn.getresponse()
    raw_data = response.read().decode('utf-8')
    conn.close()
    return json.loads(raw_data)


def clean_trafficking_paths(itineraries: list) -> list:
    """
    Decompose raw IWT itineraries into unique consecutive airport pairs.

    Each itinerary is a list of IATA codes representing the sequential stops of one documented
    trafficking incident with at least two documented stops.

    None values and empty strings should be ignored (they represent unused
    columns in rows with fewer than 5 stops).

    Duplicate pairs that appear across multiple itineraries should only be included once in the output.

    Preserve the order in which stops appear. (A,B) and (B,A) are distinct flight legs in cleaned_iwt.csv,
    even though add_edge() treats them as the same undirected edge.

    The returned list must be sorted alphabetically by the first IATA code (iata_a),
    with ties broken alphabetically by the second IATA code (iata_b).

     Examples:
        ['JNB', 'DOH', 'KUL', None, None] -> [('JNB', 'DOH'), ('DOH', 'KUL')]
        ['HKG', 'CAN', None, None, None]   -> [('HKG', 'CAN')]

    :param itineraries: list of lists - each inner list contains up to 5
                        IATA codes with None values for unused stops,
                        as returned by GET /iwt_flights
    :rtype: list of (str, str) tuples, sorted alphabetically by iata_a
            then iata_b, with no duplicates
            e.g., [('ADD', 'CAN'), ('BKK', 'HKG'), ('DOH', 'KUL'), ...]
    """

    unique_pairs = []

    for itinerary in itineraries:
        valid_stops = [stop for stop in itinerary if stop is not None and stop != ""]

        for i in range(len(valid_stops) - 1):
            pair = (valid_stops[i], valid_stops[i + 1])
            if pair not in unique_pairs:
                unique_pairs.append(pair)

    return sorted(unique_pairs, key=lambda x: (x[0], x[1]))


def write_centrality_file(centrality: dict, path: str) -> None:
    """
    Write degree centrality scores for all nodes to a CSV file.

    Requirements:
        - Header row: iata,degree_centrality
        - Sorted descending by centrality score
        - Ties broken alphabetically by IATA code (ascending)
        - Ensure centrality scores calculated in degree_centrality()
          are in rounded to 6 decimal places using Python's round() function.

    Example output:
        iata,degree_centrality
        HKG,0.022774
        BKK,0.016046
        ...

    :param centrality: dict - keys are IATA codes (str), values are
                              centrality scores (float) as output from degree_centrality()
    :param path:       str  - the output file path.
                              (should either be 'full_centrality.csv' or 'iwt_centrality.csv')
    """

    sorted_items = sorted(centrality.items(), key=lambda x: (-x[1], x[0]))

    with open(path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['iata', 'degree_centrality'])
        for iata, score in sorted_items:
            writer.writerow([iata, round(score, 6)])



if __name__ == "__main__":

    full_graph  = Graph()
    iwt_graph   = Graph()

    # --------------------------------------------------------------------------------------------------------
    # STEP 1 — Load all airports from the API for the full_graph network
    # Call get_data() to retrieve all airports from the API, and add all airports to the full-flight network.
    # --------------------------------------------------------------------------------------------------------

    airports_data = get_data('/airports')
    for airport in airports_data:
        full_graph.add_node(airport['iata'], airport['name'])


    # --------------------------------------------------------------------------------------------------------
    # STEP 2 — Load all flights from the API for the full_graph network
    # Call get_data() to retrieve all flights from the API, and add all flights to the full-flight network.
    # --------------------------------------------------------------------------------------------------------

    flights_data = get_data('/flights')
    for flight in flights_data:
        full_graph.add_edge(flight['airport_a'], flight['airport_b'])

    # --------------------------------------------------------------------------------------------------------
    # STEP 3 — Load IWT airports for the iwt network
    # Only add airports to the iwt network that have a non-zero value for the 'iwt_incidents_observed_count'
    # column in the data returned by the API in Step 1. This ensures airports that have observed IWT activity,
    # but may not have documented the inbound or outbound flights, are still included in the iwt network. This
    # highlights how challenging data collection can be in the context of wildlife trafficking, and how important
    # it is to consider all available information when analyzing the network.

    # You may use the airports response already retrieved in Step 1. Do not make another API call.
    # --------------------------------------------------------------------------------------------------------

    for airport in airports_data:
        count = airport.get('iwt_incidents_observed_count')
        if count is not None and count > 0:
            iwt_graph.add_node(airport['iata'], airport['name'])


    # --------------------------------------------------------------------------------------------------------
    # STEP 4 — Load, clean, and write IWT flights for the iwt network
    # Save the cleaned IWT legs to a CSV file titled 'cleaned_iwt.csv' with the header ['iata_a', 'iata_b']
    # and each row containing a unique airport pair (iata_a, iata_b).
    # The API returns a list of dicts. Convert to a list of lists before passing to clean_trafficking_paths()
    # e.g., [{'airport_a': 'JNB', 'airport_b': 'DOH', 'airport_c': None, ...}, ...]
    #     -> [['JNB', 'DOH', None, None, None], ...]
    # --------------------------------------------------------------------------------------------------------
    
    raw_iwt_flights = get_data('/iwt_flights')

    itineraries = []
    for item in raw_iwt_flights:
        itinerary = [
            item.get('airport_a'),
            item.get('airport_b'),
            item.get('airport_c'),
            item.get('airport_d'),
            item.get('airport_e')
        ]
        itineraries.append(itinerary)

    cleaned_pairs = clean_trafficking_paths(itineraries)

    with open('cleaned_iwt.csv', mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['iata_a', 'iata_b'])
        for pair in cleaned_pairs:
            writer.writerow([pair[0], pair[1]])

    for pair in cleaned_pairs:
        iwt_graph.add_edge(pair[0], pair[1])
    


    # --------------------------------------------------------------------------------------------------------
    # STEP 5 — Compute degree centrality and write to file for both networks
    # Call degree_centrality() on both graphs and write the results using write_centrality_file()
    # full_centrality.csv should contain the degree centrality for the full flight network
    # iwt_centrality.csv should contain the degree centrality for the IWT sub-network
    # --------------------------------------------------------------------------------------------------------

    full_centrality_scores = full_graph.degree_centrality()
    write_centrality_file(full_centrality_scores, 'full_centrality.csv')

    iwt_centrality_scores = iwt_graph.degree_centrality()
    write_centrality_file(iwt_centrality_scores, 'iwt_centrality.csv')