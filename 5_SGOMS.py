
'''
This is a model of expert-like problem solving of the rainfall programming problems.
'''

import sys
import python_actr    
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
        #yield 0.5                   
        #including yield messes up the agent's ability to use it
        with open('SGOMS.py', 'a') as out:
            print (text, file = out)

class Chronotrans(python_actr.Model):     # motor module handles typing actions
    def talk(self, text):   #how the agent is able to "program"         
        #yield 0.5                    #yield keeps fucking with the motor module
        with open('SGOMS.txt', 'a') as chrono: 
            print (text, file = chrono) #I'm also gonna do this for its talk-aloud and be able to make chronotranscripts

class MyAgent(python_actr.ACTR): # this is the agent that does the task

    # module buffers
    b_DM = Buffer()
    b_motor = Buffer()
    b_focus = Buffer()

    # goal buffers
    b_context = Buffer()
    b_plan_unit = Buffer() 
    b_unit_task = Buffer()
    b_variable = Buffer()
    b_operator = Buffer()
    talk=Chronotrans()

    DM = Memory(b_DM)  
    motor = MotorModule(b_motor)
    


    def init():
        '''
        Declarative Memory is initialized with knowledge of the planning units. Specifially
        '''
        DM.add('planning_unit:stop_loopPU         cuelag:none          cue:start          unit_task:condition       calling:ite_loopPU')
        DM.add('planning_unit:stop_loopPU         cuelag:start         cue:condition              unit_task:stop_loop      calling:ite_loopPU')
        DM.add('planning_unit:stop_loopPU         cuelag:condition             cue:stop_loop              unit_task:finished     calling:ite_loopPU')

        DM.add('planning_unit:ite_loopPU         cuelag:none          cue:start          unit_task:variables   calling:calc_avePU')
        DM.add('planning_unit:ite_loopPU         cuelag:start         cue:variables              unit_task:ite_loop     calling:calc_avePU')
        DM.add('planning_unit:ite_loopPU         cuelag:variables         cue:ite_loop              unit_task:stop_loopPU      calling:calc_avePU')
        DM.add('planning_unit:ite_loopPU         cuelag:ite_loop         cue:stop_loopPU              unit_task:track_varPU     calling:calc_avePU')
        DM.add('planning_unit:ite_loopPU         cuelag:stop_loopPU         cue:track_varPU              unit_task:pause     calling:calc_avePU')
        DM.add('planning_unit:ite_loopPU         cuelag:track_varPU             cue:pause           unit_task:finished     calling:calc_avePU')

        DM.add('planning_unit:ini_varPU         cuelag:none          cue:start          unit_task:variables         calling:calc_avePU')
        DM.add('planning_unit:ini_varPU         cuelag:start         cue:variables              unit_task:ini_var   calling:calc_avePU')
        DM.add('planning_unit:ini_varPU         cuelag:variables            cue:ini_var             unit_task:finished    calling:calc_avePU')

        DM.add('planning_unit:track_varPU         cuelag:none          cue:start          unit_task:condition       calling:ite_loopPU')
        DM.add('planning_unit:track_varPU         cuelag:start         cue:condition              unit_task:track_var1        calling:ite_loopPU')        
        DM.add('planning_unit:track_varPU         cuelag:condition         cue:track_var1              unit_task:variables        calling:ite_loopPU')
        DM.add('planning_unit:track_varPU         cuelag:track_var1         cue:variables              unit_task:track_var2       calling:ite_loopPU')
        DM.add('planning_unit:track_varPU         cuelag:variables            cue:track_var2             unit_task:finished     calling:ite_loopPU')

        DM.add('planning_unit:calc_avePU         cuelag:none          cue:start          unit_task:ini_varPU      calling:none')
        DM.add('planning_unit:calc_avePU         cuelag:start         cue:ini_varPU              unit_task:ite_loopPU      calling:none')
        DM.add('planning_unit:calc_avePU         cuelag:ini_varPU         cue:ite_loopPU              unit_task:variables     calling:none')
        DM.add('planning_unit:calc_avePU         cuelag:ite_loopPU         cue:variables              unit_task:calc_ave     calling:none')
        DM.add('planning_unit:calc_avePU         cuelag:variables             cue:calc_ave              unit_task:finished     calling:none')


        DM.add('planning_unit:stop_loopPU condition:-999')
        DM.add('planning_unit:ite_loopPU variable1:rains variable2:none')
        DM.add('planning_unit:ini_varPU variable1:count variable2:sum')
        DM.add('planning_unit:track_varPU condition:>=0')
        DM.add('planning_unit:track_varPU variable1:count variable2:sum')
        DM.add('planning_unit:calc_avePU variable1:count variable2:sum')



        b_context.set('finshed:nothing status:unoccupied condition:none variable1:none variable2:none')
        b_focus.set('none')


    def run_stop_loop(b_context='finshed:ite_loop status:occupied '):
        talk.talk('Goal: I need to stop iterating the loop when I hit the first -999 in the list')        
        b_unit_task.set('unit_task:condition state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:stop_loopPU cuelag:none cue:start unit_task:condition state:running calling_PU:ite_loopPU')
        b_context.set('finished:nothing status:occupied condition:none variable1:none variable2:none')
        print('stop loop planning unit')

    def run_ini_var(b_context='finshed:?planning_unit status:unoccupied '):
        talk.talk('Goal: I should initialize the variables sum and count to track the positive numbers')        
        b_unit_task.set('unit_task:variables state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:ini_varPU cuelag:none cue:start unit_task:variables state:running')
        b_context.set('finished:nothing status:occupied condition:none variable1:none variable2:none')
        print('initialize variables planning unit')

    def run_ite_loop(b_context='finshed:ini_varPU status:unoccupied'):
        talk.talk('Goal: I should iterate through the list')        
        b_unit_task.set('unit_task:variables state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:ite_loopPU cuelag:none cue:start unit_task:variables state:running')
        b_context.set('finished:nothing status:occupied condition:none variable1:none variable2:none')
        print('iterate loop planning unit')

    def run_track_var(b_context='finshed:stop_loopPU status:unoccupied '):
        talk.talk('Goal: I should track the positive numbers in the list using the sum and count variables')        
        b_unit_task.set('unit_task:condition state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:track_varPU cuelag:none cue:start unit_task:condition state:running')
        b_context.set('finished:nothing status:occupied condition:none variable1:none variable2:none')
        print('track variables planning unit')

    def run_calc_ave(b_context='finshed:?nothing status:unoccupied '):
        talk.talk('Goal: I should calculate the average of the positive numbers')        
        b_unit_task.set('unit_task:ini_varPU state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:calc_avePU cuelag:none cue:start unit_task:ini_varPU state:running')
        b_context.set('finished:nothing status:occupied condition:none variable1:none variable2:none')
        print('calculate average planning unit')

    def run_ini_dict(b_context='finshed:?planning_unit status:unoccupied '):
        talk.talk('Goal: I should initialize a dictionary to store the counts')        
        b_unit_task.set('unit_task:variables state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:ini_varPU cuelag:none cue:start unit_task:variables state:running')
        b_context.set('finished:nothing status:occupied condition:none variable1:none variable2:none')
        print('initialize variables planning unit')
    
    def run_ini_var(b_context='finshed:?planning_unit status:unoccupied '):
        talk.talk('Goal: I should initialize the variables sum and count to track the positive numbers')        
        b_unit_task.set('unit_task:variables state:running pu_type:ordered')
        b_plan_unit.set('planning_unit:ini_varPU cuelag:none cue:start unit_task:variables state:running')
        b_context.set('finished:nothing status:occupied condition:none variable1:none variable2:none')
        print('initialize variables planning unit')

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



    def retrieved_last_unit_task(b_plan_unit='planning_unit:?planning_unit state:retrieve',
                                 b_unit_task='unit_task:?unit_task state:end pu_type:ordered',
                                 b_DM='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:finished calling:?calling',
                                 b_context = 'finished:?finished status:occupied' ):
                                    # not, the memory retrieval indicates the plan is finished
        print('stopped planning unit='),planning_unit
        #print 'finished'
        b_unit_task.modify(state='stopped')
        DM.request("planning_unit:?calling cuelag:? cue:?planning_unit unit_task:? calling:?") 
        # save completed planning unit here

    def retrieved_last_unit_task_with_call2(b_plan_unit='planning_unit:?planning_unit state:retrieve',
                                 b_unit_task='unit_task:?unit_task state:stopped pu_type:ordered',
                                 b_DM='planning_unit:?pu cuelag:?cuelag cue:?planning_unit unit_task:?ut calling:?calling',
                                 b_context = 'finished:?finished status:occupied'):
        print ('resumed planning unit='), planning_unit
        b_plan_unit.set('planning_unit:?pu cuelag:?cuelag cue:?planning_unit unit_task:?ut state:running')
        b_unit_task.set('unit_task:?ut state:running pu_type:ordered')
        b_context.set('finished:?planning_unit status:occupied condition:none variable1:none variable2:none')


    def condition1(b_unit_task='unit_task:condition state:running', b_plan_unit = 'planning_unit:?PU unit_task:condition'):
        DM.request('planning_unit:?PU condition:?')
        b_focus.set("con2")
        print('what is the condition?')
    def condition2(b_unit_task='unit_task:condition state:running', b_focus = 'con2', b_DM = 'planning_unit:?PU condition:?condition'):
        b_context.modify(condition = condition)
        b_unit_task.modify(state='end')
        b_focus.set('')
        print('condition in context')

    def variable1(b_unit_task='unit_task:variables state:running', b_plan_unit = 'planning_unit:?PU unit_task:variables'):
        DM.request('planning_unit:?PU variable1:? variable2:?')
        b_focus.set("var2")
        print('what are the variables?')
    def variable2(b_unit_task='unit_task:variables state:running', b_focus = 'var2', b_DM = 'planning_unit:?PU variable1:?var1 variable2:?var2'):
        b_context.modify(variable1 = var1)
        b_context.modify(variable2 = var2)
        b_unit_task.modify(state='end')
        b_focus.set('')
        print('variables retireved')

    def pause(b_unit_task='unit_task:pause state:running'):
        b_unit_task.modify(state='end')
        print('pause')  

    def stop_loop(b_unit_task='unit_task:stop_loop state:running', b_context = 'condition:?condition'):
        talk.talk('Step: if x == ' + condition + ':break')
        motor.type('    if x == ' + condition + ':')
        motor.type('        break')
        b_unit_task.modify(state='end')
        print('stopping the loop')

    def ite_loop(b_unit_task='unit_task:ite_loop state:running', b_context = ' variable1:?var1'):
        talk.talk("Step: for x in " + var1 + ":")
        motor.type('for x in ' + var1 + ':')
        b_unit_task.modify(state='end')
        print('iterating loop')

    def calc_ave(b_unit_task='unit_task:calc_ave state:running', b_context = 'variable1:?var1 variable2:?var2'):
        talk.talk('Step: average = ' + var1 + '/' + var2)
        motor.type('Average = ' + var1 + '/' + var2)
        b_unit_task.modify(state='end')
        print('calculating aberage')

    def ini_var(b_unit_task='unit_task:ini_var state:running', b_context = 'variable1:?var1 variable2:?var2'):
        talk.talk("Step: " + var1 + "= 0" + var2 + "= 0") 
        motor.type(var1 + '= 0')
        motor.type(var2 + '= 0')
        b_unit_task.modify(state='end')
        print('intializing variables')

    def track_var_part1(b_unit_task='unit_task:track_var1 state:running', b_context=' condition:?condition'):
        talk.talk('Step: if x ' + condition + ':')
        motor.type('    if x ' + condition + ':')
        b_unit_task.modify(state='end')
        print('track variables setup')

    def track_var_part2(b_unit_task='unit_task:track_var2 state:running', b_context='variable1:?var1 variable2:?var2'):
        talk.talk('Step:'+ var1 +'+=1,' + var2 + "+= x")
        motor.type('        ' + var1 + "+=1")
        motor.type('        ' + var2 + "+= x")
        b_unit_task.modify(state='end')  
        print('track variables payoff')

    def stop_loopPU(b_unit_task='unit_task:stop_loopPU state:running'):
        b_context.set('finshed:ite_loop status:occupied calling_PU:ite_loopPU')
        b_unit_task.modify(state='stopped')
        print('stopping the loop - PU')


tim = MyAgent()  # name the agent
subway = MyEnvironment()  # name the environment
subway.agent = tim  # put the agent in the environment


python_actr.log_everything(subway)  # #print out what happens in the environment
subway.run()  # run the environment
python_actr.finished()  # stop the environment
