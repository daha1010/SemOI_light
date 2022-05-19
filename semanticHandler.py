import re, os, rdflib, logging
from rdflib import Graph
from owlready2 import *

class SemanticHandler():

    def __init__(self):

        # self.onto = get_ontology('http://192.168.178.55/augmentionOntology.owl').load()
        self.onto = get_ontology('http://192.168.178.195/augmentionOntology.owl').load()
        #self.onto = get_ontology('http://192.168.178.55/augmentionOntology.owl').load() #je nachdem welche IP


    def getSemanticEnhancement(self, detectorIds: list):
        filter = 'FILTER(?classifier = "'
        for i, detectorId in enumerate(detectorIds):
            if i < len(detectorIds) - 1:
                filter += detectorId[4] + '" || ?classifier = "'
            else:
                filter += detectorId[4] + '")'
        if len(detectorId) == 0:
            filter = ""
        queryBuilder = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX win: <http://wirtschaftsinformatik.uni-rostock.de/studentimagerecog#>

SELECT  ?detected ?classifier ?context (Count(DISTINCT ?allContextConnections) as ?relationCount)

WHERE {
        ?detected rdfs:subClassOf+ win:DetectedClasses ;
                win:ImageClassifier ?classifier .

        ?context rdfs:subClassOf* win:context ;
                       rdfs:subClassOf [
                                owl:onProperty win:hasDetectedClass ;
                                owl:someValuesFrom ?detected ] .
        ?context rdfs:subClassOf [
                 	owl:onProperty win:hasDetectedClass ;
                    owl:someValuesFrom ?allContextConnections ] .
        """ + filter + """
}
GROUP BY ?detected ?classifier ?context 
ORDER BY ?detected ?context"""
        logging.debug(queryBuilder)
        #print("sparql:" + queryBuilder)
        #for x in self.rdf:
        #    print(str(x))
        #print(list(self.onto.classes()))
        test = list(default_world.sparql("""
                   SELECT (COUNT(?x) AS ?nb)
                   { ?x a owl:Class . }
            """))
        qres = (list(default_world.sparql(queryBuilder)))
        # Converts the SPARQL-Query to a Dict-Array
        #print("FERTIG")
        responseBuilder = []
        # Converts the SPARQL-Query to a Dict-Array
        for row in qres:
            responseBuilder.append({
                "objectName": row[0].name,
                "imageClassifier": row[1],
                "contextItems": row[2].name,
                "numberOfRelations": int(row[3])
            })
        return responseBuilder
