# Copyright (c) 2024 Robert Bosch GmbH
# SPDX-License-Identifier: MIT

import timeit
start = timeit.default_timer()
import io
import os
import time
import json
import textwrap
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import itertools
from itertools import product
from tabulate import tabulate

import sys
dirname = os.path.dirname(__file__)
sys.path.append(os.path.join(dirname, '..', 'lib'))
from XIFASST_lib import *

######################################Configurable inputs#####################################
#Configurable inputs for security features
secFeaturePkgID_list = []  #Specify XMI IDs of each security feature

#Configurable inputs for safety features
ecu_sa_main_pkg_path = ".//packagedElement[@xmi:id='{}'][@xmi:type='uml:Package']/packagedElement[@xmi:type='uml:Package']".format('') #Specify XMI ID of the main package inside quotes of .format(''); this main package contains other packages, of which each package represents a specific safety feature

#Configure security relevant components for each security feature
secFeID_compID_dict = {} #Specify a dict in which each key is the XMI ID of a security feature and the value corresponding to the key is the list of XMI IDs of security relevant components for the security feature e.g. {'EAPK_8451D5F3_2430_4c17_BBA3_FCDD12AFD7DD': ['EAID_CE767137_4FA5_4ed2_9CD5_C504E3D349F2', 'EAID_7FBBC274_4A52_4b4d_AD3C_C4881393D12F']}

#Configure safety relevant components for each safety feature
safFeID_compID_dict = {} #Specify a dict in which each key is the XMI ID of a safety feature and the value corresponding to the key is the list of XMI IDs of security relevant components for the security feature

#For each security relevant component ID, configure its name. Note that alternatively, the names can be automatically extracted from the architecture model
secComponentID_name_dict = {} #Specify a dict in which each key is the XMI ID of a security relevant component and the value corresponding to the key is the name of the security relevant component e.g. {'EAID_CE767137_4FA5_4ed2_9CD5_C504E3D349F2':'MasterSecModule'}

#For each safety relevant component ID, configure its name. Note that alternatively, the names can be automatically extracted from the architecture model
safComponentID_name_dict = {} #Specify a dict in which each key is the XMI ID of a safety relevant component and the value corresponding to the key is the name of the safety relevant component
##############################################################################################
nextiterationcheck = object()

class GetSecurityFeatures():
    "Get a list of all security features"
    def __init__(self, security_feature_list):
        self.security_feature_list = security_feature_list
    
    def get_security_feature_name(self, iterator_type):
        "For each element in the list, find its name and store it in a dict with the key as the feature id and the name as value"
        feature_id_name_dict = {}
        for element in self.security_feature_list:
            path = ".//packagedElement[@xmi:id = '{}'][@xmi:type = 'uml:Package']".format(element)
            path_iterator = get_iterator(path, iterator_type) #search will be performed in the specified input xmi file
            for object in path_iterator:
                id, name, type = get_iterator_attributes(object)
                feature_id_name_dict.update({element:name})
        return feature_id_name_dict

class GetSafetyFeatures():
    "Get a list of all safety features"
    def __init__(self, path):
        self.path = path
    
    def get_safety_feature(self, iterator_type):
        "get all safety features from the main/master safety package"
        feature_id_name_dict = {}
        safety_feature_list = []
        sa_feature_path_iterator = get_iterator(self.path, iterator_type) #search will be performed in the specified input xmi file
        for element in sa_feature_path_iterator:
            id, name, type = get_iterator_attributes(element)
            safety_feature_list.append(id)
            feature_id_name_dict.update({id:name})
        return safety_feature_list, feature_id_name_dict

class GetBehavioralElements():
    "Extract messages and lifelines from sequence diagrams; group (create lists) lifelines that are safety-relevant, security relevant, both safety and security relevant, and neither safety nor security relevant"
    def __init__(self, featurePkgID_list, featurePkgID_name_dict, relComponentID_set, feID_relCompID_dict):
        self.featurePkgID_list = featurePkgID_list
        self.featurePkgID_name_dict = featurePkgID_name_dict
        self.relComponentID_set = relComponentID_set
        self.feID_relCompID_dict = feID_relCompID_dict
    
    def extract_references_inSD(self, lifelineID, referenceID, iterator_type):
        "Extract if the reference to an interaction fragment in a sequence diagram of a feature refers to an interaction fragment in another feature or same feature"
        ownerfeaturepackage = None
        diagramID = None
        dependentfeature_id = None
        dependentfeature_name = None
        dependentfeature_type = None
        referenceSD_dependentFeID_dict = {}
        searchdiagram_path = ".//element[@xmi:idref = '{}'][@xmi:type = 'uml:InteractionOccurrence']/extendedProperties".format(referenceID)
        searchdiagram_iterator = get_iterator(searchdiagram_path, iterator_type) #search will be performed in the specified input xmi file
        for ele1 in searchdiagram_iterator:
            diagramID = ele1.get('diagram')
        if diagramID is not None:
            featureofdiagram_path = ".//diagram[@xmi:id = '{}']/model".format(diagramID)
            featureofdiagram_iterator = get_iterator(featureofdiagram_path, iterator_type) #search will be performed in the specified input xmi file
            for ele2 in featureofdiagram_iterator:
                ownerfeaturepackage = ele2.get('package')
            if ownerfeaturepackage in self.featurePkgID_list:
                pass
            else:
                parentfeaturesearch_path = ".//packagedElement[@xmi:id='{}'][@xmi:type = 'uml:Package']/..".format(ownerfeaturepackage)
                parentfeaturesearch_iterator = get_iterator(parentfeaturesearch_path, iterator_type) #search will be performed in the specified input xmi file
                for ele3 in parentfeaturesearch_iterator:
                    dependentfeature_id, dependentfeature_name, dependentfeature_type = get_iterator_attributes(ele3)
                if dependentfeature_id in self.featurePkgID_list:
                    referenceSD_dependentFeID_dict.update({lifelineID:dependentfeature_id})
                else:
                    grandparentfeaturesearch_path = ".//packagedElement[@xmi:id='{}'][@xmi:type = 'uml:Package']/..".format(dependentfeature_id)
                    grandparentfeaturesearch_iterator = get_iterator(grandparentfeaturesearch_path, iterator_type) #search will be performed in the specified input xmi file
                    for ele4 in grandparentfeaturesearch_iterator:
                        dependentfeature_id, dependentfeature_name, dependentfeature_type = get_iterator_attributes(ele4)
                        if dependentfeature_id in self.featurePkgID_list:
                            referenceSD_dependentFeID_dict.update({lifelineID:dependentfeature_id})
                        else:
                            print("Warning! Parent feature of reference_interaction_fragment: ", referenceID, " not found!")
        return referenceSD_dependentFeID_dict
    
    def extract_classifier_of_lifelines(self, feature, lifeline_set, iterator_type):
        "For a given list of lifelines that may have associated classifiers (i.e. lifelines starting with EAID_LL000000), identify their classifiers"
        name = None
        type = None
        instSpec_ID = None #instance specification ID
        ISclassifier_ID = None #classifier (ID) of the instance specification
        classifier_id = None
        classifierID_set = set()
        classifierID_name_dict = {}
        mappedLLID_classifierID_dict = {}
        refSD_dependentFeID_dict = {}
        
        instSpecID_set = set()
        mappedLLID_ISID_dict = {}
        mappedISID_classifierID_dict = {}
        
        for element in lifeline_set:
            id = None
            represents = None
            if element.startswith('EAID_LL000000'):
                LLsearch_path = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//lifeline[@xmi:id = '{}']".format(feature, element)
                LLsearch_iterator = get_iterator(LLsearch_path, iterator_type) #search will be performed in the specified input xmi file
                for ele1 in LLsearch_iterator:
                    represents = ele1.get('represents')
                ISsearch_path = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//*[@xmi:id='{}']/type".format(feature, represents)
                ISsearch_iterator = get_iterator(ISsearch_path, iterator_type) #search will be performed in the specified input xmi file
                for ele2 in ISsearch_iterator:
                    instSpec_ID = ele2.get('{http://schema.omg.org/spec/XMI/2.1}idref')
                #if instSpec_ID is not None
                ISdetailssearch_path = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//*[@xmi:id='{}']".format(feature, instSpec_ID)
                ISdetailssearch_iterator = get_iterator(ISdetailssearch_path, iterator_type) #search will be performed in the specified input xmi file
                for ele2 in ISdetailssearch_iterator:
                    instSpec_ID, instSpec_name, instSpec_type = get_iterator_attributes(ele2)
                    #print("Debug! Classifier detials of owned_lifeline_id: ", element, " classifier_id: ", instSpec_ID, " classifier_name: ", instSpec_name, " classifier_type: ", instSpec_type)
                    if instSpec_type == 'uml:InstanceSpecification':
                        ISclassifier_ID = ele2.get('classifier')
                        #The following data structs are used to create a lifeline list in appropriate format and use it to find used messages. Note: X-I-FASST differentiates between owned messages and used messages
                        instSpecID_set.add(instSpec_ID)
                        mappedLLID_ISID_dict.update({element:instSpec_ID})
                        mappedISID_classifierID_dict.update({instSpec_ID:ISclassifier_ID})
                        if ISclassifier_ID is not None:
                            id, name, type, classifier_id = search_allocatedUMLelement_byID(ISclassifier_ID)
                            #print("Debug! Classifier details of instance_specID: ", instSpec_ID, " LLclassifier_ID: ", id, " LLclassifier_name: ", name, " LLclassifier_type: ", type, " LLclassifier_classifier: ", classifier_id)
                            if id is not None:
                                classifierID_set.add(id)
                                classifierID_name_dict.update({id:name})
                                mappedLLID_classifierID_dict.update({element:id})
                            else:
                                classifierID_set.add(ISclassifier_ID)
                                classifierID_name_dict.update({ISclassifier_ID:name})
                                mappedLLID_classifierID_dict.update({element:ISclassifier_ID})
                    elif instSpec_type == 'uml:Actor' or instSpec_type == 'uml:Component':
                        classifierID_set.add(instSpec_ID)
                        classifierID_name_dict.update({instSpec_ID:instSpec_name})
                        mappedLLID_classifierID_dict.update({element:instSpec_ID})
                        #The following data structs are used to create a lifeline list in appropriate format and use it to find used messages.
                        instSpecID_set.add(instSpec_ID)
                        mappedLLID_ISID_dict.update({element:instSpec_ID})
                        mappedISID_classifierID_dict.update({instSpec_ID:instSpec_ID})
                    else:
                        print("Warning! classifier of instSpec_ID: ",instSpec_ID, " not found!")
            else:
                #Checking for interface of a component; A message sent to an interface will be depicted in the interaction graph as the message to the component which has this interface.
                id, name, type, classifier_id = get_interfacebyID(feature, element)
                if id is not None:
                    if type == "uml:Interface":
                        classifierID_set.add(id)
                        classifierID_name_dict.update({id:name})
                        mappedLLID_classifierID_dict.update({element:id})
                        #The following data structs are used to create a lifeline list in appropriate format and use it to find used messages.
                        instSpecID_set.add(element)
                        mappedLLID_ISID_dict.update({element:element})
                        mappedISID_classifierID_dict.update({element:id})
                else:
                    #Checking if the classifier of element is a component, class, object, actor etc.
                    id, name, type, ISclassifier_id = search_allocatedUMLelement_byID(element)
                    #print("Debug! Classifier detils of covered_lifeline_id: ", element, " LLWoClassifier_ID: ", id, " LLWoclassifier_name: ", name, " LLWoclassifier_type: ", type, " LLWoclassifier_classifier: ", ISclassifier_id)
                    if id is not None:
                        if type == 'uml:InstanceSpecification':
                            id, name, type, classifier_id = search_allocatedUMLelement_byID(ISclassifier_id)
                            #print("Debug! LLWoClassifier_ID: ", id, " LLclassifier_name: ", name, " LLclassifier_type: ", type, " LLclassifier_classifier: ", classifier_id)
                            #The following data structs are used to create the lifeline list in appropriate format to find used messages
                            instSpecID_set.add(element)
                            mappedLLID_ISID_dict.update({element:element})
                            mappedISID_classifierID_dict.update({element:classifier_id})
                            if id is not None:
                                classifierID_set.add(id)
                                classifierID_name_dict.update({id:name})
                                mappedLLID_classifierID_dict.update({element:id})
                            else:
                                classifierID_set.add(ISclassifier_id)
                                classifierID_name_dict.update({ISclassifier_id:name})
                                mappedLLID_classifierID_dict.update({element:ISclassifier_id})
                        elif type == "uml:InteractionOccurrence": #Reference to a fragment found
                            print("Reference to internal_interaction_fragment_id: ", id, " name: ", name, " found!")
                            referenceSD_dependentFeID_dict = self.extract_references_inSD(element, id, iterator_type) #search will be performed in the specified input xmi file
                            refSD_dependentFeID_dict.update(referenceSD_dependentFeID_dict)
                        elif type == 'uml:Component' or type == 'uml:Class' or type == 'uml:Actor' or type == 'uml:Object' or type == 'uml:ProvidedInterface':
                            #print("Debug! LLWoClassifier_ID: ", id, " LLclassifier_name: ", name, " LLclassifier_type: ", type, " LLclassifier_classifier: ", classifier_id)
                            classifierID_set.add(id)
                            classifierID_name_dict.update({id:name})
                            mappedLLID_classifierID_dict.update({element:id}) 
                            #The following data structs are used to create the lifeline list in appropriate format to find used messages
                            instSpecID_set.add(element)
                            mappedLLID_ISID_dict.update({element:element})
                            mappedISID_classifierID_dict.update({element:element})
                        else:
                            print("Warning! element_id: ", element, " will not be stored! Classifier ID not None")
                    else:
                        print("Warning! element_id: ", element, " will not be stored! Classifier ID None")   
        return classifierID_set, classifierID_name_dict, mappedLLID_classifierID_dict, refSD_dependentFeID_dict, instSpecID_set, mappedLLID_ISID_dict, mappedISID_classifierID_dict
        
    def extract_lifelines(self, feature, iterator_type):
        "For a given feature, extract its lifelines from fragment element(OccurSpec, CombinedFragment etc.)"
        lifeline_set = set()
        ownedlifelineID_set = set()
        ownedlifelineID_name_dict = {}
        mappedownedLLIDclassifierID_dict = {}
        SeqOccurSpecID_set = set()
        OccurSpecID_lifelineID_dict = {}
        gate_id = None
        gate_name = None
        gate_type = None
        
        lifeline_id = None
        lifeline_name = None
        lifeline_type = None
        
        instSpecID_set = set()
        
        lifeline_path = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//lifeline".format(feature) #to extract lifeline ID
        formalGate_path = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//*[@xmi:type='uml:Gate']".format(feature) #to extract gate ID
        combinedFragmentCoveredLL_path = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//fragment[@xmi:type='uml:CombinedFragment']/covered".format(feature) #to extract xmi:idref, thereby collecting lifelines covered by the interaction fragment (alt, opt, loop, ...)
        occurSpecCoveredLL_path = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//fragment[@xmi:type='uml:OccurrenceSpecification']".format(feature) #to extract the attribute 'covered'
        
        lifeline_iterator = get_iterator(lifeline_path, iterator_type) #search will be performed in the specified input xmi file
        formalgate_iterator = get_iterator(formalGate_path, iterator_type) #search will be performed in the specified input xmi file
        combinedFragmentCoveredLL_iterator = get_iterator(combinedFragmentCoveredLL_path, iterator_type) #search will be performed in the specified input xmi file
        occurSpecCoveredLL_iterator = get_iterator(occurSpecCoveredLL_path, iterator_type) #search will be performed in the specified input xmi file
        
        for element in lifeline_iterator:
            lifeline_id, lifeline_name, lifeline_type = get_iterator_attributes(element) #extract lifeline ID
            if lifeline_id.startswith('EAID_LL'):
                lifeline_set.add(lifeline_id)
            else:
                ownedlifelineID_set.add(lifeline_id)
                ownedlifelineID_name_dict.update({lifeline_id: lifeline_name})
                mappedownedLLIDclassifierID_dict.update({lifeline_id:lifeline_id})
        
        for element in formalgate_iterator:
            gate_id, gate_name, gate_type = get_iterator_attributes(element) #extract ID of formal gate
            #print("\nDebug! gate_id: ", gate_id, " gate_name: ", gate_name, " gate_type: ", gate_type)
            if gate_id is not None:
                ownedlifelineID_set.add(gate_id)
                #print("\nDebug! Added gate_id: ", gate_id, " gate_name: ", gate_name, " gate_type: ", gate_type)
                ownedlifelineID_name_dict.update({gate_id: gate_name})
                mappedownedLLIDclassifierID_dict.update({gate_id:gate_id})
        
        for element in combinedFragmentCoveredLL_iterator:
            lifeline_id = element.get('{http://schema.omg.org/spec/XMI/2.1}idref') #extract lifeline ID covered by combined interaction fragment
            if lifeline_id not in ownedlifelineID_set:
                lifeline_set.add(lifeline_id)
        
        for element in occurSpecCoveredLL_iterator:
            OccurSpecID = element.get('{http://schema.omg.org/spec/XMI/2.1}id') #get occurence specification ID because it is used in sendEvent & receiveEvent IDs of <message xmi:type= 'uml:Message'>
            lifeline_id = element.get('covered') #extract lifeline ID indicated by occurrence specification
            SeqOccurSpecID_set.add(OccurSpecID) #create a set to add OccurSpec IDs; this list will be used to find src and dst of <message xmi:type= 'uml:Message'>
            if lifeline_id is not None:
                OccurSpecID_lifelineID_dict.update({OccurSpecID:lifeline_id}) #mapping of OccurSpec ID to its corresponding lifeline ID
                if lifeline_id not in ownedlifelineID_set:
                    lifeline_set.add(lifeline_id)
        SeqOccurSpecID_set.update(ownedlifelineID_set)
        OccurSpecID_lifelineID_dict.update(mappedownedLLIDclassifierID_dict)
        #print("\nDebug! Feature: ", self.featurePkgID_name_dict[feature], " lifeline_set: ", lifeline_set)
        classifierID_set, classifierID_name_dict, mappedLLID_classifierID_dict, refSD_dependentFeID_dict, instSpecID_set, mappedLLID_ISID_dict, mappedISID_classifierID_dict = self.extract_classifier_of_lifelines(feature, lifeline_set, iterator_type) #search will be performed in the specified input xmi file
        
        classifierID_set.update(ownedlifelineID_set)
        classifierID_name_dict.update(ownedlifelineID_name_dict)
        mappedLLID_classifierID_dict.update(mappedownedLLIDclassifierID_dict)
        instSpecID_set.update(ownedlifelineID_set)
        
        return lifeline_set, classifierID_set, classifierID_name_dict, mappedLLID_classifierID_dict, SeqOccurSpecID_set, OccurSpecID_lifelineID_dict, refSD_dependentFeID_dict, instSpecID_set, mappedISID_classifierID_dict
    
    def validate_msgtuples(self, edgelisttobevalidated, msgID_list, msgID_name_dict):
        "Validate message tuple i.e. (msgSrcID, msgDstID, msgID) with respect to message list to check if all messages are covered/included in the tuple list"
        msguncoveredintuple_list = []
        msguncoveredintupleName_list = []
        msgfromtuple_list = [ele[-1] for ele in edgelisttobevalidated]
        msguncoveredintupleID_list, msguncoveredintupleName_list = query_lists_for_uniqueelement(msgfromtuple_list, msgID_list, msgID_name_dict)
        return msguncoveredintupleID_list, msguncoveredintupleName_list
    
    def extract_owned_messages(self, feature, LLOccurSpecID_set, mappedLLOccurSpecID_LLID_dict, mappedLLID_classifierID_dict, classifierID_name_dict, refSD_dependentFeID_dict, iterator_type):
        "Extract messages contained in each feature package of type = uml:Message"
        msg_id = None
        msg_name = None
        msg_type = None
        msg_srcClassifierID = None
        msg_dstClassifierID = None
        msg_srcClassifierName = None
        msg_dstClassifierName = None
        
        ownedMsgID_list = []
        ownedMsgID_name_dict = {}
        edge_tuple = ()
        node_set = set()
        nodeID_name_labeldict = {}
        edge_list = []
        edge_label_dict = {}
        
        srcFeID = None
        dstFeID = None
        feID_dependentFeID_dict = {}
        msgID_msgSort_dict = {}
        
        msgID_path_search = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//message[@xmi:type = 'uml:Message']".format(feature)
        msgID_iterator = get_iterator(msgID_path_search, iterator_type) #search will be performed in the specified input xmi file
        #print("\nDebug! Feature: ", self.featurePkgID_name_dict[feature], " OccurSpec_list: ", LLOccurSpecID_set)
        for object in msgID_iterator:
            msg_id, msg_name, msg_type = get_iterator_attributes(object)
            msg_sort = object.get('messageSort')
            msg_signature = object.get('signature')
            #print("Debug! msgID: ", msg_id, " msgname_list: ", msg_name, " msg_sort: ", msg_sort, " msg_sign: ", msg_signature)
            
            msgID_msgSort_dict.update({msg_id: msg_sort})
            
            ownedMsgID_list.append(msg_id)
            ownedMsgID_name_dict.update({msg_id:msg_name})
            
            msg_src = object.get('sendEvent')
            msg_dst = object.get('receiveEvent')
            
            if (msg_src in LLOccurSpecID_set) and (msg_dst in LLOccurSpecID_set):
                msg_srcClassifierID = query_twodicts_by_key(msg_src, mappedLLOccurSpecID_LLID_dict, mappedLLID_classifierID_dict)
                msg_dstClassifierID = query_twodicts_by_key(msg_dst, mappedLLOccurSpecID_LLID_dict, mappedLLID_classifierID_dict)
                
                #print("\nDebug! Feature: ", self.featurePkgID_name_dict[feature], "msg_id: ", msg_id, " msg_name: ", msg_name, " msg_srcClassifierID: ", msg_srcClassifierID, " msg_dstClassifierID: ", msg_dstClassifierID)
 
                if msg_srcClassifierID is not None and msg_dstClassifierID is not None:
                    msg_srcClassifierName = classifierID_name_dict[msg_srcClassifierID]
                    msg_dstClassifierName = classifierID_name_dict[msg_dstClassifierID]
                    edge_tuple = (msg_srcClassifierID, msg_dstClassifierID, msg_id)
                    
                    node_set.add(msg_srcClassifierID)
                    node_set.add(msg_dstClassifierID)
                    nodeID_name_labeldict.update({msg_srcClassifierID: msg_srcClassifierName, msg_dstClassifierID: msg_dstClassifierName})
                
                    edge_list.append(edge_tuple)
                    edge_label_dict.update({edge_tuple:msg_name})
                elif msg_srcClassifierID is None and msg_dstClassifierID is not None:
                    srcFeID = query_twodicts_by_key(msg_src, mappedLLOccurSpecID_LLID_dict, refSD_dependentFeID_dict)
                    if srcFeID is not None:
                        feID_dependentFeID_dict.update({srcFeID:feature})
                    else:
                        print("Warning! msg_srcID: ", msg_src, " not found!")
                elif msg_srcClassifierID is not None and msg_dstClassifierID is None:
                    dstFeID = query_twodicts_by_key(msg_dst, mappedLLOccurSpecID_LLID_dict, refSD_dependentFeID_dict)
                    if dstFeID is not None:
                        feID_dependentFeID_dict.update({feature: dstFeID})
                    else:
                        print("Warning! msg_dstID: ", msg_dst, " not found!")
                elif msg_srcClassifierID is None and msg_dstClassifierID is None:
                    srcFeID = query_twodicts_by_key(msg_src, mappedLLOccurSpecID_LLID_dict, refSD_dependentFeID_dict)
                    dstFeID = query_twodicts_by_key(msg_dst, mappedLLOccurSpecID_LLID_dict, refSD_dependentFeID_dict)
                    if srcFeID is not None and dstFeID is not None:
                        feID_dependentFeID_dict.update({srcFeID: dstFeID})
                    else:
                        print("Warning! msg_srcID: ", msg_src, " or msg_dstID: ", msg_dst, " not found!")
        return ownedMsgID_list, ownedMsgID_name_dict, node_set, nodeID_name_labeldict, edge_list, edge_tuple, edge_label_dict, feID_dependentFeID_dict, msgID_msgSort_dict
    
    def get_used_message_name(self, messageID, searchfilename):
        "For a given message ID, extract its name by tracing the connector for the message"
        messagename_path_search = ".//connector[@xmi:idref = '{}']".format(messageID)
        messagename_iterator = get_iterator(messagename_path_search, searchfilename)
        for ele in messagename_iterator:
            message_name = ele.get('name')
        return message_name
    
    def get_usedmessage_tuples(self, msgSrc, msgDst, msgID, filesearchpath, LLClassifierID_name_dict, mappedISID_classifierID_dict):
        "For a given msgID, msgName, msgSrc, and msgDst, create a tuple"
        node_set = set()
        nodeID_name_labeldict = {}
        edge_label_dict = {}
        edge_tuple = ()
        seq_name = None
        
        msg_srcID = mappedISID_classifierID_dict[msgSrc]
        msg_dstID = mappedISID_classifierID_dict[msgDst]
        
        if msg_srcID is not None and msg_dstID is not None:
            seq_name = self.get_used_message_name(msgID, filesearchpath)
            msg_srcName = LLClassifierID_name_dict[msg_srcID]
            msg_dstName = LLClassifierID_name_dict[msg_dstID]
            edge_tuple = (msg_srcID, msg_dstID, msgID)
            node_set.add(msg_srcID)
            node_set.add(msg_dstID)
            nodeID_name_labeldict.update({msg_srcID: msg_srcName, msg_dstID: msg_dstName})
            edge_label_dict.update({edge_tuple:seq_name})
        else:
            if msg_srcID is None:
                print("Warning! Msg: ", msgID, " Msg_srcID: ", msgSrc, "'s classifier not found in mappedISID_classifierID_dict input!")
            elif msg_dstID is None:
                print("Warning! Msg: ", msgID, " Msg_dstID: ", msgDst, "'s classifier not found in mappedISID_classifierID_dict input!")
        return seq_name, edge_tuple, node_set, nodeID_name_labeldict, edge_label_dict
    
    def extractSeq_from_iterator(self, seqID_set, edges_list, msgDir, iterator, inputSrcOrDstSeqID, SrcOrDst_string, LLsInCombinedFragment_set, ownedMsgID_list, mappedISID_classifierID_dict, classifierID_name_dict, filesearchpath):
        "For a given sequence search iterator (search sequence with srcID or dstID as input), extract sequence ID of the message"
        seqSrcOrDstID = None
        seqID_set = set()
        seqID_name_dict = {}
        
        seqID_name_dict = {}
        edges_list = []
        edge_labels_dict = {}
        edges_tuple = ()
        nodes_set = set()
        nodesID_name_labeldict = {}
        
        for element in iterator:
            seqID = None
            seqSrcOrDstID = element.get(SrcOrDst_string) #extract source or destination of the message based on input
            if seqSrcOrDstID in LLsInCombinedFragment_set:
                seqID = element.get('{http://schema.omg.org/spec/XMI/2.1}id')
                if seqID not in ownedMsgID_list:
                    if seqID not in seqID_set:
                        seqID_set.add(seqID)
                        if msgDir == 'start':
                            seq_name, edge_tuple, node_set, nodeID_name_labeldict, edge_label_dict = self.get_usedmessage_tuples(inputSrcOrDstSeqID, seqSrcOrDstID, seqID, filesearchpath, classifierID_name_dict, mappedISID_classifierID_dict)
                            if len(edge_tuple) != 0 and edge_tuple not in edges_list:
                                seqID_name_dict.update({seqID:seq_name})
                                edges_list.append(edge_tuple)
                                edge_labels_dict.update(edge_label_dict)
                                nodes_set.update(node_set)
                                nodesID_name_labeldict.update(nodeID_name_labeldict)
                        elif msgDir == 'end':
                            seq_name, edge_tuple, node_set, nodeID_name_labeldict, edge_label_dict = self.get_usedmessage_tuples(seqSrcOrDstID, inputSrcOrDstSeqID, seqID, filesearchpath, classifierID_name_dict, mappedISID_classifierID_dict)
                            if len(edge_tuple) != 0 and edge_tuple not in edges_list:
                                seqID_name_dict.update({seqID:seq_name})
                                edges_list.append(edge_tuple)
                                edge_labels_dict.update(edge_label_dict)
                                nodes_set.update(node_set)
                                nodesID_name_labeldict.update(nodeID_name_labeldict)
                        else:
                            print("Warning! Invalid msgDir: ", msgDir)
                    else:
                        continue
        return seqID_set, nodes_set, nodesID_name_labeldict, edges_list, edge_labels_dict, seqID_name_dict

    def extract_used_messages(self, ownedMsgID_list, lifeline_set, mappedISID_classifierID_dict, classifierID_name_dict, filesearchpath):
        "Search for messages sent to or received by lifelines (lifeline_set as input) that are not owned but only used by the feature being analyzed"
        sequenceID_set = set()
        sequenceID_name_dict = {}
        node_set = set()
        nodeID_name_labeldict = {}
        edge_label_dict = {}
        edge_list = []
        for element in lifeline_set:
            seqID_set1 = set()
            seqID2_set2 = set()
            nodes_set1 = set()
            nodes_set2 = set()
            nodesID_name_labeldict1 = {}
            nodesID_name_labeldict2 = {}
            edges_list1 = []
            edges_list2 = []
            edge_labels_dict1 = {}
            edge_labels_dict2 = {}
            seqID_name_dict1 = {}
            seqID_name_dict2 = {}
            
            seq_sourcepath_search = ".//Sequence[@start = '{}']".format(element) #search for <Sequence> with the lifeline as source
            seq_targetpath_search = ".//Sequence[@end = '{}']".format(element) #search for <Sequence> with the lifeline as destination
            seqsourcepath_iterator = get_iterator(seq_sourcepath_search, filesearchpath)
            seqtargetpath_iterator = get_iterator(seq_targetpath_search, filesearchpath)
            
            seqID_set1, nodes_set1, nodesID_name_labeldict1, edges_list1, edge_labels_dict1, seqID_name_dict1 = self.extractSeq_from_iterator(sequenceID_set, edge_list, 'start', seqsourcepath_iterator, element, 'end', lifeline_set, ownedMsgID_list, mappedISID_classifierID_dict, classifierID_name_dict, filesearchpath)
            
            sequenceID_set.update(seqID_set1)
            for ele in edges_list1:
                if ele not in edge_list:
                    edge_list.append(ele)
            
            seqID2_set2, nodes_set2, nodesID_name_labeldict2, edges_list2, edge_labels_dict2, seqID_name_dict2 = self.extractSeq_from_iterator(sequenceID_set, edge_list, 'end', seqtargetpath_iterator, element, 'start', lifeline_set, ownedMsgID_list, mappedISID_classifierID_dict, classifierID_name_dict, filesearchpath)
            
            sequenceID_set.update(seqID2_set2)
            for ele in edges_list2:
                if ele not in edge_list:
                    edge_list.append(ele)
            
            nodes_set1.update(nodes_set2)
            nodesID_name_labeldict1.update(nodesID_name_labeldict2)
            edge_labels_dict1.update(edge_labels_dict2)
            seqID_name_dict1.update(seqID_name_dict2)
            
            node_set.update(nodes_set1)
            nodeID_name_labeldict.update(nodesID_name_labeldict1)
            edge_label_dict.update(edge_labels_dict1)
            sequenceID_name_dict.update(seqID_name_dict1)
        return sequenceID_set, sequenceID_name_dict, node_set, nodeID_name_labeldict, edge_list, edge_label_dict
    
    def extract_lifelines_and_messages(self):
        "For each feature being analyzed, extract messages. Extract the lifelines involved in the message exchange."
        feID_dependentFeID_dict = {}
        allSD_feID_dependentFeID_dict = {'feature':'interacting_feature'}
        
        feID_nodeIDset_dict = {} # {feature1: (LL1, LL2), feature2:(), ..} here LL1 and LL2 refer to the corresponding classifiers of the lifelines
        feID_nodeIDnamedict_dict = {} # {feature1: {LL1_id:LL1_name, LL2_id:LL2_name}, feature2:(), ..}
        feID_edgeIDlist_dict = {}
        feID_edgeIDnamedict_dict = {}
        feID_msgIDnamedict_dict = {}
        feID_relMsgIDslist_dict = {}
        feID_relMsgNameslist_dict = {}
        msgID_name_dict = {}
        feGroup_msgID_msgSort_dict = {}
        
        for feature in self.featurePkgID_list:
            feature_name = self.featurePkgID_name_dict[feature]
            msguncoveredintupleID_list = []
            msguncoveredintupleName_list = []
            uncoveredMsgintupleID_list = []
            uncoveredMsgintupleName_list = []
            
            lifeline_set = set()
            classifierID_set = set()
            classifierID_name_dict = {}
            mappedLLID_classifierID_dict = {}
            mappedOccurSpecID_lifelineID_dict = {}
            nodeID_set = set()
            nodeID_name_labeldict = {}
            edge_list = []
            edge_label_dict = {}
            
            #extracting lifelines of each feature
            lifeline_set, classifierID_set, classifierID_name_dict, mappedLLID_classifierID_dict, SeqOccurSpecID_set, mappedOccurSpecID_lifelineID_dict, refSD_dependentFeID_dict, instSpecID_set, mappedISID_classifierID_dict = self.extract_lifelines(feature, 2) #search will be performed in the specified input xmi file
            classifierNames_list = [value for value in classifierID_name_dict.values()]
            #print("\nDebug! Feature: ", feature_name, " len(lifelines): ", len(classifierID_set), " lifelines: ", classifierID_name_dict)
            
            #extracting owned messages of each feature
            ownedMsgID_list, ownedMsgID_name_dict, ownednode_set, ownednodeID_name_labeldict, ownededge_list, ownededge_tuple, ownededge_label_dict, feID_dependentFeID_dict, msgID_msgSort_dict = self.extract_owned_messages(feature, SeqOccurSpecID_set, mappedOccurSpecID_lifelineID_dict, mappedLLID_classifierID_dict, classifierID_name_dict, refSD_dependentFeID_dict, 2) #search will be performed in the specified input xmi file; for our case study, it is input xmi file 2
            
            #ownedMsgname_list = [value for value in ownedMsgID_name_dict.values()]
            allSD_feID_dependentFeID_dict.update(feID_dependentFeID_dict)
            feGroup_msgID_msgSort_dict.update(msgID_msgSort_dict)
            
            #validating tuples obtained from extracted owned messages
            msguncoveredintupleID_list, msguncoveredintupleName_list = self.validate_msgtuples(ownededge_list, ownedMsgID_list, ownedMsgID_name_dict)
            
            #print("\nDebug! Feature: ", feature_name, " owned_message_no: ", len(ownedMsgID_list), " ownedMsg: ", ownedMsgID_name_dict)
            #print("\nDebug! Feature: ", feature_name, " owned_tuple_no: ", len(ownededge_list), " ownedMsg: ", ownededge_label_dict)
            print("\nDebug! Feature: ", feature_name, " uncoveredMsgInTuples_no : ", len(msguncoveredintupleID_list), ", uncoveredMsgInTupleIDs: ", msguncoveredintupleID_list, " uncoveredMsgInTuples: ", msguncoveredintupleName_list)
            
            #extracting used messages of each feature
            usedMsgID_set, usedMsgID_name_dict, usednode_set, usednodeID_name_labeldict, usededge_list, usededge_label_dict = self.extract_used_messages(ownedMsgID_list, instSpecID_set, mappedISID_classifierID_dict, classifierID_name_dict, 3) #search will be performed in the specified input xmi file; for our case study, it is input xmi file 3
            
            #validating tuples obtained from extracted used messages
            uncoveredMsgintupleID_list, uncoveredMsgintupleName_list = self.validate_msgtuples(usededge_list, list(usedMsgID_set), usedMsgID_name_dict)
            
            #print("\nDebug! Feature: ", feature_name, " used_message_no: ", len(usedMsgID_set), " usedMsg: ", usedMsgID_name_dict)
            #print("\nDebug! Feature: ", feature_name, " used_tuple_no: ", len(usededge_list), " usedTuple_list: ", usededge_list, " usedTuple_dict: ", usededge_label_dict)
            print("\nDebug! Feature: ", feature_name, " uncoveredMsgInTuples_no : ", len(uncoveredMsgintupleID_list), ", uncoveredMsgInTupleIDs: ", uncoveredMsgintupleID_list, " uncoveredMsgInTuples: ", uncoveredMsgintupleName_list)
            
            msgID_name_dict.update(ownedMsgID_name_dict)
            msgID_name_dict.update(usedMsgID_name_dict)
            nodeID_set.update(ownednode_set)
            nodeID_set.update(usednode_set)
            nodeID_name_labeldict.update(ownednodeID_name_labeldict)
            nodeID_name_labeldict.update(usednodeID_name_labeldict)
            edge_list.extend(ownededge_list)
            for ele in usededge_list:
                if ele not in edge_list:
                    edge_list.append(ele)
            edge_label_dict.update(ownededge_label_dict)
            edge_label_dict.update(usededge_label_dict)
            
            #Distinguishing relevant messages for each feature i.e. mapping each feature to its relevant messages
            relCompID_list = self.feID_relCompID_dict[feature]
            relCompNames_list = get_listnames_from_listIDs_fromdictwithmissingkeys(relCompID_list, nodeID_name_labeldict)
            relMsgIDs_list = []
            relMsgNames_list = []
            for element in edge_list:
                eachtuples_srcID = element[-3]
                eachtuples_dstID = element[-2]
                if eachtuples_dstID in relCompID_list or eachtuples_srcID in relCompID_list:
                    relMsgID = element[-1]
                    if relMsgID not in relMsgIDs_list:
                        relMsgIDs_list.append(relMsgID)
            relMsgNames_list = get_listnames_from_listIDs(relMsgIDs_list, msgID_name_dict)
            print("\nFeature: ", feature_name, " relevant_lifelines: ", relCompNames_list, "relevant_msgs: ", relMsgNames_list)
            feID_relMsgIDslist_dict.update({feature: relMsgIDs_list}) #Map feature id to its relevant message ids
            feID_relMsgNameslist_dict.update({feature_name: relMsgNames_list}) #Map feature name to its relevant message names
            
            #Creating data structures to store node and edge details for each feature for the next step: interaction analysis.
            feID_nodeIDset_dict.update({feature:nodeID_set}) #each feature and its corresponding lifeline (i.e. classifier) ID set
            feID_nodeIDnamedict_dict.update({feature:nodeID_name_labeldict})
            feID_edgeIDlist_dict.update({feature:edge_list})
            feID_edgeIDnamedict_dict.update({feature:edge_label_dict})
            feID_msgIDnamedict_dict.update({feature:msgID_name_dict})
        print("\nDebug! Dependency list created by .sd analysis: ", allSD_feID_dependentFeID_dict)
        print(tabulate(allSD_feID_dependentFeID_dict, tablefmt = 'grid', maxcolwidths=[20,20]), "\n")
        return feID_nodeIDset_dict, feID_nodeIDnamedict_dict, feID_edgeIDlist_dict, feID_edgeIDnamedict_dict, msgID_name_dict, feGroup_msgID_msgSort_dict, feID_relMsgIDslist_dict, feID_msgIDnamedict_dict

class InteractionAnalysis():
    "Create a multi directed graph using classifiers of lifelines and messages in the sequence diagrams of all safety and security features. Then identify safety and security relevant lifelines and query the graph to find interaction paths between relevant lifelines."
    def __init__(self, featurePkgID_list, featurePkgID_name_dict, secComponentID_set, safComponentID_set, secsafComponentID_set, feID_nodeIDset_dict, feID_nodeIDnamedict_dict, feID_edgeIDlist_dict, feID_edgeIDnamedict_dict, secFeID_compID_dict, safFeID_compID_dict, msgID_name_dict, secComponentID_name_dict, safComponentID_name_dict, msgID_msgSort_dict, feID_relMsgIDslist_dict, feID_compID_dict, secFeaturePkgID_list, safFeature_pkg_list, relevantComponentID_set):
        self.featurePkgID_list = featurePkgID_list
        self.featurePkgID_name_dict = featurePkgID_name_dict
        self.secComponentID_set = secComponentID_set
        self.safComponentID_set = safComponentID_set
        self.secsafComponentID_set = secsafComponentID_set
        self.feID_nodeIDset_dict = feID_nodeIDset_dict
        self.feID_nodeIDnamedict_dict = feID_nodeIDnamedict_dict
        self.feID_edgeIDlist_dict = feID_edgeIDlist_dict
        self.feID_edgeIDnamedict_dict = feID_edgeIDnamedict_dict
        self.secFeID_compID_dict = secFeID_compID_dict
        self.safFeID_compID_dict = safFeID_compID_dict
        self.msgID_name_dict = msgID_name_dict
        self.secComponentID_name_dict = secComponentID_name_dict
        self.safComponentID_name_dict = safComponentID_name_dict
        self.msgID_msgSort_dict = msgID_msgSort_dict
        self.feID_relMsgIDslist_dict = feID_relMsgIDslist_dict
        self.feID_compID_dict = feID_compID_dict
        self.secFeaturePkgID_list = secFeaturePkgID_list
        self.safFeature_pkg_list = safFeature_pkg_list
        self.relevantComponentID_set = relevantComponentID_set
    
    def get_summed_itertoolsproductoflists(self, set1, set2):
        "For sets, i.e. set1 and set2, get the product of set1 and set2, and the product of set2 and set1 and combine (summation) the output of both products obtained"
        bidirectionalproduct_list = []
        productfrom1to2_list = list(itertools.product(list(set1), list(set2)))
        productfrom2to1_list = list(itertools.product(list(set2), list(set1)))
        bidirectionalproduct_list = [*productfrom1to2_list, *productfrom2to1_list]
        return bidirectionalproduct_list
    
    def get_relevant_lifelines(self, featurenodeIDs_set):
        "Identify which lifelines are safety relevant, security relevant and both safety and security relevant"
        relevantnodeID_list = []
            
        secsafnodeID_set = get_commonelementIDsset(featurenodeIDs_set, self.secsafComponentID_set)
        secnodeID_set = get_commonelementIDsset(featurenodeIDs_set, self.secComponentID_set)
        safnodeID_set = get_commonelementIDsset(featurenodeIDs_set, self.safComponentID_set)
        
        secsafnodeID_list = list(secsafnodeID_set)
        secnodeID_list = list(secnodeID_set)
        safnodeID_list = list(safnodeID_set)
        relevantnodeID_list = list(set(secsafnodeID_list + secnodeID_list + safnodeID_list))
        nonrelnodeID_list = list(filter(lambda i: i not in relevantnodeID_list, list(featurenodeIDs_set))) #set of feature lifelines that are neither safety nor security relevant
            
        return secnodeID_set, safnodeID_set, secsafnodeID_set, set(nonrelnodeID_list)
        
    def get_graphquery_list(self, seclifelineIDs_set, saflifelineID_set, secsaflifelineID_set):
        "Get list of relevant node combinations for querrying the graph"
        queryID_list = []
        queryIDtuple_list = []
        if len(seclifelineIDs_set) != 0 and len(saflifelineID_set) != 0: #safety relevant lifelines and security relevant lifelines
            productA_list = list(itertools.product(list(seclifelineIDs_set), list(saflifelineID_set)))
            productB_list = list(itertools.product(list(saflifelineID_set), list(seclifelineIDs_set)))
            if len(productA_list) != 0:
                queryIDtuple_list.extend(productA_list)
            if len(productB_list) != 0:
                queryIDtuple_list.extend(productB_list)
            if len(secsaflifelineID_set) != 0: #safety relevant lifelines and security relevant lifelines and safety-and-security relevant lifelines
                productB_list = list(itertools.product(list(saflifelineID_set), list(secsaflifelineID_set)))
                productC_list = list(itertools.product(list(secsaflifelineID_set), list(saflifelineID_set)))
                productD_list = list(itertools.product(list(seclifelineIDs_set), list(secsaflifelineID_set)))
                productE_list = list(itertools.product(list(secsaflifelineID_set), list(seclifelineIDs_set)))
                if len(productB_list) != 0:
                    queryIDtuple_list.extend(productB_list)
                if len(productC_list) != 0:
                    queryIDtuple_list.extend(productC_list)
                if len(productD_list) != 0:
                    queryIDtuple_list.extend(productD_list)
                if len(productE_list) != 0:
                    queryIDtuple_list.extend(productE_list)
        elif len(seclifelineIDs_set) == 0 and len(saflifelineID_set) != 0 and len(secsaflifelineID_set) != 0: #safety relevant lifelines and safety-and-security relevant lifelines
            productF_list = list(itertools.product(list(saflifelineID_set), list(secsaflifelineID_set)))
            productG_list = list(itertools.product(list(secsaflifelineID_set), list(saflifelineID_set)))
            if len(productF_list) != 0:
                queryIDtuple_list.extend(productF_list)
            if len(productG_list) != 0:
                queryIDtuple_list.extend(productG_list)
        elif len(seclifelineIDs_set) != 0 and len(saflifelineID_set) == 0 and len(secsaflifelineID_set) != 0: #security relevant lifelines and safety-and-security relevant lifelines
            productH_list = list(itertools.product(list(seclifelineIDs_set), list(secsaflifelineID_set)))
            productI_list = list(itertools.product(list(secsaflifelineID_set), list(seclifelineIDs_set)))
            if len(productH_list) != 0:
                queryIDtuple_list.extend(productH_list)
            if len(productI_list) != 0:
                queryIDtuple_list.extend(productI_list)
        elif len(seclifelineIDs_set) == 0 and len(saflifelineID_set) == 0 and len(secsaflifelineID_set) != 0: #only safety-and-security relevant lifelines
            pass
        else: #either only security relevant lifelines or only safety relevant lifelines
            pass
        for element in queryIDtuple_list:
            if element not in queryID_list:
                queryID_list.append(list(element))
        return queryID_list
    
    def get_Inodes(self, path, currentQueryID):
        "for a received path that contains sub-paths, collect all intermediate nodes; note that format of subpath is (SWC1, SWC2, msg)"
        Inodes_list = []
        for index, subpath in enumerate(path):
            if index == 0:
                Inode = subpath[1] #get the first intermediate node by extracting the second element (& skipping the first element) of the first subpath
                if Inode not in Inodes_list:
                    Inodes_list.append(Inode)
            elif index != 0 and index != len(path)-1:
                Inode1 = subpath[1]
                Inode2 = subpath[0]
                if Inode1 not in Inodes_list:
                    Inodes_list.append(Inode1)
                if Inode2 not in Inodes_list:
                    Inodes_list.append(Inode2)
            elif index == len(path)-1: #get the last intermediate node by extracting the first element (& skipping the second element) of the last subpath
                Inode = subpath[0]
                if Inode not in Inodes_list:
                    Inodes_list.append(Inode)
            else:
                print("Warning! no condition met for index: ", index, " for subpath: ", subpath, " in the path: ", path, "!")
        for Inode in Inodes_list:
            if Inode in currentQueryID:
                Inodes_list.remove(Inode)
            else:
                continue
        return Inodes_list
        
    def check_Inodes_relevance(self, Inodes_list, firstandlastnode_list):
        "check if any node in the given list of intermediate nodes (for a path) is either safety or security relevant; if at least one intermediate node is safety or security relevant, set the intermediate node (Inode) relevance flag to 0 i.e. the path will be analyzed further to check if it is a secondary path"
        Inode_rel_flag = 1 #consider the path as primary path unless this flag is set to 0
        relvComponentID_list = list(set(firstandlastnode_list).symmetric_difference(self.relevantComponentID_set))
        relvInodes_list = []
        for node in Inodes_list:
            if node in relvComponentID_list:
                relvInodes_list.append(node)
        if len(relvInodes_list) == 0:
            Inode_rel_flag = 1 #path is primary path
        else:
            Inode_rel_flag = 0 #path may be a secondary path; check further if it is secondary
        return Inode_rel_flag, relvInodes_list
    
    def get_path_name(self, path, nodeID_name_dict):
        "For a path consisting of subpaths represented in IDs format; get its path name"
        path_name = []
        #print("Debug! path: ", path)
        for subpath in path:
            src_name = nodeID_name_dict[subpath[0]]
            dst_name = nodeID_name_dict[subpath[1]]
            if subpath[-1] in self.msgID_name_dict.keys():
                key_name = self.msgID_name_dict[subpath[-1]]
            else: #if key_name is None
                key_name = "-"
            subpath_name = (src_name,dst_name,key_name)
            path_name.append(subpath_name)
        return path_name
    
    def get_features_fromFeSWCmap(self, lifelineID, SafORSec_flag):
        "For a given component (classifier of a lifeline), get a list of safety and/or security features that the component realizes."
        featureNames_list = []
        if SafORSec_flag == "sec":
            featureIDs_list = query_dict_by_wlistvalue(self.secFeID_compID_dict, lifelineID)
        elif SafORSec_flag == "saf":
            featureIDs_list = query_dict_by_wlistvalue(self.safFeID_compID_dict, lifelineID)
        else:
            print("Warning! Invalid value of SafORSec_flag: ", SafORSec_flag, " received!")
        #print("Debug! featureIDs_list: ", featureIDs_list, " for lifeline: ", lifelineID, " that is ", SafORSec_flag, " relevant!")
        for featureID in featureIDs_list:
            feature_name = self.featurePkgID_name_dict[featureID]
            featureNames_list.append(feature_name)
        return featureIDs_list, str(featureNames_list)
    
    def edgepath_tabular_rep(self, query, path, componentID_name_dict):
        "For a given path, create a tabular representation for it!"
        #The variables below are used to check the safety and security relevance of the source and destination components (classifiers of lifelines) of each subpath of a path.
        SafORSecRelv_LL1_RxC3 = None #security relevance of first/src component in a subpath
        SafORSecRelv_LL1_RxC4 = None #safety relevance of first/src component in a subpath
        SafORSecRelv_LL2_RxC3 = None #security relevance of second/dst component in a subpath
        SafORSecRelv_LL2_RxC4 = None #safety relevance of second/dst component in a subpath)
        
        pathtable = [["LL:SWC","Msg", "SWCSecRelevance", "SWCSafRelevance", "SWCsec_features", "SWCsaf_features"]] #this variable contains data to create a path table
        
        for i, subpath in enumerate(path): #subpath is an edge tuple with key as message sequence ID
            subpathrow = [] #contains parts of data for creating path table
            nextsubpathrow = [] #for special cases e.g. [(A,B,K)]
            
            if subpath[0] in self.secComponentID_set: #check if source node is safety or security relevant
                SafORSecRelv_LL1_RxC3 = "sec"
                SafORSecRelv_LL1_RxC4 = "-"
            elif subpath[0] in self.safComponentID_set:
                SafORSecRelv_LL1_RxC3 = "-"
                SafORSecRelv_LL1_RxC4 = "saf"
            elif subpath[0] in self.secsafComponentID_set:
                SafORSecRelv_LL1_RxC3 = "sec"
                SafORSecRelv_LL1_RxC4 = "saf"
            else:
                SafORSecRelv_LL1_RxC3 = "-"
                SafORSecRelv_LL1_RxC4 = "-"
            
            if subpath[1] in self.secComponentID_set: #check if destination node is safety or security relevant
                SafORSecRelv_LL2_RxC3 = "sec"
                SafORSecRelv_LL2_RxC4 = "-"
            elif subpath[1] in self.safComponentID_set:
                SafORSecRelv_LL2_RxC3 = "-"
                SafORSecRelv_LL2_RxC4 = "saf"
            elif subpath[1] in self.secsafComponentID_set:
                SafORSecRelv_LL2_RxC3 = "sec"
                SafORSecRelv_LL2_RxC4 = "saf"
            else:
                SafORSecRelv_LL2_RxC3 = "-"
                SafORSecRelv_LL2_RxC4 = "-"
            
            if SafORSecRelv_LL1_RxC3 == "sec":
                seC0_featurename_CSWCactivitynameslist_dict, seC0_featurename_CSWCactivitynameslist_str = self.get_features_fromFeSWCmap(subpath[0], "sec")
            if SafORSecRelv_LL1_RxC4 == "saf":
                saC0_featurename_CSWCactivitynameslist_dict, saC0_featurename_CSWCactivitynameslist_str = self.get_features_fromFeSWCmap(subpath[0], "saf")
            if SafORSecRelv_LL2_RxC3 == "sec":
                seC1_featurename_CSWCactivitynameslist_dict, seC1_featurename_CSWCactivitynameslist_str = self.get_features_fromFeSWCmap(subpath[1], "sec")
            if SafORSecRelv_LL2_RxC4 == "saf":
                saC1_featurename_CSWCactivitynameslist_dict, saC1_featurename_CSWCactivitynameslist_str = self.get_features_fromFeSWCmap(subpath[1], "saf")
            
            #Creating list of lists for tabular representation of data
            if (i==0 and i==(len(path)-1)) or (i!=0 and i==(len(path)-1)): #for special cases e.g. [(A,B,K)]
                subpathrow.append(componentID_name_dict[subpath[0]]) #first/source component
                if self.msgID_name_dict[subpath[2]] is None:
                    subpathrow.append("-")
                else:
                    subpathrow.append(self.msgID_name_dict[subpath[2]]) #key as msgseq ID
                subpathrow.append(SafORSecRelv_LL1_RxC3)
                subpathrow.append(SafORSecRelv_LL1_RxC4)
                if SafORSecRelv_LL1_RxC3 == "sec":
                    subpathrow.append(seC0_featurename_CSWCactivitynameslist_str)
                else:
                    subpathrow.append("-")
                if SafORSecRelv_LL1_RxC4 == "saf":
                    subpathrow.append(saC0_featurename_CSWCactivitynameslist_str)
                else:
                    subpathrow.append("-")
                nextsubpathrow.append(componentID_name_dict[subpath[1]]) #second component
                nextsubpathrow.append("-") #key as msgseq ID
                nextsubpathrow.append(SafORSecRelv_LL2_RxC3)
                nextsubpathrow.append(SafORSecRelv_LL2_RxC4)
                if SafORSecRelv_LL2_RxC3 == "sec":
                    nextsubpathrow.append(seC1_featurename_CSWCactivitynameslist_str)
                else:
                    nextsubpathrow.append("-")
                if SafORSecRelv_LL2_RxC4 == "saf":
                    nextsubpathrow.append(saC1_featurename_CSWCactivitynameslist_str)
                else:
                    nextsubpathrow.append("-")
            elif (i==0 and i!=(len(path)-1)) or (i!=0 and i!=(len(path)-1)):
                subpathrow.append(componentID_name_dict[subpath[0]]) #first/source component
                if self.msgID_name_dict[subpath[2]] is None:
                    subpathrow.append("-")
                else:
                    subpathrow.append(self.msgID_name_dict[subpath[2]]) #key as msgseq ID
                subpathrow.append(SafORSecRelv_LL1_RxC3)
                subpathrow.append(SafORSecRelv_LL1_RxC4)
                if SafORSecRelv_LL1_RxC3 == "sec":
                    subpathrow.append(seC0_featurename_CSWCactivitynameslist_str)
                else:
                    subpathrow.append("-")
                if SafORSecRelv_LL1_RxC4 == "saf":
                    subpathrow.append(saC0_featurename_CSWCactivitynameslist_str)
                else:
                    subpathrow.append("-")
            else:
                print("\nMet an unexpected condition :( !!!")
            
            pathtable.append(subpathrow)
            if len(nextsubpathrow) != 0:
                pathtable.append(nextsubpathrow)
    
    def extract_FI_based_on_relvMsgs_and_SWC(self, path, src, dst, secnodeID_set, safnodeID_set, nodeID_name_dict):
        "For a given path, check the safety and security relevances of the first and last messages and components of a path"
        srcfeID_list = []
        dstfeID_list = []
        perpath_FIs_list = []   
        for index, subpath in enumerate(path):
            if index == 0 and index == len(path) - 1:
                firstorlastmsg = subpath[-1]
                feID_list = query_dict_by_wlistvalue(self.feID_relMsgIDslist_dict, firstorlastmsg)
                if len(feID_list) == 0:
                    srcfeID_list = query_dict_by_wlistvalue(self.feID_compID_dict, src)
                    dstfeID_list = query_dict_by_wlistvalue(self.feID_compID_dict, dst)
                else:
                    for element in feID_list:
                        if (element in self.secFeaturePkgID_list and src in secnodeID_set) or (element in self.safFeature_pkg_list and src in safnodeID_set):
                            dstfeID_list = query_dict_by_wlistvalue(self.feID_compID_dict, dst)
                            if element not in srcfeID_list:
                                srcfeID_list.append(element)
                        elif (element in self.secFeaturePkgID_list and dst in secnodeID_set) or (element in self.safFeature_pkg_list and dst in safnodeID_set):
                            srcfeID_list = query_dict_by_wlistvalue(self.feID_compID_dict, src)
                            if element not in dstfeID_list:
                                dstfeID_list.append(element)
                        else:
                            print("Warning! Mismatch in safety and security relevance of software component & feature!")
            elif index != 0 and index != len(path)-1:
                continue
            elif index != 0 and index == len(path)-1:
                lastmsg = subpath[-1]
                feID_list = query_dict_by_wlistvalue(self.feID_relMsgIDslist_dict, lastmsg)
                if len(feID_list) == 0:
                    dstfeID_list = query_dict_by_wlistvalue(self.feID_compID_dict, dst)
                else:
                    for element in feID_list:
                        if (element in self.secFeaturePkgID_list and dst in secnodeID_set) or (element in self.safFeature_pkg_list and dst in safnodeID_set):
                            if element not in dstfeID_list:
                                dstfeID_list.append(element)
                        else:
                            print("Warning! Mismatch in safety and security relevance of software component & feature!")
            elif index == 0 and index != len(path)-1:
                firstmsg = subpath[-1]
                feID_list = query_dict_by_wlistvalue(self.feID_relMsgIDslist_dict, firstmsg)
                if len(feID_list) == 0:
                    srcfeID_list = query_dict_by_wlistvalue(self.feID_compID_dict, src)
                else:
                    for element in feID_list:
                        if (element in self.secFeaturePkgID_list and src in secnodeID_set) or (element in self.safFeature_pkg_list and src in safnodeID_set):
                            if element not in srcfeID_list:
                                srcfeID_list.append(element)
                        else:
                            print("Warning! Mismatch in safety and security relevance of software component & feature!")
            else:
                print("Warning! uncovered/unexpected condition found! index: ", index)
        if len(srcfeID_list) != 0 and len(dstfeID_list) != 0:
            perpath_FIs_list = get_itertoolsproductoflists(srcfeID_list, dstfeID_list)
        return perpath_FIs_list
    
    def get_direct_indirect_primary_interactions(self, graph, queryID_list, nodeID_name_dict, secnodeID_set, safnodeID_set, secsafnodeID_set, primarydirectIP_list, primaryindirectIP_list, queryID_directPPF_list, queryID_indirectPPF_list, componentID_name_dict, depth):
        path_count = 0 #count total number of paths found for all queries
        primarydirectPath_count = 0
        primaryindirectPath_count = 0
        primarydirectFI_IDs_list = []
        primaryindirectFI_IDs_list = []
        directprimaryFI_IDs_list = []
        indirectprimaryFI_IDs_list = []
        for index, value in enumerate(queryID_list):
            src = value[0]
            dst = value[1]
            current_queryID_list = [src, dst]
            for path in nx.all_simple_edge_paths(graph, source = src, target = dst, cutoff = depth): #query graph to get paths for the selected query (source and destination components) in the graph query list
                if path not in primarydirectIP_list and path not in primaryindirectIP_list:
                    path_count = path_count + 1 #counting total number of paths found for all queries
                    path_name = self.get_path_name(path, nodeID_name_dict) #get pathname for debugging/validating the path as primary or secondary
                    primaryIP_flag = 0 #this flag is set to 1 if the path is a primary interaction path.
                    if len(path) == 1:
                        primaryIP_flag = 1
                    elif len(path) > 1:
                        Inodes_list = self.get_Inodes(path, current_queryID_list)
                        if len(Inodes_list) != 0:
                            Inode_rel_flag, relvInodes_list = self.check_Inodes_relevance(Inodes_list, current_queryID_list) #flag set to 0 if there exists at least one safety or security relevant Inode
                            if Inode_rel_flag == 1:
                                primaryIP_flag = 1
                        elif len(Inodes_list) == 0:
                            primaryIP_flag = 1
                        else:
                            print("Warning! Invalid length of intermediate nodes: ", len(Inodes_list))
                    else:
                        print("Warning! Unexpected path len found: ", len(path))
                    if primaryIP_flag == 1 and len(path) == 1:
                        #print("Direct_primary_path: ", path_name, " found!")
                        primarydirectIP_list.append(path)
                        primarydirectPath_count = primarydirectPath_count + 1
                        if current_queryID_list not in queryID_directPPF_list:
                            queryID_directPPF_list.append(current_queryID_list)
                        ############### Retrieve FIs based on relevant messages and software components##########
                        perpathPriFI_IDs_list = self.extract_FI_based_on_relvMsgs_and_SWC(path, src, dst, secnodeID_set, safnodeID_set, nodeID_name_dict)
                        #print("Debug! perpathPriFI_IDs_list: ", perpathPriFI_IDs_list)
                        perpathPriFI_names_list = get_listoflistnames_from_listoflistIDs(perpathPriFI_IDs_list, self.featurePkgID_name_dict)
                        for element in perpathPriFI_IDs_list:
                            if element not in directprimaryFI_IDs_list:
                                directprimaryFI_IDs_list.append(element)
                    elif primaryIP_flag == 1 and len(path) > 1:
                        #print("Indirect_primary_path: ", path_name, " found!")
                        primaryindirectIP_list.append(path)
                        primaryindirectPath_count = primaryindirectPath_count + 1
                        if current_queryID_list not in queryID_indirectPPF_list:
                            queryID_indirectPPF_list.append(current_queryID_list)
                        ############### Retrieve FIs based on relevant messages and software components##########
                        perpathPriFI_IDs_list = self.extract_FI_based_on_relvMsgs_and_SWC(path, src, dst, secnodeID_set, safnodeID_set, nodeID_name_dict)
                        #print("Debug! perpathPriFI_IDs_list: ", perpathPriFI_IDs_list)
                        perpathPriFI_names_list = get_listoflistnames_from_listoflistIDs(perpathPriFI_IDs_list, self.featurePkgID_name_dict)
                        for element in perpathPriFI_IDs_list:
                            if element not in directprimaryFI_IDs_list:
                                if element not in indirectprimaryFI_IDs_list:
                                    indirectprimaryFI_IDs_list.append(element)
                    else:
                        pass
        return path_count, queryID_directPPF_list, queryID_indirectPPF_list, primarydirectPath_count, primaryindirectPath_count, primarydirectIP_list, primaryindirectIP_list, directprimaryFI_IDs_list, indirectprimaryFI_IDs_list
                            
    def get_primary_interactions(self, graph, queryID_list, nodeID_name_dict, secnodeID_set, safnodeID_set, secsafnodeID_set, primaryIP_list, queryID_pripathfound_list, componentID_name_dict, depth):
        "Query the graph to identify primary interaction paths for the each query in the query list"
        path_count = 0 #count total number of paths found for all queries
        primaryPath_count = 0 #count number of primary paths found for all queries
        primaryFI_IDs_list = [] #store feature interactions (FIs) for primary interaction paths based on relevant messages; in case of missing relevant messages, store FIs based on relevant components
        
        for index, value in enumerate(queryID_list):
            src = value[0]
            dst = value[1]
            current_queryID_list = [src, dst]
            for path in nx.all_simple_edge_paths(graph, source = src, target = dst, cutoff = depth): #query graph to get paths for the current query (source and destination pair) in the graph query list
                if path not in primaryIP_list:
                    path_count = path_count + 1 #counting total number of paths found for all queries
                    path_name = self.get_path_name(path, nodeID_name_dict) #get pathname for debugging/validating the path as primary or secondary
                    primaryIP_flag = 0 #This flag is set to 1 if the path is a primary interaction path.
                    if len(path) == 1:
                        primaryIP_flag = 1
                    elif len(path) > 1:
                        Inodes_list = self.get_Inodes(path, current_queryID_list) #Get intermediate nodes for the path whose path length > 1 & remove the intermediate node that is same as the src or dst in the current query
                        #print("\nDebug! Inodes_list: ", Inodes_list, " len(Inodes_list): ", len(Inodes_list), " for a pathID: ", path, " path_name: ", path_name)
                        if len(Inodes_list) != 0:
                            Inode_rel_flag, relvInodes_list = self.check_Inodes_relevance(Inodes_list, current_queryID_list) #flag set to 0 if there exists at least one safety or security relevant Inode
                            #print("\nDebug! Inode_rel_flag: ", Inode_rel_flag, " relvInodes_list: ", relvInodes_list)
                            if Inode_rel_flag == 1:
                                primaryIP_flag = 1
                        elif len(Inodes_list) == 0:
                            primaryIP_flag = 1
                        else:
                            print("Warning! Invalid length of intermediate nodes: ", len(Inodes_list))
                    else:
                        print("Warning! Unexpected path len found: ", len(path))
                    
                    if primaryIP_flag == 1:
                        print("Primary_path: ", path_name, " found!")
                        primaryIP_list.append(path)
                        primaryPath_count = primaryPath_count + 1
                        if current_queryID_list not in queryID_pripathfound_list:
                            queryID_pripathfound_list.append(current_queryID_list)
                        ############### Retrieve FIs based on relevant messages and relevant software components##########
                        perpathPriFI_IDs_list = self.extract_FI_based_on_relvMsgs_and_SWC(path, src, dst, secnodeID_set, safnodeID_set, nodeID_name_dict)
                        #print("Debug! perpathPriFI_IDs_list: ", perpathPriFI_IDs_list)
                        perpathPriFI_names_list = get_listoflistnames_from_listoflistIDs(perpathPriFI_IDs_list, self.featurePkgID_name_dict)
                        #print("Debug! path: ", path_name, " extracted_FIs_based_on_msg_relv_and_SWC: ", len(perpathPriFI_IDs_list), " : ", perpathPriFI_names_list, "\n")
                        for element in perpathPriFI_IDs_list:
                            if element not in primaryFI_IDs_list:
                                primaryFI_IDs_list.append(element)
        return path_count, queryID_pripathfound_list, primaryPath_count, primaryIP_list, primaryFI_IDs_list
    
    def get_secondary_interactions(self, graph, queryID_list, nodeID_name_dict, secnodeID_set, safnodeID_set, secsafnodeID_set, secondaryIP_list, queryID_secondarypathfound_list, componentID_name_dict, depth):
        "Query the graph to identify secondary interaction paths for the each query in the (filtered) query list"
        path_count = 0 #count total number of paths found for all queries
        secondaryPath_count = 0 #count number of secondary paths found for all queries
        secondaryFI_IDs_list = [] #store feature interactions (FIs) for both primary & secondary paths based on relevant messages; in case of missing relevant messages, store FIs based on relevant components
        secondaryFI_IDs_dict = {} #secondary feature interaction (FI) is stored in the format {FI: [Intermedite features]} wherein FI = [F1, F2]
        for index, value in enumerate(queryID_list):
            src = value[0]
            dst = value[1]
            current_queryID_list = [src, dst]
            queryFeIDs_list = []
            
            #get a list of features that are mapped to src and dst lifelines of the current query; this list will be used to inspect whether the path obtained for the current query is a secondary path or not.
            for element in current_queryID_list:
                feID_list = query_dict_by_wlistvalue(self.feID_compID_dict, element)
                for featureID in feID_list:
                    if featureID not in queryFeIDs_list:
                        queryFeIDs_list.append(featureID)
            
            #query graph to find paths for the current query of the graph query list
            for path in nx.all_simple_edge_paths(graph, source = src, target = dst, cutoff = depth):
                if path not in secondaryIP_list:
                    relvInodesFeIDs_list = [] #get features realized by the intermediate nodes
                    secondaryInodesFeIDs_list = [] #get features realized by the intermediate nodes that are different/unique with respect to features realized by the lifelines specified in the query
                    secondaryIP_flag = 0 #This flag is set to 1 if the path is a secondary interaction path.
                    path_count = path_count + 1 #counting total number of paths found for all queries
                    path_name = self.get_path_name(path, nodeID_name_dict) #get pathname for debugging/validating the path as primary or secondary
                    if len(path) > 1:
                        Inodes_list = self.get_Inodes(path, current_queryID_list) #Get intermediate nodes for the path whose path length > 1 & remove the intermediate node that is same as the source or destination component in the current query
                        #print("\nDebug! Inodes_list: ", Inodes_list, " len(Inodes_list): ", len(Inodes_list), " for a pathID: ", path, " path_name: ", path_name)
                        if len(Inodes_list) != 0:
                            Inode_rel_flag, relvInodes_list = self.check_Inodes_relevance(Inodes_list, current_queryID_list) #flag is set to 0 if at least one relevant Inode found; flag is set to 1 if the path is a primary interaction path
                            #print("\nDebug! Inode_rel_flag: ", Inode_rel_flag, " relvInodes_list: ", relvInodes_list)
                            if Inode_rel_flag == 0:
                                for relvInode in relvInodes_list:
                                    feID_list = query_dict_by_wlistvalue(self.feID_compID_dict, relvInode)
                                    for featureID in feID_list:
                                        if featureID not in relvInodesFeIDs_list:
                                            relvInodesFeIDs_list.append(featureID)
                                #check if at least one of the obtained features is unique with respect to features realized by source and destination node/component (classifier of lifeline)
                                for featureID in relvInodesFeIDs_list:
                                    if featureID not in queryFeIDs_list:
                                        if featureID not in secondaryInodesFeIDs_list:
                                            secondaryInodesFeIDs_list.append(featureID)
                                if len(secondaryInodesFeIDs_list) != 0:
                                    secondaryIP_flag = 1
                                #print("Debug! After secondary path analysis, check secondaryIP_flag: ", secondaryIP_flag)
                    if secondaryIP_flag == 1:
                        self.edgepath_tabular_rep(current_queryID_list, path, componentID_name_dict)
                        #print("Debug! features mapped to lifelines in query: ", get_listnames_from_listIDs(queryFeIDs_list, self.featurePkgID_name_dict))
                        #print("\nSecondary_path: ", path_name, " found!", "\nRelevant Inodes: ", len(relvInodes_list), get_listnames_from_listIDs(relvInodes_list, nodeID_name_dict), " intermediateInteractingFeatures: ", get_listnames_from_listIDs(secondaryInodesFeIDs_list, self.featurePkgID_name_dict), "\nfeatures mapped to lifelines in query: ", get_listnames_from_listIDs(queryFeIDs_list, self.featurePkgID_name_dict))
                        secondaryIP_list.append(path)
                        secondaryPath_count = secondaryPath_count + 1
                        if current_queryID_list not in queryID_secondarypathfound_list:
                            queryID_secondarypathfound_list.append(current_queryID_list)
                        ############### Retrieve FIs based on relevant messages and relevant software components##########
                        perpathSecFI_IDs_list = self.extract_FI_based_on_relvMsgs_and_SWC(path, src, dst, secnodeID_set, safnodeID_set, nodeID_name_dict)
                        #print("Extracted_FIs: ", len(perpathSecFI_IDs_list), " are ", perpathSecFI_IDs_list)
                        #print("Debug! secondaryFI_IDs_dict: ", secondaryFI_IDs_dict, " Extracted_FIs(perpathSecFI_IDs_list): ", perpathSecFI_IDs_list, " intermediateFeatureIDs(secondaryInodesFeIDs_list): ", secondaryInodesFeIDs_list)
                        if len(perpathSecFI_IDs_list) != 0:
                            for FI_ID in perpathSecFI_IDs_list:
                                FI_tuple = tuple(FI_ID) #converting type of feature interaction (FI) from list to tuple becuase the keys of dict must be of hashable data type
                                #print("Debug! FI_ID: ", FI_ID, " type(FI_ID): ", type(FI_ID), " FI_tuple: ", FI_tuple, " type(FI_tuple): ", type(FI_tuple))
                                if FI_tuple not in secondaryFI_IDs_dict.keys():
                                    secondaryFI_IDs_dict.update({FI_tuple: secondaryInodesFeIDs_list})
                                elif FI_tuple in secondaryFI_IDs_dict.keys():
                                    IFe_forFI = secondaryFI_IDs_dict[FI_tuple] #get the intermediate (interacting) features for this FI (feature interaction)
                                    for featureID in secondaryInodesFeIDs_list:
                                        if featureID not in IFe_forFI:
                                            IFe_forFI.append(featureID)
                                    secondaryFI_IDs_dict[FI_tuple] = IFe_forFI
                        perpathSecFI_names_list = get_listoflistnames_from_listoflistIDs(perpathSecFI_IDs_list, self.featurePkgID_name_dict)
                        print("Extracted_FIs: ", len(perpathSecFI_IDs_list), " are ", perpathSecFI_names_list)
                        for element in perpathSecFI_IDs_list:
                            if element not in secondaryFI_IDs_list:
                                secondaryFI_IDs_list.append(element)
        return path_count, queryID_secondarypathfound_list, secondaryPath_count, secondaryIP_list, secondaryFI_IDs_list, secondaryFI_IDs_dict
    
    def get_feIDactIDlistdict(self, featureID_list, activityID_list, feID_actWdependencylist_dict, actID_name_dict):
        lifelinesactivityID_list = []
        feID_actIDlist_dict = {}
        fename_actnamelist_dict = {}
        fe_name = None
        
        for ele in featureID_list:
            lifelinesactivityID_list = []
            featuresactivityID_list = feID_actWdependencylist_dict[ele]
            for obj in featuresactivityID_list:
                if obj in activityID_list:
                    lifelinesactivityID_list.append(obj)
            lifelinesactivityname_list = get_listnames_from_listIDs(lifelinesactivityID_list, actID_name_dict)
            feID_actIDlist_dict.update({ele: lifelinesactivityID_list})
            fe_name = self.featurePkgID_name_dict[ele]
            fename_actnamelist_dict.update({fe_name:lifelinesactivityname_list})
        return feID_actIDlist_dict, fename_actnamelist_dict
     
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
        #print("\nDebug! edgeID_name_dict: ", edgeID_name_dict)
        return nodeIDs_set, nodeID_name_dict, edgeIDs_list, edgeID_name_dict
    
    def get_interaction_list(self, depth):
        "Get a list of primary and secondary feature interactions between safety and security features"
        safFe_interactingSecFe_list = []
        secFe_interactingSafFe_list = []
        relComponentID_name_dict = {}
        relComponentID_name_dict.update(self.secComponentID_name_dict)
        relComponentID_name_dict.update(self.safComponentID_name_dict)
        all_FInames_listsoflist = []
        queryID_list = [] #List of queries to search the graph for primary interaction paths
        queryID_SIP_list = [] #List of queries to search the graph for secondary interaction paths
        primaryIP_list = [] #List of primary interaction paths
        secondaryIP_list = [] #List of secondary interaction paths
        queryID_pripathfound_list = [] #collect queries for which atleast 1 primary path was found.
        queryID_secondarypathfound_list = [] #collect queries for which atleast 1 secondary path was found.
        
        componentID_name_dict = {}
        nodeIDnamedict_list = list(self.feID_nodeIDnamedict_dict.values())
        for nodeIDnamedict in nodeIDnamedict_list:
            componentID_name_dict.update(nodeIDnamedict)
        
        #unpack the node_list, nodeID_name_labeldict, edge_list, edgeID_name_dict for all safety and security features
        nodeIDs_set, nodeID_name_dict, edgeIDs_list, edgeID_name_dict = self.get_nodes_edges_of_all_saf_and_sec_features() #data struct of all nodes and edges
        print("\nDebug! len(nodes): ", len(nodeIDs_set), " and len(edges): ", len(edgeIDs_list), " for all saf & sec features!")
        
        #identify only safety relevant, only security relevant and both safety and security relevant lifeline
        secnodeID_set, safnodeID_set, secsafnodeID_set, nonrelnodeID_set = self.get_relevant_lifelines(nodeIDs_set)
        print("\nDebug! Relevant lifelines for .sd of all saf-&sec features! secnodeID_no: ", len(secnodeID_set), ", safnodeID_no: ", len(safnodeID_set), ", secsafnodeID_no: ", len(secsafnodeID_set))
        
        print("\nCreating nx multi directed graph ...")
        featureseqdiags_graph = create_multidi_graph(nodeIDs_set, edgeIDs_list)
        
        print("\nGenerating graph query list ...")
        queryID_list = self.get_graphquery_list(secnodeID_set, safnodeID_set, secsafnodeID_set)
        print("\nDebug! len(queryID_list): ", len(queryID_list))
        
        primarydirectIP_list = []
        primaryindirectIP_list = []
        queryID_directPPF_list = []
        queryID_indirectPPF_list = []
        
        print("\nQuerying graph to get primary direct and indirect interaction paths...")
        path_count, queryID_directPPF_list, queryID_indirectPPF_list, primarydirectPath_count, primaryindirectPath_count, primarydirectIP_list, primaryindirectIP_list, directprimaryFI_IDs_list, indirectprimaryFI_IDs_list = self.get_direct_indirect_primary_interactions(featureseqdiags_graph, queryID_list, nodeID_name_dict, secnodeID_set, safnodeID_set, secsafnodeID_set, primarydirectIP_list, primaryindirectIP_list, queryID_directPPF_list, queryID_indirectPPF_list, componentID_name_dict, depth)
        
        for FI in indirectprimaryFI_IDs_list:
            if FI in directprimaryFI_IDs_list:
                indirectprimaryFI_IDs_list.remove(FI)
        
        directpriFInames_list = get_listoflistnames_from_listoflistIDs(directprimaryFI_IDs_list, self.featurePkgID_name_dict)
        #create_table_for_interactingfeatures(directpriFInames_list)
        indirectpriFInames_list = get_listoflistnames_from_listoflistIDs(indirectprimaryFI_IDs_list, self.featurePkgID_name_dict)
        #create_table_for_interactingfeatures(indirectpriFInames_list)
        
        print("\nSummary! depth:", depth, "\nDirect primary interactions...", "\nlen(queryID_directPPF_list): ", len(queryID_directPPF_list), "\nprimarydirectPath_count: ", primarydirectPath_count, "\nlen(directprimaryFI_IDs_list): ", len(directprimaryFI_IDs_list), "\ndirectpriFInames_list: ", directpriFInames_list, "\n\nIndirect primary interactions...", "\nlen(queryID_indirectPPF_list): ", len(queryID_indirectPPF_list), "\nprimaryindirectPath_count: ", primaryindirectPath_count, "\nlen(indirectprimaryFI_IDs_list): ", len(indirectprimaryFI_IDs_list), "\nindirectpriFInames_list: ", indirectpriFInames_list)
        
        #Generating queryID_pripathfound_list (queryID_directPPF_list + queryID_indirectPPF_list)
        for query in queryID_directPPF_list:
            if query not in queryID_pripathfound_list:
                queryID_pripathfound_list.append(query)
        for query in queryID_indirectPPF_list:
            if query not in queryID_pripathfound_list:
                queryID_pripathfound_list.append(query)
        
        #Generating primaryFI_IDs_list (directprimaryFI_IDs_list + indirectprimaryFI_IDs_list)
        primaryFI_IDs_list = []
        for FI in directprimaryFI_IDs_list:
            if FI not in primaryFI_IDs_list:
                primaryFI_IDs_list.append(FI)
        for FI in indirectprimaryFI_IDs_list:
            if FI not in primaryFI_IDs_list:
                primaryFI_IDs_list.append(FI)
        
        #Generating primaryIPs_list (primarydirectIP_list + primaryindirectIP_list)
        primaryIPs_list = []
        for IP in primarydirectIP_list:
            if IP not in primaryIPs_list:
                primaryIPs_list.append(IP)
        for IP in primaryindirectIP_list:
            if IP not in primaryIPs_list:
                primaryIPs_list.append(IP)
        #Generating primaryPath_count
        primaryPath_count = len(primaryIPs_list)
        
        #preparing the query list for identifying secondary paths by removing the queries for which at least 1 primary interaction path has been found.
        #print("Debug!Before! len(queryID_list): ", len(queryID_list), " queryID_list: ", queryID_list, "\nlen(queryID_pripathfound_list): ", len(queryID_pripathfound_list), " queryID_pripathfound_list: ", queryID_pripathfound_list, "\nlen(queryID_SIP_list): ", len(queryID_SIP_list))
        for queryID in queryID_list:
            if queryID in queryID_pripathfound_list:
                continue
            else:
                queryID_SIP_list.append(queryID)
        #print("Debug!After! len(queryID_list): ", len(queryID_list), " len(queryID_SIP_list): ", len(queryID_SIP_list))
        
        print("\nQuerying graph to get secondary interaction paths...")
        path_count, queryID_secondarypathfound_list, secondaryPath_count, secondaryIPs_list, secondaryFI_IDs_list, secondaryFI_IDs_dict = self.get_secondary_interactions(featureseqdiags_graph, queryID_SIP_list, nodeID_name_dict, secnodeID_set, safnodeID_set, secsafnodeID_set, secondaryIP_list, queryID_secondarypathfound_list, componentID_name_dict, depth)
        secondaryFI_names_list = get_listoflistnames_from_listoflistIDs(secondaryFI_IDs_list, self.featurePkgID_name_dict)
        create_table_for_interactingfeatures(secondaryFI_names_list)
        print("Debug! secondaryFI_IDs_list: ", secondaryFI_IDs_list)
        
        print("\nSummary! secondary_interactions! depth: ", depth, "\nQueries for which atleast 1 secondary path was found: ", len(queryID_secondarypathfound_list), " out of ", len(queryID_SIP_list), " queries in total.", "\nsecondaryPaths_count: ", secondaryPath_count, "\nTotal Secondary FIs (before removing FIs common to primary FIs): ", len(secondaryFI_IDs_list), "\nsecondaryFI_names_list: ", secondaryFI_names_list)
        
        common_primary_and_secondaryFI = [] #common primary and secondary feature interactions
        for FI_ID in secondaryFI_IDs_list:
            if FI_ID in primaryFI_IDs_list:
                common_primary_and_secondaryFI.append(FI_ID)
        
        commonQuery_pathFound = [] #queries for which both a primary and a secondary path was found.
        for query in queryID_secondarypathfound_list:
            if query in queryID_pripathfound_list:
                commonQuery_pathFound.append(query)
        print("\nDebug! Common query for which atleast 1 primary or secondary IP was found: ", len(commonQuery_pathFound), " commonQuery_pathFound: ", commonQuery_pathFound)
        
        Query_pathFound = [] #total queries for which a primary or secondary path was found.
        for queryID in queryID_pripathfound_list:
            if queryID not in Query_pathFound:
                Query_pathFound.append(queryID)
        for queryID in queryID_secondarypathfound_list:
            if queryID not in Query_pathFound:
                Query_pathFound.append(queryID)
        
        common_priANDsecIP = [] #common primary and secondary interaction path.
        for IP in secondaryIPs_list:
            if IP in primaryIPs_list:
                common_priANDsecIP.append(IP)
        print("Debug! Common primary & secondary IP: ", len(common_priANDsecIP))
        
        priANDsecIP_list = [] #total primary and secondary interaction paths.
        for IP in primaryIPs_list:
            if IP not in priANDsecIP_list:
                priANDsecIP_list.append(IP)
        for IP in secondaryIPs_list:
            if IP not in priANDsecIP_list:
                priANDsecIP_list.append(IP)
        
        total_FIs = [] #total primary and secondary feature interactions.
        total_FIs.extend(primaryFI_IDs_list)
        for FI in secondaryFI_IDs_list:
            if FI not in total_FIs:
                total_FIs.append(FI)
        total_SafToSec_FIs = [] #total primary and secondary feature interactions in the direction safety to security features
        total_SecToSaf_FIs = [] #total primary and secondary feature interactions in the direction security to safety features
        for FI in total_FIs:
            if FI[0] in self.secFeaturePkgID_list:
                if FI not in total_SecToSaf_FIs:
                    total_SecToSaf_FIs.append(FI)
            elif FI[0] in self.safFeature_pkg_list:
                if FI not in total_SafToSec_FIs:
                    total_SafToSec_FIs.append(FI)
            else:
                print("Warning! Unexpected condition for FI: ", FI, " found!")
        
        secondaryFI_IDs_updatedlist = [] #total secondary feature interactions (after removing FIs found by both primary and secondary interactions analysis)
        for FI in secondaryFI_IDs_list:
            if FI not in primaryFI_IDs_list:
                secondaryFI_IDs_updatedlist.append(FI)
        
        print("\nSummary Overview (of primary and secondary interactions)! depth: ", depth, "\n\nSummary_Primary_Interactions...", "\nlen(queryID_list): ", len(queryID_list), "\nqueryID_forwhich_primaryIPfound_list: ", len(queryID_pripathfound_list), "\nprimaryPaths_count: ", primaryPath_count, "\nTotal Primary FIs: ", len(primaryFI_IDs_list), "\n\nSummary_Secondary_Interactions...", "\nlen(queryID_SIP_list): ", len(queryID_SIP_list),"\nqueryID_forwhich_secondaryIPfound_list: ", len(queryID_secondarypathfound_list), "\nsecondaryPaths_count: ", secondaryPath_count, "\nTotal Secondary FIs (before removing FIs common to primary FIs): ", len(secondaryFI_IDs_list), "\nTotal Secondary FIs (after removing FIs that are same as primary ones): ", len(secondaryFI_IDs_updatedlist), "\n\nSummary_Common_Primary_and_Secondary_Interactions...", "\nlen(common_primary_and_secondaryFI): ", len(common_primary_and_secondaryFI), "\ncommon_primary_and_secondaryFI: ", get_listoflistnames_from_listoflistIDs(common_primary_and_secondaryFI, self.featurePkgID_name_dict), "\n\nSummary_Total_Interactions...", "\nlen(Query_pathFound): ", len(Query_pathFound), "\nlen(priANDsecIP_list): ", len(priANDsecIP_list), "\nlen(total_FIs): ", len(total_FIs), "\nlen(total_SafToSec_FIs): ", len(total_SafToSec_FIs), "\nlen(total_SecToSaf_FIs): ", len(total_SecToSaf_FIs), "\ntotal_FIs: ", get_listoflistnames_from_listoflistIDs(total_FIs, self.featurePkgID_name_dict), "\ntotal_SafToSec_FIs: ", get_listoflistnames_from_listoflistIDs(total_SafToSec_FIs, self.featurePkgID_name_dict), "\ntotal_SecToSaf_FIs: ", get_listoflistnames_from_listoflistIDs(total_SecToSaf_FIs, self.featurePkgID_name_dict))
        
        for FI in common_primary_and_secondaryFI:
            FI_tuple = tuple(FI) #FI converted from list to tuple as tuple is a hashable data type used as key in the dict secondaryFI_IDs_dict
            secondaryFI_IDs_dict.pop(FI_tuple, None) #remove common FIs from the secondary FI dict
        print("\n\nDebug! Number of FIs obtained after removing common FIs from secondaryFI_IDs_dict: ", len(secondaryFI_IDs_dict.keys()))
        
        secondaryFIs_SecToSaf = []
        secondaryFIs_SafToSec = []
        for key in secondaryFI_IDs_dict:
            IFe_list = secondaryFI_IDs_dict[key]
            FI_ID_list = list(key)
            src_feID = FI_ID_list[0]
            src_feName = self.featurePkgID_name_dict[src_feID]
            dst_feID = FI_ID_list[1]
            dst_feName = self.featurePkgID_name_dict[dst_feID]
            FI_names_list = get_listnames_from_listIDs(IFe_list, self.featurePkgID_name_dict)
            each_secFI = [src_feName, dst_feName, FI_names_list]
            if src_feID in self.secFeaturePkgID_list:
                if each_secFI not in secondaryFIs_SecToSaf:
                    secondaryFIs_SecToSaf.append(each_secFI)
            elif src_feID in self.safFeature_pkg_list:
                if each_secFI not in secondaryFIs_SafToSec:
                    secondaryFIs_SafToSec.append(each_secFI)
            else:
                pass
        print("\n\nTotal secondary FIs (cleaned) from security to safety features: ", len(secondaryFIs_SecToSaf), "are: ")
        secondaryFIs_SecToSaf.sort()
        updated_secondaryFIs_SecToSaf = list(secondaryFIs_SecToSaf for secondaryFIs_SecToSaf, _ in itertools.groupby(secondaryFIs_SecToSaf))
        print(tabulate(updated_secondaryFIs_SecToSaf, headers = ["Security_feature", "Safety_feature", "Intermediate_features"], tablefmt = 'grid'))
        
        print("\n\nTotal secondary FIs (cleaned) from safety to security features: ", len(secondaryFIs_SafToSec), "are: ")
        secondaryFIs_SafToSec.sort()
        updated_secondaryFIs_SafToSec = list(secondaryFIs_SafToSec for secondaryFIs_SafToSec, _ in itertools.groupby(secondaryFIs_SafToSec))
        print(tabulate(updated_secondaryFIs_SafToSec, headers = ["Security_feature", "Safety_feature", "Intermediate_features"], tablefmt = 'grid'))
        
        secondaryFI_IDs_withIFe = []
        for key in secondaryFI_IDs_dict:
            IFe_list = secondaryFI_IDs_dict[key]
            FI_ID_list = list(key)
            src_feID = FI_ID_list[0]
            src_feName = self.featurePkgID_name_dict[src_feID]
            dst_feID = FI_ID_list[1]
            dst_feName = self.featurePkgID_name_dict[dst_feID]
            FI_names_list = get_listnames_from_listIDs(IFe_list, self.featurePkgID_name_dict)
            each_secFI = [src_feName, dst_feName, FI_names_list]
            if each_secFI not in secondaryFI_IDs_withIFe:
                secondaryFI_IDs_withIFe.append(each_secFI)
        print("\n\nTotal secondary FIs (cleaned): ", len(secondaryFI_IDs_withIFe), "are: ")
        secondaryFI_IDs_withIFe.sort()
        updated_secondaryFI_IDs_withIFe = list(secondaryFI_IDs_withIFe for secondaryFI_IDs_withIFe, _ in itertools.groupby(secondaryFI_IDs_withIFe))
        print(tabulate(updated_secondaryFI_IDs_withIFe, headers = ["Interacting_source_feature", "Interacting_destination_feature", "Intermediate_features"], tablefmt = 'grid'))

def main():
    msgID_name_dict = {}
    featurePkgID_list = []
    featurePkgID_name_dict = {}
    featureID_nodeIDset_dict = {}
    featureID_nodeIDnamedict_dict = {}
    featureID_edgeIDlist_dict = {}
    featureID_edgeIDnamedict_dict = {}
    msgID_msgSort_dict = {}
    feID_relMsgIDslist_dict = {}
    feID_compID_dict = {}
    relevantComponentID_set = set() #this set will include both safety and security relevant components
    
    iterator_type = 2 #configure the search to be performed in the appropriate input file (for our case study, it was input xmi file 2)
    
    print("\nGetting security features...")
    GSeF = GetSecurityFeatures(secFeaturePkgID_list)
    secFeaturePkgID_name_dict = GSeF.get_security_feature_name(iterator_type) #search will be performed in the specified input xmi file
    #print("\nsecurity_feature_list: ", secFeaturePkgID_list, "\n\nse_feature_pkg_dict: ", secFeaturePkgID_name_dict)
    
    print("\n\nGetting safety features...")
    GSaF = GetSafetyFeatures(ecu_sa_main_pkg_path)
    safFeature_pkg_list, safFeaturePkgID_name_dict = GSaF.get_safety_feature(iterator_type) #search will be performed in the specified input xmi file
    #print("\nsafety_feature_list: ", safFeature_pkg_list, "\n\nsafFeaturePkgID_name_dict: ", safFeaturePkgID_name_dict)
    
    secComponentID_set = get_values_from_dict(secFeID_compID_dict)
    safComponentID_set = get_values_from_dict(safFeID_compID_dict)
    secsafComponentID_set = get_commonelementIDsset(secComponentID_set, safComponentID_set) #Getting components that are both safety and security relevant
    if len(secsafComponentID_set) != 0:
        secComponentID_set = get_uniqueelementIDsset(secComponentID_set, secsafComponentID_set)
        safComponentID_set = get_uniqueelementIDsset(safComponentID_set, secsafComponentID_set)
    print("\nlen(safComponentID_set): ", len(safComponentID_set), " len(secComponentID_set): ", len(secComponentID_set), " len(secsafComponentID_set): ", len(secsafComponentID_set))    
    
    print("\nAnalyzing sequence diagrams of security features to get messages and lifelines")
    GSecSDA = GetBehavioralElements(secFeaturePkgID_list, secFeaturePkgID_name_dict, secComponentID_set, secFeID_compID_dict)
    secFeID_nodeIDset_dict, secFeID_nodeIDnamedict_dict, secFeID_edgeIDlist_dict, secFeID_edgeIDnamedict_dict, secMsgID_name_dict, secMsgID_msgSort_dict, secFeID_relMsgIDslist_dict, secFeID_msgIDnamedict_dict = GSecSDA.extract_lifelines_and_messages()
    
    print("\nAnalyzing sequence diagrams of safety features to get messages and lifelines")
    GSafSDA = GetBehavioralElements(safFeature_pkg_list, safFeaturePkgID_name_dict, safComponentID_set, safFeID_compID_dict)
    safFeID_nodeIDset_dict, safFeID_nodeIDnamedict_dict, safFeID_edgeIDlist_dict, safFeID_edgeIDnamedict_dict, safMsgID_name_dict, safMsgID_msgSort_dict, safFeID_relMsgIDslist_dict, safFeID_msgIDnamedict_dict = GSafSDA.extract_lifelines_and_messages()
    
    msgID_name_dict.update(secMsgID_name_dict)
    msgID_name_dict.update(safMsgID_name_dict)

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
    msgID_msgSort_dict.update(safMsgID_msgSort_dict)
    msgID_msgSort_dict.update(secMsgID_msgSort_dict)
    feID_relMsgIDslist_dict.update(safFeID_relMsgIDslist_dict)
    feID_relMsgIDslist_dict.update(secFeID_relMsgIDslist_dict)
    feID_compID_dict.update(secFeID_compID_dict)
    feID_compID_dict.update(safFeID_compID_dict)
    relevantComponentID_set.update(secComponentID_set)
    relevantComponentID_set.update(safComponentID_set)
    
    depth = 2 #cutoff for edge path search
    
    print("\nDebug! Performing interaction analysis of security and safety features")
    GINA = InteractionAnalysis(featurePkgID_list, featurePkgID_name_dict, secComponentID_set, safComponentID_set, secsafComponentID_set, featureID_nodeIDset_dict, featureID_nodeIDnamedict_dict, featureID_edgeIDlist_dict, featureID_edgeIDnamedict_dict, secFeID_compID_dict, safFeID_compID_dict, msgID_name_dict, secComponentID_name_dict, safComponentID_name_dict, msgID_msgSort_dict, feID_relMsgIDslist_dict, feID_compID_dict, secFeaturePkgID_list, safFeature_pkg_list, relevantComponentID_set)
    GINA.get_interaction_list(depth)
    
    stop = timeit.default_timer()
    print('Time: ', stop - start)

if __name__ == "__main__":
    main()