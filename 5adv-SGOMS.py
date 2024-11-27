

'''
This is a model of expert-like problem solving of the rainfall and ballot programming problems. 
'''


import sys
import python_actr      
log=python_actr.log()
log=python_actr.log(html=True)   
from python_actr import *  




class MyEnvironment(python_actr.Model):
    pass    

class MotorModule(python_actr.Model):     # motor module handles typing actions
    def type_first(self, text):           # note that technically the motor module is outside the agent
        #yield 2
        with open('SGOMS.py', 'w') as out: 
            print (text, file = out)
    def type(self, text):           
        #yield 0.5                    #including yield messes up the agent's ability to use it
        with open('SGOMS.py', 'a') as out: 
            print (text, file = out)

class Chronotrans(python_actr.Model):     # motor module handles typing actions
    def talk(self, text):   #how the agent is able to "program"         
        #yield 0.5                    #yield keeps fucking with the motor module
        with open('SGOMS.txt', 'a') as chrono: 
            print (text, file = chrono) #I'm also gonna do this for its talk-aloud and be able to make chronotranscripts

class MyAgent(ACTR): # this is the agent that does the task

    # module buffers
    b_DM = Buffer()
    b_motor = Buffer()
    b_focus = Buffer() #don't need this -> are using set of goal buffers below instead

    # goal buffers
    b_context = Buffer()
    b_plan_unit = Buffer() 
    b_unit_task = Buffer()

    #initialize modules
    talk=Chronotrans()
    DM = Memory(b_DM)  
    motor = MotorModule(b_motor)
    


    def init():
        ''' 
        When initializing the model, the Declarative Memory must be initialized with knowledge of the planning units.
        Specifially the planning units encode the order in which unit tasks(including other other planning units) are executed. 
        
        planning units encode the order of their unit tasks using the cuelag, cue and unit_task slots; the task type is either tunit (a unit task that 
        interacts with the motor module), punit (a unit task that is itself a planning unit) or finish(kill planning unit), calling refers to whether or not the planning unit, 
        to which the unit task belongs, was called by another planning unit

        The way planning units (and their unit tasks) are implemented & stacked is as follows:
        data_storePU
            select_data(UT)
                (ini_var
                    size_set(UT)
                    name_conv(UT)
                    ini_var(UT))
                or (data store has two planning unit trees -> depending on who gets picked by select data -> both callable by data_storePU)
                (ini_dict
                    size_set(UT)
                    name_conv(UT)
                    ini_dict(UT))    
            dep_wins
                usr_in
                    request_in(UT)
                ite_loop
                    ite_loop(UT) 
                    select_ite(UT)
                        (track var
                            condition(UT)
                            inc_var(UT))
                        or
                        (track_dict
                            condition(UT)
                            inc_dict(UT))
                    stop_loop
                        condition(UT)
                        stop_loop(UT)
            pres_winsPU
                select_comparators(UT)

        '''
        # Planning Unit for overseeing of problem solving -> focal point resting on data structure used
        DM.add('planning_unit:data_storePU      cuelag:none          cue:start            unit_task:select_data    task_type:tunit    calling:none')
        DM.add('planning_unit:data_storePU      cuelag:start         cue:select_data      unit_task:ini_varPU      task_type:punit    calling:none')
        DM.add('planning_unit:data_storePU      cuelag:select_data   cue:ini_varPU        unit_task:dep_winsPU     task_type:punit    calling:none')
        DM.add('planning_unit:data_storePU      cuelag:ini_varPU     cue:dep_winsPU       unit_task:pres_winPU     task_type:punit    calling:none')
        DM.add('planning_unit:data_storePU      cuelag:dep_winsPU    cue:pres_winsPU      unit_task:finished       task_type:finish   calling:none')
        
        # Same as above except uses dict
        DM.add('planning_unit:data_storePU      cuelag:none          cue:start            unit_task:select_data    task_type:tunit    calling:none')
        DM.add('planning_unit:data_storePU      cuelag:start         cue:select_data      unit_task:ini_dictPU     task_type:punit    calling:none')
        DM.add('planning_unit:data_storePU      cuelag:select_data   cue:ini_dictPU       unit_task:dep_winsPU     task_type:punit    calling:none')
        DM.add('planning_unit:data_storePU      cuelag:ini_dictPU    cue:dep_winsPU       unit_task:pres_winPU     task_type:punit    calling:none')
        DM.add('planning_unit:data_storePU      cuelag:dep_winsPU    cue:pres_winsPU      unit_task:finished       task_type:finish   calling:none')


        #Planning unit that handles the initialization of variables, once they has been selected. 
        DM.add('planning_unit:ini_varPU         cuelag:none          cue:start            unit_task:size_set       task_type:tunit    calling:data_storePU')
        DM.add('planning_unit:ini_varPU         cuelag:start         cue:size_set         unit_task:name_conv      task_type:tunit    calling:data_storePU')
        DM.add('planning_unit:ini_varPU         cuelag:size_set      cue:name_conv        unit_task:ini_var        task_type:tunit    calling:data_storePU')
        DM.add('planning_unit:ini_varPU         cuelag:name_conv     cue:ini_var          unit_task:finished       task_type:finish   calling:data_storePU')


        #Planning unit that handles the initialization of the dictionary, once it has been selected. 
        DM.add('planning_unit:ini_dictPU        cuelag:none          cue:start            unit_task:size_set       task_type:tunit    calling:data_storePU')
        DM.add('planning_unit:ini_dictPU        cuelag:start         cue:size_set         unit_task:name_conv      task_type:tunit    calling:data_storePU')
        DM.add('planning_unit:ini_dictPU        cuelag:size_set      cue:name_conv        unit_task:ini_dict       task_type:tunit    calling:data_storePU')
        DM.add('planning_unit:ini_dictPU        cuelag:name_conv     cue:ini_dict         unit_task:finished       task_type:finish   calling:data_storePU')
        
        #Planning unit that calculates departmental winners 
        DM.add('planning_unit:dep_winsPU        cuelag:start         cue:usr_inPU         unit_task:ite_loopPU     task_type:punit    calling:data_storePU') 
        DM.add('planning_unit:dep_winsPU        cuelag:usr_inPU      cue:ite_loopPU       unit_task:compare        task_type:tunit    calling:data_storePU')
        DM.add('planning_unit:dep_winsPU        cuelag:ite_loopPU    cue:compare          unit_task:output         task_type:tunit    calling:data_storePU')
        DM.add('planning_unit:dep_winsPU        cuelag:compare       cue:output           unit_task:finished       task_type:finish   calling:data_storePU')

        #PU that handles requesting user input - var
        DM.add('planning_unit:usr_inPU          cuelag:none          cue:start            unit_task:request_in     task_type:tunit    calling:dep_winspu')
        DM.add('planning_unit:usr_inPU          cuelag:start         cue:request_in       unit_task:finished       task_type:finish   calling:dep_winsPU')

        #PU that handles requesting user input - dict
        """
        DM.add('planning_unit:usr_inPU          cuelag:none          cue:start            unit_task:request_in     task_type:tunit    calling:dep_winsPU')
        DM.add('planning_unit:usr_inPU          cuelag:start         cue:request_in       unit_task:finished       task_type:finish   calling:dep_winsPU')
        """

        #PU that handles initializion of looping through the data, and attend to the correct kind of tracker
        DM.add('planning_unit:ite_loopPU        cuelag:none          cue:start            unit_task:ite_loop       task_type:tunit    calling:dep_wins')
        DM.add('planning_unit:ite_loopPU        cuelag:start         cue:ite_loop         unit_task:select_ite     task_type:tunit    calling:dep_wins')
        DM.add('planning_unit:ite_loopPU        cuelag:ite_loop      cue:select_ite       unit_task:stop_loopPU    task_type:punit    calling:dep_wins')
        DM.add('planning_unit:ite_loopPU        cuelag:select_ite    cue:stop_loopPU      unit_task:finished       task_type:finish   calling:dep_wins')
        
 
        # PU that tracks the votes - variables
        DM.add('planning_unit:track_varPU       cuelag:none          cue:start            unit_task:condition      task_type:tunit    calling:ite_loopPU')
        DM.add('planning_unit:track_varPU       cuelag:start         cue:condition        unit_task:inc_var        task_type:tunit    calling:ite_loopPU')
        DM.add('planning_unit:track_varPU       cuelag:condition     cue:inc_var          unit_task:finished       task_type:finish   calling:ite_loopPU')

        # PU that tracks the votes - dictionary
        DM.add('planning_unit:track_dictPU      cuelag:none          cue:start            unit_task:condition      task_type:tunit    calling:ite_loopPU')
        DM.add('planning_unit:track_dictPU      cuelag:start         cue:condition        unit_task:inc_dict       task_type:tunit    calling:ite_loopPU')
        DM.add('planning_unit:track_dictPU      cuelag:condition     cue:inc_dict         unit_task:finished       task_type:finish   calling:ite_loopPU')


        #PU that handles loop stopping
        DM.add('planning_unit:stop_loopPU       cuelag:none          cue:start            unit_task:condition      task_type:tunit    calling:ite_loopPU')
        DM.add('planning_unit:stop_loopPU       cuelag:start         cue:condition        unit_task:stop_loop      task_type:tunit    calling:ite_loopPU')
        DM.add('planning_unit:stop_loopPU       cuelag:condition     cue:stop_loop        unit_task:finished       task_type:finish   calling:ite_loopPU')


        #Planning unit that calculates departmental winners 
        DM.add('planning_unit:pres_winsPU       cuelag:none          cue:start            unit_task:sel_com        task_type:tunit    calling:data_storePU')
        DM.add('planning_unit:pres_winsPU       cuelag:start         cue:sel_com          unit_task:ite_loopPU     task_type:punit    calling:data_storePU') 
        DM.add('planning_unit:pres_winsPU       cuelag:sel_com       cue:ite_loopPU       unit_task:finished       task_type:finish   calling:data_storePU')
        

        #here we allow for the selection of the teo primary means of data storage used by experts and novices
        DM.add('unit_task:select_data store_type:dictionary')
        DM.add('unit_task:select_data store_type:variables')

        #here we define the variables or dictionary used
        DM.add('unit_task:size_set store_type:dictionary defined:{(A:),(H:),(S:)}')
        DM.add('unit_task:size_set store_type:variables defined:(AR, AB, HR, HB, SR, SB)')


        # Now we initialize our context and focus buffers
        #To save time and not do the keyword nonesense, we assume the expert SGOMs agent is initialized to start 
        #with the data store production
        b_context.set('planning_unit:data_storePU finshed:nothing status:unoccupied store_type:none')
        b_focus.set('retrieve PU')

        '''
        The following productions initialize the planning units. They represent 
        the generation of goals for problem solving by exert agents.
        They also act to intitalize that step of the problem solving process, 
        and through interactions with the DM and the productions defining unit
        asks  enable the agent to generate a solution program to the problem.


        Most of this will be moved to a "prefrontal cortex" module for act-r. And will be generalized to allow
        for hierarchical goal behaviour across all probelm domains. 
        '''
        '''
        The production set below handles the retrieval of planning units
        '''
        #The following production should be replaced by some productions that translate problem statement keywords 
        #into selecting the good starting (orienting) planning unit. however for the sake of simplicity I have just made
        #this into the initial productions and it gets the ball rolling.
    def retrieve_initial_punit(b_context='planning_unit:data_storePU finished:nothing status:unoccupied store_type:none',
                               b_focus='retrieve PU'):
        talk.talk('I think I should..')
        DM.request('planning_unit:data_storePU cuelag:none cue:start unit_task:?unit_task task_type:?unit calling:none')
        b_focus.set('retrieve first task')

        '''
        run_planning_unit: once punit in context and first step retrieved -> begin executing unit tasks of punit

        '''

    def run_planning_unit(b_context='planning_unit:?planning_unit finshed:nothing status:unoccupied store_type:?stype',
                          b_DM='planning_unit:?planning_unit cuelag:none cue:start unit_task:?unit_task task_type:?ttype calling:?calling',
                          b_focus='retrieve first task'):
        b_unit_task.set('unit_task:?unit_task state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:?planning_unit cuelag:none cue:start unit_task:?unit_task task_type:?ttype calling:?calling')
        talk.talk('execute the goal' planning_unit)        
        b_context.set('planning_unit:?planning_unit finished:nothing status:occupied store_type:?stype')
        b_focus.set('unit task')
        print('running planning unit ')
       
        '''
        retrieve_calling_unit: when all utasks of a punit are complete -> production check if punit was called and returns the context to the
        appropriate calling planning unit + requests the next step

        planning_unit_runpunit: when retrieved step is a planning unit -> switches context to new called planning unit, and requests first step


        planning_unit_runtunit: when retrieved step is a unit task -> updates unit task buffer -> trigger desired unit task

        retrieve_next_unit_task:

        '''



    def retrieve_nxt_unit_task(b_unit_task='unit_task:?tunit state:end pu_type:ordered',
                               b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?tunit task_type:?ttype calling:?calling',
                               b_focus='next unit'):
        DM.request('planning_unit:?planning_unit cuelag:?cue cue:?tunit unit_task:?new_task task_type:?ttype calling:?calling')
        b_focus.set('retrieving next step')



    def planning_unit_runpunit(b_DM='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?punit task_type:punit calling:?calling'.
                               b_focus='retrieving next step',
                               b_context='planning_unit:?planning_unit finished:?cue status:unoccupied store_type:?type'):
        DM.request('planning_unit:?punit cuelag:none cue:start unit_task:?unit_task task_type:?type calling:?planning_unit')
        b_context.set('planning_unit:?punit finished:nothing status:unoccupied store_type:?type')
        b_focus.set('retrieve first task')

    def planning_unit_runtunit(b_DM='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?tunit task_type:tunit calling:?calling',
                               b_focus='retrieving next step',
                               b_context='planning_unit:?planning_unit finished:?cue status:unoccupied store_type:?type'):
        b_context.set('planning_unit:?planning_unit finished:nothing status:occupied store_type:?type')
        b_plan_unit.set('planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?tunit task_type:tunit calling:?calling')
        b_unit_task.set('unit_task:?tunit state:running pu_type:ordered')
        b_focus('unit task')

    def retrieve_calling_unit(b_context='planning_unit:?planning_unit finished:?cue status:unoccupied store_type:?type',
                              b_DM='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:finished task_type:?unit calling:?calling',
                              b_focus='retrieving next step'):
        talk.talk('I think I should..')
        DM.request('planning_unit:?calling cuelag:?cuel cue:?planning_unit unit_task:?u_task calling:?call')
        b_context.set('planning_unit:?calling finished:?planning_unit status:unoccupied store_type:?type')
        b_focus.set('retrieving next step')
       

       """
        The following productions execute the unit tasks necessary for problem solving.
        """
    #The select_ productions select the data type by retrieving a data type from memory and starting the right planning unit associated with that store type
    #These productions bypass the 
    def select_data_ut(b_unit_task='unit_task:select_data state:running pu_type:ordered',
                       b_focus='unit_task'):
        DM.request('unit_task:select_data store:?')
        b_focus.set('select_data_2')

    def select_varibs_ut(b_unit_task='unit_task:select_data state:running pu_type:ordered',
                        b_DM='unit_task:select_data store_type:variables',
                        b_focus='select_data_2'):
        b_context.set('finshed:select_varibs status:unoccupied store_type:variables')
        b_unit_task.set('unit_task:select_data state:end pu_type:ordered')
        b_focus.set('next unit')
    
    def select_dicts_ut(b_unit_task='unit_task:select_data state:running pu_type:ordered',
                        b_DM='unit_task:select_data store_type:dictionary',
                        b_focus='select_data_2'):
        b_context.set('finshed:select_dict status:unoccupied store_type:dictionary')
        b_unit_task.set('unit_task:select_data state:end pu_type:ordered')
        b_focus.set('next_unit')

    # The size set productions retrieve a known size of data_store and initialize the data store 
    def size_set_vars1(b_unit_task='unit_task:size_set state:running pu_type:order',
                       b_plan_unit='planning_unit:?planning_unit cuelag:none cue:start unit_task:size_set state:running',
                       b_context='finished:nothing status:occupied store_type:?type'):
        DM.request('unit_task:size_set store_type:?')






    
tim = MyAgent()  # name the agent
subway = MyEnvironment()  # name the environment
subway.agent = tim  # put the agent in the environment


python_actr.log_everything(subway)  # #print out what happens in the environment
subway.run()  # run the environment
python_actr.finished()  # stop the environment
