

'''
This is a model of expert-like problem solving of the rainfall and ballot programming problems. 
'''


import sys
import python_actr      
log=python_actr.log()
log=python_actr.log(html=True)   
from python_actr import *  




class MyEnvironment(python_actr.Model):
    
    warning_light = python_actr.Model(isa='warning_light', state='off')



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
    #b_focus = Buffer() don't need this -> are using set of goal buffers below instead

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
    Specifially the planning units encode the order in which unit tasks (including other other planning units) are executed. 

    The wasy planning units (and their unit tasks) are implemented & stacked is as follows:
    data_storePU
        select_data(UT)
            (ini_var
                size_set(UT)
                name_conv(UT)
                ini_var(UT))
            or
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
        DM.add('planning_unit:data_storePU      cuelag:none          cue:start            unit_task:select_data    calling:none')
        DM.add('planning_unit:data_storePU      cuelag:start         cue:select_data      unit_task:dep_winsPU     calling:none')
        DM.add('planning_unit:data_storePU      cuelag:select_data   cue:dep_winsPU       unit_task:pres_winPU     calling:none')
        DM.add('planning_unit:data_storePU      cuelag:dep_winsPU    cue:pres_winsPU      unit_task:finished       calling:none')


        #Planning unit that handles the initialization of variables, once they has been selected. 
        DM.add('planning_unit:ini_varPU         cuelag:none          cue:start            unit_task:size_set       calling:data_storePU')
        DM.add('planning_unit:ini_varPU         cuelag:start         cue:size_set         unit_task:name_conv      calling:data_storePU')
        DM.add('planning_unit:ini_varPU         cuelag:size_set      cue:name_conv        unit_task:ini_var        calling:data_storePU')
        DM.add('planning_unit:ini_varPU         cuelag:name_conv     cue:ini_var          unit_task:finished       calling:data_storePU')


        #Planning unit that handles the initialization of the dictionary, once it has been selected. 
        DM.add('planning_unit:ini_dictPU        cuelag:none          cue:start            unit_task:size_set       calling:data_storePU')
        DM.add('planning_unit:ini_dictPU        cuelag:start         cue:size_set         unit_task:name_conv      calling:data_storePU')
        DM.add('planning_unit:ini_dictPU        cuelag:size_set      cue:name_conv        unit_task:ini_dict       calling:data_storePU')
        DM.add('planning_unit:ini_dictPU        cuelag:name_conv     cue:ini_dict         unit_task:finished       calling:data_storePU')
        
        #Planning unit that calculates departmental winners 
        DM.add('planning_unit:dep_winsPU        cuelag:none          cue:start            unit_task:usr_inPU       calling:data_storePU')
        DM.add('planning_unit:dep_winsPU        cuelag:start         cue:usr_inPU         unit_task:ite_loopPU     calling:data_storePU') 
        DM.add('planning_unit:dep_winsPU        cuelag:usr_inPU      cue:ite_loopPU       unit_task:compare        calling:data_storePU')
        DM.add('planning_unit:dep_winsPU        cuelag:ite_loopPU    cue:compare          unit_task:output         calling:data_storePU')
        DM.add('planning_unit:dep_winsPU        cuelag:compare       cue:output           unit_task:finished       calling:data_storePU')

        #PU that handles requesting user input - var
        DM.add('planning_unit:usr_inPU          cuelag:none          cue:start            unit_task:request_in     calling:dep_winsPU')
        DM.add('planning_unit:usr_inPU          cuelag:start         cue:request_in       unit_task:finished       calling:dep_winsPU')

        #PU that handles requesting user input - dict
        """
        DM.add('planning_unit:usr_inPU          cuelag:none          cue:start            unit_task:request_in     calling:dep_winsPU')
        DM.add('planning_unit:usr_inPU          cuelag:start         cue:request_in       unit_task:finished       calling:dep_winsPU')
        """

        #PU that handles initializion of looping through the data, and attend to the correct kind of tracker
        DM.add('planning_unit:ite_loopPU        cuelag:none          cue:start            unit_task:ite_loop       calling:dep_wins')
        DM.add('planning_unit:ite_loopPU        cuelag:start         cue:ite_loop         unit_task:select_ite     calling:dep_wins')
        DM.add('planning_unit:ite_loopPU        cuelag:ite_loop      cue:select_ite       unit_task:stop_loopPU    calling:dep_wins')
        DM.add('planning_unit:ite_loopPU        cuelag:select_ite    cue:stop_loopPU      unit_task:finished       calling:dep_wins')
        
 
        # PU that tracks the votes - variables
        DM.add('planning_unit:track_varPU       cuelag:none          cue:start            unit_task:condition      calling:ite_loopPU')
        DM.add('planning_unit:track_varPU       cuelag:start         cue:condition        unit_task:inc_var        calling:ite_loopPU')
        DM.add('planning_unit:track_varPU       cuelag:condition     cue:inc_var          unit_task:finished       calling:ite_loopPU')

        # PU that tracks the votes - dictionary
        DM.add('planning_unit:track_dictPU      cuelag:none          cue:start            unit_task:condition      calling:ite_loopPU')
        DM.add('planning_unit:track_dictPU      cuelag:start         cue:condition        unit_task:inc_dict       calling:ite_loopPU')
        DM.add('planning_unit:track_dictPU      cuelag:condition     cue:inc_dict         unit_task:finished       calling:ite_loopPU')


        #PU that handles loop stopping
        DM.add('planning_unit:stop_loopPU       cuelag:none          cue:start            unit_task:condition      calling:ite_loopPU')
        DM.add('planning_unit:stop_loopPU       cuelag:start         cue:condition        unit_task:stop_loop      calling:ite_loopPU')
        DM.add('planning_unit:stop_loopPU       cuelag:condition     cue:stop_loop        unit_task:finished       calling:ite_loopPU')

        #Planning unit that calculates departmental winners 
        DM.add('planning_unit:pres_winsPU       cuelag:none          cue:start            unit_task:sel_com        calling:data_storePU')
        DM.add('planning_unit:pres_winsPU       cuelag:start         cue:sel_com          unit_task:ite_loopPU     calling:data_storePU') 
        DM.add('planning_unit:pres_winsPU       cuelag:sel_com       cue:ite_loopPU       unit_task:finished       calling:data_storePU')

        DM.add('planning_unit:stop_loopPU condition:-1 ')
        DM.add('planning_unit:ite_loopPU variable1:rains variable2:none')
        DM.add('planning_unit:ini_varPU variable1:count variable2:sum')
        DM.add('planning_unit:track_varPU condition:>=0')
        DM.add('planning_unit:track_varPU variable1:count variable2:sum')
        DM.add('planning_unit:calc_avePU variable1:count variable2:sum')


        DM.add('unit_task:select_data store:dictionary')
        DM.add('unit_task:select_data store:variables')


        b_context.set('finshed:nothing status:unoccupied store_type:none')
        b_focus.set('none')

    '''
    The following productions initialize the planning units. They represent the generation of goals for problem solving by exert agents.
    They also act to intitalize that step of the problem solving process, and through interactions with the DM and the productions defining unit tasks
    enable the agent to generate a solution program to the problem.
    '''

    def run_data_store(b_context='finshed:?nothing status:unoccupied'):
        talk.talk('Goal: I should select a data structure to store the votes in')        
        b_unit_task.set('unit_task:select_data state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:data_storePU cuelag:none cue:start unit_task:select_data state:running')
        b_context.set('finished:nothing status:occupied store_type:none')
        b_focus.set('select_data')
        print('data store planning unit')

    def run_ini_var(b_context='finshed:?planning_unit status:unoccupied store_type:variables'):
        talk.talk('Goal: I should create some variables to track my count(s)')        
        b_unit_task.set('unit_task:size_set state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:ini_varPU cuelag:none cue:start unit_task:size_set state:running')
        b_context.set('finished:nothing status:occupied store_type:variables')
        print('initialize variables planning unit')

    def run_ini_dict(b_context='finshed:?planning_unit status:unoccupied store_type:dictionary'):
        talk.talk('Goal: I should create a dictionary to track my count(s)')        
        b_unit_task.set('unit_task:size_set state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:ini_dictPU cuelag:none cue:start unit_task:size_set state:running')
        b_context.set('finished:nothing status:occupied store_type:dictionary')
        print('initialize dictionary planning unit')

    def run_dep_wins(b_context='finshed:?planning_unit status:unoccupied store_type:?store'):
        talk.talk('Goal: I need to track counts by department')        
        b_unit_task.set('unit_task:usr_inPU state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:dep_winsPU cuelag:none cue:start unit_task:usr_inPU state:running')
        b_context.set('finished:nothing status:occupied store_type:?store')
        print('initialize department winners planning unit')

    def run_usr_in(b_context='finshed:?planning_unit status:unoccupied store_type:?store'):
        talk.talk('Goal: I need to request input from the user')        
        b_unit_task.set('unit_task:request_in state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:usr_inPU cuelag:none cue:start unit_task:request_in state:running')
        b_context.set('finished:nothing status:occupied store_type:?store')
        print('initialize user input planning unit')
    
    def run_ite_loop(b_context='finshed:?planning_unit status:unoccupied store_type:?store'):
        talk.talk('Goal: I need to iterate through a set')        
        b_unit_task.set('unit_task:ite_loop state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:ite_loopPU cuelag:none cue:start unit_task:ite_loop state:running')
        b_context.set('finished:nothing status:occupied store_type:?store')
        print('initialize iterate loop planning unit')

    def run_track_var(b_context='finshed:?planning_unit status:unoccupied store_type:variables'):
        talk.talk('Goal: I need to increment the proper variable')        
        b_unit_task.set('unit_task:condition state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:track_varPU cuelag:none cue:start unit_task:condition state:running')
        b_context.set('finished:nothing status:occupied store_type:variables')
        print('initialize track variables planning unit')

    def run_track_dict(b_context='finshed:?planning_unit status:unoccupied store_type:dictionary'):
        talk.talk('Goal: I need to increment the proper slot in the dictionary')        
        b_unit_task.set('unit_task:condition state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:track_dictPU cuelag:none cue:start unit_task:condition state:running')
        b_context.set('finished:nothing status:occupied store_type:dictionary')
        print('initialize track variables planning unit')

    def run_stop_loop(b_context='finshed:?planning_unit status:unoccupied store_type:?store'):
        talk.talk('Goal: I need to stop iterating the loop when I hit the terminal signal')        
        b_unit_task.set('unit_task:condition state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:stop_loopPU cuelag:none cue:start unit_task:condition state:running calling_PU:ite_loopPU')
        b_context.set('finished:nothing status:occupied store_type:?store')
        print('stop loop planning unit')

    def run_pres_winner(b_context='finshed:?planning_unit status:unoccupied store_type:?store'):
        talk.talk('Goal: I need to calculate the winner')        
        b_unit_task.set('unit_task:condition state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:stop_loopPU cuelag:none cue:start unit_task:condition state:running calling_PU:ite_loopPU')
        b_context.set('finished:nothing status:occupied store_type:?store')
        print('stop loop planning unit')
    
    """
        The following productions cycle through the unit tasks that compose the productions.
    """

    def request_next_unit_task(b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running',
                               b_unit_task='unit_task:?unit_task state:end pu_type:ordered'):
        DM.request('planning_unit:?planning_unit cue:?unit_task unit_task:? cuelag:?cue')
        b_plan_unit.set('planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:retrieve')  # next unit task
        print('ordered planning unit: finished unit task = ')
        print(unit_task)
        # save completed unit task here
    
    def retrieved_next_unit_task(b_plan_unit='state:retrieve',
                                 b_DM='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task!finished'):
        b_plan_unit.set('planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running')
        b_unit_task.set('unit_task:?unit_task state:running pu_type:ordered')
        print('ordered planning unit: next unit_task = ')
        print(unit_task)
    
    """
        The following productions execute the unit tasks necessary for problem solving.
    """
    
    def select_data_ut(b_unit_task='unit_task:select_data state:running pu_type:ordered',
                       b_focus='select_data'):
        DM.request('unit_task:select_data store:?')
        b_focus.set('select_data_2')

    def select_varibs_ut(b_unit_task='unit_task:select_data state:running pu_type:ordered',
                        Memory='unit_task:select_data store:variables',
                        b_focus-'select_data_2'):







    
tim = MyAgent()  # name the agent
subway = MyEnvironment()  # name the environment
subway.agent = tim  # put the agent in the environment


python_actr.log_everything(subway)  # #print out what happens in the environment
subway.run()  # run the environment
python_actr.finished()  # stop the environment