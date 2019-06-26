from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?label
    WHERE { <http://dbpedia.org/resource/Asturias> rdfs:label ?label }
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    print('%s: %s' % (result["label"]["xml:lang"], result["label"]["value"]))

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.addDefaultGraph("https://ronsm.com/courses/mscr-project/sho.owl#")
sparql.setQuery("""
    PREFIX sho: <https://ronsm.com/courses/mscr-project/sho.owl#>
    SELECT ?activity
    WHERE { 
        sho:bedroom_location_bed sho:hasPossibleActivity ?activity
    }
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

print(results)

for result in results["results"]["bindings"]:
    print('yes')
    print('%s: %s' % (result["label"]["xml:lang"], result["label"]["value"]))
    print(result["label"]["value"])