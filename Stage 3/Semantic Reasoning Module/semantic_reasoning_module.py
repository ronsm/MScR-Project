import pprint
import sys
import rdflib
from rdflib import Graph

class semantic_reasoning_module:
    def __init__(self, ontology_name, ontology_IRI):
        print("[semantic_reasoning_module][STAT] Starting up... ", end="", flush=True)
        self.ont = self.load_ontology(ontology_name)
        self.ontology_IRI = ontology_IRI
        print("[OK]")

    def start(self):
        print("[semantic_reasoning_module][STAT] Module under test...")
        
        results = self.get_possible_activities_for_location("bedroom_location_bed")
        results = self.get_default_activity_for_location("bedroom_location_bed")
        results = self.get_super_object_of_object("object_coffee_container")
        results = self.get_neighbours_of_location("bedroom_location_bed")
        
        results = self.calculate_dependency_satisfaction("activity_make_hot_drink", ["object_kettle", "object_mug", "object_coffee_container"])

    def load_ontology(self, ontology_name):
        load_name = 'knowledge/' + ontology_name

        ont = Graph()
        ont.parse(load_name)

        return ont

# ***************************
# Ontology Querying Functions
# ***************************

    def add_IRI(self, label):
        ontology_IRI_len = len(self.ontology_IRI)

        potential_IRI = label[:ontology_IRI_len]

        if potential_IRI == self.ontology_IRI:
            label_with_IRI = label
        else:
            label_with_IRI = self.ontology_IRI + label
        
        return label_with_IRI

    def submit_query_single_return(self, subject, predicate, object):
        query = """
            PREFIX sho: <file://sho.owl#>
            SELECT ?""" + object + """
            WHERE { 
                sho:""" + subject + """ sho:""" + predicate +  """ ?""" + object + """
            }
        """

        raw_result = self.ont.query(query)
        print(query)

        results = []
        for row in raw_result:
            results.append(str(getattr(row, object)))

        if len(results) == 0:
            results.append('no_results')

        #  uncomment the line below to see submitted queries
        print(results)

        return results

    def get_possible_activities_for_location(self, location):
        subject = location
        predicate = "hasPossibleActivity"
        object = "activity"

        results = self.submit_query_single_return(subject, predicate, object)

        return results

    def get_default_activity_for_location(self, location):
        subject = location
        predicate = "hasDefaultActivity"
        object = "defaultActivity"

        results = self.submit_query_single_return(subject, predicate, object)

        return results

    def get_super_object_of_object(self, sub_object):
        subject = sub_object
        predicate = "subObjectOf"
        object = "superObject"

        results = self.submit_query_single_return(subject, predicate, object)

        return results

    def get_neighbours_of_location(self, location):
        subject = location
        predicate = "isNextTo"
        object = "neighbour"

        results = self.submit_query_single_return(subject, predicate, object)

        return results

    def get_possible_actors_for_activity(self, activity):
        subject = activity
        predicate = "hasPossibleActor"
        object = "possibleActor"

        results = self.submit_query_single_return(subject, predicate, object)

        return results

    def calculate_dependency_satisfaction(self, activity, objects):
        possible_actors = self.get_possible_actors_for_activity(activity)
        max_actors = len(possible_actors)

        objects_to_add = []
        for object in objects:
            superObject = self.get_super_object_of_object(object)
            if superObject[0] != 'no_results':
                objects_to_add.append(superObject[0])

        objects = objects + objects_to_add

        actor_count = 0

        for object in objects:
            if self.add_IRI(object) in possible_actors:
                actor_count = actor_count + 1

        score = actor_count / max_actors

        print('Score', score)

        return score