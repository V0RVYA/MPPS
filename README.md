# MPPS
Modelling Programming Problem Solving

This is an ongoing project looking to codify programming strategies used by expert and novice programmers,
into various python ACT-R models of problem solving. Requires: https://github.com/CarletonCognitiveModelingLab/CCMSuite3.git

Currently Problem models are solving: Rainfall

	  Design a program that has as a first line in it a list of numbers representing daily rainfall amounts. 
	  The list may include zeros and will include the value -999 at least once but possibly more than once.
	  The first -999 indicates the end of the valid input and as soon as it is encountered, the program stops processing the list.   
	  The program outputs the AVERAGE of the NON-NEGATIVE values in the list up to the first -999 (if it shows up).  
	  There may be negative numbers (as although there cannot be negative rainfall there may be erroneous inputs)  other than -999 in the list. 
	  The program must work with a list of any length 

	  ====================================

	  Here is an example. Suppose we have the list [50, 400, 300, -27, 50, -999]. The program outputs: 

	  Problem_1[]: 200

	  Where -27 is ignored in the list and -999 is the stop signal.

	  Write your code using the input provided below. Please follow the preset code so that we can provide feedback as to the correctness of your answer.


Algorithm Driven (all of these have the solution in its entirety in mind prior to problem solving):

	  1: Production only - problem solutions exist as a set of hard-wired production -> solution triggered immediately upon encountering problem of the type

	  2: Declarative Memory innate - problem solution exists in its entirety as a set of statements in the declarative memory -> agent's productions then execute

	  3: Generated - based on a few concepts + problem components -> agent generates solution in its entirety then executes it
