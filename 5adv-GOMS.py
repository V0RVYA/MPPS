

'''
This is a model of expert-like problem solving of the rainfall and ballot programming problems. 
'''


import sys
import python_actr      
#log=python_actr.log()
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
        DM.add('planning_unit:data_storePU      cuelag:dep_winsPU    cue:pres_winPU       unit_task:finished       task_type:finish   calling:none')
        
        # Same as above except uses dict
        DM.add('planning_unit:data_storePU      cuelag:none          cue:start            unit_task:select_data    task_type:tunit    calling:none')
        DM.add('planning_unit:data_storePU      cuelag:start         cue:select_data      unit_task:ini_dictPU     task_type:punit    calling:none')
        DM.add('planning_unit:data_storePU      cuelag:select_data   cue:ini_dictPU       unit_task:dep_winsPU     task_type:punit    calling:none')
        DM.add('planning_unit:data_storePU      cuelag:ini_dictPU    cue:dep_winsPU       unit_task:pres_winPU     task_type:punit    calling:none')
        DM.add('planning_unit:data_storePU      cuelag:dep_winsPU    cue:pres_winsPU      unit_task:finished       task_type:finish   calling:none')


        #Planning unit that handles the initialization of variables, once they has been selected. 
        DM.add('planning_unit:ini_varPU         cuelag:none          cue:start            unit_task:size_set       task_type:tunit    calling:data_storePU')
        DM.add('planning_unit:ini_varPU         cuelag:start         cue:size_set         unit_task:ini_var        task_type:tunit    calling:data_storePU')
        DM.add('planning_unit:ini_varPU         cuelag:size_set      cue:ini_var          unit_task:finished       task_type:finish   calling:data_storePU')


        #Planning unit that handles the initialization of the dictionary, once it has been selected. 
        DM.add('planning_unit:ini_dictPU        cuelag:none          cue:start            unit_task:size_set       task_type:tunit    calling:data_storePU')
        DM.add('planning_unit:ini_dictPU        cuelag:start         cue:size_set         unit_task:ini_dict       task_type:tunit    calling:data_storePU')
        DM.add('planning_unit:ini_dictPU        cuelag:size_set      cue:ini_dict         unit_task:finished       task_type:finish   calling:data_storePU')
        
        #Planning unit that calculates departmental winners 
        DM.add('planning_unit:dep_winsPU        cuelag:none          cue:start            unit_task:ite_loop       task_type:tunit    calling:data_storePU') 
        DM.add('planning_unit:dep_winsPU        cuelag:start         cue:ite_loop         unit_task:usr_inPU       task_type:punit    calling:data_storePU') 
        DM.add('planning_unit:dep_winsPU        cuelag:ite_loop      cue:usr_inPU         unit_task:run_loopPU     task_type:punit    calling:data_storePU')
        DM.add('planning_unit:dep_winsPU        cuelag:usr_inPU      cue:run_loopPU       unit_task:trackdep       task_type:tunit    calling:data_storePU')
        DM.add('planning_unit:dep_winsPU        cuelag:run_loopPU    cue:trackdep         unit_task:compare        task_type:tunit    calling:data_storePU')
        DM.add('planning_unit:dep_winsPU        cuelag:trackdep      cue:compare          unit_task:finished       task_type:finish   calling:data_storePU')

        #PU that handles requesting user input - var
        DM.add('planning_unit:usr_inPU          cuelag:none          cue:start            unit_task:request_in     task_type:tunit    calling:dep_winsPU')
        DM.add('planning_unit:usr_inPU          cuelag:start         cue:request_in       unit_task:finished       task_type:finish   calling:dep_winsPU')

        #PU that handles requesting user input - dict
        """
        DM.add('planning_unit:usr_inPU          cuelag:none          cue:start            unit_task:request_in     task_type:tunit    calling:dep_winsPU')
        DM.add('planning_unit:usr_inPU          cuelag:start         cue:request_in       unit_task:finished       task_type:finish   calling:dep_winsPU')
        """

        #PU that handles initializion of looping through the data, and attend to the correct kind of tracker
        DM.add('planning_unit:run_loopPU        cuelag:none          cue:start            unit_task:trackPU        task_type:punit    calling:dep_winsPU')
        DM.add('planning_unit:run_loopPU        cuelag:start         cue:trackPU          unit_task:stop_loopPU    task_type:punit    calling:dep_winsPU')
        DM.add('planning_unit:run_loopPU        cuelag:trackPU       cue:stop_loopPU      unit_task:finished       task_type:finish   calling:dep_winsPU')
        
 
        # PU that tracks the votes - variables
        DM.add('planning_unit:trackPU           cuelag:none          cue:start            unit_task:select_ite     task_type:tunit    calling:run_loopPU')
        DM.add('planning_unit:trackPU           cuelag:start         cue:select_ite       unit_task:finished       task_type:finish   calling:run_loopPU')

        #PU that handles loop stopping
        DM.add('planning_unit:stop_loopPU       cuelag:none          cue:start            unit_task:condition      task_type:tunit    calling:run_loopPU')
        DM.add('planning_unit:stop_loopPU       cuelag:start         cue:condition        unit_task:stop_loop      task_type:tunit    calling:run_loopPU')
        DM.add('planning_unit:stop_loopPU       cuelag:condition     cue:stop_loop        unit_task:finished       task_type:finish   calling:run_loopPU')


        #Planning unit that calculates departmental winners 
        DM.add('planning_unit:pres_winPU        cuelag:none          cue:start            unit_task:output         task_type:tunit    calling:data_storePU')
        DM.add('planning_unit:pres_winPU        cuelag:start         cue:output           unit_task:finished       task_type:finish   calling:data_storePU')
        

        #here we allow for the selection of the teo primary means of data storage used by experts and novices
        DM.add('unit_task:select_data store_type:dictionary')
        DM.add('unit_task:select_data store_type:variables')

        #here we define the variables or dictionary used
        DM.add('unit_task:size_set store_type:dictionary data_def:2x3')
        DM.add('unit_task:size_set store_type:variables data_def:1x6')

        DM.add('unit_task:condition1 condition:-1')


        # Now we initialize our context and focus buffers
        #To save time and not do the keyword nonesense, we assume the expert SGOMs agent is initialized to start 
        #with the data store production
        b_context.set('planning_unit:data_storePU finished:nothing status:unoccupied store_type:none data_def:none stop:none')
        b_focus.set('retrieve PU')

        '''
        
        The following productions handle planning units declared in the DM. 

        retrieve_initial_punit: starts us off -> will only fire once should be made more general 

        run_planning_unit: once first step of planning unit retrieved then start executirng steps of planning unit

        retrieve_calling_unit: when all utasks of a punit are complete -> production check if punit was called and returns the context to the
        appropriate calling planning unit + requests the next step

        planning_unit_runpunit: when retrieved step is a planning unit -> switches context to the new called planning unit, and requests first step

        planning_unit_runtunit: when retrieved step is a unit task -> updates unit task buffer -> trigger desired unit task

        retrieve_next_unit_task: once unit task complete retrieve next unit task from memory


        Most of this will be moved to a "prefrontal cortex" module for act-r. And will be generalized to allow
        for hierarchical goal behaviour across all probelm domains. 
        '''
        #The following production should be replaced by some productions that translate problem statement keywords 
        #into selecting the good starting (orienting) planning unit. however for the sake of simplicity I have just made
        #this into the initial productions and it gets the ball rolling.
    def retrieve_initial_punit(b_context='planning_unit:data_storePU finished:nothing status:unoccupied store_type:none data_def:none stop:?stop',
                               b_focus='retrieve PU'):
        talk.talk('I think I should..')
        DM.request('planning_unit:data_storePU cuelag:none cue:start unit_task:?unit_task task_type:?unit calling:none')
        b_focus.set('retrieve first task')

    def run_planning_tunit(b_context='planning_unit:?planning_unit finished:nothing status:unoccupied store_type:?stype data_def:?data_def stop:?stop',
                          b_DM='planning_unit:?planning_unit cuelag:none cue:start unit_task:?unit_task task_type:tunit calling:?calling',
                          b_focus='retrieve first task'):
        b_unit_task.set('unit_task:?unit_task state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:?planning_unit cuelag:none cue:start unit_task:?unit_task task_type:tunit calling:?calling')
        talk.talk('Goal: execute the goal ' + planning_unit)        
        b_context.set('planning_unit:?planning_unit finished:nothing status:occupied store_type:?stype data_def:?data_def stop:?stop')
        b_focus.set('unit task')
        print('running planning unit ')
    
    def run_planning_punit(b_context='planning_unit:?planning_unit finished:nothing status:unoccupied store_type:?stype data_def:?data_def stop:?stop',
                           b_DM='planning_unit:?planning_unit cuelag:none cue:start unit_task:?unit_task task_type:punit calling:?calling',
                           b_focus='retrieve first task'):
        DM.request('planning_unit:?unit_task cuelag:none cue:start unit_task:? task_type:? calling:?planning_unit')
        talk.talk('Goal: execute the goal ' + planning_unit)        
        b_context.set('planning_unit:?unit_task finished:nothing status:unoccupied store_type:?stype data_def:?data_def stop:?stop')
        b_focus.set('retrieve first task')
      

    def retrieve_nxt_unit_task(b_unit_task='unit_task:?tunit state:end pu_type:ordered',
                               b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?tunit task_type:?ttype calling:?calling',
                               b_focus='next unit'):
        DM.request('planning_unit:?planning_unit cuelag:?cue cue:?tunit unit_task:?new_task task_type:?newttype calling:?calling')
        b_focus.set('retrieving next step')



    def planning_unit_runpunit(b_DM='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?punit task_type:punit calling:?calling',
                               b_focus='retrieving next step',
                               b_context='planning_unit:?planning_unit finished:?cue status:unoccupied store_type:?stype data_def:?data_def stop:?stop'):
        b_context.set('planning_unit:?punit finished:nothing status:unoccupied store_type:?stype data_def:?data_def stop:?stop')
        DM.request('planning_unit:?punit cuelag:none cue:start unit_task:? task_type:? calling:?planning_unit')
        b_focus.set('retrieve first task')

    def planning_unit_runtunit(b_DM='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:!finished?tunit task_type:tunit calling:?calling',
                               b_focus='retrieving next step',
                               b_context='planning_unit:?planning_unit finished:?cue status:unoccupied store_type:?type data_def:?data_def stop:?stop'):
        b_context.set('planning_unit:?planning_unit finished:nothing status:occupied store_type:?type data_def:?data_def stop:?stop')
        b_plan_unit.set('planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?tunit task_type:tunit calling:?calling')
        b_unit_task.set('unit_task:?tunit state:running pu_type:ordered')
        b_focus.set('unit task')

    def retrieve_calling_unit(b_context='planning_unit:?planning_unit finished:?cue status:unoccupied store_type:?type data_def:?data_def stop:?stop',
                              b_DM='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:finished task_type:finish calling:!none?calling',
                              b_focus='retrieving next step'):
        talk.talk('I think I should..')
        b_context.set('planning_unit:?calling finished:?planning_unit status:unoccupied store_type:?type data_def:?data_def stop:?stop')
        DM.request('planning_unit:?calling cuelag:?cuel cue:?planning_unit unit_task:?u_task calling:?call')
        b_focus.set('retrieving next step')

    def end_no_calling_unit(b_context='planning_unit:?planning_unit finished:?cue status:unoccupied store_type:?type data_def:?data_def stop:?stop',
                            b_DM='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:finished task_type:finish calling:none',
                            b_focus='retrieving next step'):
        talk.talk('I think I am done')
        b_focus.set('stopping')
             

        """
        The following productions execute the unit tasks necessary for problem solving.
        """
    #The select_ productions select the data type by retrieving a data type from memory and starting the right planning unit associated with that store type
    #These productions bypass the 
    def select_data_ut(b_unit_task='unit_task:select_data state:running pu_type:ordered',
                       b_focus='unit task'):
        DM.request('unit_task:select_data store_type:?stype')
        b_focus.set('select data 2')

    def selected_varib_ut(b_unit_task='unit_task:select_data state:running pu_type:ordered',
                          b_context='planning_unit:?planning_unit finished:?finished status:occupied store_type:none data_def:none stop:?stop',
                          b_DM='unit_task:select_data store_type:variables',
                          b_focus='select data 2'):
        b_context.set('planning_unit:?planning_unit finished:select_data status:unoccupied store_type:variables data_def:none stop:?stop')
        b_unit_task.set('unit_task:select_data state:end pu_type:ordered')
        DM.request('planning_unit:?planning_unit cuelag:?cuel cue:select_data unit_task:ini_varPU task_type:punit calling:?calling')
        b_focus.set('retrieving next step')

    def selected_dict_ut(b_unit_task='unit_task:select_data state:running pu_type:ordered',
                         b_context='planning_unit:?planning_unit finished:?finished status:occupied store_type:none data_def:none stop:?stop',
                         b_DM='unit_task:select_data store_type:dictionary',
                         b_focus='select data 2'):
        b_context.set('planning_unit:?planning_unit finished:select_data status:unoccupied store_type:dictionary data_def:none stop:?stop')
        b_unit_task.set('unit_task:select_data state:end pu_type:ordered')
        DM.request('planning_unit:?planning_unit cuelag:?cuel cue:select_data unit_task:ini_dictPU task_type:punit calling:?calling')
        b_focus.set('retrieving next step')


    # The size set productions retrieve a known size of data_store and initialize the data store 
    def size_set(b_unit_task='unit_task:size_set state:running pu_type:ordered',
                 b_context='planning_unit:?planning_unit finished:?finished status:occupied store_type:?stype data_def:none stop:?stop',
                 b_focus='unit task'):
        DM.request('unit_task:size_set store_type:?stype data_def:?data')
        b_focus.set('size set 2')

    def size_set_too(b_DM='unit_task:size_set store_type:?stype data_def:?data_def',
                     b_context='planning_unit:?planning_unit finished:nothing status:occupied store_type:?stype data_def:none stop:?stop',
                     b_focus='size set 2'):
        b_context.set('planning_unit:?planning_unit finished:size_set status:unoccupied store_type:?stype data_def:?data_def stop:?stop')
        b_unit_task.set('unit_task:size_set state:end pu_type:ordered')
        b_focus.set('next unit')

    #The following production initialize the data structure - either 6 variables or a 1x6 dictionary

    def ini_var_ut(b_unit_task='unit_task:ini_var state:running pu_type:ordered',
                   b_context='planning_unit:?planning_unit finished:?finished status:occupied store_type:variables data_def:1x6 stop:?stop',
                   b_focus='unit task'):
        motor.type_first('AR = 0, AB = 0, HR = 0, HB = 0, SR = 0, SB = 0')
        talk.talk('STEP: AR = 0, AB = 0, HR = 0, HB = 0, SR = 0, SB = 0')
        b_context.set('planning_unit:?planning_unit finished:ini_var status:unoccupied store_type:variables data_def:1x6 stop:?stop')
        b_unit_task.set('unit_task:ini_var state:end pu_type:ordered')
        b_focus.set('next unit')

    def ini_dict_ut(b_unit_task='unit_task:ini_dict state:running pu_type:ordered',
                    b_context='planning_unit:?planning_unit finished:?finished status:occupied store_type:dictionary data_def:2x3 stop:?stop',
                    b_focus='unit task'):
        motor.type_first('r_box = {"A":0,"H":0,"S":0}')
        talk.talk('STEP:r_box = {"A":0,"H":0,"S":0}')
        motor.type_first('b_box = {"A":0,"H":0,"S":0}')
        talk.talk('STEP: b_box = {"A":0,"H":0,"S":0}')
        b_context.set('planning_unit:?planning_unit finished:ini_dict status:unoccupied store_type:dictionary data_def:2x3 stop:?stop')
        b_unit_task.set('unit_task:ini_dict state:end pu_type:ordered')
        b_focus.set('next unit')

    #The following productions handle unit tasks for looping for department and total winners.
    def request_in(b_unit_task='unit_task:request_in state:running pu_type:ordered',
                   b_context='planning_unit:?planning_unit finished:?finished status:occupied store_type:?stype data_def:?data_def stop:?stop',
                   b_focus='unit task'):
        motor.type('    faculty = input("Faculty (-1 to end)")')
        motor.type('    if faculty != -1: president = input("President")')
        talk.talk('STEP:     faculty = input("Faculty (-1 to end)"')
        talk.talk('STEP:     if faculty !=-1: president = input("President")')
        b_context.set('planning_unit:?planning_unit finished:request_in status:unoccupied store_type:?stype data_def:?data_def stop:?stop')
        b_unit_task.set('unit_task:request_in state:end pu_type:ordered')
        b_focus.set('next unit')

    def ite_loop(b_unit_task='unit_task:ite_loop state:running pu_type:ordered',
                 b_context='planning_unit:?planning_unit finished:?finished status:occupied store_type:?stype data_def:?data_def stop:?stop',
                 b_focus='unit task'):
        motor.type('while True:')
        talk.talk('STEP: while True:')
        b_unit_task.set('unit_task:ite_loop state:end pu_type:ordered')
        b_context.set('planning_unit:?planning_unit finished:ite_loop status:unoccupied store_type:?stype data_def:?data_def stop:?stop')
        b_focus.set('next unit')

        
    def select_ite_d(b_unit_task='unit_task:select_ite state:running pu_type:ordered',
                     b_context='planning_unit:?planning_unit finished:?finished status:occupied store_type:dictionary data_def:?data_def stop:?stop',
                     b_focus='unit task'):
        motor.type('            if president == "R": r_box[faculty] += 1')
        talk.talk('STEP:             if president == R:_box[(faculty,president)] += 1')
        motor.type('            else: b_box[faculty] += 1')
        talk.talk('STEP:             else:b_box[faculty] += 1')
        b_context.set('planning_unit:?planning_unit finished:select_ite status:unoccupied store_type:dictionary data_def:?data_def stop:?stop')
        b_unit_task.set('unit_task:select_ite state:end pu_type:ordered')
        b_focus.set('next unit')

    def select_ite_v(b_unit_task='unit_task:select_ite state:running pu_type:ordered',
                     b_context='planning_unit:?planning_unit finished:?finished status:occupied store_type:variables data_def:?data_def stop:?stop',
                     b_focus='unit task'):
        motor.type('            if faculty == A and president == R: AR+=1')
        motor.type('            if faculty == A and president == B: AB+=1')
        motor.type('            if faculty == H and president == R: HR+=1')
        motor.type('            if faculty == H and president == B: HB+=1')
        motor.type('            if faculty == S and president == R: SR+=1')
        motor.type('STEP:            if faculty == S and president == B: SB+=1')
        talk.talk('STEP:            if faculty == A and president == R: AR+=1')
        talk.talk('STEP:            if faculty == A and president == B: AB+=1')
        talk.talk('STEP:             if faculty == H and president == R: HR+=1')
        talk.talk('STEP:            if faculty == H and president == B: HB+=1')
        talk.talk('STEP:            if faculty == S and president == R: SR+=1')
        talk.talk('STEP:             if faculty == S and president == B: SB+=1')
        b_context.set('planning_unit:?planning_unit finished:select_ite status:unoccupied store_type:variables data_def:?data_def stop:?stop')
        b_unit_task.set('unit_task:select_ite state:end pu_type:ordered')
        b_focus.set('next unit')

    # The condition productions retrieve stop condition 
    def condition(b_unit_task='unit_task:condition state:running pu_type:ordered',
                  b_context='planning_unit:?planning_unit finished:?finished status:occupied store_type:?stype data_def:?data_def stop:none',
                  b_focus='unit task'):
        DM.request('unit_task:condition1 condition:?')
        b_focus.set('condition')

    def condition2(b_DM='unit_task:condition1 condition:?cond',
                   b_context='planning_unit:?planning_unit finished:?finished status:occupied store_type:?stype data_def:?data_def stop:none',
                   b_focus='condition'):
        b_context.set('planning_unit:?planning_unit finished:condition status:unoccupied store_type:?stype data_def:?data_def stop:?cond')
        b_unit_task.set('unit_task:condition state:end pu_type:ordered')
        b_focus.set('next unit')

    # The stop_loop productions stops the loop
    def stop_loop(b_unit_task='unit_task:stop_loop state:running pu_type:ordered',
                  b_context='planning_unit:?planning_unit finished:?finished status:occupied store_type:?stype data_def:?data_def stop:?stop',
                  b_focus='unit task'):
        motor.type('    if faculty == -1: break')
        talk.talk('STEP:      if faculty == -1: break')
        b_unit_task.set('unit_task:stop_loop state:end pu_type:ordered')
        b_context.set('planning_unit:?planning_unit finished:stop_loop status:unoccupied store_type:?stype data_def:?data_def stop:?stop')
        b_focus.set('next unit')

    def compare_d(b_unit_task='unit_task:compare state:running pu_type:ordered',
                  b_context='planning_unit:?planning_unit finished:?finished status:occupied store_type:dictionary data_def:?data_def stop:?stop',
                  b_focus='unit task'):
        motor.type('if r_box["A"] > b_box["A"]: A+=1')
        motor.type('if r_box["A"] < b_box["A"]: A-=1')
        motor.type('if r_box["S"] > b_box["S"]: S+=1')
        motor.type('if r_box["S"] < b_box["S"]: S-=1')
        motor.type('if r_box["H"] > b_box["H"]: H+=1')
        motor.type('if r_box["H"] < b_box["H"]: H-=1')
        talk.talk('STEP: if r_box["A"] > b_box["A"]: A+=1')
        talk.talk('STEP: if r_box["A"] < b_box["A"]: A-=1')
        talk.talk('STEP: if r_box["S"] > b_box["S"]: S+=1')
        talk.talk('STEP: if r_box["S"] < b_box["S"]: S-=1')
        talk.talk('STEP: if r_box["H"] > b_box["H"]: H+=1')
        talk.talk('STEP: if r_box["H"] < b_box["H"]: H-=1')
        b_context.set('planning_unit:?planning_unit finished:compare status:unoccupied store_type:dictionary data_def:?data_def stop:?stop')
        b_unit_task.set('unit_task:compare state:end pu_type:ordered')
        b_focus.set('next unit')

    def compare_v(b_unit_task='unit_task:compare state:running pu_type:ordered',
                  b_context='planning_unit:?planning_unit finished:?finished status:occupied store_type:variables data_def:?data_def stop:?stop',
                  b_focus='unit task'):
        motor.type('if AR < AB: A-=1')
        motor.type('if AR > AB: A+=1')
        motor.type('if SR > SB: S+=1')
        motor.type('if SR < SB: S-=1')
        motor.type('if HR > HB: H+=1')
        motor.type('if HR < HB: H-=1')
        talk.talk('if AR < AB: A-=1')
        talk.talk('if AR > AB: A+=1')
        talk.talk('if SR > SB: S+=1')
        talk.talk('if SR < SB: S-=1')
        talk.talk('if HR > HB: H+=1')
        talk.talk('if HR < HB: H-=1')
        b_context.set('planning_unit:?planning_unit finished:compare status:unoccupied store_type:variables data_def:?data_def stop:?stop')
        b_unit_task.set('unit_task:compare state:end pu_type:ordered')
        b_focus.set('next unit')

    def trackdep(b_unit_task='unit_task:trackdep state:running pu_type:ordered',
                 b_context='planning_unit:?planning_unit finished:?finished status:occupied store_type:?stype data_def:?data_def stop:?stop',
                 b_focus='unit task'):
        motor.type('A = 0, H = 0, S = 0')
        talk.talk('STEP: A = 0, H = 0, S = 0')
        b_context.set('planning_unit:?planning_unit finished:trackdep status:unoccupied store_type:?stype data_def:?data_def stop:?stop')
        b_unit_task.set('unit_task:trackdep state:end pu_type:ordered')
        b_focus.set('next unit')

    def output(b_unit_task='unit_task:output state:running pu_type:ordered',
               b_context='planning_unit:?planning_unit finished:?finished status:occupied store_type:?stype data_def:?data_def stop:?stop',
               b_focus='unit task'):
        motor.type('if A+H+S > 0: print("RED WINS")')
        motor.type('if A+H+S < 0: print("BLUE WINS")')
        talk.talk('STEP: if A+H+S < 0: print("BLUE WINS")')
        talk.talk('STEP: if A+H+S > 0: print("RED WINS")')
        b_context.set('planning_unit:?planning_unit finished:output status:unoccupied store_type:?stype data_def:?data_def stop:?stop')
        b_unit_task.set('unit_task:output state:end pu_type:ordered')
        b_focus.set('next unit')

    def stop(b_focus='stopping'):
        self.stop()








    
tim = MyAgent()  # name the agent
subway = MyEnvironment()  # name the environment
subway.agent = tim  # put the agent in the environment


python_actr.log_everything(subway)  # #print out what happens in the environment
subway.run()  # run the environment
python_actr.finished()  # stop the environment
