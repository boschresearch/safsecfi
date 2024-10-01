# Copyright (c) 2024 Robert Bosch GmbH
# SPDX-License-Identifier: MIT

import sys
from lib import *
import networkx as nx
from tabulate import tabulate

######################################Configurable inputs#####################################
#list of security features
secFeaturePkgID_list = [] #Specify XMI IDs of each security feature
secFeaturePkgID_name_dict = {} #Specify a dict in which each key is the XMI ID of a security feature and the value corresponding to the key is the name of the security feature e.g. {'EAPK_8451D5F3_2430_4c17_BBA3_FCDD12AFD7DD': 'Secure Boot uP'}

#list of safety features
safFeature_pkg_list = [] #Specify XMI IDs of each safety feature
safFeaturePkgID_name_dict = {} #Specify a dict in which each key is the XMI ID of a safety feature and the value corresponding to the key is the name of the safety feature e.g. {'EAPK_5BB67621_1726_4b9f_A073_C64ADDD673B6': 'Ethernet end-to-end protection'}

#mapping to each security feature to its security relevant components
#the variable secFeID_compID_dict can be user defined or automatically generated.
secFeID_compID_dict = {} #Specify a dict in which each key is the XMI ID of a security feature and the value corresponding to the key is the list of XMI IDs of security relevant components for the security feature e.g. {'EAPK_8451D5F3_2430_4c17_BBA3_FCDD12AFD7DD': ['EAID_CE767137_4FA5_4ed2_9CD5_C504E3D349F2', 'EAID_7FBBC274_4A52_4b4d_AD3C_C4881393D12F']}
secComponentID_name_dict = {} #Specify a dict in which each key is the XMI ID of a security relevant component and the value corresponding to the key is the name of the security relevant component e.g. {'EAID_CE767137_4FA5_4ed2_9CD5_C504E3D349F2':'MasterSecModule'}

#mapping to each safety feature to its safety relevant components
#the variable secFeID_compID_dict can be user defined or automatically generated.
safFeID_compID_dict = {} #Specify a dict in which each key is the XMI ID of a safety feature and the value corresponding to the key is the list of XMI IDs of security relevant components for the security feature
safComponentID_name_dict = {} #Specify a dict in which each key is the XMI ID of a safety relevant component and the value corresponding to the key is the name of the safety relevant component

#list of components and messages of all safety and security features extracted/parsed from the UML software architecture model of the system
secFeID_nodeIDset_dict = {} #Specify a dict in which each key is a XMI ID of a security feature and the value corresponding to the key is a set of XMI IDs of lifelines modeled in sequence diagrams of the security feature e.g. {'EAPK_8451D5F3_2430_4c17_BBA3_FCDD12AFD7DD': {'EAID_CE767137_4FA5_4ed2_9CD5_C504E3D349F2', 'EAID_4971CC93_65E3_4707_90A3_633215958773'}}
safFeID_nodeIDset_dict = {} #Specify a dict in which each key is a XMI ID of a safety feature and the value corresponding to the key is a set of XMI IDs of lifelines modeled in sequence diagrams of the safety feature

secFeID_nodeIDnamedict_dict = {} #Specify a dict in which each key is a XMI ID of a security feature and the value corresponding to the key is another dict in which each key is a XMI ID of a lifeline modeled in sequence diagrams of the security feature and the corresponding value is the name of the lifeline. For e.g. {'EAPK_8451D5F3_2430_4c17_BBA3_FCDD12AFD7DD': {'EAID_CE767137_4FA5_4ed2_9CD5_C504E3D349F2':'MasterSecModule'}}
safFeID_nodeIDnamedict_dict = {} #Specify a dict in which each key is a XMI ID of a safety feature and the value corresponding to the key is another dict in which each key is a XMI ID of a lifeline modeled in sequence diagrams of the safety feature and the corresponding value is the name of the lifeline.

secFeID_edgeIDlist_dict =  {} #Specify a dict in which each key is a XMI ID of a security feature and the value corresponding to the key is a set of XMI IDs of messages modeled in the sequence diagrams of the security feature
safFeID_edgeIDlist_dict = {} #Specify a dict in which each key is a XMI ID of a safety feature and the value corresponding to the key is a set of XMI IDs of messages modeled in the sequence diagrams of the safety feature

secFeID_edgeIDnamedict_dict = {} #Specify a dict in which each key is a XMI ID of a security feature and the value corresponding to the key is another dict in which each key is a XMI ID of a message modeled in the sequence diagrams of the security feature and the corresponding value is the name of the message. For e.g. {'EAPK_8451D5F3_2430_4c17_BBA3_FCDD12AFD7DD': {'EAID_32A65DFF_AA41_4ad3_8EC6_F9288554C66D':'MAC_verify'}}
safFeID_edgeIDnamedict_dict = {} #Specify a dict in which each key is a XMI ID of a safety feature and the value corresponding to the key is another dict in which each key is a XMI ID of a message modeled in the sequence diagrams of the safety feature and the corresponding value is the name of the message.

secMsgID_name_dict = {} #Specify a dict in which each key is a XMI ID of a message modeled in a sequence diagram of the security feature and the corresponding value is the name of the message. 
safMsgID_name_dict = {} #Specify a dict in which each key is a XMI ID of a message modeled in a sequence diagram of the safety feature and the corresponding value is the name of the message.

#Output of the FIISS and X-I-FASST methods (for comparison with Vogelsang's output)
FIISS_FIs_names = [] #Specify a list of feature interaction names that has been found by the FIISS method. For e.g. [['secure communication via Ethernet', 'Ethernet end-to-end protection']]
X_IFASST_FIs_names = [] ##Specify a list of feature interaction names that has been found by the X-I-FASST method.
##############################################################################################

featureID_nodeIDset_dict = {}
componentID_name_dict = {}
messageID_name_dict = {}
featureID_nodeIDnamedict_dict = {}
featureID_edgeIDlist_dict = {}
featureID_edgeIDnamedict_dict = {}
featurePkgID_list = []
featurePkgID_name_dict = {}
componentID_name_dict.update(secComponentID_name_dict)
componentID_name_dict.update(safComponentID_name_dict)
messageID_name_dict.update(secMsgID_name_dict)
messageID_name_dict.update(safMsgID_name_dict)
featurePkgID_list.extend(secFeaturePkgID_list)
featurePkgID_list.extend(safFeature_pkg_list)
featurePkgID_name_dict.update(secFeaturePkgID_name_dict)
featurePkgID_name_dict.update(safFeaturePkgID_name_dict)
featureID_nodeIDset_dict.update(secFeID_nodeIDset_dict)
featureID_nodeIDset_dict.update(safFeID_nodeIDset_dict)
featureID_nodeIDnamedict_dict.update(secFeID_nodeIDnamedict_dict)
featureID_nodeIDnamedict_dict.update(safFeID_nodeIDnamedict_dict)
featureID_edgeIDlist_dict.update(secFeID_edgeIDlist_dict)
featureID_edgeIDlist_dict.update(safFeID_edgeIDlist_dict)
featureID_edgeIDnamedict_dict.update(secFeID_edgeIDnamedict_dict)
featureID_edgeIDnamedict_dict.update(safFeID_edgeIDnamedict_dict)
##################################################################################################
    
class GetSecurityFeatures():
    "Get list of all security features as packages"
    def __init__(self, security_feature_list):
        self.security_feature_list = security_feature_list
    
    def get_security_feature_name(self):
        "For each element in the list, find the name and store it in dict with key as feature id and name as value"
        feature_id_name_dict = {}
        for element in self.security_feature_list:
            path = ".//packagedElement[@xmi:id = '{}'][@xmi:type = 'uml:Package']".format(element)
            path_iterator = get_iterator(path, 2)
            for object in path_iterator:
                id, name, type = get_iterator_attributes(object)
                feature_id_name_dict.update({element:name})
        return feature_id_name_dict

class GetSafetyFeatures():
    "Get list of all safety features as packages"
    def __init__(self, path):
        self.path = path
    
    def get_safety_feature(self):
        "get all safety features from the main safety package"
        feature_id_name_dict = {}
        safety_feature_list = []
        sa_feature_path_iterator = get_iterator(self.path, 2)
        for element in sa_feature_path_iterator:
            id, name, type = get_iterator_attributes(element)
            safety_feature_list.append(id)
            feature_id_name_dict.update({id:name})
        return safety_feature_list, feature_id_name_dict

class CreateInteractionGraph():
    "Create a graph containing nodes as components, i.e. classifiers of lifelines and directed edges as messages exchanges between lifelines"
    def __init__(self, featurePkgID_list, featureID_nodeIDset_dict, featureID_nodeIDnamedict_dict, featureID_edgeIDlist_dict, featureID_edgeIDnamedict_dict):
        self.featurePkgID_list = featurePkgID_list
        self.feID_nodeIDset_dict = featureID_nodeIDset_dict
        self.feID_nodeIDnamedict_dict = featureID_nodeIDnamedict_dict
        self.feID_edgeIDlist_dict = featureID_edgeIDlist_dict
        self.feID_edgeIDnamedict_dict = featureID_edgeIDnamedict_dict
    
    def get_nodes_edges_of_all_saf_and_sec_features(self):
        "store nodes of all safety and security features in a single data struct; do the same for edges"
        nodeIDs_set = set()
        nodeID_name_dict = {}
        edgeIDs_list = []
        edgeID_name_dict = {}
        for element in self.featurePkgID_list: #for each safety or security feature
            perelement_nodeIDs_set = self.feID_nodeIDset_dict[element]
            if len(perelement_nodeIDs_set) != 0:
                nodeIDs_set.update(perelement_nodeIDs_set)
            perelement_nodeID_name_dict = self.feID_nodeIDnamedict_dict[element]
            if len(perelement_nodeID_name_dict.keys()) != 0:
                nodeID_name_dict.update(perelement_nodeID_name_dict)
            
            perelement_edgeIDs_list = self.feID_edgeIDlist_dict[element]
            if len(perelement_edgeIDs_list) != 0:
                edgeIDs_list.extend(perelement_edgeIDs_list)
            perelement_edgeID_name_dict = self.feID_edgeIDnamedict_dict[element]
            if len(perelement_edgeID_name_dict.keys()) != 0:
                edgeID_name_dict.update(perelement_edgeID_name_dict)
        return nodeIDs_set, nodeID_name_dict, edgeIDs_list, edgeID_name_dict
    
    def create_multidi_graph(self):
        "Create a multi directed graph that stores lifelines as nodes and messages exchanged between lifelines as edges of the graph."
        nodeIDs_set, nodeID_name_dict, edgeIDs_list, edgeID_name_dict = self.get_nodes_edges_of_all_saf_and_sec_features() #get nodes and edges from seq. diags.
        G1 = nx.MultiDiGraph()
        G1.add_nodes_from(nodeIDs_set)
        G1.add_edges_from(edgeIDs_list)
        return G1

class ExtractFeatureDependencies():
    def __init__(self, securityFeIDs_list, safetyFeIDs_list, componentInterac_graph, secFeID_compID_dict, safFeID_compID_dict, featurePkgID_name_dict, componentID_name_dict, messageID_name_dict):
        self.secFeIDs_list = securityFeIDs_list
        self.safFeIDs_list = safetyFeIDs_list
        self.SWCInterac_graph = componentInterac_graph
        self.secFe_to_SWCid_map = secFeID_compID_dict
        self.safFe_to_SWCid_map = safFeID_compID_dict
        self.featurePkgID_name_dict = featurePkgID_name_dict
        self.componentID_name_dict = componentID_name_dict
        self.messageID_name_dict = messageID_name_dict
    
    def get_interaction_paths(self, feature_combID, graphquery_list, graph):
        pathIDs_list = []
        pathNames_list = []
        queryPathsFoundFeComb_list = []
        for index, value in enumerate(graphquery_list):
            src = value[0]
            dst = value[1]
            eachQueryPathIDs_list = []
            eachQueryPathNames_list = []
            #print("src in G: ", graph.has_node(src), " dst in G: ", graph.has_node(dst))
            if graph.has_node(src) is True and graph.has_node(dst) is True:
                for path in nx.all_simple_edge_paths(graph, source = src, target = dst, cutoff = 1): #query graph to find paths from source node to destination node
                    eachsubpathNames_list = []
                    eachQueryPathIDs_list.append(path)
                    #print("type(path): ", type(path), " path: ", path)
                    for index1, subpath in enumerate(path):
                        mSG_name = None
                        msgID = subpath[-1]
                        if msgID in self.messageID_name_dict:
                            mSG_name = self.messageID_name_dict[msgID]
                        subpathname_tuple = tuple((self.componentID_name_dict[src], self.componentID_name_dict[dst], mSG_name))
                        eachsubpathNames_list.append(subpathname_tuple)
                        #print("type(subpath): ", type(subpath), " subpath: ", subpath, " subpathname_tuple: ", subpathname_tuple)
                    eachQueryPathNames_list.append(eachsubpathNames_list)
                    if len(path) != 0:
                        print("Path for queryID:", value, " queryName: ", [self.componentID_name_dict[src], self.componentID_name_dict[dst]], " is: ", eachsubpathNames_list)
                        break
                if len(eachQueryPathIDs_list) != 0:
                    if value not in queryPathsFoundFeComb_list:
                        queryPathsFoundFeComb_list.append(value) #Store the query (for the selected feature combination) for which atleast one interaction path was found
                pathIDs_list.extend(eachQueryPathIDs_list)
                pathNames_list.extend(eachQueryPathNames_list)
            else:
                print("Warning! One of the components specified in the query: ", [self.componentID_name_dict[src], self.componentID_name_dict[dst]], "is absent in the graph!")
            
        return pathIDs_list, pathNames_list, queryPathsFoundFeComb_list
    
    def getProductoflists(self):
        "For lists, i.e. list1 and list2, get the product of list1 and list2, and the product of list2 and list1 and combine (summation) the output of both products obtained"
        bidirectionalproduct_list = []
        productfrom1to2_list = list(itertools.product(list(set1), list(set2)))
        productfrom2to1_list = list(itertools.product(list(set2), list(set1)))
        bidirectionalproduct_list = [*productfrom1to2_list, *productfrom2to1_list]
        return bidirectionalproduct_list
    
    def extractFeatureDependencies(self):
        "For wach feature combination, extract their mapped components and create a component query list to query the interaction path."
        feID_to_SWCid_map_dict = {}
        query_list = []
        pathIDs_list = []
        FI_list = []
        
        #create a single dict containing of mapping of security features to their relevant components (SWCs) and safety features to their safety relevant SWCs
        feID_to_SWCid_map_dict.update(self.secFe_to_SWCid_map)
        feID_to_SWCid_map_dict.update(self.safFe_to_SWCid_map)
        
        #Create a combination (2 ways) using the sets safety to security features
        productfrom1to2_list = list(itertools.product(self.secFeIDs_list, self.safFeIDs_list))
        productfrom2to1_list = list(itertools.product(self.safFeIDs_list, self.secFeIDs_list))
        featureIDcomb_list = [*productfrom1to2_list, *productfrom2to1_list]
        
        print("Debug! len(featureIDcomb_list): ", len(featureIDcomb_list), " featureIDcomb_list: ", featureIDcomb_list)
        
        all_queries_list = []
        queryIDsPathsFound_list = []
        feComb_pathsfound_list = []
        for element in featureIDcomb_list:
            query_list = []
            pathIDs_list = []
            pathNames_list = []
            queryPathsFoundFeComb_list = []
            srcSWCids_list = feID_to_SWCid_map_dict[element[0]] #extract components mapped to the source feature
            dstSWCids_list = feID_to_SWCid_map_dict[element[1]] #extract components mapped to the destination feature
            #print("\nFeatureCombID: ", element, " srcSWCids_list: ", srcSWCids_list, " dstSWCids_list: ", dstSWCids_list)
            print("\nFor_feature_comb: ", get_listnames_from_listIDs(element, featurePkgID_name_dict))
            print("Before removing shared components! \nlen(srcSWCids_list): ", len(srcSWCids_list), " srcSWCids_list: ", srcSWCids_list, "\nlen(dstSWCids_list): ", len(dstSWCids_list), " dstSWCids_list: ", dstSWCids_list)
            
            #checking for shared components and removing them
            srcSWCids_list, dstSWCids_list = remove_commoncomponents(set(srcSWCids_list), set(dstSWCids_list))
            elementname_list = get_listnames_from_listIDs(element, featurePkgID_name_dict)
            srcSWCnames_list = get_listnames_from_listIDs(srcSWCids_list, self.componentID_name_dict)
            dstSWCnames_list = get_listnames_from_listIDs(dstSWCids_list, self.componentID_name_dict)
            print("After removing shared components! \nlen(srcSWCids_list): ", len(srcSWCids_list), " srcSWCids_list: ", srcSWCids_list, "\nsrcSWCnames_list: ", srcSWCnames_list, "\nlen(dstSWCids_list): ", len(dstSWCids_list), " dstSWCids_list: ", dstSWCids_list, "\ndstSWCnames_list: ", dstSWCnames_list)
            
            #print("After removing shared components! srcSWCids_list: ", srcSWCids_list, " dstSWCids_list: ", dstSWCids_list)
            #print("\nFeatureCombID: ", element, " srcSWCids_list: ", srcSWCids_list, " dstSWCids_list: ", dstSWCids_list)
            #print("\nFeatureCombName: ", elementname_list, " srcSWCnames_list: ", srcSWCnames_list, " dstSWCnames_list: ", dstSWCnames_list)
            
            #generate component query list
            if len(srcSWCids_list) != 0 and len(dstSWCids_list) !=0:
                query_list = list(itertools.product(list(srcSWCids_list), list(dstSWCids_list)))
            else:
                print("Can't generate query list as the components realizing either the source or destination feature are empty")
            
            #query interaction graph for each query in the query list
            if len(query_list) != 0:
                querynames_list = []
                #creating a list of query names for debugging and store the queries generated per feature combination in a single list called all_queries_list
                for query in query_list:
                    if query not in all_queries_list:
                        all_queries_list.append(query)
                    queryname_list = get_listnames_from_listIDs(query, self.componentID_name_dict)
                    if len(queryname_list) != 0:
                        querynames_list.append(queryname_list)
                print("Generated query_list! len(query_list): ", len(query_list), " queryIDs_list: ", query_list, "\nqueryNames_list: ", querynames_list)
                print("Beginning search for the interaction paths for this query list...")
                pathIDs_list, pathNames_list, queryPathsFoundFeComb_list = self.get_interaction_paths(element, query_list, self.SWCInterac_graph)
                #print("queryIDs_list: ", query_list, " queryNames_list: ", querynames_list)
                #print("pathIDs_list: ", pathIDs_list)
            
            #extract feature dependency if at-least one direct path was identified
            if len(pathIDs_list) != 0:
                FI_list.append(list(element))
                if element not in feComb_pathsfound_list:
                    feComb_pathsfound_list.append(element)
                queryNamesPathsFound_list = []
                for query in queryPathsFoundFeComb_list:
                    queryname_list = get_listnames_from_listIDs(query, self.componentID_name_dict)
                    if len(queryname_list) != 0:
                        queryNamesPathsFound_list.append(queryname_list)
                    if query not in queryIDsPathsFound_list:
                        queryIDsPathsFound_list.append(query)
                print("Summary: \nlen(queryPathsFoundFeComb_list): ", len(queryPathsFoundFeComb_list), " queryPathsFoundFeComb_list: ", queryPathsFoundFeComb_list, " queryNamesPathsFound_list: ", queryNamesPathsFound_list, "\npathIDs_list: ", pathIDs_list, "\npathNames_list: ", pathNames_list, "\nFI: ", get_listnames_from_listIDs(list(element), self.featurePkgID_name_dict), "\n")
        return FI_list, all_queries_list, queryIDsPathsFound_list, feComb_pathsfound_list

def main():
    FInameslist_of_list = []
    feCombNames_pathsfound_list = []
    
    print("No of security features: ", len(secFeaturePkgID_list), "no of safety features: ", len(safFeature_pkg_list))
    
    print("\n\nGenerating component interaction graph from the sequence diagrams of safety and security features")
    CInG = CreateInteractionGraph(featurePkgID_list, featureID_nodeIDset_dict, featureID_nodeIDnamedict_dict, featureID_edgeIDlist_dict, featureID_edgeIDnamedict_dict)
    G_CI = CInG.create_multidi_graph() #graph of component interactions
    
    print("\nFor each feature combination, checking for direct message exchange between the components realizing the features ...\n")
    EFeD = ExtractFeatureDependencies(secFeaturePkgID_list, safFeature_pkg_list, G_CI, secFeID_compID_dict, safFeID_compID_dict, featurePkgID_name_dict, componentID_name_dict, messageID_name_dict)
    FIids_list, QueryIDs_list, queryPathsFound_list, feCombIDs_pathsfound_list = EFeD.extractFeatureDependencies()
    #print("\n\nFeature dependency list: ", FIids_list)
    
    for element in FIids_list:
        FIname_list = get_listnames_from_listIDs(element, featurePkgID_name_dict)
        FInameslist_of_list.append(FIname_list)
    
    for element in feCombIDs_pathsfound_list:
        FIname_list = get_listnames_from_listIDs(element, featurePkgID_name_dict)
        feCombNames_pathsfound_list.append(FIname_list)
    
    print("\n\nallQueries_len: ", len(QueryIDs_list), " allQueries_list: ", QueryIDs_list, "\nqueryPathsFound_len: ", len(queryPathsFound_list), " queryPathsFound_list: ", queryPathsFound_list)
    print("\nlen(feCombIDs_pathsfound_list): ", len(feCombIDs_pathsfound_list), " feCombNames_pathsfound_list: ", feCombNames_pathsfound_list) #print the number of feature combinations for which a message based path for found.
    print("\n\nlen(TotalFI_list): ", len(FIids_list), " FIids_list: ", FIids_list, "\nlen(FInameslist_of_list): ", len(FInameslist_of_list), "\nFInameslist_of_list", FInameslist_of_list)
    print("\n\nVogelsang case1 output: \n", tabulate(FInameslist_of_list, headers = ["Interacting_source_feature", "Interacting_destination_feature"], tablefmt = 'grid'))
    
    sectosafFInames_list = []
    saftosecFInames_list = []
    for FI in FIids_list:
        FIname_list = get_listnames_from_listIDs(FI, featurePkgID_name_dict)
        if FI[0] in secFeaturePkgID_list:
            if FIname_list not in sectosafFInames_list:
                sectosafFInames_list.append(FIname_list)
        elif FI[0] in safFeature_pkg_list:
            if FIname_list not in saftosecFInames_list:
                saftosecFInames_list.append(FIname_list)
    print("\nlen(FI_SaftoSec): ", len(saftosecFInames_list), " FI_SaftoSec: \n", tabulate(saftosecFInames_list, headers = ["Interacting_source_feature", "Interacting_destination_feature"], tablefmt = 'grid'))
    print("\nlen(FI_SectoSaf): ", len(sectosafFInames_list), " FI_SectoSaf: \n", tabulate(sectosafFInames_list, headers = ["Interacting_source_feature", "Interacting_destination_feature"], tablefmt = 'grid'))
    
    ######################################Compare Vogelsang output with FIISS output##################################################################
    vogelsang_uniqueFI = []
    vogelsang_sameFI = []
    FIISS_uniqueFI = []
    for element in FInameslist_of_list:
        if element not in FIISS_FIs_names:
            vogelsang_uniqueFI.append(element)
        else:
            vogelsang_sameFI.append(element)
    for element in FIISS_FIs_names:
        if element not in FInameslist_of_list:
            FIISS_uniqueFI.append(element)
    print("\n\nComparing Vogelsang output with FIISS output...")
    print("len(FIISS_output): ", len(FIISS_FIs_names), " len(vogelsang_case1_output): ", len(FInameslist_of_list))
    print("Unique FIs found by Vogelsang wrt FIISS: ", len(vogelsang_uniqueFI), "\n", tabulate(vogelsang_uniqueFI, headers = ["Interacting_source_feature", "Interacting_destination_feature"], tablefmt = 'grid'))
    print("Unique FIs found by FIISS wrt Vogelsang: ", len(FIISS_uniqueFI), "\n", tabulate(FIISS_uniqueFI, headers = ["Interacting_source_feature", "Interacting_destination_feature"], tablefmt = 'grid'))
    print("Same FIs found by Vogelsang wrt FIISS: ", len(vogelsang_sameFI), "\n", tabulate(vogelsang_sameFI, headers = ["Interacting_source_feature", "Interacting_destination_feature"], tablefmt = 'grid'))
    
    ##################################Compare Vogelsang output with X-I-FASST output###############################################################
    vogelsang_uniqueFI = []
    vogelsang_sameFI = []
    X_IFASST_uniqueFI = []
    for element in FInameslist_of_list:
        if element not in X_IFASST_FIs_names:
            vogelsang_uniqueFI.append(element)
        else:
            vogelsang_sameFI.append(element)
    for element in X_IFASST_FIs_names:
        if element not in FInameslist_of_list:
            X_IFASST_uniqueFI.append(element)
    print("\n\nComparing Vogelsang output with X-I-FASST output...")
    print("len(IFASST_output): ", len(X_IFASST_FIs_names), " len(vogelsang_case1_output): ", len(FInameslist_of_list))
    print("Unique FIs found by Vogelsang wrt X-I-FASST:", len(vogelsang_uniqueFI), "\n", tabulate(vogelsang_uniqueFI, headers = ["Interacting_source_feature", "Interacting_destination_feature"], tablefmt = 'grid'))
    print("Unique FIs found by X-I-FASST wrt Vogelsang:", len(X_IFASST_uniqueFI), "\n", tabulate(X_IFASST_uniqueFI, headers = ["Interacting_source_feature", "Interacting_destination_feature"], tablefmt = 'grid'))
    print("Same FIs found by Vogelsang wrt X-I-FASST:", len(vogelsang_sameFI), "\n", tabulate(vogelsang_sameFI, headers = ["Interacting_source_feature", "Interacting_destination_feature"], tablefmt = 'grid'))

if __name__ == "__main__":
    main()