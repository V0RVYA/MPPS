import ccm      
log=ccm.log()
log=ccm.log(html=True)   

from ccm.lib.actr import *  
'''
This is the most basic variant. All it does is follow a set of productions, in order, to write a basic program for the rainfall problem. Canonical solution is followed. 
This would be interpreted as an expert having productions which rapidly execute upon encountering the rainfall problem. 
'''


class Problem_Sheet(ccm.Model):        # this is the environment, not relevant for now, will be more important in later models
    rain_problem=ccm.Model(isa='problem', name='rainfall', status='unsolved', text_exp='Given list, sum positive numbers, stop at first -999 in list')


class MotorModule(ccm.Model):     # motor module handles typing actions
    def type_first(self, text):           # still working this one out
        #yield 2
        with open('out.py', 'w') as out: 
            print (text, file = out)
    def type(self, text):   #how the agent is able to "program"         
        #yield 0.5                    #yield keeps fucking with the motor module
        with open('out.py', 'a') as out: 
            print (text, file = out) #I'm also gonna do this for its talk-aloud and be able to make chronotranscripts



class MyAgent(ACTR):
    focus=Buffer()
    motor=MotorModule()
    DMbuffer=Buffer()                           
    DM=Memory(DMbuffer)                             
    
    def init():
        focus.set("start")
        
    def start_problem(focus='start', rain_problem= 'status:unsolved' ):   #identifies unsolved problem
        focus.set('initialize sum' )

    def ini_sum(focus = 'initialize sum'):  #initializes sum
        motor.type_first("sum = 0")
        focus.set('initialize count') 

    def ini_count(focus='initialize count'): #initializes count
        motor.type("count = 0")
        focus.set('iterate loop')

    def looper(focus = 'iterate loop'): 
        motor.type("for x in list:")        
        focus.set('loop stop at -999')

    def looper_stop(focus = 'loop stop at -999'): #could technically be further divided into a step for conditional and break
        motor.type("    if x == -999:")
        motor.type("        break")        
        focus.set('loop track nums')

    def looper_track(focus = 'loop track nums'): #again could also technically be divided into a series of smaller productions
        motor.type("    if x>= 0:")
        motor.type("        sum += x")
        motor.type("        count += 1")          
        focus.set('calculate average')

    def average(focus = 'calculate average'):
        motor.type("average = sum/count")
        motor.type("print (average)")        
        focus.set('stop')

    def stop_production(focus='stop'):
        self.stop()


tim=MyAgent()
env=Problem_Sheet()
env.agent=tim 
ccm.log_everything(env)

env.run()
ccm.finished()