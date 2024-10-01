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
from lxml import etree
import itertools
from itertools import product
from tabulate import tabulate

######################################Configurable inputs#####################################
#Path to input files
dirname = os.path.dirname(__file__)
#Relative path of input xml files to be parsed
file_path_inputfile1 = os.path.join(dirname, '..', 'data', 'inputfile1.xml')
file_path_inputfile2 = os.path.join(dirname, '..', 'data', 'inputfile2.xml')
file_path_inputfile3 = os.path.join(dirname, '..', 'data', 'inputfile3.xml')
file_path_inputfile4 = os.path.join(dirname, '..', 'data', 'inputfile4.xml')
file_path_inputfile5 = os.path.join(dirname, '..', 'data', 'inputfile5.xml')
file_path_inputfile6 = os.path.join(dirname, '..', 'data', 'inputfile6.xml')
file_path_inputfile7 = os.path.join(dirname, '..', 'data', 'inputfile7.xml')

#Configurable inputs for security features
security_feature_pkg_list = []  #Specify XMI IDs of each security feature

#Configurable inputs for safety features
ecu_safety_main_pkg_path = ".//packagedElement[@xmi:id='{}'][@xmi:type='uml:Package']/packagedElement[@xmi:type='uml:Package']".format('') #Specify XMI ID of the main package inside quotes of .format(''); this main package contains other packages, of which each package represents a specific safety feature

#output files with date and time stamp
timestr = time.strftime("%Y%m%d-%H%M%S")
interaction_sequences_txt = "interaction_sequences_output" + timestr + ".txt"
output_nx_name = "nx_graph" + timestr + ".png"

#path to store output files
output_file_nxdraw = os.path.join(dirname, '..', 'build', output_nx_name)
interaction_sequences = os.path.join(dirname, '..', 'build', interaction_sequences_txt)

#Parsing input xml using etree parser of lxml
tree_inputfile1 = etree.parse(file_path_inputfile1) #Parse input file 1
root_inputfile1 = tree_inputfile1.getroot() #Get the root element of the xmi

tree_inputfile2 = etree.parse(file_path_inputfile2) #Parse input file 2
root_inputfile2 = tree_inputfile2.getroot() #Get the root element of the xmi

tree_inputfile3 = etree.parse(file_path_inputfile3)
root_inputfile3 = tree_inputfile3.getroot()

tree_inputfile4 = etree.parse(file_path_inputfile4)
root_inputfile4 = tree_inputfile4.getroot()

tree_inputfile5 = etree.parse(file_path_inputfile5)
root_inputfile5 = tree_inputfile5.getroot()

tree_inputfile6 = etree.parse(file_path_inputfile6)
root_inputfile6 = tree_inputfile6.getroot()

tree_inputfile7 = etree.parse(file_path_inputfile7)
root_inputfile7 = tree_inputfile7.getroot()

#Define namespace
ns = {
    'uml':'http://schema.omg.org/spec/UML/2.1',
    'xmi':'http://schema.omg.org/spec/XMI/2.1',
    'SysML':'http://www.omg.org/spec/SysML/20120322/SysML',
    'sysml':'http://www.omg.org/spec/SysML/20080501/SysML-profile'
    }
##############################################################################################

class Parent:
    def __init__(self):
        pass
    
    def get_iterator(self, path, var_select_etree):
        "get iterator based on input i.e. 1 for input file 1, 2 for input file 2 or 3 for input file 3"
        if var_select_etree == 1:
            element_object = root_inputfile1.iterfind(path=path, namespaces=ns) #Iterator from parsed input file 1
        elif var_select_etree == 2:
            element_object = root_inputfile2.iterfind(path=path, namespaces=ns) #Iterator from parsed input file 2
        elif var_select_etree == 3:
            element_object = root_inputfile3.iterfind(path=path, namespaces=ns) #Iterator from parsed input file 3
        elif var_select_etree == 4:
            element_object = root_inputfile4.iterfind(path=path, namespaces=ns) #Iterator from parsed input file 4
        elif var_select_etree == 5:
            element_object = root_inputfile5.iterfind(path=path, namespaces=ns) #Iterator from parsed input file 5
        elif var_select_etree == 6:
            element_object = root_inputfile6.iterfind(path=path, namespaces=ns) #Iterator from parsed input file 6
        elif var_select_etree == 7:
            element_object = root_inputfile7.iterfind(path=path, namespaces=ns) #Iterator from parsed input file 7
        else:
            print("Invalid iterator type entered!")
            #assert "Invalid selection of parsed lxml etree"
        return element_object
    
    def get_iterator_attributes(self, element):
        "Get id, name and type attributes from the iteratable element/object"
        id = element.get('{http://schema.omg.org/spec/XMI/2.1}id')
        name = element.get('name')
        type = element.get('{http://schema.omg.org/spec/XMI/2.1}type')
        return id, name, type
    
    def get_type_by_id(self, element_id, iterator_type):
        "Get xmi_type corresponding to xmi_id by searching for the element of this ID in a particular input file"
        type = None
        name = None
        id = None
        classifier_id = None
        path_search_by_id = ".//packagedElement[@xmi:id='{}']".format(element_id)
        id_iterator = self.get_iterator(path_search_by_id, iterator_type)
        path_search_by_idref = ".//element[@xmi:idref='{}']".format(element_id)
        idref_iterator = self.get_iterator(path_search_by_idref, iterator_type)
        for element in id_iterator:
            id, name, type = self.get_iterator_attributes(element)
        if id == None: #if a packaged element having this ID wasn't found
            for element in idref_iterator: #iterate into elements with id as idref
                id, name, type = self.get_iterator_attributes(element)
        if type == "uml:InstanceSpecification": #if the element is an instance of a class or component, then get the id of the class or component.
            classifier_id = element.get('classifier')
        return name, type, classifier_id
    
    def supplier_typeNone_handler(self, element):
        "handler to find element if supplier_type is None/not found"
        iterator_type = None
        stereotype = None
        #Configure the xml input files in which the search is to be performed
        for i,v in enumerate([3,4,5,6,7]): #[3,4,5,6,7] refers to the xml input files in which the search will be performed.
            name, type, c_id = self.get_type_by_id(element, v) #c_id refers to the classifier id corresponding to the input element_id; ignore c_id in this case
            #print("Debug!...element_id: ", element, " name: ", name, " type: ", type)
            if type != None and element != None:
                #print("\nDebug!...supplier_id: ", element, " name: ", name, " type: ", type, " iterator_type: ", v)
                if type == "uml:Component":
                    stereotype = self.get_stereotype_by_path_andID(element, v)
                iterator_type = v
                break
        return name, type, id, stereotype, iterator_type
    
    def get_stereotype_path(self, element):
        "Get the stereotype path by passing the xmi element ID"
        #Configure component_stereotype_path and composition_stereotype_path
        component_stereotype_path = ".//thecustomprofile:COMPONENT__Software_Component[@base_Component='{}']".format(element)
        composition_stereotype_path = ".//thecustomprofile:COMPONENT__Software_Composition[@base_Component='{}']".format(element)
        return component_stereotype_path, composition_stereotype_path
    
    def get_stereotype_from_stereotype_iterator(self, iterator):
        "get the stereotype by iterating through the iterator"
        stereotype = None
        for element in iterator:
            stereotype = element.get('__EAStereoName')
        return stereotype
    
    def get_stereotype_by_path_andID(self, element_id, iterator_type):
        "Get stereotype (__EAStereoName) corresponding to xmi_id and search_path for the provided iterator, i.e. the input file in which the search is to be performed"
        stereotype = None
        component_stereotype_path, composition_stereotype_path = self.get_stereotype_path(element_id)
        component_stereotype_iterator = self.get_iterator(component_stereotype_path, iterator_type)
        stereotype = self.get_stereotype_from_stereotype_iterator(component_stereotype_iterator)
        if stereotype == None:
            composition_stereotype_iterator = self.get_iterator(composition_stereotype_path, iterator_type)
            stereotype = self.get_stereotype_from_stereotype_iterator(composition_stereotype_iterator) 
        return stereotype
    
    def get_classifier_details_from_itsID(self, classifier_id, iterator_type):
        "Search classifier details using its ID to obtain its name, type, and stereotype"
        classifier_stereotype = None
        classifier_name, classifier_type, id = self.get_type_by_id(classifier_id, iterator_type) #the output "id" here refers to a dummy variable (classifier id) and this variable will not be used in the if condition below
        if classifier_type == "uml:Component":
            classifier_stereotype = self.get_stereotype_by_path_andID(classifier_id, iterator_type)
        return classifier_name, classifier_type, classifier_stereotype
    
    def get_activity_list(self, element, iterator_type):
        "Get activity(ies) for each feature package ID"
        activity_search_path = ".//packagedElement[@xmi:id='{}'][@xmi:type='uml:Package']/.//*[@xmi:type='uml:Activity']".format(element)
        action_search_path = ".//packagedElement[@xmi:id='{}'][@xmi:type='uml:Package']/.//*[@xmi:type='uml:Action']".format(element)
        activity_iterator = self.get_iterator(activity_search_path, iterator_type)
        action_iterator = self.get_iterator(action_search_path, iterator_type)
        activity_id_list = []
        activity_dict = {}
        for object in activity_iterator:
            activity_id, activity_name, activity_type = self.get_iterator_attributes(object)
            activity_id_list.append(activity_id)
            activity_dict.update({activity_id:activity_name})
        for object in action_iterator:
            action_id, action_name, action_type = self.get_iterator_attributes(object)
            activity_id_list.append(action_id)
            activity_dict.update({action_id:action_name})
        return activity_id_list, activity_dict
    
    def get_supplierIDs_per_activity(self, activity, iterator_type):
        "Get all instance specification of allocated components for each activity; info: no repetition of components expected here"
        abstraction_search_path = ".//packagedElement[@xmi:type='uml:Dependency'][@client='{}']".format(activity)
        realization_search_path = ".//packagedElement[@xmi:type='uml:Realization'][@client='{}']".format(activity)
        abstraction_iterator = self.get_iterator(abstraction_search_path, iterator_type)
        realization_iterator= self.get_iterator(realization_search_path, iterator_type)
        abstraction_supplier_ids_list = []
        for element in abstraction_iterator:
            abstraction_supplier_id = element.get('supplier')
            abstraction_supplier_ids_list.append(abstraction_supplier_id)
        for element in realization_iterator:
            abstraction_supplier_id = element.get('supplier')
            abstraction_supplier_ids_list.append(abstraction_supplier_id)
        return abstraction_supplier_ids_list
    
    def get_supplierIDs_set_per_feature(self, feature_id, feature_id_name_dict, iterator_type):
        "Get a set of supplier IDs for a feature"
        activity_list = []
        feature_supplierIDs_set = set()
        featureID_activityID_dict = {}
        activity_id_list, activity_dict = self.get_activity_list(feature_id, iterator_type) #get all activities for a feature
        featureID_activityID_dict.update({feature_id:activity_id_list})
        activity_supplierID_dict = {} #{activity_id:[list of supplier IDs]} can be used later for behavioral analysis
        activity_list = [value for value in activity_dict.values()]
        #print("Debug! Feature: ", feature_id_name_dict[feature_id], " len(activity_id_list): ", len(activity_id_list), " activities: ", activity_list)
        for list_element in activity_id_list: #for each activity
            activity_supplierIDs_list = self.get_supplierIDs_per_activity(list_element, iterator_type) #get supplier_ids_list for each activity
            activity_supplierID_dict.update({list_element:activity_supplierIDs_list})
            feature_supplierIDs_set.update(activity_supplierIDs_list) #append the obtained supplier_ids_list to a supplier_ids_set
        #print("\nfeature: ", feature_id, " feature_name: ", feature_id_name_dict[feature_id], " feature_activity_dict: ", activity_dict, " activity_supplierID_dict", activity_supplierID_dict)
        return set(activity_id_list), feature_supplierIDs_set, activity_supplierID_dict, activity_dict, featureID_activityID_dict    
    
    def get_activity_component_mapping(self, activityID_supplierID_dict, supplierID_componentID_dict):
        "Input 1 {activityID:[supplier ID1, supplier ID2,..]}  Input 2 {supplierID1:componentID1, supplierID2:componentID2,..} Expected output {activityID:[componentID1, componentID2,..]}"
        QD = QueryDataStruct()
        activityID_componentsID_dict = {}
        for k,v in activityID_supplierID_dict.items():
            componentsID_peractivity_list = []
            for j,l in enumerate(v):
                if l in supplierID_componentID_dict.keys():
                    value = QD.query_dict_by_key(supplierID_componentID_dict, l)
                    componentsID_peractivity_list.append(value)
                else:
                    continue
            if len(componentsID_peractivity_list) != 0:
                activityID_componentsID_dict.update({k:componentsID_peractivity_list})
        return activityID_componentsID_dict
    
    def get_component_from_interfaceID(self, interface_id, iterator_type, pI_rI_selection_flag):
        "Get the component which has the given provided or required interface ID; the function returns pI (provided interface) when flag is 0 and rI (required interface) when flag is 1"
        if pI_rI_selection_flag == 0: #select provided interface
            search_path = ".//packagedElement[@xmi:type='uml:Component']/provided[@xmi:id = '{}']/..".format(interface_id)
        elif pI_rI_selection_flag == 1: #select required interface
            search_path = ".//packagedElement[@xmi:type='uml:Component']/required[@xmi:id = '{}']/..".format(interface_id)
        else:
            print("Invalid flag!")
        iterator = self.get_iterator(search_path, iterator_type) #search in the specified input file
        component_id = None
        component_name = None
        component_type = None
        for element in iterator:
            component_id, component_name, component_type = self.get_iterator_attributes(element)
        return component_id, component_name, component_type
    
    def get_supplier_structEleIDs_set(self, supplier_IDs_set):
        "Get sructural element IDs set (e.g. set of components, compositions, class etc.) from the set of supplier IDs; this function may need to be modified based on the modeling sytle used for the software architecture model"
        feature_struct_element_ID_set = set() #set of components that corresponds to set of input supplier IDs (instance specification, component,...)
        component_set = set()
        componentID_name_dict = {}
        componentID_type_dict = {}
        
        supplierID_type_dict = {} #dict {suplier id:type}
        classifierID_type_dict = {} #dict {component:type} of components traced by their corresponding instance specification
        classifierID_name_dict = {}
        supplierID_to_classifierID_dict = {} #dict {supplier ID: classifier ID} of key as supplier ID (here instance specification) and its corresponding component as value
        non_classifierID_type_dict = {} #dict of components not traced by their corresponding instance specification
        non_classifierID_name_dict = {}
        requirementID_type_dict = {} #ID {requirement:type} will be derived from SW requirements package
        requirementID_name_dict = {} #dict {re_ID:req_name}
        unknown_non_classifierID_type_dict = {} #dict {supplier_id:its_type}, collect suppliers whos type could not found in the input xmi files
        classifierID_stereotype_dict = {}
        non_classifierID_stereotype_dict = {}
        component_ID_stereotype_dict = {}
        supplierID_componentID_dict = {}
        supplier_stereotype = None
        for element in supplier_IDs_set:
            supplier_name, supplier_type, classifier_id = self.get_type_by_id(element, 2)#check type of supplier id e.g. instance specification, class, artifact, activity, etc.
            supplier_stereotype = self.get_stereotype_by_path_andID(element, 2)
            supplierID_type_dict.update({element:supplier_type})
            if supplier_type == "uml:InstanceSpecification":
                classifier_name, classifier_type, classifier_stereotype = self.get_classifier_details_from_itsID(classifier_id, 3)
                classifierID_type_dict.update({classifier_id:classifier_type})
                classifierID_name_dict.update({classifier_id:classifier_name})
                classifierID_stereotype_dict.update({classifier_id:classifier_stereotype})
                supplierID_to_classifierID_dict.update({element:classifier_id})
                supplierID_componentID_dict.update({element:classifier_id})
            elif supplier_type == "uml:Class": #store in requirementID_type_dict if all such elements are found to be SW requirements
                requirementID_type_dict.update({element:supplier_type})
                requirementID_name_dict.update({element:supplier_name})
            elif supplier_type == "uml:Component":
                non_classifierID_type_dict.update({element:supplier_type})
                non_classifierID_name_dict.update({element:supplier_name})
                non_classifierID_stereotype_dict.update({element:supplier_stereotype})
                supplierID_componentID_dict.update({element:element})
            elif supplier_type == "uml:Activity": #dependency between activities are ignored when finding components allocated to each activity
                pass
            elif supplier_type == "uml:Artifact":
                pass
            elif supplier_type == "uml:Constraint":
                pass
            elif supplier_type == None:
                name, type, id, element_stereotype, iterator_type = self.supplier_typeNone_handler(element)
                if type == "uml:Class" and iterator_type == 7:
                    requirementID_type_dict.update({element:type})
                    requirementID_name_dict.update({element:name})
                elif type == "uml:Component":
                    non_classifierID_type_dict.update({element:type})
                    non_classifierID_name_dict.update({element:name})
                    non_classifierID_stereotype_dict.update({element:element_stereotype})
                    supplierID_componentID_dict.update({element:element})
                elif type == "uml:ProvidedInterface":
                    pI_flag = 0 #return component that corresponds to pI interface
                    pIcomponent_id, pIcomponent_name, pIcomponent_type = self.get_component_from_interfaceID(element, 3, pI_flag) #get component id, name, stereotype
                    pIcomponent_stereotype = self.get_stereotype_by_path_andID(pIcomponent_id, 3)
                    non_classifierID_type_dict.update({pIcomponent_id:pIcomponent_type})
                    non_classifierID_name_dict.update({pIcomponent_id:pIcomponent_name})
                    non_classifierID_stereotype_dict.update({pIcomponent_id:pIcomponent_stereotype})
                    supplierID_componentID_dict.update({element:element})
                else:
                    unknown_non_classifierID_type_dict.update({element:type})
        componentID_type_dict = {**classifierID_type_dict, **non_classifierID_type_dict}
        component_ID_stereotype_dict = {**classifierID_stereotype_dict, **non_classifierID_stereotype_dict}
        component_set = {key for key in componentID_type_dict.keys()}
        componentID_name_dict = {**classifierID_name_dict, **non_classifierID_name_dict}
        return component_set, componentID_name_dict, componentID_type_dict, supplierID_type_dict, classifierID_type_dict, supplierID_to_classifierID_dict, non_classifierID_type_dict, unknown_non_classifierID_type_dict, requirementID_type_dict, component_ID_stereotype_dict, supplierID_componentID_dict
    
    def get_listnames_from_listIDs(self, elementIDs_list, elementID_name_dict):
        "Get list of names from a list of their IDs by querying data struct"
        value = None
        element_names_list = []
        for element in elementIDs_list:
            value = elementID_name_dict[element]
            element_names_list.append(value)
        return element_names_list
    
    def get_feature_components(self, feature_list, feature_id_name_dict, iterator_type):
        "Get component_list, component_dict and feature_component_dict"
        all_componentID_set = set()
        activityID_set = set()
        all_activityID_set = set()
        all_componentID_name_dict = {}
        all_componentID_stereotype_dict = {}
        feature_componentID_dict = {} #dict = {feature_id:{set of component_IDs}}
        all_supplierID_componentID_dict = {}
        all_activityID_name_dict = {}
        all_activity_supplierID_dict = {}
        all_featureID_activityID_dict = {}
        for element in feature_list: #for each feature
            activityID_set, feature_supplier_ids_set, activity_supplierID_dict, activity_dict, featureID_activityID_dict = self.get_supplierIDs_set_per_feature(element, feature_id_name_dict, iterator_type) #Get supplier set per feature
            componentID_set, componentID_name_dict, componentID_type_dict, supplierID_type_dict, classifierID_type_dict, supplierID_to_classifierID_dict, non_classifierID_type_dict, unknown_non_classifierID_type_dict, requirementID_type_dict, componentID_stereotype_dict, supplierID_componentID_dict = self.get_supplier_structEleIDs_set(feature_supplier_ids_set)
            all_activityID_set.update(activityID_set)
            all_featureID_activityID_dict.update(featureID_activityID_dict)
            all_activity_supplierID_dict.update(activity_supplierID_dict)
            all_activityID_name_dict.update(activity_dict)
            all_supplierID_componentID_dict.update(supplierID_componentID_dict)
            all_componentID_set.update(componentID_set)
            all_componentID_name_dict.update(componentID_name_dict)
            all_componentID_stereotype_dict.update(componentID_stereotype_dict)
            componentID_list = list(componentID_set)
            feature_componentID_dict.update({element:componentID_list})
            component_list = [value for value in componentID_name_dict.values()]
        return feature_componentID_dict, all_componentID_set, all_componentID_name_dict, all_componentID_stereotype_dict, all_supplierID_componentID_dict, all_activityID_name_dict, all_activity_supplierID_dict, all_featureID_activityID_dict          
    
    def redirect_txt_output(self, output_file_path, text_to_write):
        "Dump print output in a text file in append mode"
        with open(output_file_path, "a") as external_file: #write/append to file
            received_text = text_to_write
            print(received_text, file=external_file)
            external_file.close()

class QueryDataStruct(Parent):
    def __init__(self):
        super().__init__()
    
    def query_dict_by_key(self, dict_to_be_querried, key_to_query):
        "query a dict by key"
        value = dict_to_be_querried[key_to_query]
        return value
    
    def query_dict_by_wlistvalue(self, dict_to_be_querried, value_to_query):
        "query a dict by value; each value corresponding to a key is a list of items"
        key_list = []
        for k,v in dict_to_be_querried.items():
            for j,l in enumerate(v):
                if l == value_to_query:
                    key_list.append(k)
                    break
        return key_list
    
    def query_dict_by_value(self, dict_to_be_querried, value_to_query):
        "query a dict (with a key and a value pair) by value"
        key = [k for k,v in dict_to_be_querried.items() if v == value_to_query]
        return key
    
    def query_lists_for_commonelement(self, list1, list2, list1ID_name_dict):
        "get common elements of 2 lists using Python's set intersection"
        common_elementID_list = list(set(list1).intersection(list2))
        common_elementname_list = []
        common_elementname_list = self.get_listnames_from_listIDs(common_elementID_list, list1ID_name_dict) #getting names for debugging
        return common_elementID_list, common_elementname_list
    
    def query_lists_for_uniqueelement(self, list1, list2, list1ID_name_dict):
        "get unique elements present in 2 lists using Python's symmetric difference"
        unique_elementID_list = list(set(list1).symmetric_difference(set(list2)))
        unique_elementname_list = []
        unique_elementname_list = self.get_listnames_from_listIDs(unique_elementID_list, list1ID_name_dict) #getting names for debugging
        return unique_elementID_list, unique_elementname_list
    
    def get_listoflistnames_from_listoflistIDs(self, listIDs_of_list, elementID_name_dict):
        "For a list of list of IDs, create a list of list of names"
        names_list_of_list = []
        for element in listIDs_of_list:
            element_name_list = self.get_listnames_from_listIDs(element, elementID_name_dict)
            if element_name_list not in names_list_of_list:
                names_list_of_list.append(element_name_list)
        return names_list_of_list
    
    def get_itertoolsproductoflists(self, list1, list2):
        "For lists, i.e. list1 and list2, get the product of list1 and list2, and the product of list2 and list1 and combine (summation) the output of both products obtained"
        productfrom1to2_list = list(itertools.product(list1, list2))
        return productfrom1to2_list

class GetSecurityFeatures(Parent):
    "Get a list of all security features as packages"
    def __init__(self, security_feature_list):
        super().__init__()
        self.security_feature_list = security_feature_list
    
    def get_security_feature_name(self, iterator_type):
        "For each element in the list, find the name and store it in a dict with each key as a feature id and each name as a value"
        feature_id_name_dict = {}
        for element in self.security_feature_list:
            path = ".//packagedElement[@xmi:id = '{}'][@xmi:type = 'uml:Package']".format(element)
            path_iterator = self.get_iterator(path, iterator_type)
            for object in path_iterator:
                id, name, type = self.get_iterator_attributes(object)
                feature_id_name_dict.update({element:name})
        return feature_id_name_dict

class GetSafetyFeatures(Parent):
    "Get a list of all safety features as packages"
    def __init__(self, path):
        super().__init__()
        self.path = path
    
    def get_safety_feature(self, iterator_type):
        "get all safety features from the main safety package"
        feature_id_name_dict = {}
        safety_feature_list = []
        sa_feature_path_iterator = self.get_iterator(self.path, iterator_type)
        for element in sa_feature_path_iterator:
            id, name, type = self.get_iterator_attributes(element)
            safety_feature_list.append(id)
            feature_id_name_dict.update({id:name})
        return safety_feature_list, feature_id_name_dict

class GetSaSeCommonSWC(QueryDataStruct):
    "Get software components that are used to realize both safety and security features"
    def __init__(self, se_set, sa_set, componentID_name_dict):
        super().__init__()
        self.se_set = se_set
        self.sa_set = sa_set
        self.componentID_name_dict = componentID_name_dict
    
    def get_features_from_componentID(self, component_ID, featureID_componentsID_dict):
        "For a provided component ID and a mapping of each feature to its components, get a list of feature IDs that the component realizes."
        featureIDs_list = self.query_dict_by_wlistvalue(featureID_componentsID_dict, component_ID)
        return featureIDs_list
    
    def get_common_set_elements(self):
        common_elements_set = self.se_set.intersection(self.sa_set)
        common_element_name_dict = {}
        for element in common_elements_set:
            element_name = self.componentID_name_dict[element]
            common_element_name_dict.update({element:element_name})
        print("\n\ncommon_SWC_set: ", common_elements_set, ", dict: ", common_element_name_dict)
        return common_elements_set, common_element_name_dict

class SaSeCommonSWCAnalysis(QueryDataStruct):
    "For each common sa_se_SWcomponent, get their corresponding sa_se_features, and get the safety and security activities corresponding to each feature"
    def __init__(self, componentID_name_dict, se_featureID_name_dict, sa_featureID_name_dict, se_featureID_componentsID_dict, sa_featureID_componentsID_dict, se_activityID_componentsID_dict, sa_activityID_componentsID_dict, se_featureID_activityID_dict, sa_featureID_activityID_dict, se_activity_dict, sa_activity_dict):
        super().__init__()
        self.componentID_name_dict = componentID_name_dict
        self.se_featureID_name_dict = se_featureID_name_dict
        self.sa_featureID_name_dict = sa_featureID_name_dict
        self.se_featureID_componentsID_dict = se_featureID_componentsID_dict
        self.sa_featureID_componentsID_dict = sa_featureID_componentsID_dict
        self.se_activityID_componentsID_dict = se_activityID_componentsID_dict
        self.sa_activityID_componentsID_dict = sa_activityID_componentsID_dict
        self.se_featureID_activityID_dict = se_featureID_activityID_dict
        self.sa_featureID_activityID_dict = sa_featureID_activityID_dict
        self.se_activity_dict = se_activity_dict
        self.sa_activity_dict = sa_activity_dict
    
    def get_features_from_componentID(self, component_ID, featureID_componentsID_dict):
        "For a provided component ID and a mapping of each feature to its components, get a list of feature IDs that the component realizes."
        featureIDs_list = self.query_dict_by_wlistvalue(featureID_componentsID_dict, component_ID)
        return featureIDs_list
    
    def get_CSWCactivity(self, element, activityID_componentsID_dict):
        "For a given component, get its allocated activities by querying the dict {activityID:[componentID1, componentID2]}"
        activityID_list = self.query_dict_by_wlistvalue(activityID_componentsID_dict, element)
        return activityID_list
    
    def get_CSWCactivity_per_feature(self, featureID_list, featureID_activityIDlist_dict, CSWCactivityID_list, activityID_name_dict, featureID_name_dict, featureID):
        "Get activity allocated to a software component that is associated to a given feature in a given feature_list"
        Pa = Parent()
        featureID_CSWCactivityIDslist_dict = {}
        featurename_CSWCactivitynameslist_dict = {} #for debugging
        feCSWCactivityID_list = []
        if featureID in featureID_list:
            element_name = self.query_dict_by_key(featureID_name_dict, featureID)
            activitylist = self.query_dict_by_key(featureID_activityIDlist_dict, featureID)
            for activity in activitylist:
                if activity in CSWCactivityID_list:
                    feCSWCactivityID_list.append(activity)
            feCSWCactivityname_list = Pa.get_listnames_from_listIDs(feCSWCactivityID_list, activityID_name_dict) #for debugging
            featureID_CSWCactivityIDslist_dict.update({featureID:feCSWCactivityID_list})
            featurename_CSWCactivitynameslist_dict.update({element_name:feCSWCactivityname_list})
        else:
            for element in featureID_list:
                feCSWCactivityID_list = []
                element_name = self.query_dict_by_key(featureID_name_dict, element)
                activitylist = self.query_dict_by_key(featureID_activityIDlist_dict, element)
                for activity in activitylist:
                    if activity in CSWCactivityID_list:
                        feCSWCactivityID_list.append(activity)
                feCSWCactivityname_list = Pa.get_listnames_from_listIDs(feCSWCactivityID_list, activityID_name_dict) #for debugging
                featureID_CSWCactivityIDslist_dict.update({element:feCSWCactivityID_list})
                featurename_CSWCactivitynameslist_dict.update({element_name:feCSWCactivityname_list})
                #print("Debug! ", element_name, " its_activities", featurename_CSWCactivitynameslist_dict)  #for debugging
        return featureID_CSWCactivityIDslist_dict, featurename_CSWCactivitynameslist_dict
    
    def getSWCfeature_withactivity(self, common_elements_list, sase_flag, featureID):
        "For each common software component, get features that the component realizes and the activities associated with each feature"
        for element in common_elements_list:
            element_name = self.query_dict_by_key(self.componentID_name_dict, element) #for debugging
            if sase_flag == "se":
                se_featureIDs_list = self.get_features_from_componentID(element, self.se_featureID_componentsID_dict)
                se_CSWCactivityID_list = self.get_CSWCactivity(element, self.se_activityID_componentsID_dict)
                featureID_CSWCactivityIDslist_dict, featurename_CSWCactivitynameslist_dict = self.get_CSWCactivity_per_feature(se_featureIDs_list, self.se_featureID_activityID_dict, se_CSWCactivityID_list, self.se_activity_dict, self.se_featureID_name_dict, featureID)
            elif sase_flag == "sa":
                sa_featureIDs_list = self.get_features_from_componentID(element, self.sa_featureID_componentsID_dict)
                sa_CSWCactivityID_list = self.get_CSWCactivity(element, self.sa_activityID_componentsID_dict)
                featureID_CSWCactivityIDslist_dict, featurename_CSWCactivitynameslist_dict = self.get_CSWCactivity_per_feature(sa_featureIDs_list, self.sa_featureID_activityID_dict, sa_CSWCactivityID_list, self.sa_activity_dict, self.sa_featureID_name_dict, featureID)
            else:
                print("\nWarning! invalid flag!!!")
        featurename_CSWCactivitynameslist_str = str(featurename_CSWCactivitynameslist_dict)
        return featurename_CSWCactivitynameslist_dict, featurename_CSWCactivitynameslist_str

class FeatureSDMultiDiGraph():
    def __init__(self, graph, graph_title, node_set, edge_list, node_label_dict, edge_label_dict):
        self.graph = graph
        self.graph_title = graph_title
        self.node_set = node_set
        self.edge_list = edge_list
        self.node_label_dict = node_label_dict
        self.edge_label_dict = edge_label_dict
    
    def store_text_output(self,output_file_path, text):
        "Dump print output in a text file in append mode"
        with open(output_file_path, "a") as external_file: #write/append to file
            received_text = text
            print(received_text, file=external_file)
            external_file.close()    
    
    def create_nx_graph(self):
        "Create networkx graph using nodes and edges and their labels"
        self.graph.add_nodes_from(self.node_set)
        self.graph.add_edges_from(self.edge_list)        
        pos = nx.circular_layout(self.graph)
        plt.figure(figsize=(50,50))
        nx.draw(self.graph, pos, labels = self.node_label_dict, with_labels = True)
        plt.title(self.graph_title)
        plt.savefig(output_file_nxdraw)
        #plt.show()
    
    def collect_Inodes_for_a_path(self, path):
        "for a given path that contains sub-paths, collect all intermediate nodes/lifelines/components"
        Inodes_set = set()
        if len(path) > 1: #check intermediate nodes if path_len > 1, i.e. if there are any intermediate nodes present in the path
            for index, subpath in enumerate(path):
                if index == 0:
                    Inode2 = subpath[-2]
                    Inodes_set.add(Inode2)
                elif index != 0 and index != len(path)-1:
                    Inode1 = subpath[-2]
                    Inode2 = subpath[-3]
                    Inodes_set.add(Inode1)
                    Inodes_set.add(Inode2)
                elif index == len(path)-1:
                    Inode1 = subpath[-3]
                    Inodes_set.add(Inode1)
                else:
                    print("Warning! no condition met for index: ", index, " for subpath: ", subpath, " in the path: ", path, "!")
        return list(Inodes_set)
    
    def check_Inodes_relevance(self, Inodes_list, firstandlastnode_list, relevant_lifelines_list):
        "check if any node in the list of intermediate nodes given as inputs (for a path) is either safety or security relevant; if relevant, set flag to 0 i.e. it can be a secondary interaction path"
        Inode_rel_flag = 1 #consider as a primary interaction path unless this flag is set to 0
        relvComponentID_list = list(set(firstandlastnode_list).symmetric_difference(relevant_lifelines_list))
        for element in Inodes_list:
            if element in relvComponentID_list:
                Inode_rel_flag = 0 #a potential secondary interaction path because there exists atleast one intermediate node that is safety or security relevant
                break
        return Inode_rel_flag
    
    def rI_pI_nx_simple_paths(self, src, dst, depth, strng, out_txt_file, msgseqID_name_dict, relevant_lifelines_list):
        var_bool = nx.has_path(self.graph, src, dst)
        var_str = strng + str(var_bool)
        self.store_text_output(out_txt_file, var_str)
        pathAB_list_of_lists = []
        all_path_with_names_list = []
        pathAB_IDs_list = []
        pri_pathAB_IDs_list = []
        pathAB_names_list = []
        current_queryID_list = [src, dst]
        counter = 0
        
        for path in nx.all_simple_edge_paths(self.graph, source = src, target = dst, cutoff=depth):
            counter = counter + 1
            path_with_names_list = []
            
            Inodes_list = self.collect_Inodes_for_a_path(path)
            if len(Inodes_list) != 0: #check safety and security relevance of Inodes of the current path whose path length > 1
                Inode_rel_flag = self.check_Inodes_relevance(Inodes_list, current_queryID_list, relevant_lifelines_list) #flag set to 0 if at least 1 safety or security relevant Inode found; flag is set to 1 if it is a primary interaction path
            else: #path with no intermediate nodes is automatically included as primary path
                Inode_rel_flag = 1 #path considered as primary interaction path
            
            if Inode_rel_flag == 1:
                pri_pathAB_IDs_list.append(path)
            elif Inode_rel_flag == 0:
                pathAB_IDs_list.append(path)
            
            for subpath in path:
                src_name = self.node_label_dict[subpath[0]]
                dst_name = self.node_label_dict[subpath[1]]
                key_name = msgseqID_name_dict[subpath[-1]]
                if key_name is None:
                    key_name = "-"
                subpath_with_names = (src_name,dst_name,key_name)
                path_with_names_list.append(subpath_with_names)
            all_path_with_names_list.append(path_with_names_list)
        return var_bool, pathAB_IDs_list, all_path_with_names_list, counter, pri_pathAB_IDs_list

class SDanalysisOfSeandSaFeatures(Parent):
    "sequence diagram (SD) analysis per feature"
    def __init__(self, security_feature_list, sefeatureID_name_dict, safety_feature_list, safeatureID_name_dict, seSWCid_list, saSWCid_list, saseCSWC_list, se_feature_componentID_dict, sa_feature_componentID_dict, se_activityID_componentsID_dict, sa_activityID_componentsID_dict, se_featureID_activityID_dict, sa_featureID_activityID_dict, se_activity_dict, sa_activity_dict):
        super().__init__()
        self.security_feature_list = security_feature_list
        self.sefeatureID_name_dict = sefeatureID_name_dict
        self.safety_feature_list = safety_feature_list
        self.safeatureID_name_dict = safeatureID_name_dict
        self.seSWCid_list = seSWCid_list
        self.saSWCid_list = saSWCid_list
        self.saseCSWC_list = saseCSWC_list
        self.se_feature_componentID_dict = se_feature_componentID_dict
        self.sa_feature_componentID_dict = sa_feature_componentID_dict
        self.se_activityID_componentsID_dict = se_activityID_componentsID_dict
        self.sa_activityID_componentsID_dict = sa_activityID_componentsID_dict
        self.se_featureID_activityID_dict = se_featureID_activityID_dict
        self.sa_featureID_activityID_dict = sa_featureID_activityID_dict
        self.se_activity_dict = se_activity_dict
        self.sa_activity_dict = sa_activity_dict
    
    def get_lifelines_per_feature(self, lifelineIS_iterator, iterator_type):
        "Get all lifeline objects (components) for all sequence diagrams per feature"
        propertyIS_id = None
        id = None
        name = None
        type = None
        classifier_id = None
        component_name = None
        component_type = None
        classifier_id2 = None
        propertyISids_list = []
        propertyISid_name_dict = {}
        objectlifeline_id_list = []
        objectlifeline_name_list = []
        objectlifelineID_name_dict = {}
        objectlifelineID_type_dict = {}
        objectlifelineID_componentID_dict = {} #{lifelinepropertyIS_id:component_id}; IS refers to instance specification
        for element in lifelineIS_iterator:
            propertyIS_id = element.get('{http://schema.omg.org/spec/XMI/2.1}idref')
            if propertyIS_id != None:
                propertyISids_list.append(propertyIS_id)
                name, type, classifier_id = self.get_type_by_id(propertyIS_id, iterator_type)
                if type == "uml:InstanceSpecification":
                    component_name, component_type, classifier_id2 = self.get_type_by_id(classifier_id, 3)
                    propertyISid_name_dict.update({propertyIS_id:component_name})
                    objectlifeline_id_list.append(classifier_id)
                    objectlifeline_name_list.append(component_name)
                    objectlifelineID_name_dict.update({classifier_id:component_name})
                    objectlifelineID_type_dict.update({classifier_id:component_type})
                    objectlifelineID_componentID_dict.update({propertyIS_id:classifier_id})
                elif type == "uml:Component" or type == "uml:Actor":
                    propertyISid_name_dict.update({propertyIS_id:name})
                    objectlifeline_id_list.append(propertyIS_id)
                    objectlifeline_name_list.append(name)
                    objectlifelineID_name_dict.update({propertyIS_id:name})
                    objectlifelineID_type_dict.update({propertyIS_id:type})
                    objectlifelineID_componentID_dict.update({propertyIS_id:propertyIS_id})
                else:
                    continue
        return objectlifeline_id_list, objectlifelineID_name_dict, objectlifelineID_type_dict, objectlifeline_name_list, objectlifelineID_componentID_dict, propertyISids_list, propertyISid_name_dict      
    
    def get_component_lifelines_per_feature(self, element, featureID_name_dict, iterator_type):
        "For each feature, get its lifeline and the corresponding classifiers, i.e. components; categorize the components into safety(sa)/security(se)/both safety and security (sa_se)/others; extract direct and indirect message sequences"
        QD = QueryDataStruct()
        featureID_lifelineIDlist_dict = {}
        featurename_lifelinenamelist_dict = {}
        element_name = featureID_name_dict[element]
        
        #extract lifelines
        lifelineIS_path_search = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//packagedElement[@xmi:type = 'uml:Collaboration']/ownedAttribute[@xmi:type='uml:Property']/type".format(element)
        lifelineIS_iterator = self.get_iterator(lifelineIS_path_search, iterator_type)
        
        componentlifelineID_list, objectlifelineID_name_dict, objectlifelineID_type_dict, objectlifeline_name_list, objectlifelineID_componentID_dict, propertyISids_list, propertyISid_name_dict = self.get_lifelines_per_feature(lifelineIS_iterator, iterator_type)
        #print("Debug! ", element_name, " lifelines: ", objectlifeline_name_list)
        featureID_lifelineIDlist_dict.update({element:componentlifelineID_list}) #{featureID:componentlifelineIDs}
        featurename_lifelinenamelist_dict.update({element_name:objectlifeline_name_list}) #{feature_name:componentlifeline_names}
        return featureID_lifelineIDlist_dict, featurename_lifelinenamelist_dict, componentlifelineID_list, objectlifelineID_componentID_dict, objectlifelineID_name_dict, propertyISids_list, propertyISid_name_dict
    
    def get_msgIDs_per_feature(self, element, featureID_name_dict, iterator_type):
        "Get a list of msgIDs for all sequence diagrams per feature; get sequence of id as msgID and extract both its start and end instance specification IDs"
        msgID_list = []
        msgID_name_dict = {}
        msgID_path_search = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//message[@xmi:type = 'uml:Message']".format(element)
        msgID_iterator = self.get_iterator(msgID_path_search, iterator_type)
        feature_name = featureID_name_dict[element]
        for object in msgID_iterator:
            msg_id, msg_name, msg_type = self.get_iterator_attributes(object)
            msgID_list.append(msg_id)
            msgID_name_dict.update({msg_id:msg_name})
        msgname_list = self.get_listnames_from_listIDs(msgID_list, msgID_name_dict)
        return msgID_list, msgID_name_dict
    
    def non_propertylifeline_handler(self, element_id, objectlifelineID_componentID_dict, componentlifelineID_list, objectlifelineID_name_dict):
        "If a lifeline property is not specified as an instance specification, search for it in another input xmi file and return its type and name"    
        id = None
        name = None
        type = None
        id_ele2 = None
        name_ele2 = None
        type_ele2 = None
        if element_id not in objectlifelineID_componentID_dict.keys():
            #if type = lifeline in first input xmi file, add it to the node list and dict and then proceed
            element_path_search = ".//*[@xmi:id = '{}']".format(element_id)
            #configure the input file in which the search is to be performned
            element_iterator = self.get_iterator(element_path_search, 2) #2 refers to input xmi file 2 for our case study
            for element in element_iterator:
                id,name,type = self.get_iterator_attributes(element)
            if type == "uml:Lifeline" or type == "uml:InterfaceRealization" or type == "uml:Gate":
                objectlifelineID_componentID_dict.update({element_id:element_id})
                componentlifelineID_list.append(element_id)
                objectlifelineID_name_dict.update({element_id: name}) #update objectlifeline_id_name_dict
            elif type == None:
                alt_path_search = ".//*[@xmi:id = '{}']".format(element_id)
                #configure the input file in which the search is to be performned
                alt_path_iterator = self.get_iterator(alt_path_search, 3) #3 refers to input xmi file 3 for our case study
                for element2 in alt_path_iterator:
                    id_ele2,name_ele2,type_ele2 = self.get_iterator_attributes(element2)
                if type_ele2 == "uml:Component":
                    objectlifelineID_componentID_dict.update({element_id:element_id})
                    componentlifelineID_list.append(element_id)
                    objectlifelineID_name_dict.update({element_id: name_ele2})
                else:
                    print("Warning! element: ", element_id, " type in the xmi input file is: ", type_ele2)
        return objectlifelineID_componentID_dict, componentlifelineID_list, objectlifelineID_name_dict
    
    def get_msgseq_per_feature(self, msgID_list, msgID_name_dict, objectlifelineID_componentID_dict, componentlifelineID_list, objectlifelineID_name_dict, iterator_type):
        "For each feature, get message sequence using msg_id; prepare edges, edge_label, nodes and node_label"
        QD = QueryDataStruct()
        edge_list = []
        edge_label_dict = {}
        msgseqID_name_dict = {}
        edge_tuple = ()
        node_set = set()
        nodeID_name_labeldict = {}
        for element in msgID_list:
            seq_path_search = ".//Sequence[@xmi:id = '{}']".format(element)
            #configure the input file in which the search is to be performned
            seq_iterator = self.get_iterator(seq_path_search, iterator_type)
            edge_name = msgID_name_dict[element]
            for object in seq_iterator:
                src = object.get('start')
                end = object.get('end')
            #print("\n\nmessage_seq: ", element, ", src: ", src, ", end: ", end)
            objectlifelineID_componentID_dict, componentlifelineID_list, objectlifelineID_name_dict = self.non_propertylifeline_handler(src, objectlifelineID_componentID_dict, componentlifelineID_list, objectlifelineID_name_dict)
            objectlifelineID_componentID_dict, componentlifelineID_list, objectlifelineID_name_dict = self.non_propertylifeline_handler(end, objectlifelineID_componentID_dict, componentlifelineID_list, objectlifelineID_name_dict)
            if (src in objectlifelineID_componentID_dict.keys()) and (end in objectlifelineID_componentID_dict.keys()): #if src != None and end != None:
                src_componentID = QD.query_dict_by_key(objectlifelineID_componentID_dict, src)
                target_componentID = QD.query_dict_by_key(objectlifelineID_componentID_dict, end)
                #print("\nmessage_seq: ", element, ", src: ", src, " src_componentID: ",src_componentID, ", end: ", end, ", target_componentID: ", target_componentID)
                src_componentname = objectlifelineID_name_dict[src_componentID]
                target_componentname = objectlifelineID_name_dict[target_componentID]
                node_set.add(src_componentID)
                node_set.add(target_componentID)
                nodeID_name_labeldict.update({src_componentID:src_componentname,target_componentID:target_componentname})
                edge_tuple = (src_componentID,target_componentID, element)
                edge_list.append(edge_tuple)
                edge_label_dict.update({edge_tuple:edge_name})
                msgseqID_name_dict.update({element:edge_name})
            else:
                print("\nWarning! either src or end of sequence not found in dict.keys()")
        return edge_list, edge_label_dict, node_set, nodeID_name_labeldict, objectlifelineID_componentID_dict, componentlifelineID_list, objectlifelineID_name_dict, msgseqID_name_dict
    
    def get_sase_relevant_nodes_per_feature(self, nodeID_list, objectlifelineID_name_dict):
        "For the given lifeline nodes per feature, filter to get safety only, security only and both safety and security relevant lifelines"
        QD = QueryDataStruct()
        seSWCid_list = []
        seSWCname_list = []
        saSWCid_list = []
        saSWCname_list = []
        sase_mergedSWC_list = []
        otherLLid_list = []
        otherLLname_list = []
        #classify lifelines into 4 categories: safety(sa), security(se), both safety and security(sase), and other by comparing the list of lifeline's classifiers (nodeID_list) with safety(sa), security(se), both safety and security(sase) relevant lifeline's classifiers
        saseCSWCLLid_list, saseCSWCLLname_list = QD.query_lists_for_commonelement(nodeID_list, self.saseCSWC_list, objectlifelineID_name_dict)
        seSWCid_list, seSWCname_list = QD.query_lists_for_commonelement(nodeID_list, self.seSWCid_list, objectlifelineID_name_dict)
        if len(seSWCid_list) != 0 and len(saseCSWCLLid_list) != 0:
            seSWCid_list, seSWCname_list = QD.query_lists_for_uniqueelement(saseCSWCLLid_list, seSWCid_list, objectlifelineID_name_dict)
        saSWCid_list, saSWCname_list = QD.query_lists_for_commonelement(nodeID_list, self.saSWCid_list, objectlifelineID_name_dict)
        if len(saSWCid_list) != 0 and len(saseCSWCLLid_list) != 0:
            saSWCid_list, saSWCname_list = QD.query_lists_for_uniqueelement(saseCSWCLLid_list, saSWCid_list, objectlifelineID_name_dict)
        sase_mergedSWC_list = list(set(seSWCid_list+saSWCid_list+saseCSWCLLid_list)) #needed to get otherLLid_list
        otherLLid_list = list(filter(lambda i: i not in sase_mergedSWC_list, nodeID_list))
        if len(otherLLid_list) != 0:
            otherLLname_list = self.get_listnames_from_listIDs(otherLLid_list, objectlifelineID_name_dict)
        return seSWCid_list, saSWCid_list, saseCSWCLLid_list, otherLLid_list
    
    def product_of_elements(self, ele_list1, ele_list2):
        "Create a product of two lists of unequal size"
        IDcombinations_dir_1_to_2_list = list(itertools.product(ele_list1, ele_list2))
        IDcombinations_dir_2_to_1_list = list(itertools.product(ele_list2, ele_list1))
        return  IDcombinations_dir_1_to_2_list, IDcombinations_dir_2_to_1_list

    def nx_simple_paths_in_multidigraph(self, FeSDMDG_obj, node_product_list, str_to_print, updated_objectlifelineID_name_dict, msgseqID_name_dict):
        "get simple interaction paths from the multi directed graph using the node (lifeline's classifier) product list"
        all_pri_pathAB_IDs_list = []
        all_pathAB_IDs_list = []
        all_pathAB_names_list = []
        counter_all_nodes = 0
        relevant_lifelines_list = []
        relevant_lifelines_list.extend(self.seSWCid_list)
        relevant_lifelines_list.extend(self.saSWCid_list)
        relevant_lifelines_list.extend(self.saseCSWC_list)
        for index, value in enumerate(node_product_list):
            src = value[0]
            dst = value[1]
            var_bool, pathAB_IDs_list, pathAB_names_list, counter_per_node, pri_pathAB_IDs_list = FeSDMDG_obj.rI_pI_nx_simple_paths(src, dst, None, str_to_print, interaction_sequences, msgseqID_name_dict, relevant_lifelines_list)
            print("\nFinding simple paths from: ", updated_objectlifelineID_name_dict[src] , " to: ", updated_objectlifelineID_name_dict[dst], pathAB_names_list)
            counter_all_nodes = counter_all_nodes + counter_per_node
            all_pri_pathAB_IDs_list.extend(pri_pathAB_IDs_list)
            all_pathAB_IDs_list.extend(pathAB_IDs_list)
            all_pathAB_names_list.extend(pathAB_names_list)
        return all_pathAB_IDs_list, all_pathAB_names_list, counter_all_nodes, all_pri_pathAB_IDs_list
    
    def nx_edgepath_tabular_rep(self, feature_type_flag, featureID, feature_name, all_pathIDs_list, se_nodeID_list, sa_nodeID_list, sase_nodeID_list, nodeID_name_labeldict, msgseqID_name_dict):
        "Prepare data to create a tabular column for each interaction path: get all edge paths called all_pathIDs_list [[(),()],[()]] for each path from src to dst; reconstruct edge path to simple path; create a list of lists to store path table data [[software component (SWC), message sequence (MsgSeq), security relevance of SWC (SWCSeRelevance), safety relevance of SWC (SWCSaRelevance), security feature and security activities associated with the SWC(SWCse_act), safety feature and safety activities associated with the SWC(SWCsa_act)],[],[]]; print the table for each path"
        QD = QueryDataStruct()
        featureID_name_dict = {}
        featureID_name_dict.update(self.sefeatureID_name_dict)
        featureID_name_dict.update(self.safeatureID_name_dict)
        saFe_interactingSeFe_list = []
        seFe_interactingSaFe_list = []
        src_dst_interacFIs_list = []
        
        seC0_featurename_CSWCactivitynameslist_dict = {}
        saC0_featurename_CSWCactivitynameslist_dict = {}
        seC1_featurename_CSWCactivitynameslist_dict = {}
        saC1_featurename_CSWCactivitynameslist_dict = {}
        
        sa_se_rel_C0_RxC3 = None #security relevance of first/src component in a subpath
        sa_se_rel_C0_RxC4 = None #safety relevance of first/src component in a subpath
        sa_se_rel_C1_RxC3 = None #security relevance of second/dst component in a subpath
        sa_se_rel_C1_RxC4 = None #safety relevance of second/dst component in a subpath)
        
        SWCA = SaSeCommonSWCAnalysis(nodeID_name_labeldict, self.sefeatureID_name_dict, self.safeatureID_name_dict, self.se_feature_componentID_dict, self.sa_feature_componentID_dict, self.se_activityID_componentsID_dict, self.sa_activityID_componentsID_dict, self.se_featureID_activityID_dict, self.sa_featureID_activityID_dict, self.se_activity_dict, self.sa_activity_dict)
        
        for path in all_pathIDs_list: #all_pathIDs_list is a list of list containing tuples; each tuple consists of 3 elements
            pathtable = [["SWC","MsgSeq", "SWCSeRelevance", "SWCSaRelevance", "SWCse_act", "SWCsa_act"]] #pathtable will contain the data needed to create a table for each interaction path
            #print("Debug! for path: ", path, " len(path): ", len(path), " path_length: ", len(path)-1)
            srcID = None
            dstID = None
            src_featureIDs_list = []
            dst_featureIDs_list = []
            perpath_src_dst_interacFI_list = []
            for i, subpath in enumerate(path):
                if i == 0 and i == (len(path)-1):
                    srcID = subpath[0]
                    dstID = subpath[1]
                elif i == 0 and i != (len(path)-1):
                    srcID = subpath[0]
                elif i !=0 and i == (len(path)-1):
                    dstID = subpath[1]
                elif i !=0 and i != (len(path)-1):
                    pass
                else:
                    print("Warning! Unexpected if else condition found!")
            
            for i, subpath in enumerate(path): #subpath is an edge tuple with key as message sequence ID
                subpathrow = [] #contains parts of data for create path table
                nextsubpathrow = [] #for special cases e.g. [(A,B,K)]
                
                if subpath[0] in se_nodeID_list: #check if source node is safety or security relevant
                    sa_se_rel_C0_RxC3 = "se"
                    sa_se_rel_C0_RxC4 = "-"
                elif subpath[0] in sa_nodeID_list:
                    sa_se_rel_C0_RxC3 = "-"
                    sa_se_rel_C0_RxC4 = "sa"
                elif subpath[0] in sase_nodeID_list:
                    sa_se_rel_C0_RxC3 = "se"
                    sa_se_rel_C0_RxC4 = "sa"
                else:
                    sa_se_rel_C0_RxC3 = "-"
                    sa_se_rel_C0_RxC4 = "-"
                
                if subpath[1] in se_nodeID_list: #check if dst node is safety or security relevant
                    sa_se_rel_C1_RxC3 = "se"
                    sa_se_rel_C1_RxC4 = "-"
                elif subpath[1] in sa_nodeID_list:
                    sa_se_rel_C1_RxC3 = "-"
                    sa_se_rel_C1_RxC4 = "sa"
                elif subpath[1] in sase_nodeID_list:
                    sa_se_rel_C1_RxC3 = "se"
                    sa_se_rel_C1_RxC4 = "sa"
                else:
                    sa_se_rel_C1_RxC3 = "-"
                    sa_se_rel_C1_RxC4 = "-"
                
                if sa_se_rel_C0_RxC3 == "se":
                    seC0_featurename_CSWCactivitynameslist_dict, seC0_featurename_CSWCactivitynameslist_str = SWCA.getSWCfeature_withactivity([subpath[0]],"se", featureID)
                    #print("Debug! i: ", i, "SWC0: ", nodeID_name_labeldict[subpath[0]], "se_fe_act: ", seC0_featurename_CSWCactivitynameslist_str)
                if sa_se_rel_C0_RxC4 == "sa":
                    saC0_featurename_CSWCactivitynameslist_dict, saC0_featurename_CSWCactivitynameslist_str = SWCA.getSWCfeature_withactivity([subpath[0]],"sa", featureID)
                    #print("Debug! i: ", i, "SWC0: ", nodeID_name_labeldict[subpath[0]], "sa_fe_act: ", saC0_featurename_CSWCactivitynameslist_str)
                if sa_se_rel_C1_RxC3 == "se":
                    seC1_featurename_CSWCactivitynameslist_dict, seC1_featurename_CSWCactivitynameslist_str = SWCA.getSWCfeature_withactivity([subpath[1]],"se", featureID)
                    #print("Debug! i: ", i, "SWC1: ", nodeID_name_labeldict[subpath[1]], "se_fe_act: ", seC1_featurename_CSWCactivitynameslist_str)
                if sa_se_rel_C1_RxC4 == "sa":
                    saC1_featurename_CSWCactivitynameslist_dict, saC1_featurename_CSWCactivitynameslist_str = SWCA.getSWCfeature_withactivity([subpath[1]],"sa", featureID)
                    #print("Debug! i: ", i, "SWC1: ", nodeID_name_labeldict[subpath[1]], "sa_fe_act: ", saC1_featurename_CSWCactivitynameslist_str)
                
                #Automated feature extraction
                if i == 0 and i == (len(path)-1): #extract source and destination features
                    if (srcID in se_nodeID_list and dstID in sa_nodeID_list) or (srcID in se_nodeID_list and dstID in sase_nodeID_list) or (srcID in sase_nodeID_list and dstID in sa_nodeID_list):
                        if feature_type_flag == 0: #if the feature whose sequence diagrams are being analyzed is a security feature
                            #extraction of source feature using the source lifeline/component
                            if len(seC0_featurename_CSWCactivitynameslist_dict.keys()) != 0: #get feature using feature to activity mapping (if feature:activity mapping is non empty)
                                for key in seC0_featurename_CSWCactivitynameslist_dict.keys():    
                                    if key == featureID: #if the features extracted include the feature being analyzed, consider only this feature and discard other features
                                        if key not in src_featureIDs_list:
                                            src_featureIDs_list.append(key)
                                    else:
                                        continue
                                if len(src_featureIDs_list) == 0:
                                    for key in seC0_featurename_CSWCactivitynameslist_dict.keys():
                                        if key not in src_featureIDs_list:
                                            src_featureIDs_list.append(key)
                            else: #get feature from the feature to component mapping (if feature to activity mapping is empty)
                                fe_list = QD.query_dict_by_wlistvalue(srcID, self.se_feature_componentID_dict)
                                for element in fe_list:
                                    if element not in src_featureIDs_list:
                                        src_featureIDs_list.append(element)
                            #extraction of destination feature using the destination lifeline/component
                            if len(saC1_featurename_CSWCactivitynameslist_dict.keys()) != 0: #get feature using feature to activity mapping (if feature:activity mapping is non empty)
                                for key in saC1_featurename_CSWCactivitynameslist_dict.keys():
                                    if key not in dst_featureIDs_list:
                                        dst_featureIDs_list.append(key)
                            else: #get feature using feature to component mapping (if feature:activity mapping is empty)
                                fe_list = QD.query_dict_by_wlistvalue(dstID, self.sa_feature_componentID_dict) 
                                for element in fe_list:
                                    if element not in dst_featureIDs_list:
                                        dst_featureIDs_list.append(element)
                        elif feature_type_flag == 1: #if the feature whose sequence diagrams are being analyzed is a safety feature
                            #extraction of source feature using the source lifeline/component
                            if len(seC0_featurename_CSWCactivitynameslist_dict.keys()) != 0: #get feature using feature to activity mapping (if feature:activity mapping is non empty)
                                for key in seC0_featurename_CSWCactivitynameslist_dict.keys():
                                    if key not in src_featureIDs_list:
                                        src_featureIDs_list.append(key)
                            else: #get feature using feature to component mapping (if feature to activity mapping is empty)
                                fe_list = QD.query_dict_by_wlistvalue(srcID, self.se_feature_componentID_dict)
                                for element in fe_list:
                                    if element not in src_featureIDs_list:
                                        src_featureIDs_list.append(element)
                            #extraction of destination feature using the destination lifeline/component
                            if len(saC1_featurename_CSWCactivitynameslist_dict.keys()) != 0: #get feature using feature to activity mapping (if feature:activity mapping is non empty)
                                for key in saC1_featurename_CSWCactivitynameslist_dict.keys():
                                    if key == featureID: #if the features extracted include the feature being analyzed, consider only this feature and discard other features
                                        if key not in dst_featureIDs_list:
                                            dst_featureIDs_list.append(key)
                                    else:
                                        continue
                                if len(dst_featureIDs_list) == 0:
                                    for key in saC1_featurename_CSWCactivitynameslist_dict.keys():
                                        if key not in dst_featureIDs_list:
                                            dst_featureIDs_list.append(key)
                            else: #get feature using feature to component mapping (if feature to activity mapping is empty)
                                fe_list = QD.query_dict_by_wlistvalue(dstID, self.sa_feature_componentID_dict) 
                                for element in fe_list:
                                    if element not in dst_featureIDs_list:
                                        dst_featureIDs_list.append(element)
                        else:
                            print("Warning! Invalid value of feature_type_flag!")
                    elif (srcID in sa_nodeID_list and dstID in se_nodeID_list) or (srcID in sase_nodeID_list and dstID in se_nodeID_list) or (srcID in sa_nodeID_list and dstID in sase_nodeID_list):
                        if feature_type_flag == 0: #if the feature whose sequence diagrams are being analyzed is a security feature
                            #extraction of source feature using the source lifeline/component
                            if len(saC0_featurename_CSWCactivitynameslist_dict.keys()) != 0: #get feature using feature to activity mapping (if feature:act mapping non empty)
                                for key in saC0_featurename_CSWCactivitynameslist_dict.keys():
                                    if key not in src_featureIDs_list:
                                        src_featureIDs_list.append(key)
                            else: #get feature using feature to component mapping (if feature:act mapping empty)
                                fe_list = QD.query_dict_by_wlistvalue(srcID, self.sa_feature_componentID_dict)
                                for element in fe_list:
                                    if element not in src_featureIDs_list:
                                        src_featureIDs_list.append(element)
                            #extraction of destination feature using the destination lifeline/component
                            if len(seC1_featurename_CSWCactivitynameslist_dict.keys()) != 0: #get feature using feature to activity mapping (if feature:act mapping non empty)
                                for key in seC1_featurename_CSWCactivitynameslist_dict.keys():    
                                    if key == featureID: #if the features extracted include the feature being analyzed, consider only this feature and discard other features
                                        if key not in dst_featureIDs_list:
                                            dst_featureIDs_list.append(key)
                                    else:
                                        continue
                                if len(dst_featureIDs_list) == 0:
                                    for key in seC1_featurename_CSWCactivitynameslist_dict.keys():
                                        if key not in dst_featureIDs_list:
                                            dst_featureIDs_list.append(key)
                            else: #get feature using feature to component mapping (if feature:act mapping empty)
                                fe_list = QD.query_dict_by_wlistvalue(dstID, self.se_feature_componentID_dict) 
                                for element in fe_list:
                                    if element not in dst_featureIDs_list:
                                        dst_featureIDs_list.append(element)
                        elif feature_type_flag == 1: #if the feature whose sequence diagrams are being analyzed is a safety feature
                            #extraction of source feature using the source lifeline/component
                            if len(saC0_featurename_CSWCactivitynameslist_dict.keys()) != 0: #get feature using feature to activity mapping (if feature:act mapping non empty)
                                for key in saC0_featurename_CSWCactivitynameslist_dict.keys():
                                    if key == featureID: #if a feature extracted includes feature being analyzed, consider only this feature and discard other features
                                        if key not in src_featureIDs_list:
                                            src_featureIDs_list.append(key)
                                    else:
                                        continue
                                if len(src_featureIDs_list) == 0:
                                    for key in saC0_featurename_CSWCactivitynameslist_dict.keys():
                                        if key not in src_featureIDs_list:
                                            src_featureIDs_list.append(key)
                            else: #get feature using feature to component mapping (if feature:act mapping empty)
                                fe_list = QD.query_dict_by_wlistvalue(srcID, self.sa_feature_componentID_dict)
                                for element in fe_list:
                                    if element not in src_featureIDs_list:
                                        src_featureIDs_list.append(element)
                            #extraction of destination feature using the destination lifeline/component
                            if len(seC1_featurename_CSWCactivitynameslist_dict.keys()) != 0: #get feature using feature to activity mapping (if feature:act mapping non empty)
                                for key in seC1_featurename_CSWCactivitynameslist_dict.keys():    
                                    if key not in dst_featureIDs_list:
                                        dst_featureIDs_list.append(key)
                            else: #get feature using feature to component mapping (if feature:act mapping empty)
                                fe_list = QD.query_dict_by_wlistvalue(dstID, self.se_feature_componentID_dict) 
                                for element in fe_list:
                                    if element not in dst_featureIDs_list:
                                        dst_featureIDs_list.append(element)
                        else:
                            print("Warning! Invalid value of feature_type_flag!")
                    else:
                        print("Warning! Invalid combination of source and destination lifeline with their safety and security relevance!")
                
                elif i == 0 and i != (len(path)-1): #extract source feature
                    if (srcID in se_nodeID_list and dstID in sa_nodeID_list) or (srcID in se_nodeID_list and dstID in sase_nodeID_list) or (srcID in sase_nodeID_list and dstID in sa_nodeID_list):
                        if feature_type_flag == 0: #if the feature whose sequence diagrams are being analyzed is a security feature
                            #extraction of source feature using the source lifeline/component
                            if len(seC0_featurename_CSWCactivitynameslist_dict.keys()) != 0: #get feature using feature to activity mapping (if feature:act mapping non empty)
                                for key in seC0_featurename_CSWCactivitynameslist_dict.keys():    
                                    if key == featureID: #if the features extracted include feature being analyzed, consider only this feature and discard other features
                                        if key not in src_featureIDs_list:
                                            src_featureIDs_list.append(key)
                                    else:
                                        continue
                                if len(src_featureIDs_list) == 0:
                                    for key in seC0_featurename_CSWCactivitynameslist_dict.keys():
                                        if key not in src_featureIDs_list:
                                            src_featureIDs_list.append(key)
                            else: #get feature using feature to component mapping (if feature to activity mapping empty)
                                fe_list = QD.query_dict_by_wlistvalue(srcID, self.se_feature_componentID_dict)
                                for element in fe_list:
                                    if element not in src_featureIDs_list:
                                        src_featureIDs_list.append(element)
                        elif feature_type_flag == 1: #if the feature whose sequence diagrams are being analyzed is a safety feature
                            #extraction of source feature using the source lifeline/component
                            if len(seC0_featurename_CSWCactivitynameslist_dict.keys()) != 0: #get feature using feature to activity mapping (if feature:act mapping non empty)
                                for key in seC0_featurename_CSWCactivitynameslist_dict.keys():
                                    if key not in src_featureIDs_list:
                                        src_featureIDs_list.append(key)
                            else: #get feature using feature to component mapping (if feature:act mapping empty)
                                fe_list = QD.query_dict_by_wlistvalue(srcID, self.se_feature_componentID_dict)
                                for element in fe_list:
                                    if element not in src_featureIDs_list:
                                        src_featureIDs_list.append(element)
                        else:
                            print("Warning! Invalid value of feature_type_flag!")
                    elif (srcID in sa_nodeID_list and dstID in se_nodeID_list) or (srcID in sase_nodeID_list and dstID in se_nodeID_list) or (srcID in sa_nodeID_list and dstID in sase_nodeID_list):
                        if feature_type_flag == 0: #if the feature whose sequence diagrams are being analyzed is a security feature
                            #extraction of source feature using the source lifeline/component
                            if len(saC0_featurename_CSWCactivitynameslist_dict.keys()) != 0: #get feature using feature to activity mapping (if feature:act mapping non empty)
                                for key in saC0_featurename_CSWCactivitynameslist_dict.keys():
                                    if key not in src_featureIDs_list:
                                        src_featureIDs_list.append(key)
                            else: #get feature using feature to component mapping (if feature:act mapping empty)
                                fe_list = QD.query_dict_by_wlistvalue(srcID, self.sa_feature_componentID_dict)
                                for element in fe_list:
                                    if element not in src_featureIDs_list:
                                        src_featureIDs_list.append(element)
                        elif feature_type_flag == 1: #if the feature whose sequence diagrams are being analyzed is a safety feature
                            #extraction of source feature using the source lifeline/component
                            if len(saC0_featurename_CSWCactivitynameslist_dict.keys()) != 0: #get feature using feature to activity mapping (if feature:act mapping non empty)
                                for key in saC0_featurename_CSWCactivitynameslist_dict.keys():
                                    if key == featureID: #if a feature extracted includes the feature being analyzed, consider only this feature and discard other features
                                        if key not in src_featureIDs_list:
                                            src_featureIDs_list.append(key)
                                    else:
                                        continue
                                if len(src_featureIDs_list) == 0:
                                    for key in saC0_featurename_CSWCactivitynameslist_dict.keys():
                                        if key not in src_featureIDs_list:
                                            src_featureIDs_list.append(key)
                            else: #get feature using feature to component mapping (if feature:act mapping empty)
                                fe_list = QD.query_dict_by_wlistvalue(srcID, self.sa_feature_componentID_dict)
                                for element in fe_list:
                                    if element not in src_featureIDs_list:
                                        src_featureIDs_list.append(element)
                        else:
                            print("Warning! Invalid value of feature_type_flag!")
                    else:
                        print("Warning! Invalid combination of source and destination lifeline with their safety and security relevance!")
                
                elif i !=0 and i != (len(path)-1):
                    pass
                
                elif i !=0 and i == (len(path)-1): #extract destination feature
                    if (srcID in se_nodeID_list and dstID in sa_nodeID_list) or (srcID in se_nodeID_list and dstID in sase_nodeID_list) or (srcID in sase_nodeID_list and dstID in sa_nodeID_list):
                        if feature_type_flag == 0: #if the feature whose sequence diagrams are being analyzed is a security feature
                            #extraction of destination feature using the destination lifeline/component
                            if len(saC1_featurename_CSWCactivitynameslist_dict.keys()) != 0: #get feature using feature to activity mapping (if feature:act mapping non empty)
                                for key in saC1_featurename_CSWCactivitynameslist_dict.keys():
                                    if key not in dst_featureIDs_list:
                                        dst_featureIDs_list.append(key)
                            else: #get feature using feature to component mapping (if feature:act mapping empty)
                                fe_list = QD.query_dict_by_wlistvalue(dstID, self.sa_feature_componentID_dict) 
                                for element in fe_list:
                                    if element not in dst_featureIDs_list:
                                        dst_featureIDs_list.append(element)
                        elif feature_type_flag == 1: #if the feature whose sequence diagrams are being analyzed is a safety feature
                            #extraction of destination feature using the destination lifeline/component
                            if len(saC1_featurename_CSWCactivitynameslist_dict.keys()) != 0: #get feature using feature to activity mapping (if feature:act mapping non empty)
                                for key in saC1_featurename_CSWCactivitynameslist_dict.keys():
                                    if key == featureID: #if a feature extracted includes feature being analyzed, consider only this feature and discard other features
                                        if key not in dst_featureIDs_list:
                                            dst_featureIDs_list.append(key)
                                    else:
                                        continue
                                if len(dst_featureIDs_list) == 0:
                                    for key in saC1_featurename_CSWCactivitynameslist_dict.keys():
                                        if key not in dst_featureIDs_list:
                                            dst_featureIDs_list.append(key)
                            else: #get feature using feature to component mapping (if feature:act mapping empty)
                                fe_list = QD.query_dict_by_wlistvalue(dstID, self.sa_feature_componentID_dict) 
                                for element in fe_list:
                                    if element not in dst_featureIDs_list:
                                        dst_featureIDs_list.append(element)
                        else:
                            print("Warning! Invalid value of feature_type_flag!")
                    elif (srcID in sa_nodeID_list and dstID in se_nodeID_list) or (srcID in sase_nodeID_list and dstID in se_nodeID_list) or (srcID in sa_nodeID_list and dstID in sase_nodeID_list):
                        if feature_type_flag == 0: #if the feature whose sequence diagrams are being analyzed is a security feature
                            #extraction of destination feature using the destination lifeline/component
                            if len(seC1_featurename_CSWCactivitynameslist_dict.keys()) != 0: #get feature using feature to activity mapping (if feature:act mapping non empty)
                                for key in seC1_featurename_CSWCactivitynameslist_dict.keys():    
                                    if key == featureID: #if the features extracted include the feature being analyzed, consider only this feature and discard other features
                                        if key not in dst_featureIDs_list:
                                            dst_featureIDs_list.append(key)
                                    else:
                                        continue
                                if len(dst_featureIDs_list) == 0:
                                    for key in seC1_featurename_CSWCactivitynameslist_dict.keys():
                                        if key not in dst_featureIDs_list:
                                            dst_featureIDs_list.append(key)
                            else: #get feature using feature to component mapping (if feature:act mapping empty)
                                fe_list = QD.query_dict_by_wlistvalue(dstID, self.se_feature_componentID_dict) 
                                for element in fe_list:
                                    if element not in dst_featureIDs_list:
                                        dst_featureIDs_list.append(element)
                        elif feature_type_flag == 1: #if the feature whose sequence diagrams are being analyzed is a safety feature
                            #extraction of destination feature using the destination lifeline/component
                            if len(seC1_featurename_CSWCactivitynameslist_dict.keys()) != 0: #get feature using feature to activity mapping (if feature:act mapping non empty)
                                for key in seC1_featurename_CSWCactivitynameslist_dict.keys():    
                                    if key not in dst_featureIDs_list:
                                        dst_featureIDs_list.append(key)
                            else: #get feature using feature to component mapping (if feature:act mapping empty)
                                fe_list = QD.query_dict_by_wlistvalue(dstID, self.se_feature_componentID_dict) 
                                for element in fe_list:
                                    if element not in dst_featureIDs_list:
                                        dst_featureIDs_list.append(element)
                        else:
                            print("Warning! Invalid value of feature_type_flag!")
                    else:
                        print("Warning! Invalid combination of source and destination lifeline with their safety and security relevance!")
                else:
                    print("Warning! Unexpected and uncovered if else condition found!")
                
                #Creating list of lists for tabular representation of each interaction path
                if (i==0 and i==(len(path)-1)) or (i!=0 and i==(len(path)-1)): #for special cases e.g. [(A,B,K)]
                    subpathrow.append(nodeID_name_labeldict[subpath[0]]) #1st/src component
                    if msgseqID_name_dict[subpath[2]] is None:
                        subpathrow.append("-")
                    else:
                        subpathrow.append(msgseqID_name_dict[subpath[2]]) #key as msgseq ID
                    subpathrow.append(sa_se_rel_C0_RxC3)
                    subpathrow.append(sa_se_rel_C0_RxC4)
                    if sa_se_rel_C0_RxC3 == "se":
                        subpathrow.append(seC0_featurename_CSWCactivitynameslist_str)
                    else:
                        subpathrow.append("-")
                    if sa_se_rel_C0_RxC4 == "sa":
                        subpathrow.append(saC0_featurename_CSWCactivitynameslist_str)
                    else:
                        subpathrow.append("-")
                    nextsubpathrow.append(nodeID_name_labeldict[subpath[1]]) #2nd/dst component
                    nextsubpathrow.append("-") #key as msgseq ID
                    nextsubpathrow.append(sa_se_rel_C1_RxC3)
                    nextsubpathrow.append(sa_se_rel_C1_RxC4)
                    if sa_se_rel_C1_RxC3 == "se":
                        nextsubpathrow.append(seC1_featurename_CSWCactivitynameslist_str)
                    else:
                        nextsubpathrow.append("-")
                    if sa_se_rel_C1_RxC4 == "sa":
                        nextsubpathrow.append(saC1_featurename_CSWCactivitynameslist_str)
                    else:
                        nextsubpathrow.append("-")
                elif (i==0 and i!=(len(path)-1)) or (i!=0 and i!=(len(path)-1)):
                    subpathrow.append(nodeID_name_labeldict[subpath[0]]) #1st/src component
                    if msgseqID_name_dict[subpath[2]] is None:
                        subpathrow.append("-")
                    else:
                        subpathrow.append(msgseqID_name_dict[subpath[2]]) #key as msgseq ID
                    subpathrow.append(sa_se_rel_C0_RxC3)
                    subpathrow.append(sa_se_rel_C0_RxC4)
                    if sa_se_rel_C0_RxC3 == "se":
                        subpathrow.append(seC0_featurename_CSWCactivitynameslist_str)
                    else:
                        subpathrow.append("-")
                    if sa_se_rel_C0_RxC4 == "sa":
                        subpathrow.append(saC0_featurename_CSWCactivitynameslist_str)
                    else:
                        subpathrow.append("-")
                else:
                    print("\nMet an unexpected condition :( !!!")
                
                pathtable.append(subpathrow)
                if len(nextsubpathrow) != 0:
                    pathtable.append(nextsubpathrow)
            
            if len(src_featureIDs_list) != 0 and len(dst_featureIDs_list) != 0:
                perpath_src_dst_interacFI_list = QD.get_itertoolsproductoflists(src_featureIDs_list, dst_featureIDs_list)
            for element in perpath_src_dst_interacFI_list:
                if element not in src_dst_interacFIs_list:
                    src_dst_interacFIs_list.append(element)
            print("feature: ", feature_name, " perpath_src_dst_interacFInames_list: ", perpath_src_dst_interacFI_list)
            print(tabulate(pathtable, tablefmt = 'grid', maxcolwidths=[12,12,5,5,33,33]), "\n") #print path table
        return src_dst_interacFIs_list
    
    def sd_analysis_per_feature(self, feature_type_flag, element, featureID_name_dict, all_objectlifelineID_componentID_dict, all_componentlifelineID_list, all_objectlifelineID_name_dict, feature_componentID_dict, iterator_type):
        "extraction of direct and indirect message sequences exchanged between safety and security relevant lifelines in sequence diagrams of each feature"
        pri_interacting_features_list = []
        interacting_features_list = []
        msgNames_list = []
        lifelineNames_list = []
        msgID_list, msgID_name_dict = self.get_msgIDs_per_feature(element, featureID_name_dict, iterator_type) #get message sequences for each feature
        msgNames_list = [value for value in msgID_name_dict.values()]
        #print("\nDebug! Feature: ", featureID_name_dict[element], " len(msgID_list) ", len(msgID_list), " messages: ", msgID_name_dict)
        edge_list, edgelabel_dict, node_set, nodeID_name_labeldict, updated_objectlifelineID_componentID_dict, updated_componentlifelineID_list, updated_objectlifelineID_name_dict, msgseqID_name_dict = self.get_msgseq_per_feature(msgID_list, msgID_name_dict, all_objectlifelineID_componentID_dict, all_componentlifelineID_list, all_objectlifelineID_name_dict, iterator_type) #get edge_list from message_seq for each feature
        #print("\nDebug! Feature: ", featureID_name_dict[element], " len(edge_list): ", len(edge_list), " messages: ", edgelabel_dict)
        lifelineNames_list = [value for value in nodeID_name_labeldict.values()]
        #print("\nDebug! Feature: ", featureID_name_dict[element], " lifeline_no: ", len(node_set), " lifelines: ", nodeID_name_labeldict)
        print("\nCreating MultiDiGraph for the feature: ", featureID_name_dict[element])
        G1 = nx.MultiDiGraph()
        FeSDMDG = FeatureSDMultiDiGraph(G1, featureID_name_dict[element], node_set, edge_list, nodeID_name_labeldict, edgelabel_dict)
        FeSDMDG.create_nx_graph()
        counter_plus_sase_paths = 0
        counter_minus_sase_paths = 0
        act_components_list = feature_componentID_dict[element]
        print("Debug! Feature: ", featureID_name_dict[element], " nodes: ", G1.number_of_nodes(), " edges: ", G1.number_of_edges())
        #print("\nGetting safety only, security only and both safety-security relevant nodes from the graph node list..")
        if len(node_set) == 0:
            print("No lifelines in sequence diagrams of feature: ", featureID_name_dict[element], " were found!!!")
            if len(act_components_list) == 0:
                print("Allocation of activities missing for feature: ", featureID_name_dict[element])
        else:
            if len(act_components_list) == 0:
                print("Allocation of activities missing for feature: ", featureID_name_dict[element])
            
            se_nodeID_list, sa_nodeID_list, sase_nodeID_list, non_saorse_nodeID_list = self.get_sase_relevant_nodes_per_feature(list(node_set), updated_objectlifelineID_name_dict)
            
            if (len(sa_nodeID_list) != 0) and (len(se_nodeID_list) != 0):
                se_sa_node_IDcombinations_list, sa_se_node_IDcombinations_list = self.product_of_elements(se_nodeID_list, sa_nodeID_list) #Preparing node query list to query the multidigraph.
                joined_nodeID_combination_list = [*se_sa_node_IDcombinations_list, *sa_se_node_IDcombinations_list]
                str_sa_se_uC = "Check! message sequence has path: "
                pathIDs_list, path_names_list, counter_sa_se, pri_pathAB_IDs_list = self.nx_simple_paths_in_multidigraph(FeSDMDG, joined_nodeID_combination_list, str_sa_se_uC, updated_objectlifelineID_name_dict, msgseqID_name_dict)
                counter_minus_sase_paths = counter_minus_sase_paths + counter_sa_se
                ###only for primary paths
                pri_src_dst_interacFIs_list = self.nx_edgepath_tabular_rep(feature_type_flag, element, featureID_name_dict[element], pri_pathAB_IDs_list, se_nodeID_list, sa_nodeID_list, sase_nodeID_list, nodeID_name_labeldict, msgseqID_name_dict)
                pri_interacting_features_list.extend(pri_src_dst_interacFIs_list)
                ###only for secondary paths
                src_dst_interacFIs_list = self.nx_edgepath_tabular_rep(feature_type_flag, element, featureID_name_dict[element], pathIDs_list, se_nodeID_list, sa_nodeID_list, sase_nodeID_list, nodeID_name_labeldict, msgseqID_name_dict)
                interacting_features_list.extend(src_dst_interacFIs_list)
                
                if len(sase_nodeID_list) != 0: #paths between sa to sa/se and se to sa/se
                    sa_sase_node_IDcombinations_list, sase_sa_node_IDcombinations_list = self.product_of_elements(sa_nodeID_list, sase_nodeID_list)
                    se_sase_node_IDcombinations_list, sase_se_node_IDcombinations_list = self.product_of_elements(se_nodeID_list, sase_nodeID_list)
                    joined_nodeID_combination_list = [*sa_sase_node_IDcombinations_list, *sase_sa_node_IDcombinations_list, *se_sase_node_IDcombinations_list, *sase_se_node_IDcombinations_list]
                    print("\nfeature: ",featureID_name_dict[element]," interaction(s): safety to safety/security components\n")
                    str_sa_seorsa_uC = "Check! safety to security/safety message sequence has path: "
                    pathSaSeorSa_IDs_list, pathSaSeorSa_names_list, counter_sa_or_se_with_sase, pri_pathSaSeorSa_IDs_list = self.nx_simple_paths_in_multidigraph(FeSDMDG, joined_nodeID_combination_list, str_sa_seorsa_uC, updated_objectlifelineID_name_dict, msgseqID_name_dict)
                    counter_plus_sase_paths = counter_plus_sase_paths + counter_sa_or_se_with_sase
                    ###only for primary paths
                    pri_src_dst_interacFIs_list = self.nx_edgepath_tabular_rep(feature_type_flag, element, featureID_name_dict[element], pri_pathSaSeorSa_IDs_list, se_nodeID_list, sa_nodeID_list, sase_nodeID_list, nodeID_name_labeldict, msgseqID_name_dict)
                    pri_interacting_features_list.extend(pri_src_dst_interacFIs_list)
                    ###only for secondary paths
                    src_dst_interacFIs_list = self.nx_edgepath_tabular_rep(feature_type_flag, element, featureID_name_dict[element], pathSaSeorSa_IDs_list, se_nodeID_list, sa_nodeID_list, sase_nodeID_list, nodeID_name_labeldict, msgseqID_name_dict)
                    interacting_features_list.extend(src_dst_interacFIs_list)
            
            elif (len(se_nodeID_list) == 0) and (len(sa_nodeID_list) != 0) and (len(sase_nodeID_list) != 0):
                sa_sase_node_IDcombinations_list, sase_sa_node_IDcombinations_list = self.product_of_elements(sa_nodeID_list, sase_nodeID_list)
                joined_nodeID_combination_list = [*sa_sase_node_IDcombinations_list, *sase_sa_node_IDcombinations_list]
                print("\nfeature: ",featureID_name_dict[element]," interaction: safety to safety/security components\n")
                str_sa_seorsa_uC = "Check! safety to security/safety message sequence has path: "
                pathSaSeorSa_IDs_list, pathSaSeorSa_names_list, counter_sa_to_sase, pri_pathSaSeorSa_IDs_list = self.nx_simple_paths_in_multidigraph(FeSDMDG, joined_nodeID_combination_list, str_sa_seorsa_uC, updated_objectlifelineID_name_dict, msgseqID_name_dict)
                counter_plus_sase_paths = counter_plus_sase_paths + counter_sa_to_sase
                ###only for primary paths
                pri_src_dst_interacFIs_list = self.nx_edgepath_tabular_rep(feature_type_flag, element, featureID_name_dict[element], pri_pathSaSeorSa_IDs_list, se_nodeID_list, sa_nodeID_list, sase_nodeID_list, nodeID_name_labeldict, msgseqID_name_dict)
                pri_interacting_features_list.extend(pri_src_dst_interacFIs_list)
                ###only for secondary paths
                src_dst_interacFIs_list = self.nx_edgepath_tabular_rep(feature_type_flag, element, featureID_name_dict[element], pathSaSeorSa_IDs_list, se_nodeID_list, sa_nodeID_list, sase_nodeID_list, nodeID_name_labeldict, msgseqID_name_dict)
                interacting_features_list.extend(src_dst_interacFIs_list)
                
            elif (len(se_nodeID_list) != 0) and (len(sa_nodeID_list) == 0) and (len(sase_nodeID_list) != 0):
                se_sase_node_IDcombinations_list, sase_se_node_IDcombinations_list = self.product_of_elements(se_nodeID_list, sase_nodeID_list)
                joined_nodeID_combination_list = [*se_sase_node_IDcombinations_list, *sase_se_node_IDcombinations_list]
                print("\nfeature: ",featureID_name_dict[element]," interaction: security to safety/security components\n")
                str_se_seorsa_uC = "Check! security to security/safety message sequence has path: "
                pathSeSaorSe_IDs_list, pathSeSaorSe_names_list, counter_se_to_sase, pri_pathSeSaorSe_IDs_list = self.nx_simple_paths_in_multidigraph(FeSDMDG, joined_nodeID_combination_list, str_se_seorsa_uC, updated_objectlifelineID_name_dict, msgseqID_name_dict)
                counter_plus_sase_paths = counter_plus_sase_paths + counter_se_to_sase
                ###only for primary paths
                pri_src_dst_interacFIs_list = self.nx_edgepath_tabular_rep(feature_type_flag, element, featureID_name_dict[element], pri_pathSeSaorSe_IDs_list, se_nodeID_list, sa_nodeID_list, sase_nodeID_list, nodeID_name_labeldict, msgseqID_name_dict)
                pri_interacting_features_list.extend(pri_src_dst_interacFIs_list)
                ###only for secondary paths
                src_dst_interacFIs_list = self.nx_edgepath_tabular_rep(feature_type_flag, element, featureID_name_dict[element], pathSeSaorSe_IDs_list, se_nodeID_list, sa_nodeID_list, sase_nodeID_list, nodeID_name_labeldict, msgseqID_name_dict)
                interacting_features_list.extend(src_dst_interacFIs_list)             
        print("\nDebug! Path_count!!!Feature: ", featureID_name_dict[element], " has ", counter_minus_sase_paths, " paths bw se and sa SWC, and ", counter_plus_sase_paths, " paths between se or sa and sase")
        return pri_interacting_features_list, interacting_features_list
        
    def objectlifelines_all_featureset(self, featureID_list, featureID_name_dict, iterator_type):
        all_propertyISids_set = set()
        componentlifelineID_set = set()
        all_propertyISid_name_dict = {}
        all_objectlifelineID_name_dict = {}
        all_objectlifelineID_componentID_dict = {}
        for element in featureID_list:
            featureID_lifelineIDlist_dict, featurename_lifelinenamelist_dict, componentlifelineID_list, objectlifelineID_componentID_dict, objectlifelineID_name_dict, propertyISids_list, propertyISid_name_dict = self.get_component_lifelines_per_feature(element, featureID_name_dict, iterator_type) #get lifelines of each feature
            all_propertyISids_set.update(propertyISids_list)
            componentlifelineID_set.update(componentlifelineID_list)
            all_propertyISid_name_dict.update(propertyISid_name_dict)
            all_objectlifelineID_name_dict.update(objectlifelineID_name_dict)
            all_objectlifelineID_componentID_dict.update(objectlifelineID_componentID_dict)
        return all_propertyISids_set, all_propertyISid_name_dict, componentlifelineID_set, all_objectlifelineID_name_dict, all_objectlifelineID_componentID_dict
    
    def sd_analysis_sasefeatures(self, iterator_type):
        "direct and indirect message sequence extraction for all safety and security sequence diagrams"
        print("\n\nStarting sequence diagram analysis per security feature...")
        all_se_propertyISids_set, all_se_propertyISid_name_dict, all_se_componentlifelineID_set, all_se_objectlifelineID_name_dict, all_se_objectlifelineID_componentID_dict = self.objectlifelines_all_featureset(self.security_feature_list, self.sefeatureID_name_dict, iterator_type)
        feature_type_flag = 0 #set this flag to 0 if the feature is a security feature
        all_pri_interacting_features_list = []
        all_sec_interacting_features_list = []
        
        for feature in self.security_feature_list:
            pri_interacting_features_list1, interacting_features_list1 = self.sd_analysis_per_feature(feature_type_flag, feature, self.sefeatureID_name_dict, all_se_objectlifelineID_componentID_dict, list(all_se_componentlifelineID_set), all_se_objectlifelineID_name_dict, self.se_feature_componentID_dict, iterator_type)
            all_pri_interacting_features_list.extend(pri_interacting_features_list1)
            all_sec_interacting_features_list.extend(interacting_features_list1)
        
        print("\n\nStarting sequence diagram analysis per safety feature...")
        all_sa_propertyISids_set, all_sa_propertyISid_name_dict, all_sa_componentlifelineID_set, all_sa_objectlifelineID_name_dict, all_sa_objectlifelineID_componentID_dict = self.objectlifelines_all_featureset(self.safety_feature_list, self.safeatureID_name_dict, iterator_type)
        feature_type_flag = 1 #set this flag to 1 if the feature is a safety feature
        
        for feature in self.safety_feature_list:
            pri_interacting_features_list2, interacting_features_list2 = self.sd_analysis_per_feature(feature_type_flag, feature, self.safeatureID_name_dict, all_sa_objectlifelineID_componentID_dict, list(all_sa_componentlifelineID_set), all_sa_objectlifelineID_name_dict, self.sa_feature_componentID_dict, iterator_type)
            all_pri_interacting_features_list.extend(pri_interacting_features_list2)
            all_sec_interacting_features_list.extend(interacting_features_list2)
        all_pri_interacting_features_list.sort()
        all_sec_interacting_features_list.sort()
        
        all_pri_interacting_features_updatedlist = list(all_pri_interacting_features_list for all_pri_interacting_features_list, _ in itertools.groupby(all_pri_interacting_features_list))
        all_sec_interacting_features_updatedlist = list(all_sec_interacting_features_list for all_sec_interacting_features_list, _ in itertools.groupby(all_sec_interacting_features_list))
        print("Summary! len(all_pri_interact_FInames_updatedlist): ", len(all_pri_interacting_features_updatedlist), " len(all_sec_interact_FInames_updatedlist): ", len(all_sec_interacting_features_updatedlist))
        print("\n\n")
        print(tabulate(all_pri_interacting_features_updatedlist, headers = ["primary_src_feature", "primary_interacting_dst_feature"], tablefmt = 'grid'))
        print("\n\n")
        print(tabulate(all_sec_interacting_features_updatedlist, headers = ["secondary_src_feature", "secondary_interacting_dst_feature"], tablefmt = 'grid'))
    
def main():
    Pa = Parent()
    iterator_type = 2 #configure the search to be performed in the appropriate input file (for our case study, it was input xmi file 2)
    print("\nGetting security features...")
    GSeF = GetSecurityFeatures(security_feature_pkg_list)
    se_feature_pkg_dict = GSeF.get_security_feature_name(iterator_type)
    print("\nsecurity_feature_list: ", security_feature_pkg_list, "\n\nse_feature_pkg_dict: ", se_feature_pkg_dict)
    
    print("\n\nGetting safety features...")
    GSaF = GetSafetyFeatures(ecu_safety_main_pkg_path)
    safety_feature_pkg_list, sa_feature_pkg_dict = GSaF.get_safety_feature(iterator_type)
    print("\nsafety_feature_list: ", safety_feature_pkg_list, "\n\nsa_feature_pkg_dict: ", sa_feature_pkg_dict)
    
    print("\nGetting security components...")
    se_feature_componentID_dict, all_security_componentID_set, all_security_componentID_name_dict, component_ID_stereotype_dict, se_supplierID_componentID_dict, se_activity_dict, se_activity_supplierID_dict, se_featureID_activityID_dict = Pa.get_feature_components(security_feature_pkg_list, se_feature_pkg_dict, iterator_type)
    print("\nlen(all_security_componentID_set)", len(all_security_componentID_set), " all_security_componentID_set: ", all_security_componentID_set, "\nse_feature_componentID_dict: ", se_feature_componentID_dict, "\nse_featureID_activityID_dict: ", se_featureID_activityID_dict, "\nse_activity_dict: ", se_activity_dict)
    
    print("\n\nGetting safety components...")
    sa_feature_componentID_dict, all_safety_componentID_set, all_safety_componentID_name_dict, all_safety_componentID_stereotype_dict, sa_supplierID_componentID_dict, sa_activity_dict, sa_activity_supplierID_dict, sa_featureID_activityID_dict = Pa.get_feature_components(safety_feature_pkg_list, sa_feature_pkg_dict, iterator_type)
    print("\nlen(all_safety_componentID_set): ", len(all_safety_componentID_set), " all_safety_componentID_set: ", all_safety_componentID_set, "\nsa_feature_componentID_dict: ", sa_feature_componentID_dict, "\nsa_featureID_activityID_dict: ", sa_featureID_activityID_dict, "\nsa_activity_dict: ", sa_activity_dict)
    
    print("\n\nGetting components that are both safety and security relevant...")
    GSaSeCSWC = GetSaSeCommonSWC(all_security_componentID_set, all_safety_componentID_set, all_security_componentID_name_dict)
    common_elements_set, common_element_name_dict = GSaSeCSWC.get_common_set_elements()
    print("\nlen(common_elements_set): ", len(common_elements_set), " common_elements_set: ", common_elements_set, "\ncommon_element_name_dict: ", common_element_name_dict)
    
    print("\n\nData preparation - getting mapping of safety and security activityID_componentID_dict")
    se_activityID_componentsID_dict = Pa.get_activity_component_mapping(se_activity_supplierID_dict, se_supplierID_componentID_dict)
    sa_activityID_componentsID_dict = Pa.get_activity_component_mapping(sa_activity_supplierID_dict, sa_supplierID_componentID_dict)    
    print("\nse_activityID_componentsID_dict: ", se_activityID_componentsID_dict, "\nsa_activityID_componentsID_dict: ", sa_activityID_componentsID_dict)
    
    print("\n\nPerforming sequence diagram analysis per feature to identify interaction between safety and security components")
    sdA = SDanalysisOfSeandSaFeatures(security_feature_pkg_list, se_feature_pkg_dict, safety_feature_pkg_list, sa_feature_pkg_dict, list(all_security_componentID_set), list(all_safety_componentID_set), list(common_elements_set), se_feature_componentID_dict, sa_feature_componentID_dict, se_activityID_componentsID_dict, sa_activityID_componentsID_dict, se_featureID_activityID_dict, sa_featureID_activityID_dict, se_activity_dict, sa_activity_dict)
    sdA.sd_analysis_sasefeatures(iterator_type)
    
    stop = timeit.default_timer()
    print('Time: ', stop - start)

if __name__ == "__main__":
    main()