import python_actr      
log=python_actr.log()
log=python_actr.log(html=True)   

from python_actr import *  



class Problem_Sheet(python_actr.Model):        
    rain_problem=python_actr.Model(isa='problem', name='rainfall', status='unsolved', text_exp='Given list, sum positive numbers, stop at first -999 in list')


class MotorModule(python_actr.Model):     
    def type_first(self, text):           
        #yield 2
        with open('algDM.py', 'w') as out: 
            print (text, file = out)
    def type(self, text):           
        #yield 0.5                    #including yield messes up the agent's ability to use it
        with open('algDM.py', 'a') as out: 
            print (text, file = out)

class Chronotrans(python_actr.Model):     # motor module handles typing actions
    def talk(self, text):   #how the agent is able to "program"         
        #yield 0.5                    #yield keeps fucking with the motor module
        with open('algdriven-DM-talk.txt', 'a') as chrono: 
            print (text, file = chrono) #I'm also gonna do this for its talk-aloud and be able to make chronotranscripts


 
class MyAgent(ACTR):
    focus=Buffer()
    motor=MotorModule()
    DMbuffer=Buffer()
    talk=Chronotrans()                           
    DM=Memory(DMbuffer, finst_size=5,finst_time=30.0)  

    '''
    Similar to the production driven one (in that all the steps are already there) but this time they're in the DM and not just productions => productions can then act on these steps
    in the declarative knowledge -> buffers/preconditions in description
    '''

    DM.add("step:initialize_variable name1:sum name2:count lstep:None nstep:initialize_loop") 
    DM.add("step:initialize_loop name1:x name2:rain lstep:initialize_variable nstep:stop_list") 
    DM.add("step:stop_list name1:x name2:-999 lstep:initialize_loop nstep:track_variable") 
    DM.add("step:track_variables name1:x name2:0 name3:count name4:sum lstep:stop_list nstep:initialize_variable_2")
    DM.add("step:calculate_average name1:sum name2:count lstep:track_variables nstep:stop") 
    
                            
    
    def init():
        focus.set("request lstep:None")
 
    def requests(focus = "request lstep:?lstep"):
        DM.request("step:? lstep:?lstep")
        focus.set("goal")

    def stateGoal(focus = "goal", DMbuffer = "step:?step"):
        talk.talk('Goal:I am going to:' + step)
        focus.set("step")       

    def ini_variable(focus = 'step', DMbuffer = "step:initialize_variable name1:?name1 name2:?name2 lstep:None" ):
        talk.talk("Step:"+name1+"=0," + name2 + "=0")
        motor.type(name1 + "= 0")
        motor.type(name2 + "= 0")
        focus.set('request lstep:initialize_variable')

    def ini_loop(focus = 'step', DMbuffer = "step:initialize_loop name1:?name1 name2:?name2 lstep:initialize_variable" ):
        talk.talk('Step: for'+ name1 + " in " + name2 + ":")
        motor.type('for ' + name1 + " in " + name2 + ":")
        focus.set('request lstep:initialize_loop')

    def stop_loop(focus = 'step', DMbuffer = "lstep:initialize_loop name1:?name1 name2:?name2 step:stop_list" ):
        talk.talk('Step:if ' + name1 + ' == ' + name2 + ': break')
        motor.type('    if ' + name1 + ' == ' + name2 + ':')
        motor.type('        break')
        focus.set('request lstep:stop_list')

    def track_var_ave(focus = 'step', DMbuffer = "step:track_variables lstep:stop_list name1:?name1 name2:?name2 name3:?name3 name4:?name4 " ):
        talk.talk("Step:if"+ name1 + ' >= ' + name2 + ':'+ name3 + "+=1,"+ name4 + "+= " + name1)
        motor.type('    if ' + name1 + ' >= ' + name2 + ':')
        motor.type('        ' + name3 + "+=1")
        motor.type('        ' + name4 + "+= " + name1)
        focus.set('request lstep:track_variables')


    def calc_ave(focus = 'step', DMbuffer = "step:calculate_average lstep:track_variables name1:?name1 name2:?name2"):
        talk.talk('Step:average = ' + name1 + '/' + name2 )
        motor.type('average = ' + name1 + '/' + name2 )
        focus.set('stop')

    def stop_production(focus='stop'):
        self.stop()


tim=MyAgent()
env=Problem_Sheet()
env.agent=tim 
python_actr.log_everything(env)

env.run()
python_actr.finished()