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

        return NotImplemented


    def add_edge(self, iata_a: str, iata_b: str) -> None:
        """
        Add a tuple (iata_a, iata_b) to self.edges if this edge does not already exist.
        The graph is undirected: (iata_a, iata_b) and (iata_b, iata_a) are the same edge.
        Duplicate edges must be ignored.

        :param iata_a: str - IATA code of one airport in the flight path
        :param iata_b: str - IATA code of the other airport in the flight path
        """

        return NotImplemented


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

        return NotImplemented


def get_data(endpoint: str, host: str = 'localhost', port: int = 3000) -> list:
    """
    Make a GET request to the specified endpoint of the API.

    You may only use packages in the Python Standard Library or Requests.

    :param endpoint: str - the API endpoint to call e.g. '/airports', '/flights', or '/iwt_flights'
    :param host:     str - the API host (e.g. 'localhost')
    :param port:     int - the API port (e.g. 3000)
    :rtype: list
    """

    return NotImplemented


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

    return NotImplemented


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

    return NotImplemented



if __name__ == "__main__":

    full_graph  = Graph()
    iwt_graph   = Graph()

    # --------------------------------------------------------------------------------------------------------
    # STEP 1 — Load all airports from the API for the full_graph network
    # Call get_data() to retrieve all airports from the API, and add all airports to the full-flight network.
    # --------------------------------------------------------------------------------------------------------





    # --------------------------------------------------------------------------------------------------------
    # STEP 2 — Load all flights from the API for the full_graph network
    # Call get_data() to retrieve all flights from the API, and add all flights to the full-flight network.
    # --------------------------------------------------------------------------------------------------------





    # --------------------------------------------------------------------------------------------------------
    # STEP 3 — Load IWT airports for the iwt network
    # Only add airports to the iwt network that have a non-zero value for the 'iwt_incidents_observed_count'
    # column in the data returned by the API in Step 1. This ensures airports that have observed IWT activity,
    # but may not have documented the inbound or outbound flights, are still included in the iwt network. This
    # highlights how challenging data collection can be in the context of wildlife trafficking, and how important
    # it is to consider all available information when analyzing the network.

    # You may use the airports response already retrieved in Step 1. Do not make another API call.
    # --------------------------------------------------------------------------------------------------------





    # --------------------------------------------------------------------------------------------------------
    # STEP 4 — Load, clean, and write IWT flights for the iwt network
    # Save the cleaned IWT legs to a CSV file titled 'cleaned_iwt.csv' with the header ['iata_a', 'iata_b']
    # and each row containing a unique airport pair (iata_a, iata_b).
    # The API returns a list of dicts. Convert to a list of lists before passing to clean_trafficking_paths()
    # e.g., [{'airport_a': 'JNB', 'airport_b': 'DOH', 'airport_c': None, ...}, ...]
    #     -> [['JNB', 'DOH', None, None, None], ...]
    # --------------------------------------------------------------------------------------------------------
    

    


    # --------------------------------------------------------------------------------------------------------
    # STEP 5 — Compute degree centrality and write to file for both networks
    # Call degree_centrality() on both graphs and write the results using write_centrality_file()
    # full_centrality.csv should contain the degree centrality for the full flight network
    # iwt_centrality.csv should contain the degree centrality for the IWT sub-network
    # --------------------------------------------------------------------------------------------------------



