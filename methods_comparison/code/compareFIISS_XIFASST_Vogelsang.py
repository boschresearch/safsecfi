# Copyright (c) 2024 Robert Bosch GmbH
# SPDX-License-Identifier: MIT

import numpy as np
import matplotlib.pyplot as plt
from matplotlib_venn import venn3

######################################Configurable inputs#####################################
#--------------------------The Vogelsang (Case1) method-------------------------------------------
#List of Vogelsang-Case1 output
VogelsangCase1_output = [] #Specify a list of feature interactions (FIs) in the format [feature1, feature2] obtained by Vogelsang case 1
#List of Vogelsang-Case1 FIoIs
VogelsangCase1_FIoIs = [] #Specify a list of feature interactions of interest (FIoIs) in the format [feature1, feature2] obtained by Vogelsang case 1
print("VogelsangCase1! len(VogelsangCase1_output): ", len(VogelsangCase1_output), " len(VogelsangCase1_FIoIs): ", len(VogelsangCase1_FIoIs))

#--------------------------The Vogelsang (Case2) method-------------------------------------------
#List of Vogelsang-Case2 output
VogelsangCase2_output = [] #Specify a list of feature interactions (FIs) in the format [feature1, feature2] obtained by Vogelsang case 2
#List of Vogelsang-Case2 FIoIs
VogelsangCase2_FIoIs = [] #Specify a list of feature interactions of interest (FIoIs) in the format [feature1, feature2] obtained by Vogelsang case 2
print("\nVogelsangCase2! len(VogelsangCase2_output): ", len(VogelsangCase2_output), " len(VogelsangCase2_FIoIs): ", len(VogelsangCase2_FIoIs))

#--------------------------The FIISS method (p = 1) ----------------------------------------------
FIISSp1_output = [] #Specify a list of feature interactions (FIs) in the format [feature1, feature2] obtained by FIISS for the interaction path length = 1
FIISSp1_FIoIs = [] #Specify a list of feature interactions of interest (FIoIs) in the format [feature1, feature2] obtained by FIISS for the interaction path length = 1
print("\nFIISS (p = 1)! len(FIISSp1_output): ", len(FIISSp1_output), " FIISSp1_FIoIs: ", len(FIISSp1_FIoIs))

#--------------------------The X-I-FASST (p = 1) method-------------------------------------------
XIFASSTp1_output = [] #Specify a list of feature interactions (FIs) in the format [feature1, feature2] obtained by X-I-FASST for the interaction path length = 1
XIFASSTp1_FIoIs = [] #Specify a list of feature interactions of interest (FIoIs) in the format [feature1, feature2] obtained byX-I-FASST for the interaction path length = 1
print("\nXIFASST (p = 1)! len(XIFASSTp1_output): ", len(XIFASSTp1_output), " len(XIFASSTp1_FIoIs): ", len(XIFASSTp1_FIoIs))

#--------------------------The FIISS method-------------------------------------------
#List of FIISS output
FIISS_output = [] #Specify a list of feature interactions (FIs) in the format [feature1, feature2] obtained by FIISS for the interaction path length = None

#List of FIISS FIoIs
FIISS_FIoIs = [] #Specify a list of feature interactions of interest (FIoIs) in the format [feature1, feature2] obtained by FIISS for the interaction path length = None
print("\nFIISS! len(FIISS_output): ", len(FIISS_output), " len(FIISS_FIoIs): ", len(FIISS_FIoIs))

#--------------------------The X-I-FASST (p = 2) method-------------------------------------------
#List of XIFASST output (primary + secondary)
XIFASST_p2_output = [] #Specify a list of feature interactions (FIs) in the format [feature1, feature2] obtained by X-I-FASST for the interaction path length = 2

#List of XIFASST FIoIs (primary + secondary)
XIFASST_p2_FIoIs = [] #Specify a list of feature interactions of interest (FIoIs) in the format [feature1, feature2] obtained byX-I-FASST for the interaction path length = 2
print("\nXIFASST (p = 2)! len(XIFASST_p2_output): ", len(XIFASST_p2_output), " len(XIFASST_p2_FIoIs): ", len(XIFASST_p2_FIoIs))

#--------------------------The X-I-FASST (p = 4) method-------------------------------------------
#List of XIFASST output (primary + secondary)
XIFASST_p4_output = [] #Specify a list of feature interactions (FIs) in the format [feature1, feature2] obtained by X-I-FASST for the interaction path length = 4

#List of XIFASST FIoIs (primary + secondary)
XIFASST_p4_FIoIs = [] #Specify a list of feature interactions of interest (FIoIs) in the format [feature1, feature2] obtained byX-I-FASST for the interaction path length = 4
print("\nXIFASST (p = 4)! len(XIFASST_p4_output): ", len(XIFASST_p4_output), " len(XIFASST_p4_FIoIs): ", len(XIFASST_p4_FIoIs))
##############################################################################################

#-----------------------------Functions for comparing the methods------------------------------------------------
def get_list_of_tuples(listoflists):
    "Convert a list of lists to a list of tuples"
    listoftuples = []
    for element in listoflists:
        element_tuple = tuple(element)
        if element_tuple not in listoftuples:
            listoftuples.append(element_tuple)
    return listoftuples

def get_intersect_diff_of_2lists(list1, list2):
    "For two lists given as inputs, find 1) elements common to both lists, 2) elements uniquely found by first list 3) elements uniquely found by second list."
    unique_elements_list1 = []
    unique_elements_list2 = []
    
    #Finding elements common in list1 & list2
    common_elements_list = get_intersection_of_2lists(list1, list2)
    
    #Finding elements uniquely found by list1 in comparison to list2
    for element in list1:
        if element not in common_elements_list:
            if element not in unique_elements_list1:
                unique_elements_list1.append(element)
    
    #Finding elements uniquely found by list2 in comparison to list1
    for element in list2:
        if element not in common_elements_list:
            if element not in unique_elements_list2:
                unique_elements_list2.append(element)
    
    return common_elements_list, unique_elements_list1, unique_elements_list2

def get_intersection_of_2lists(list1, list2):
    "For the given lists as inputs, find the elements that are common in these two lists."
    common_in_list1and2 = []
    for FI in list1:
        if FI in list2:
            if FI not in common_in_list1and2:
                common_in_list1and2.append(FI)
    return common_in_list1and2

def get_intersection_of_3lists(list1, list2, list3):
    "For the given three lists as inputs, find the elements that are common in these three lists."
    common_in_list1and2 = []
    common_in_list1_2_3 = []
    for FI in list1:
        if FI in list2:
            if FI not in common_in_list1and2:
                common_in_list1and2.append(FI)
    if len(common_in_list1and2) != 0:
        for FI in common_in_list1and2:
            if FI in list3:
                if FI not in common_in_list1_2_3:
                    common_in_list1_2_3.append(FI)
    else:
        common_in_list1_2_3 = []
    return common_in_list1_2_3

def get_intersection2lists_venn(common_elements_2lists, common_elements_3lists):
    "[Venn diagram for 3 sets] For the common elements between 2 lists (A∩B), remove the elements that are common between 3 lists (A∩B∩C)"
    venn_commonelements2lists = []
    for element in common_elements_2lists:
        if element not in common_elements_3lists:
            if element not in venn_commonelements2lists:
                venn_commonelements2lists.append(element)
    return venn_commonelements2lists
    
def get_uniqueelements_vennof3sets(list1, overlap_oflist1_withlist2, overlap_oflist1_withlist3, overlap_list1_2_3):
    "[Venn diagram for 3 sets] For the given overlap of (set 1 with set 2), of (set 1 with set 3), and of (set 1,2, and 3), find the unique elements found by set 1"
    unique_elements_in_list1 = []
    for FI in list1:
        if FI not in overlap_oflist1_withlist2 and FI not in overlap_oflist1_withlist3 and FI not in overlap_list1_2_3:
            if FI not in unique_elements_in_list1:
                unique_elements_in_list1.append(FI)
    return unique_elements_in_list1

#---------------------------------------------------------------------------------------------------------------------------
#---------------FIoIs intersection & unique FIoIs between FIISS & XIFASST methods-------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
#FIoIs intersection & unique FIoIs between FIISS & XIFASST (p = 2) methods
print("\nComparing FIISS & X-IFASST (p = 2) methods!")
print("Debug! len(FIISS_FIoIs): ", len(FIISS_FIoIs), " len(XIFASST_p2_FIoIs): ", len(XIFASST_p2_FIoIs))
commonFIISS_XIFASSTp2_list, unique_FIISS_FIoIs_list, unique_XIFASSTp2_FIoIs_list = get_intersect_diff_of_2lists(FIISS_FIoIs, XIFASST_p2_FIoIs)
print("Intersection between FIISS & XIFASST (p = 2): ", len(commonFIISS_XIFASSTp2_list), "\nunique_FIISS_FIoIs wrt XIFASST: ", len(unique_FIISS_FIoIs_list), "\nunique_XIFASST_p2_FIoIs wrt FIISS: ", len(unique_XIFASSTp2_FIoIs_list))

#FIoIs intersection & unique FIoIs between FIISS & XIFASST (p = 4) methods
print("\nComparing FIISS & X-IFASST (p = 4) methods!")
print("Debug! len(FIISS_FIoIs): ", len(FIISS_FIoIs), " len(XIFASST_p4_FIoIs): ", len(XIFASST_p4_FIoIs))
commonFIISS_XIFASSTp4_list, unique_FIISS_FIoIs_list, unique_XIFASSTp4_FIoIs_list = get_intersect_diff_of_2lists(FIISS_FIoIs, XIFASST_p4_FIoIs)
print("Intersection between FIISS & XIFASST (p = 4): ", len(commonFIISS_XIFASSTp4_list), "\nunique_FIISS_FIoIs wrt XIFASST: ", len(unique_FIISS_FIoIs_list), "\nunique_XIFASST_p4_FIoIs wrt FIISS: ", len(unique_XIFASSTp4_FIoIs_list))

#---------------------------------------------------------------------------------------------------------------------------
#----------------------FIoIs intersection & unique FIoIs between FIISS & Vogelsang methods ---------------------------------
#---------------------------------------------------------------------------------------------------------------------------
#FIoIs intersection & unique FIoI between FIISS & Vogelsang Case 1
print("\nComparing FIISS & Vogelsang Case 1 methods!")
print("Debug! len(FIISS_FIoIs): ", len(FIISS_FIoIs), " len(VogelsangCase1_FIoIs): ", len(VogelsangCase1_FIoIs))
commonFIISS_VCase1_list, unique_FIISS_FIoIs_list, unique_VCase1_FIoIs_list = get_intersect_diff_of_2lists(FIISS_FIoIs, VogelsangCase1_FIoIs)
print("Intersection between FIISS & Vogelsang Case 1: ", len(commonFIISS_VCase1_list), "\nunique_FIISS_FIoIs wrt Vogelsang Case 1: ", len(unique_FIISS_FIoIs_list), "\nunique_VogelsangCase1_FIoIs wrt FIISS: ", len(unique_VCase1_FIoIs_list))

#FIoIs intersection & unique FIoI between FIISS & Vogelsang Case 2
print("\nComparing FIISS & Vogelsang Case 2 methods!")
print("Debug! len(FIISS_FIoIs): ", len(FIISS_FIoIs), " len(VogelsangCase2_FIoIs): ", len(VogelsangCase2_FIoIs))
commonFIISS_VCase2_list, unique_FIISS_FIoIs_list, unique_VCase2_FIoIs_list = get_intersect_diff_of_2lists(FIISS_FIoIs, VogelsangCase2_FIoIs)
print("Intersection between FIISS & Vogelsang Case 2: ", len(commonFIISS_VCase2_list), "\nunique_FIISS_FIoIs wrt Vogelsang Case 2: ", len(unique_FIISS_FIoIs_list), "\nunique_VogelsangCase2_FIoIs wrt FIISS: ", len(unique_VCase2_FIoIs_list))

#---------------------------------------------------------------------------------------------------------------------------
#----------------------FIoIs intersection & unique FIoIs between XIFASST & Vogelsang methods -------------------------------
#---------------------------------------------------------------------------------------------------------------------------
#FIoIs intersection & unique FIoI between XIFASST (p = 2) & Vogelsang Case 1
print("\nComparing XIFASST (p = 2) & Vogelsang Case 1 methods!")
print("Debug! len(XIFASST_p2_FIoIs): ", len(XIFASST_p2_FIoIs), " len(VogelsangCase1_FIoIs): ", len(VogelsangCase1_FIoIs))
commonXIFASSTp2_VCase1_list, unique_XIFASSTp2_FIoIs_list, unique_VCase1_FIoIs_list = get_intersect_diff_of_2lists(XIFASST_p2_FIoIs, VogelsangCase1_FIoIs)
print("Intersection between XIFASST (p = 2) & Vogelsang Case 1: ", len(commonXIFASSTp2_VCase1_list), "\nunique_XIFASST_FIoIs wrt Vogelsang Case 1: ", len(unique_XIFASSTp2_FIoIs_list), "\nunique_VogelsangCase1_FIoIs wrt XIFASST: ", len(unique_VCase1_FIoIs_list))

#FIoIs intersection & unique FIoI between XIFASST (p = 2) & Vogelsang Case 2
print("\nComparing XIFASST (p = 2) & Vogelsang Case 2 methods!")
print("Debug! len(XIFASST_p2_FIoIs): ", len(XIFASST_p2_FIoIs), " len(VogelsangCase2_FIoIs): ", len(VogelsangCase2_FIoIs))
commonXIFASSTp2_VCase2_list, unique_XIFASSTp2_FIoIs_list, unique_VCase2_FIoIs_list = get_intersect_diff_of_2lists(XIFASST_p2_FIoIs, VogelsangCase2_FIoIs)
print("Intersection between XIFASST (p = 2) & Vogelsang Case 2: ", len(commonXIFASSTp2_VCase2_list), "\nunique_XIFASST_FIoIs wrt Vogelsang Case 2: ", len(unique_XIFASSTp2_FIoIs_list), "\nunique_VogelsangCase2_FIoIs wrt XIFASST: ", len(unique_VCase2_FIoIs_list))

#FIoIs intersection & unique FIoI between XIFASST (p = 4) & Vogelsang Case 1
print("\nComparing XIFASST (p = 4) & Vogelsang Case 1 methods!")
print("Debug! len(XIFASST_p4_FIoIs): ", len(XIFASST_p4_FIoIs), " len(VogelsangCase1_FIoIs): ", len(VogelsangCase1_FIoIs))
commonXIFASSTp4_VCase1_list, unique_XIFASSTp4_FIoIs_list, unique_VCase1_FIoIs_list = get_intersect_diff_of_2lists(XIFASST_p4_FIoIs, VogelsangCase1_FIoIs)
print("Intersection between XIFASST (p = 4) & Vogelsang Case 1: ", len(commonXIFASSTp4_VCase1_list), "\nunique_XIFASST_FIoIs wrt Vogelsang Case 1: ", len(unique_XIFASSTp4_FIoIs_list), "\nunique_VogelsangCase1_FIoIs wrt XIFASST: ", len(unique_VCase1_FIoIs_list))

#FIoIs intersection & unique FIoI between XIFASST (p = 4) & Vogelsang Case 2
print("\nComparing XIFASST (p = 4) & Vogelsang Case 2 methods!")
print("Debug! len(XIFASST_p4_FIoIs): ", len(XIFASST_p4_FIoIs), " len(VogelsangCase2_FIoIs): ", len(VogelsangCase2_FIoIs))
commonXIFASSTp4_VCase2_list, unique_XIFASSTp4_FIoIs_list, unique_VCase2_FIoIs_list = get_intersect_diff_of_2lists(XIFASST_p4_FIoIs, VogelsangCase2_FIoIs)
print("Intersection between XIFASST (p = 4) & Vogelsang Case 2: ", len(commonXIFASSTp4_VCase2_list), "\nunique_XIFASST_FIoIs wrt Vogelsang Case 2: ", len(unique_XIFASSTp4_FIoIs_list), "\nunique_VogelsangCase2_FIoIs wrt XIFASST: ", len(unique_VCase2_FIoIs_list))

#---------------------------------------------------------------------------------------------------------------------------
#---------------FIoIs intersection between FIISS (p=1), XIFASST (p=1) & Vogelsang (p=1) methods-----------------------------
#---------------------------------------------------------------------------------------------------------------------------
print("\n[Venn diagram1 (p1)]Finding direct FIoIs common in FIISS, XIFASST & Vogelsang Case 1 methods for p=1 for all the three methods.")
FIISSp1_FIoIs_listoftuples = get_list_of_tuples(FIISSp1_FIoIs)
XIFASSTp1_FIoIs_listoftuples = get_list_of_tuples(XIFASSTp1_FIoIs)
VogelsangCase1_FIoIs_listoftuples = get_list_of_tuples(VogelsangCase1_FIoIs)
FIISSp1_FIoIs_set = set(FIISSp1_FIoIs_listoftuples)
XIFASSTp1_FIoIs_set = set(XIFASSTp1_FIoIs_listoftuples)
VogelsangCase1_FIoIs_set = set(VogelsangCase1_FIoIs_listoftuples)
venn3([FIISSp1_FIoIs_set, XIFASSTp1_FIoIs_set, VogelsangCase1_FIoIs_set], ('FIISS', 'X-I-FASST', 'Vogelsang Case1'))
plt.show

print("Debug! len(FIISSp1_FIoIs): ", len(FIISSp1_FIoIs), " len(XIFASSTp1_FIoIs): ", len(XIFASSTp1_FIoIs), " len(VogelsangCase1_FIoIs): ", len(VogelsangCase1_FIoIs))
commonFIISS_XIFASST_VCase1_list = get_intersection_of_3lists(FIISSp1_FIoIs, XIFASSTp1_FIoIs, VogelsangCase1_FIoIs)
print("Intersection between FIISS, XIFASST & Vogelsang Case 1 (p=1 for all 3 methods): ", len(commonFIISS_XIFASST_VCase1_list), "\nare: ", commonFIISS_XIFASST_VCase1_list)
print("Calculations for Venn diagram1 (p1)!")

#Common FIs between FIISS (p=1) & Vogelsang case1 excluding intersection(FIISS (p=1), XIFASST (p=1) & Vogelsang Case 1)
commonFIISSp1_Vcase1, unique_FIISSp1_FIoIs_list, unique_VCase1p1_FIoIs_list = get_intersect_diff_of_2lists(FIISSp1_FIoIs, VogelsangCase1_FIoIs)
venn1p1_commonFIISS_Vcase1 = get_intersection2lists_venn(commonFIISSp1_Vcase1, commonFIISS_XIFASST_VCase1_list)
print("Common FIs between FIISS (p=1) & Vogelsang case1 excluding intersection(FIISS (p=1), XIFASST (p=1) & Vogelsang Case 1): ", len(venn1p1_commonFIISS_Vcase1))

#Common FIs between FIISS (p=1) & XIFASST (p=1) excluding intersection(FIISS (p=1), XIFASST (p=1) & Vogelsang Case 1)
commonFIISSp1_XIFASSTp1, unique_FIISSp1_FIoIs_list, unique_XIFASSTp1_FIoIs_list  = get_intersect_diff_of_2lists(FIISSp1_FIoIs, XIFASSTp1_FIoIs)
venn1p1_commonFIISS_XIFASST = get_intersection2lists_venn(commonFIISSp1_XIFASSTp1, commonFIISS_XIFASST_VCase1_list)
print("Common FIs between FIISS (p=1) & XIFASST (p=1) excluding intersection(FIISS (p=1), XIFASST (p=1) & Vogelsang Case 1): ", len(venn1p1_commonFIISS_XIFASST))

#Common FIs between XIFASST (p=1) & Vogelsang Case 1 excluding intersection(FIISS (p=1), XIFASST (p=1) & Vogelsang Case 1)
commonXIFASSTp1_Vcase1, unique_XIFASSTp1_FIoIs_list, unique_VCase1p1_FIoIs_list  = get_intersect_diff_of_2lists(XIFASSTp1_FIoIs, VogelsangCase1_FIoIs)
venn1p1_commonXIFASST_Vcase1 = get_intersection2lists_venn(commonXIFASSTp1_Vcase1, commonFIISS_XIFASST_VCase1_list)
print("Common FIs between XIFASST (p=1) & Vogelsang Case 1 excluding intersection(FIISS (p=1), XIFASST (p=1) & Vogelsang Case 1): ", len(venn1p1_commonXIFASST_Vcase1))

#Unique FIs found by FIISS (p=1) wrt XIFASST (p=1) & Vogelsang Case 1
venn1p1_uniqueFIISS = get_uniqueelements_vennof3sets(FIISSp1_FIoIs, venn1p1_commonFIISS_Vcase1, venn1p1_commonFIISS_XIFASST, commonFIISS_XIFASST_VCase1_list)
print("Unique FIs found by FIISS (p=1) wrt XIFASST (p=1) & Vogelsang Case 1: ", len(venn1p1_uniqueFIISS))

#Unique FIs found by XIFASST (p=1) wrt FIISS (p=1) & Vogelsang Case 1
venn1p1_uniqueXIFASSTp1 = get_uniqueelements_vennof3sets(XIFASSTp1_FIoIs, venn1p1_commonFIISS_XIFASST, commonXIFASSTp1_Vcase1, commonFIISS_XIFASST_VCase1_list)
print("Unique FIs found by XIFASST (p=1) wrt FIISS (p=1) & Vogelsang Case 1: ", len(venn1p1_uniqueXIFASSTp1))

#Unique FIs found by Vogelsang Case 1 wrt FIISS (p=1) & XIFASST (p=1)
venn1p1_uniqueVcase1 = get_uniqueelements_vennof3sets(VogelsangCase1_FIoIs, venn1p1_commonFIISS_Vcase1, commonXIFASSTp1_Vcase1, commonFIISS_XIFASST_VCase1_list)
print("Unique FIs found by Vogelsang Case 1 wrt FIISS (p=1) & XIFASST (p=1): ", len(venn1p1_uniqueVcase1))

print("\n[Venn diagram2 (p1)]Finding direct FIoIs common in FIISS, XIFASST & Vogelsang Case 2 methods for p=1 for all the three methods.")
print("Debug! len(FIISSp1_FIoIs): ", len(FIISSp1_FIoIs), " len(XIFASSTp1_FIoIs): ", len(XIFASSTp1_FIoIs), " len(VogelsangCase2_FIoIs): ", len(VogelsangCase2_FIoIs))
commonFIISS_XIFASST_VCase2_list = get_intersection_of_3lists(FIISSp1_FIoIs, XIFASSTp1_FIoIs, VogelsangCase2_FIoIs)
print("Intersection between FIISS, XIFASST & Vogelsang Case 2 (p=1 for all 3 methods): ", len(commonFIISS_XIFASST_VCase2_list), "\nare: ", commonFIISS_XIFASST_VCase2_list)
print("Calculations for Venn diagram2 (p1)!")

#Common FIs between FIISS (p=1) & Vogelsang Case 2 excluding intersection(FIISS (p=1), XIFASST (p=1) & Vogelsang Case 2)
commonFIISSp1_Vcase2, unique_FIISSp1_FIoIs_list, unique_VCase2p1_FIoIs_list  = get_intersect_diff_of_2lists(FIISSp1_FIoIs, VogelsangCase2_FIoIs)
venn2p1_commonFIISS_Vcase2 = get_intersection2lists_venn(commonFIISSp1_Vcase2, commonFIISS_XIFASST_VCase2_list)
print("Common FIs between FIISS (p=1) & Vogelsang Case 2 excluding intersection(FIISS (p=1), XIFASST (p=1) & Vogelsang Case 2): ", len(venn2p1_commonFIISS_Vcase2))

#Common FIs between FIISS (p=1) & XIFASST (p=1) excluding intersection(FIISS (p=1), XIFASST (p=1) & Vogelsang Case 2)
commonFIISSp1_XIFASSTp1, unique_FIISSp1_FIoIs_list, unique_XIFASSTp1_FIoIs_list  = get_intersect_diff_of_2lists(FIISSp1_FIoIs, XIFASSTp1_FIoIs)
venn2p1_commonFIISS_XIFASST = get_intersection2lists_venn(commonFIISSp1_XIFASSTp1, commonFIISS_XIFASST_VCase2_list)
print("Common FIs between FIISS (p=1) & XIFASST (p=1) excluding intersection(FIISS (p=1), XIFASST (p=1) & Vogelsang Case 2): ", len(venn2p1_commonFIISS_XIFASST))

#Common FIs between XIFASST (p=1) & Vogelsang Case 2 excluding intersection(FIISS (p=1), XIFASST (p=1) & Vogelsang Case 2)
commonXIFASSTp1_Vcase2, unique_XIFASSTp1_FIoIs_list, unique_VCase2p1_FIoIs_list  = get_intersect_diff_of_2lists(XIFASSTp1_FIoIs, VogelsangCase2_FIoIs)
venn2p1_commonXIFASST_Vcase2 = get_intersection2lists_venn(commonXIFASSTp1_Vcase2, commonFIISS_XIFASST_VCase2_list)
print("Common FIs between XIFASST (p=1) & Vogelsang Case 2 excluding intersection(FIISS (p=1), XIFASST (p=1) & Vogelsang Case 2): ", len(venn2p1_commonXIFASST_Vcase2))

#Unique FIs found by FIISS (p=1) wrt XIFASST (p=1) & Vogelsang Case 2
venn2p1_uniqueFIISS = get_uniqueelements_vennof3sets(FIISSp1_FIoIs, venn2p1_commonFIISS_XIFASST, venn2p1_commonFIISS_Vcase2, commonFIISS_XIFASST_VCase2_list)
print("Unique FIs found by FIISS (p=1) wrt XIFASST (p=1) & Vogelsang Case 2: ", len(venn2p1_uniqueFIISS))

#Unique FIs found by XIFASST (p=1) wrt FIISS (p=1) & Vogelsang Case 2
venn2p1_uniqueXIFASST = get_uniqueelements_vennof3sets(XIFASSTp1_FIoIs, venn2p1_commonFIISS_XIFASST, venn2p1_commonXIFASST_Vcase2, commonFIISS_XIFASST_VCase2_list)
print("Unique FIs found by XIFASST (p=1) wrt FIISS (p=1) & Vogelsang Case 2: ", len(venn2p1_uniqueXIFASST))

#Unique FIs found by Vogelsang Case 2 wrt FIISS (p=1) & XIFASST (p=1)
venn2p1_uniqueVcase2 = get_uniqueelements_vennof3sets(VogelsangCase2_FIoIs, venn2p1_commonFIISS_Vcase2, venn2p1_commonXIFASST_Vcase2, commonFIISS_XIFASST_VCase2_list)
print("Unique FIs found by Vogelsang Case 2 wrt FIISS (p=1) & XIFASST (p=1): ", len(venn2p1_uniqueVcase2))

#---------------------------------------------------------------------------------------------------------------------------
#--------------------------FIoIs intersection between FIISS, XIFASST & Vogelsang methods------------------------------------
#---------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------Venn diagram 1----------------------------------------------------------------
#FIoIs intersection between FIISS, XIFASST (p = 2) & Vogelsang Case 1
print("\n[Venn diagram 1]Finding FIoIs common in FIISS, XIFASST (p = 2) & Vogelsang Case 1 methods.")
print("Debug! len(FIISS_FIoIs): ", len(FIISS_FIoIs), " len(XIFASST_p2_FIoIs): ", len(XIFASST_p2_FIoIs), " len(VogelsangCase1_FIoIs): ", len(VogelsangCase1_FIoIs))
commonFIISS_XIFASSTp2_VCase1_list = get_intersection_of_3lists(FIISS_FIoIs, XIFASST_p2_FIoIs, VogelsangCase1_FIoIs)
print("Intersection between FIISS, XIFASST (p = 2) & Vogelsang Case 1: ", len(commonFIISS_XIFASSTp2_VCase1_list), "\nare: ", commonFIISS_XIFASSTp2_VCase1_list)
print("Calculations for Venn diagram 1!")

#Common FIs between FIISS & Vogelsang case1 excluding intersection(FIISS, XIFASST (p = 2) & Vogelsang Case 1)
venn1_commonFIISS_VCase1 = get_intersection2lists_venn(commonFIISS_VCase1_list, commonFIISS_XIFASSTp2_VCase1_list)
print("Common FIs between FIISS & Vogelsang case1 excluding intersection(FIISS, XIFASST (p = 2) & Vogelsang Case 1): ", len(venn1_commonFIISS_VCase1))

#Common FIs between FIISS & XIFASST (p = 2) excluding intersection(FIISS, XIFASST (p = 2) & Vogelsang Case 1)
venn1_commonFIISS_XIFASSTp2 = get_intersection2lists_venn(commonFIISS_XIFASSTp2_list, commonFIISS_XIFASSTp2_VCase1_list)
print("Common FIs between FIISS & XIFASST (p = 2) excluding intersection(FIISS, XIFASST (p = 2) & Vogelsang Case 1)", len(venn1_commonFIISS_XIFASSTp2))

#Common FIs between XIFASST (p = 2) & Vogelsang Case 1 excluding intersection(FIISS, XIFASST (p = 2) & Vogelsang Case 1)
venn1_XIFASSTp2_VCase1 = get_intersection2lists_venn(commonXIFASSTp2_VCase1_list, commonFIISS_XIFASSTp2_VCase1_list)
print("Common FIs between XIFASST (p = 2) & Vogelsang Case 1 excluding intersection(FIISS, XIFASST (p = 2) & Vogelsang Case 1)", len(venn1_XIFASSTp2_VCase1))

#Unique FIs found by FIISS wrt XIFASST (p = 2) & Vogelsang Case 1
venn1_uniqueFIISS = get_uniqueelements_vennof3sets(FIISS_FIoIs, venn1_commonFIISS_VCase1, venn1_commonFIISS_XIFASSTp2, commonFIISS_XIFASSTp2_VCase1_list)
print("Unique FIs found by FIISS wrt XIFASST (p = 2) & Vogelsang Case 1: ", len(venn1_uniqueFIISS))

#Unique FIs found by XIFASST (p = 2) wrt FIISS & Vogelsang Case 1
venn1_uniqueXIFASSTp2 = get_uniqueelements_vennof3sets(XIFASST_p2_FIoIs, venn1_commonFIISS_XIFASSTp2, venn1_XIFASSTp2_VCase1, commonFIISS_XIFASSTp2_VCase1_list)
print("Unique FIs found by XIFASST (p = 2) wrt FIISS & Vogelsang Case 1: ", len(venn1_uniqueXIFASSTp2))

#Unique FIs found by Vogelsang Case 1 wrt FIISS & XIFASST (p = 2)
venn1_uniqueVCase1 = get_uniqueelements_vennof3sets(VogelsangCase1_FIoIs, venn1_commonFIISS_VCase1, venn1_XIFASSTp2_VCase1, commonFIISS_XIFASSTp2_VCase1_list)
print("Unique FIs found by Vogelsang Case 1 wrt FIISS & XIFASST (p = 2): ", len(venn1_uniqueVCase1))
#---------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------Venn diagram 2----------------------------------------------------------------
#FIoIs intersection between FIISS, XIFASST (p = 2) & Vogelsang Case 2
print("\n[Venn diagram 2]Finding FIoIs common in FIISS, XIFASST (p = 2) & Vogelsang Case 2 methods.")
print("Debug! len(FIISS_FIoIs): ", len(FIISS_FIoIs), " len(XIFASST_p2_FIoIs): ", len(XIFASST_p2_FIoIs), " len(VogelsangCase2_FIoIs): ", len(VogelsangCase2_FIoIs))
commonFIISS_XIFASSTp2_VCase2_list = get_intersection_of_3lists(FIISS_FIoIs, XIFASST_p2_FIoIs, VogelsangCase2_FIoIs)
print("Intersection between FIISS, XIFASST (p = 2) & Vogelsang Case 2: ", len(commonFIISS_XIFASSTp2_VCase2_list), "\nare: ", commonFIISS_XIFASSTp2_VCase2_list)
print("Calculations for Venn diagram 2!")

#Common FIs between FIISS & Vogelsang case2 excluding intersection(FIISS, XIFASST (p = 2) & Vogelsang Case 2)
venn2_commonFIISS_VCase2 = get_intersection2lists_venn(commonFIISS_VCase2_list, commonFIISS_XIFASSTp2_VCase2_list)
print("Common FIs between FIISS & Vogelsang case2 excluding intersection(FIISS, XIFASST (p = 2) & Vogelsang Case 2): ", len(venn2_commonFIISS_VCase2))

#Common FIs between FIISS & XIFASST (p = 2) excluding intersection(FIISS, XIFASST (p = 2) & Vogelsang Case 2)
venn2_commonFIISS_XIFASSTp2 = get_intersection2lists_venn(commonFIISS_XIFASSTp2_list, commonFIISS_XIFASSTp2_VCase2_list)
print("Common FIs between FIISS & XIFASST (p = 2) excluding intersection(FIISS, XIFASST (p = 2) & Vogelsang Case 2): ", len(venn2_commonFIISS_XIFASSTp2))

#Common FIs between XIFASST (p = 2) & Vogelsang case2 excluding intersection(FIISS, XIFASST (p = 2) & Vogelsang Case 2)
venn2_XIFASSTp2_VCase2 = get_intersection2lists_venn(commonXIFASSTp2_VCase2_list, commonFIISS_XIFASSTp2_VCase2_list)
print("Common FIs between XIFASST (p = 2) & Vogelsang case2 excluding intersection(FIISS, XIFASST (p = 2) & Vogelsang Case 2): ", len(venn2_XIFASSTp2_VCase2))

#Unique FIs found by FIISS wrt XIFASST (p = 2) & Vogelsang Case 2
venn2_uniqueFIISS = get_uniqueelements_vennof3sets(FIISS_FIoIs, venn2_commonFIISS_VCase2, venn2_commonFIISS_XIFASSTp2, commonFIISS_XIFASSTp2_VCase2_list)
print("Unique FIs found by FIISS wrt XIFASST (p = 2) & Vogelsang Case 2: ", len(venn2_uniqueFIISS))

#Unique FIs found by XIFASST (p = 2) wrt FIISS & Vogelsang Case 2
venn2_uniqueXIFASSTp2 = get_uniqueelements_vennof3sets(XIFASST_p2_FIoIs, venn2_commonFIISS_XIFASSTp2, venn2_XIFASSTp2_VCase2, commonFIISS_XIFASSTp2_VCase2_list)
print("Unique FIs found by XIFASST (p = 2) wrt FIISS & Vogelsang Case 2: ", len(venn2_uniqueXIFASSTp2))

#Unique FIs found by Vogelsang Case 2 wrt FIISS & XIFASST (p = 2)
venn2_uniqueVCase2 = get_uniqueelements_vennof3sets(VogelsangCase2_FIoIs, venn2_commonFIISS_VCase2, venn2_XIFASSTp2_VCase2, commonFIISS_XIFASSTp2_VCase2_list)
print("Unique FIs found by Vogelsang Case 2 wrt FIISS & XIFASST (p = 2): ", len(venn2_uniqueVCase2))
#---------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------Venn diagram 3----------------------------------------------------------------
#FIoIs intersection between FIISS, XIFASST (p = 4) & Vogelsang Case 1
print("\n[Venn diagram 3]Finding FIoIs common in FIISS, XIFASST (p = 4) & Vogelsang Case 1 methods.")
print("Debug! len(FIISS_FIoIs): ", len(FIISS_FIoIs), " len(XIFASST_p4_FIoIs): ", len(XIFASST_p4_FIoIs), " len(VogelsangCase1_FIoIs): ", len(VogelsangCase1_FIoIs))
commonFIISS_XIFASSTp4_VCase1_list = get_intersection_of_3lists(FIISS_FIoIs, XIFASST_p4_FIoIs, VogelsangCase1_FIoIs)
print("Intersection between FIISS, XIFASST (p = 4) & Vogelsang Case 1: ", len(commonFIISS_XIFASSTp4_VCase1_list), "\nare: ", commonFIISS_XIFASSTp4_VCase1_list)
print("Calculations for Venn diagram 3!")

#Common FIs between FIISS & Vogelsang case1 excluding intersection(FIISS, XIFASST (p = 4) & Vogelsang Case 1)
venn3_commonFIISS_VCase1 = get_intersection2lists_venn(commonFIISS_VCase1_list, commonFIISS_XIFASSTp4_VCase1_list)
print("Common FIs between FIISS & Vogelsang case1 excluding intersection(FIISS, XIFASST (p = 4) & Vogelsang Case 1): ", len(venn3_commonFIISS_VCase1))

#Common FIs between FIISS & XIFASST (p = 4) excluding intersection(FIISS, XIFASST (p = 4) & Vogelsang Case 1)
venn3_commonFIISS_XIFASSTp4 = get_intersection2lists_venn(commonFIISS_XIFASSTp4_list, commonFIISS_XIFASSTp4_VCase1_list)
print("Common FIs between FIISS & XIFASST (p = 4) excluding intersection(FIISS, XIFASST (p = 4) & Vogelsang Case 1): ", len(venn3_commonFIISS_XIFASSTp4))

#Common FIs between XIFASST (p = 4) & Vogelsang case1 excluding intersection(FIISS, XIFASST (p = 4) & Vogelsang Case 1)
venn3_commonXIFASSTp4_VCase1 = get_intersection2lists_venn(commonXIFASSTp4_VCase1_list, commonFIISS_XIFASSTp4_VCase1_list)
print("Common FIs between XIFASST (p = 4) & Vogelsang case1 excluding intersection(FIISS, XIFASST (p = 4) & Vogelsang Case 1): ", len(venn3_commonXIFASSTp4_VCase1))

#Unique FIs found by FIISS wrt XIFASST (p = 4) & Vogelsang Case 1
venn3_uniqueFIISS = get_uniqueelements_vennof3sets(FIISS_FIoIs, venn3_commonFIISS_VCase1, venn3_commonFIISS_XIFASSTp4, commonFIISS_XIFASSTp4_VCase1_list)
print("Unique FIs found by FIISS wrt XIFASST (p = 4) & Vogelsang Case 1: ", len(venn3_uniqueFIISS))

#Unique FIs found by XIFASST (p = 4) wrt FIISS & Vogelsang Case 1
venn3_uniqueXIFASSTp4 = get_uniqueelements_vennof3sets(XIFASST_p4_FIoIs, venn3_commonFIISS_XIFASSTp4, venn3_commonXIFASSTp4_VCase1, commonFIISS_XIFASSTp4_VCase1_list)
print("Unique FIs found by XIFASST (p = 4) wrt FIISS & Vogelsang Case 1: ", len(venn3_uniqueXIFASSTp4))

#Unique FIs found by Vogelsang Case 1 wrt FIISS & XIFASST (p = 4)
venn3_uniqueVCase1 = get_uniqueelements_vennof3sets(VogelsangCase1_FIoIs, venn3_commonFIISS_VCase1, venn3_commonXIFASSTp4_VCase1, commonFIISS_XIFASSTp4_VCase1_list)
print("Unique FIs found by Vogelsang Case 1 wrt FIISS & XIFASST (p = 4): ", len(venn3_uniqueVCase1))
#---------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------Venn diagram 4----------------------------------------------------------------
#FIoIs intersection between FIISS, XIFASST (p = 4) & Vogelsang Case 2
print("\n[Venn diagram 4]Finding FIoIs common in FIISS, XIFASST (p = 4) & Vogelsang Case 2 methods.")
print("Debug! len(FIISS_FIoIs): ", len(FIISS_FIoIs), " len(XIFASST_p4_FIoIs): ", len(XIFASST_p4_FIoIs), " len(VogelsangCase2_FIoIs): ", len(VogelsangCase2_FIoIs))
commonFIISS_XIFASSTp4_VCase2_list = get_intersection_of_3lists(FIISS_FIoIs, XIFASST_p4_FIoIs, VogelsangCase2_FIoIs)
print("Intersection between FIISS, XIFASST (p = 4) & Vogelsang Case 2: ", len(commonFIISS_XIFASSTp4_VCase2_list), "\nare: ", commonFIISS_XIFASSTp4_VCase2_list)
print("Calculations for Venn diagram 4!")

#Common FIs between FIISS & Vogelsang case2 excluding intersection(FIISS, XIFASST (p = 4) & Vogelsang Case 2)
venn4_commonFIISS_VCase2 = get_intersection2lists_venn(commonFIISS_VCase2_list, commonFIISS_XIFASSTp4_VCase2_list)
print("Common FIs between FIISS & Vogelsang case2 excluding intersection(FIISS, XIFASST (p = 4) & Vogelsang Case 2): ", len(venn4_commonFIISS_VCase2))

#Common FIs between FIISS & XIFASST (p = 4) excluding intersection(FIISS, XIFASST (p = 4) & Vogelsang Case 2)
venn4_commonFIISS_XIFASSTp4 = get_intersection2lists_venn(commonFIISS_XIFASSTp4_list, commonFIISS_XIFASSTp4_VCase2_list)
print("Common FIs between FIISS & XIFASST (p = 4) excluding intersection(FIISS, XIFASST (p = 4) & Vogelsang Case 2): ", len(venn4_commonFIISS_XIFASSTp4))

#Common FIs between XIFASST (p = 4) & Vogelsang Case 2 excluding intersection(FIISS, XIFASST (p = 4) & Vogelsang Case 2)
venn4_commonXIFASSTp4_VCase2 = get_intersection2lists_venn(commonXIFASSTp4_VCase2_list, commonFIISS_XIFASSTp4_VCase2_list)
print("Common FIs between XIFASST (p = 4) & Vogelsang Case 2 excluding intersection(FIISS, XIFASST (p = 4) & Vogelsang Case 2): ", venn4_commonXIFASSTp4_VCase2)

#Unique FIs found by FIISS wrt XIFASST (p = 4) & Vogelsang Case 2
venn4_uniqueFIISS = get_uniqueelements_vennof3sets(FIISS_FIoIs, venn4_commonFIISS_XIFASSTp4, venn4_commonFIISS_VCase2, commonFIISS_XIFASSTp4_VCase2_list)
print("Unique FIs found by FIISS wrt XIFASST (p = 4) & Vogelsang Case 2: ", len(venn4_uniqueFIISS))

#Unique FIs found by XIFASST (p = 4) wrt FIISS & Vogelsang Case 2
venn4_uniqueXIFASSTp4 = get_uniqueelements_vennof3sets(XIFASST_p4_FIoIs, venn4_commonFIISS_XIFASSTp4, venn4_commonXIFASSTp4_VCase2, commonFIISS_XIFASSTp4_VCase2_list)
print("Unique FIs found by XIFASST (p = 4) wrt FIISS & Vogelsang Case 2: ", len(venn4_uniqueXIFASSTp4))

#Unique FIs found by Vogelsang Case 2 wrt FIISS & XIFASST (p = 4)
venn4_uniqueVCase2 = get_uniqueelements_vennof3sets(VogelsangCase2_FIoIs, venn4_commonFIISS_VCase2, venn4_commonXIFASSTp4_VCase2, commonFIISS_XIFASSTp4_VCase2_list)
print("Unique FIs found by Vogelsang Case 2 wrt FIISS & XIFASST (p = 4):", len(venn4_uniqueVCase2))
#-------------------------------------------------------------------------------------------------------------------------