#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: Pablo Pacheco
znumber: z5222810
"""

"""
################################   BRIEF GENERAL EXPLANATION ##############################
The program is comprised by:
    1. Definitions of some function to make easier some calculations and for representing
    some constraints.
    2. Creation of some dictonaries, lists and sets to keep the data extracted from the txt file
    3. Reading the text file
    4. Application of the unary constraints on the domain
    5. Creation of the csp
    6. Solution of the csp using the MODIFIED methods in searchGeneric.py:
        - 'search' in class Searcher
        - 'pop' in class frontierPQ
        - 'add_to_frontier' in class AStarSearcher

*Apart from the modified searchGeneric, this program needs: display.py, searchProblem.py,
cspProblem.py, cspConsistency.py and cspExamples
###########################################################################################
"""


import sys
from cspProblem import CSP, Constraint

#These dictionaries 'days' and 'time' are created in order compare different starts time and ending times
days = {'mon':1,'tue':2,'wed':3,'thu':4,'fri':5}
time = {'9am':9,'10am':10,'11am':11,'12pm':12,'1pm':13,'2pm':14,'3pm':15,'4pm':16,'5pm':17}
  

#function that calculate the delay in hours that time A (day and hour) is after time B 
#the function receives strings A and B and return an integer if the delay is positive, 0 otherwise
def delay(a,b):
    #get the day and hour(time) in separate variables
    a_d,a_h=a.split()
    b_d,b_h=b.split()
    #if 'a' is before 'b' there is no delay
    if days[a_d]<days[b_d] or (days[a_d]==days[b_d] and time[a_h]<=time[b_h]):
        return 0
    else:           #There is  a delay, so 'a' is after 'b'
        #check the day delay in hours (24hrs per day)
        day_delay=(days[a_d]-days[b_d])*24
        #check the hours(time) delay
        hour_delay=time[a_h]-time[b_h]
        #return the total delay
        return day_delay + hour_delay
        
#The class CSP is extended (CSPcost) in order to add softConstraints as a new attribute. 
#softConstraints is a list with the soft constraints
class CSPcost(CSP):
    def __init__(self,domains,constraints,softConstraints):
        super().__init__(domains,constraints)
        self.softConstraints=softConstraints


#calculate the end time of a task given the start time (day and hour) and duration...the function return a string
#if the end time is out of working hours the function returns '0' (string)
def end_time(a,duration):
    L=a.split()
    #The task can't start and end in the same day    
    if time[L[1]]+duration> 17:
        return '0'
    if time[L[1]]+duration ==12:
        return (L[0]+' 12pm')
    elif time[L[1]]+ duration >12:
        return (L[0]+' '+str(time[L[1]]+duration-12)+'pm')
    else:
        return (L[0]+' '+str(time[L[1]]+duration)+'am')
    

#The next 4 functions were created to make the future representation of the binary constraints
#task 'a' ends before or when task 'b' starts
def ends_before(a,b):                
    if days[a[1].split()[0]]<days[b[0].split()[0]] or \
        (days[a[1].split()[0]]==days[b[0].split()[0]] and time[a[1].split()[1]]<=time[b[0].split()[1]]):
            return True
    else:
        return False

#task a starts after or when task b ends
def starts_after(a,b):
    if days[a[0].split()[0]]>days[b[1].split()[0]] or \
        (days[a[0].split()[0]]==days[b[1].split()[0]] and time[a[0].split()[1]]>=time[b[1].split()[1]]):
            return True
    else:
        return False

#task a and b are scheduled on the same day
def same_day(a,b):
    if days[a[0].split()[0]] == days[b[0].split()[0]]:
        return True
    else:
        return False
    
#task a starts exactly when task b ends
def starts_at(a,b):
    if a[0]==b[1]:
        return True
    else:
        return False
    

#Dictionaries to keep the possible domain constraints (the key is the name task and the value is the constraint)
domain_cons_day={}
domain_cons_time={}
domain_cons_starts_before={}
domain_cons_starts_after={}
domain_cons_ends_before={}
domain_cons_ends_after={}
domain_cons_starts_in={}
domain_cons_ends_in={}
domain_cons_starts_before_time={}
domain_cons_ends_before_time={}
domain_cons_starts_after_time={}
domain_cons_ends_after_time={}

#Sets for binary contraints. Every set has tuples with the variables associated with the constraint
binary_cons_before=set()
binary_cons_after=set()
binary_cons_same_day=set()
binary_cons_starts_at=set()

#Dictionary to save the soft constraints. Keys are going to be the task names and 
#the values are going to be a triplet with day, time and cost
soft_constraints = {}    

 #dictionary of task durations (task is the key and duration is the value)
task_duration={}   

#Read the file: getting the task name and duration, domain constraints(hard and soft) and binary constraints
file_name=sys.argv[1]
f=open(file_name,"r")
for i in f:
    #omit comments
    if i.startswith("#"):
        continue
    #split every line
    line=i.split()
    if not line:            #omit empty lines
        continue

    #Task name and duration
    if line[0]=="task,":
        if int(line[2])>8:              #A duration greater than 8 gives no possible solution
            print("No solution")
            sys.exit()    
        task_duration[line[1]]=int(line[2])
    
    #Domain constraints
    elif line[0]=="domain,":
        if line[2] != "ends-by":            #if it is True, this is a hard-domain constraint
            if line[2] in days:
                domain_cons_day[line[1]]=line[2]
            elif line[2] in time:
                domain_cons_time[line[1]]=line[2]
            elif line[2] == "starts-in":
                aux=line[4].split("-")          #It is necessary split the time and date which are joined by "-"
                domain_cons_starts_in[line[1]]=((line[3],aux[0]),(aux[1],line[5]))
            elif line[2]=="ends-in":
                aux=line[4].split("-")
                domain_cons_ends_in[line[1]]=((line[3],aux[0]),(aux[1],line[5]))
            elif len(line)==5:              #It is a constraint with day and time
                if line[2]=="starts-before":
                    domain_cons_starts_before[line[1]]=(line[3],line[4])
                elif line[2]=="starts-after":
                    domain_cons_starts_after[line[1]]=(line[3],line[4])
                elif line[2]=="ends-before":
                    domain_cons_ends_before[line[1]]=(line[3],line[4])
                elif line[2]=="ends-after":
                    domain_cons_ends_after[line[1]]=(line[3],line[4])
            else:                           #It is a constraint with just time specification
                if line[2]=="starts-before":
                    domain_cons_starts_before_time[line[1]]=line[3]
                elif line[2]=="starts-after":
                    domain_cons_starts_after_time[line[1]]=line[3]
                elif line[2]=="ends-before":
                    domain_cons_ends_before_time[line[1]]=line[3]
                elif line[2]=="ends-after":
                    domain_cons_ends_after_time[line[1]]=line[3]
                else:
                    print('input error')
        else:
            #soft constraints
            soft_constraints[line[1]]=(line[3],line[4],line[5])
    
    #binary constraints        
    elif line[0]=="constraint,":
        if line[2]=='before':
            binary_cons_before.add((line[1],line[3]))
        elif line[2]=='after':
            binary_cons_after.add((line[1],line[3]))
        elif line[2]=='same-day':
            binary_cons_same_day.add((line[1],line[3]))
        elif line[2]=='starts-at':
            binary_cons_starts_at.add((line[1],line[3]))
        else:
            print('input error')
    
    else:
        print('input error')
                        
f.close()


#Task domain is going to be represented  as a dictionary. The key will be the task name and the value
#a tuple with the start-time and end-time (strings). Maybe if the value had been represented as a tuple
#of tuples it would have been more efficient (every component would have been separated), but the visualization
#with just a tuple is easier to testing
domain={}       
  
#Mmake an empty set for every task and save it in the domain dictionary
for i in task_duration:
    domain[i]=set()

#Applying the duration of the tasks on the domain
for t in task_duration:
    for i in set(days):
        for j in set(time):
            if end_time(i+' '+j,task_duration[t])=='0':
                #this task can't start and end in the same day, so it is not a possible assignment
                continue
            domain[t].add((i+' '+j,end_time(i+' '+j,task_duration[t])))     #add to the domain of task a string with a possible start time

#applying domain constraints
aux_domain=set()          #auxiliar set to make a future intersection with the original domain in order to update the task domain after a constarint
for t in task_duration:
   
    #Day constraint
    if t in domain_cons_day:
        aux_domain.clear()               
        for j in set(time):
            aux_domain.add((domain_cons_day[t]+' '+j, end_time(domain_cons_day[t]+' '+j,task_duration[t]) ))
        domain[t].intersection_update(aux_domain)           #update the domain of task t
        
    #Time constraint
    if t in domain_cons_time:
        aux_domain.clear()
        for i in set(days):
            aux_domain.add((i+' '+domain_cons_time[t],end_time(i+' '+domain_cons_time[t],task_duration[t])))
        domain[t].intersection_update(aux_domain)
        
    #starts-before day and time constraint
    if t in domain_cons_starts_before:
        aux_domain.clear()
        for i in set(days):
            for j in set(time):
                if (days[i] < days[domain_cons_starts_before[t][0]]) or \
                    (days[i]==days[domain_cons_starts_before[t][0]] and time[j]<=time[domain_cons_starts_before[t][1]]):
                    #task starts before or at the requiere day and time (permitted)
                    aux_domain.add((i+' '+j,end_time(i+' '+j, task_duration[t])))
        domain[t].intersection_update(aux_domain)
     
    #starts-after day and time constraint
    if t in domain_cons_starts_after:
        aux_domain.clear()
        for i in set(days):
            for j in set(time):
                if (days[i] > days[domain_cons_starts_after[t][0]]) or \
                    (days[i]==days[domain_cons_starts_after[t][0]] and time[j]>=time[domain_cons_starts_after[t][1]]):
                    #task starts after or at the requiere day and time (permitted)
                    aux_domain.add((i+' '+j,end_time(i+' '+j, task_duration[t])))
        domain[t].intersection_update(aux_domain)
        
    #ends-before day and time constraint
    if t in domain_cons_ends_before:
        aux_domain.clear()
        for i in set(days):
            for j in set(time):
                if end_time(i+' '+j, task_duration[t]) != '0':        #an end time is possible
                    endDay, endHour = end_time(i+' '+j, task_duration[t]).split()         #these variables represent the end day and time for a particular assignment in t
                    if (days[endDay]<days[domain_cons_ends_before[t][0]]) or \
                        (days[endDay]==days[domain_cons_ends_before[t][0]] and time[endHour]<=time[domain_cons_ends_before[t][1]]):
                            #task ends before or at the requiere day and time
                            aux_domain.add((i+' '+j,end_time(i+' '+j, task_duration[t])))
        domain[t].intersection_update(aux_domain)
        
    #ends-after day and time constraint
    if t in domain_cons_ends_after:
        aux_domain.clear()
        for i in set(days):
            for j in set(time):
                if end_time(i+' '+j, task_duration[t]) != '0':        #an end time is possible
                    endDay, endHour = end_time(i+' '+j, task_duration[t]).split()         #these variables represent the end day and time for a particular assignment in t
                    if (days[endDay]>days[domain_cons_ends_after[t][0]]) or \
                        (days[endDay]==days[domain_cons_ends_after[t][0]] and time[endHour]>=time[domain_cons_ends_after[t][1]]):
                            #task ends after or at the requiere day and time
                            aux_domain.add((i+' '+j,end_time(i+' '+j, task_duration[t])))
        domain[t].intersection_update(aux_domain)
        
    #starts-in constraint
    if t in domain_cons_starts_in:
        aux_domain.clear()
        for i in set(days):
            for j in set(time):
                if ( days[i]>days[domain_cons_starts_in[t][0][0]] or \
                    (days[i]==days[domain_cons_starts_in[t][0][0]] and \
                      time[j]>=time[domain_cons_starts_in[t][0][1]]) ) and \
                    ( days[i]<days[domain_cons_starts_in[t][1][0]] or \
                      (days[i]==days[domain_cons_starts_in[t][1][0]] and \
                      time[j]<=time[domain_cons_starts_in[t][1][1]]) ):
                        #the task t start within the requiered time
                        aux_domain.add((i+' '+j,end_time(i+' '+j, task_duration[t])))
        domain[t].intersection_update(aux_domain)
        
    #ends-in constraint
    if t in domain_cons_ends_in:
        aux_domain.clear()
        for i in set(days):
            for j in set(time):
                if end_time(i+' '+j, task_duration[t]) != '0':        #an end time is possible
                    endDay, endHour = end_time(i+' '+j, task_duration[t]).split()
                    if ( days[endDay]>days[domain_cons_ends_in[t][0][0]] or \
                    (days[endDay]==days[domain_cons_ends_in[t][0][0]] and \
                      time[endHour]>=time[domain_cons_ends_in[t][0][1]]) ) and \
                    ( days[endDay]<days[domain_cons_ends_in[t][1][0]] or \
                      (days[endDay]==days[domain_cons_ends_in[t][1][0]] and \
                      time[endHour]<=time[domain_cons_ends_in[t][1][1]]) ):
                        #the task t ends within the requiered time
                        aux_domain.add((i+' '+j,end_time(i+' '+j, task_duration[t])))
        domain[t].intersection_update(aux_domain)
                    
    #starts-before time constraint
    if t in domain_cons_starts_before_time:
        aux_domain.clear()
        for i in set(days):
            for j in set(time):
                if time[j]<=time[domain_cons_starts_before_time[t]]:
                      aux_domain.add((i+' '+j,end_time(i+' '+j, task_duration[t])))
        domain[t].intersection_update(aux_domain)
        
    #ends-before time constraint
    if t in domain_cons_ends_before_time:
        aux_domain.clear()
        for i in set(days):
            for j in set(time):
                if end_time(i+' '+j, task_duration[t]) != '0':        #an end time is possible
                    endDay, endHour = end_time(i+' '+j, task_duration[t]).split()
                    if time[endHour]<=time[domain_cons_ends_before_time[t]]:
                        #task ends before or at the requiere time
                        aux_domain.add((i+' '+j,end_time(i+' '+j, task_duration[t])))
        domain[t].intersection_update(aux_domain)
        
    #starts-after time constraint
    if t in domain_cons_starts_after_time:
        aux_domain.clear()
        for i in set(days):
            for j in set(time):
                if time[j]>=time[domain_cons_starts_after_time[t]]:
                    #task starts after or at the requiere time 
                    aux_domain.add((i+' '+j,end_time(i+' '+j, task_duration[t])))
        domain[t].intersection_update(aux_domain)
        
    #ends-after time constraint
    if t in domain_cons_ends_after_time:
        aux_domain.clear()
        for i in set(days):
            for j in set(time):
                if end_time(i+' '+j, task_duration[t]) != '0':        #an end time is possible
                    endDay, endHour = end_time(i+' '+j, task_duration[t]).split()
                    if time[endHour]>=time[domain_cons_ends_after_time[t]]:
                        aux_domain.add((i+' '+j,end_time(i+' '+j, task_duration[t])))
        domain[t].intersection_update(aux_domain)
                
#List with all the binary constraints
binary_cons_list=[]
for i,j in binary_cons_before:
    binary_cons_list.append(Constraint((i,j),ends_before))
for i,j in binary_cons_after:
    binary_cons_list.append(Constraint((i,j),starts_after))
for i,j in binary_cons_same_day:
    binary_cons_list.append(Constraint((i,j),same_day))
for i,j in binary_cons_starts_at:
    binary_cons_list.append(Constraint((i,j),starts_at))
    

from searchGeneric import AStarSearcher
from display import Displayable
from cspConsistency import Con_solver, partition_domain, copy_with_assign, select
from searchProblem import Arc, Search_problem

#The class Search_with_AC_from_Cost_CSP is a rewritten class of Search_with_AC_from_CSP from AIPython
#it was added the attribute SOFT_constraints in the initialization and
#it has the definition of the heuristic in order to calculate the cost of a CSP
class Search_with_AC_from_Cost_CSP(Search_problem,Displayable):
    """A search problem with arc consistency and domain splitting

    A node is a CSP """
    def __init__(self, csp):
        self.SOFT_constraints=csp.softConstraints
        self.cons = Con_solver(csp)  #copy of the CSP
        self.domains = self.cons.make_arc_consistent()

    def is_goal(self, node):
        """node is a goal if all domains have 1 element"""
        return all(len(node[var])==1 for var in node)
    
    def start_node(self):
        return self.domains
    
    def neighbors(self,node):
        """returns the neighboring nodes of node.
        """
        neighs = []
        var = select(x for x in node if len(node[x])>1)
        if var:
            dom1, dom2 = partition_domain(node[var])
            self.display(2,"Splitting", var, "into", dom1, "and", dom2)
            to_do = self.cons.new_to_do(var,None)
            for dom in [dom1,dom2]:
                newdoms = copy_with_assign(node,var,dom)
                cons_doms = self.cons.make_arc_consistent(newdoms,to_do)
                if all(len(cons_doms[v])>0 for v in cons_doms):
                    # all domains are non-empty
                    neighs.append(Arc(node,cons_doms))          
                else:
                    self.display(2,"...",var,"in",dom,"has no solution")
        
        return neighs
    
    def heuristic(self, node):
        count=0         #counter to calculate the cost
        for i in node:                      #go through every task domain
            if i in self.SOFT_constraints:                #check if the task has a soft constraint
                aux_delay=120                       #This is to calculate the minimum, a maximum delay in a week is 120 hours
                for j in node[i]:           #for loop to calculate de minimum possible delay in task i
                    curr_delay=delay(j[1],self.SOFT_constraints[i][0]+' '+self.SOFT_constraints[i][1])
                    if curr_delay<aux_delay:
                        aux_delay=curr_delay
                #Add the cost of the minimum possible delay to the total cost
                count = count + aux_delay*int(self.SOFT_constraints[i][2])
        
        return count
    
#Set the display level in 0 to avoid unwanted print statements 
AStarSearcher.max_display_level = 0
Con_solver.max_display_level=0
Search_with_AC_from_Cost_CSP.max_display_level=0 

#Create the CSP with the input of the txt file
csp_from_file=CSPcost(domain,binary_cons_list,soft_constraints)

#Solve the CSP with the AStarSearcher which is modified. It consider the defined heuristic, use
#a frontier with priority queue which has a pop method which return the path and cost and the
#search method in the Searcher class was modified as well in order to keep the cost of the final solution
#All those modification were executed in searchGeneric.py 
solution=AStarSearcher(Search_with_AC_from_Cost_CSP(csp_from_file)).search()


if solution==None:                  #search method return None if there is no solution
    print('No solution')
else:
    sol_copy=solution[1].copy()
    for i in sol_copy:
        print(i+':'+sol_copy[i].pop()[0])
    print('cost:'+str(solution[0]))











    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    