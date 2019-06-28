import rdflib
from rdflib import Graph

g = Graph()
g.parse('sho.owl')

query = """
    PREFIX sho: <file://sho.owl#>
    SELECT ?activity
    WHERE { 
        sho:bedroom_location_bed sho:hasPossibleActivity ?activity
    }
"""
for row in g.query(query):
    print(row.activity)