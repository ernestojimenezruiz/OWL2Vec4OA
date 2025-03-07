from owl2vec_star.rdf2vec.walkers.random import Walker
from owl2vec_star.rdf2vec.graph import KnowledgeGraph, Vertex
import numpy as np
from hashlib import md5
import rdflib
import networkx as nx
import random as rnd
from array import *
from rdflib import URIRef, Literal, BNode

edges = []

class SevinjWalker(Walker):
    def __init__(self, depth, walks_per_graph,class_onto1, class_onto2):
        print("Depth:", depth)
        print("walks_per_graph:", walks_per_graph)
        super(SevinjWalker, self).__init__(depth, walks_per_graph)
        self.class_onto1=class_onto1
        self.class_onto2=class_onto2
        self.pct_wl_sz1_lst=list()
        self.pct_wl_sz2_lst=list()
    def printVertex(self, vertex):
        print(".")
        print("From Subject:", vertex.id)
        print("From Predicate:", vertex.predicate)
        print("From Object:", vertex.name)
        print("From From:", vertex._from)
        print("From To:", vertex._to)

    def get_edge_confidence(self, graph, node, neighbor):
        # Define a method to get the confidence value of an edge
        # This example assumes edges have a 'confidence' attribute
        #self.printVertex(node)
        #self.printVertex(neighbor)
        #edges = self.get_edges(graph, node)
        
        #print("get edge conf", node.edges)
        node_edges= graph.get_neighbors(node)
        #print("Edges:", len(node_edges))
        #print(node_edges)
        if (len(node_edges)>0):
           #print("Edges length:",len(node_edges))
           foundEdge = self.referencedVertices(node, neighbor, graph)
           #foundEdge = next(iter([v for v in node_edges if v[0] == neighbor.id]), None)
           
           #print("foundEdge:",foundEdge)
           if foundEdge is None:
              confidence = 1.0
           else:
              confidence = foundEdge[0][2]
        else:
           confidence=1.0
        return confidence
    
    @classmethod
    def referencedVertices(self,vertex, neighbor, kg):
        edge = []

        # if isinstance(vertex._from, Vertex):
        #     self.referencedVertices(vertex._from, neighbor._to, kg)
                         
        # if isinstance(vertex._to, Vertex):
        #     self.referencedVertices(neighbor._to)

        # info in the edges between nodes are added to the transition matrix. they have confidence value info 
        confidence_value=kg._confidence_values_matrix[vertex][neighbor]

        # mapping
        #object = vertex.name.partition('#')[0]
        #subject = vertex.name.partition('#')[2]
        predicate = vertex.predicate
        #vertex
        #neighbor
        if "subClassOf" in vertex.name:
              #print("adding to subClassOf edges:", vertex.name, neighbor.name, confidence_value, predicate)               
              edge.append((vertex.name, neighbor.name, confidence_value,predicate))
        elif "superClassOf" in vertex.name:
              #print("adding to superClassOf edges:", vertex.name, neighbor.name, confidence_value, predicate)
              edge.append((vertex.name, neighbor.name, confidence_value, predicate))
        elif "EquivalentOf" in vertex.name:
              #print("adding to superClassOf edges:", vertex.name, neighbor.name, confidence_value, predicate)
              edge.append((vertex.name, neighbor.name, confidence_value, predicate))
        else: 
              #Edge
              predicate = vertex.predicate
              #print("adding to Edge edges:", vertex.name, neighbor.name, confidence_value, predicate)
              edge.append((vertex.name, neighbor.name, confidence_value, predicate))
              
        return edge
    
    # @classmethod
    # def get_edges(self,knowledgegraph, node):

    #         graph = rdflib.Graph();
    #         edges = []
            
    #         vertices = knowledgegraph._vertices
            

    #         for vertex in vertices:
    #             if vertex == node:
    #                print("matched node so extracting edges...", vertex)
    #                return self.referencedVertices(vertex)
    #                break
        

    #extracts random walks from knowlwedge graph 
    def extract_random_walks(self, graph, root):
        #wl_sz is walk size of onto1 and onto2
        global wl_sz_onto1 
        global set_wl_node1
        global set_wl_node2
        global wl_sz_onto2
        global pct_wl_sz1
        global pct_wl_sz2
    	
    	
        """Extract random walks of depth - 1 hops rooted in root."""
        # Initialize one walk of length 1 (the root)
        walks = {(root,)}
        set_wl_node1=set()
        set_wl_node2=set()

        for i in range(self.depth):
            walks_copy = walks.copy()
            #print("walks length:", len(walks))
            for walk in walks_copy:
                node = walk[-1]
                #print("Node:", node)
                
                # get the edges which already have the confidences
                #node.edges = self.get_edges(graph, node)
                # print(node.edges)
                # now get the nodes neighbors
                neighbors = graph.get_neighbors(node)
                # print('\n',neighbors,'\n')
                #print("Neighbours length:", len(neighbors))

                if len(neighbors) > 0:
                    #print("Node:", node)
                    #print("Neighbours length:", len(neighbors))
                    walks.remove(walk)

                    # walker priorities the mapping 
                    for neighbor in neighbors:
                        pred_name=neighbor.name
                        if pred_name=='=':
                            if neighbor._to==node:
                                foundEdge = self.referencedVertices(node, neighbor, graph)
                                if foundEdge[0][2] != 0:
                                    chosen_neighbor=neighbor._from
                            elif neighbor._from==node:
                                foundEdge = self.referencedVertices(node, neighbor, graph)
                                if foundEdge[0][2] != 0:
                                    chosen_neighbor=neighbor._to

                     # Calculate the probability distribution for neighbor selection       
                    else:
                        confidences = [self.get_edge_confidence(graph, node, neighbor) for neighbor in neighbors]
                        total_confidence = sum(confidences)
                        #print("total_confidence", total_confidence)
                        
                        probabilities = [confidence / total_confidence for confidence in confidences]

                        # Choose a neighbor based on the probability distribution
                        #print('\n\nWalks basladi\n\n')
                        chosen_neighbor = np.random.choice(neighbors, p=probabilities)

                    #print("adding to walks walk: ", (walk, chosen_neighbor),'\n\n')
                    #walks.add((walk, chosen_neighbor))
                    walks.add(walk + (chosen_neighbor, ))

                    #n_n is a node name; wl- walk 
                    
                    # for finding percentage of walked nodes
                    n_n=chosen_neighbor.name.split("/")[-1]
                    print(n_n,self.class_onto2)
                    if n_n in self.class_onto1:
                        set_wl_node1.add(n_n)
                       

                    if n_n in self.class_onto2:
                        set_wl_node2.add(n_n)
                    
                    


                # for neighbor in neighbors:
                #     walks.add(walk + (neighbor, ))
                    #walks.add(walk + (chosen_neighbor, ))
                    #print("walks length:", len(walks))
                    #print(walks)
                
            if self.walks_per_graph is not None:
                n_walks = min(len(walks),  self.walks_per_graph)
                walks_ix = np.random.choice(range(len(walks)), replace=False,
                                            size=n_walks)
                #print('\n\nNumber of walks:', n_walks,'\n\n')
                if len(walks_ix) > 0:
                    walks_list = list(walks)
                    walks = {walks_list[ix] for ix in walks_ix}
          # pct_wl_sz - percentage of walk size          
        self.pct_wl_sz1=(len(set_wl_node1)/len(self.class_onto1))*100
        self.pct_wl_sz2=(len(set_wl_node2)/len(self.class_onto2))*100
        self.pct_wl_sz1_lst.append(self.pct_wl_sz1)
        self.pct_wl_sz2_lst.append(self.pct_wl_sz2)
        return list(walks)

        

    def extract(self, graph, instances):
        canonical_walks = set()
        import time
        import statistics
        means=[]
        stds=[]
        times=[]
        
        for i in range(10):
            hops=[]
            walks_list=[]
            # Record the starting time
            start_time = time.time()
            for instance in instances:
                walks = self.extract_random_walks(graph, Vertex(str(instance)))
                for walk in walks:
                    canonical_walk = []
                    i=0
                    #print("walk:", walk)
                    for i, hop in enumerate(walk):
                        #print("type hop",i,':', hop.name)
                        if i == 0 or i % 2 == 1:
                            if isinstance(hop, tuple):
                                canonical_walk.append(hop[1].name)
                            else: 
                                canonical_walk.append(hop.name)
                        else:
                            if isinstance(hop, tuple):
                                canonical_walk.append(hop[1].name)
                            else: 
                                canonical_walk.append(hop.name)
                    hops.append(len(walk))
                    canonical_walks.add(tuple(canonical_walk))
            # Calculate the time taken by the process
            end_time = time.time()
            elapsed_time = end_time - start_time
            # Calculate the mean
            mean = statistics.mean(hops)

            # Calculate the standard deviation
            std_dev = statistics.stdev(hops)
            walks_list.append(len(walks))
            means.append(mean)
            stds.append(std_dev)
            times.append(elapsed_time)
        
            
        mean_means_hop = statistics.mean(means)

        mean_std_hop = statistics.mean(stds)
        # std_std_hop = statistics.stdev(stds)

        mean_times_hop = statistics.mean(times)
        std_times_hop = statistics.stdev(times)
        # we run the system 10 times this is why we find mean ve std deviation
        
        print('Number of nodes',len(instances))
        #walk da ferqli hop sizelar olur her walkdan ortalama tapilmis meanlarin 10 rundaki meanini tapriq
        print(f"Mean of mean hops: {mean_means_hop}")
        print(f"Mean of Standard Deviation hops: {mean_std_hop}")

        print(f"Mean Time walks taken by the 10 process: {mean_times_hop:.4f} seconds")
        print(f"Std Time walks taken by the 10 process: {std_times_hop:.4f} seconds")
        print(f"Mean of percentage of visited nodes in ontology  1: {statistics.mean(self.pct_wl_sz1_lst)}%" )
        print(f"Mean of percentage of visited nodes in ontology  2: {statistics.mean(self.pct_wl_sz2_lst)}%")

        return canonical_walks