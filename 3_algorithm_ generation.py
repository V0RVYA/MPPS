import ccm      
log=ccm.log()
log=ccm.log(html=True)   

from ccm.lib.actr import *  
'''
So this is the first model where things get a little spicy.
This contains some minor language processing (keywords) but the focus is not on understanding the problem (i.e reading) but rather on constructing the solution (both in memory as
the instruction and in execution)
'''


class Problem_Sheet(ccm.Model):        # items in the environment look and act like chunks - but note the syntactic differences
    rain_problem=ccm.Model(isa='problem', name='rainfall', status='unsolved', text_exp='Given list , calculate average of positive numbers in it , stop at first -999')
#text_exp represents the problem description text, I've basically put in the simplest description of the problem.

class MotorModule(ccm.Model):     # motor module handles typing actions
    def type_first(self, text):           # note that technically the motor module is outside the agent
        #yield 2
        with open('algCon.py', 'w') as out: 
            print (text, file = out)
    def type(self, text):           
        #yield 0.5                    #including yield messes up the agent's ability to use it
        with open('algCon.py', 'a') as out: 
            print (text, file = out)

class Chronotrans(ccm.Model):     # motor module handles typing actions
    def talk(self, text):   #how the agent is able to "program"         
        #yield 0.5                    #yield keeps fucking with the motor module
        with open('algdriven-con-talk.txt', 'a') as chrono: 
            print (text, file = chrono) #I'm also gonna do this for its talk-aloud and be able to make chronotranscripts
 
class MyAgent(ACTR):
    focus=Buffer()
    motor=MotorModule()
    DMbuffer=Buffer()
    talk=Chronotrans()                           
    DM=Memory(DMbuffer, finst_size=5,finst_time=300.0)  

    DM.add("calculate_average average keywords")
    DM.add("calculate_average initialize_variables sum count ")
    DM.add("initialize_variables track_variables ")
    DM.add("iterate_list list keywords")
    DM.add("track_variables iterate_list positive >=0 keywords")
    DM.add("iterate_list stop_list ")
    DM.add("stop_list stop keywords")
    

    
    
    
    
 
    text_list = [] #represents the text of the problem being read

    def init():        
        focus.set("read")

    def textparse(focus = 'read', rain_problem = "status:unsolved text_exp:?text_exp"):
        self.text_list = text_exp.split()  #converts text to a list of the words      
        focus.set("check")

    def read_list(focus = "check"): #this production looks at the next word in the problem text and looks to see if it can act as a keyword to trigger recollection of the necessary step
        if len(self.text_list) != 0:
            i = self.text_list.pop(0) #looks at the next work in the list
            print(i)
            try: 
                int(i)
                DM.add("stop_list ?i no_keyword") #this identifies the number at which the program should stop iterating the list
                self.focus.set('related step:stop_list')
            except ValueError:
                DM.request("? ?i keywords") #if i is not a number -> checks if it is a keyword
                self.focus.set("identify") 
        else:
            self.focus.set('request lstep:None')  #passes to the problem solving productions

    def related_steps_search(focus = "related step:?step"):
        DM.request("?step ? ")
        focus.set("identify") 

    def average_id(focus = "identify", DMbuffer = "calculate_average average keywords"):
        talk.talk('Goal: I should calculate the average of the positive numbers')
        DM.add("step:calculate_average name1:sum name2:count lstep:track_variables nstep:stop")
        focus.set("related step:calculate_average")

    def initialize_var_id(focus = "identify", DMbuffer = "calculate_average initialize_variables sum count"):
        talk.talk('Goal: I should initialize the variables sum and count to track the positive numbers')
        DM.add("step:initialize_variable name1:sum name2:count lstep:None nstep:initialize_list") 
        focus.set("related step:initialize_variables")

    def track_var_id(focus = "identify", DMbuffer = "initialize_variables track_variables"):
        talk.talk('Goal: I should track the positive numbers in the list using the sum and count variables')
        focus.set("related step:track_variables")

    def track_var_complete(focus = "identify", DMbuffer = "track_variables iterate_list ?word ?state keywords"):
        DM.add("step:track_variables name1:?state name2:count name3:sum lstep:stop_list nstep:initialize_variables")
        focus.set("check")

    def list_id(focus = "identify", DMbuffer = "iterate_list list keywords"):
        talk.talk('Goal: I should iterate through the list')
        DM.add("step:initialize_list name1:rain lstep:initialize_variable nstep:stop_list") 
        focus.set("related step:iterate_list")
    
    def stop_list_id(focus = "identify", DMbuffer = "stop_list stop keywords"):
        talk.talk('Goal: I need to stop iterating the loop when I hit the first -999 in the list')
        DM.request("stop_list ?num no_keyword")
        focus.set("identify")

    def stop_list_id_prior(focus = "identify", DMbuffer = "iterate_list stop_list" ):
        DM.request("stop_list ?num no_keyword")
        focus.set("identify")
    
    def stop_list_complete(focus = "identify", DMbuffer = "stop_list ?num no_keyword"):
        DM.add("step:stop_list name1:?num lstep:initialize_list nstep:track_variable") 
        focus.set("check")

    def no_id(focus = "identify", DM = 'error:True'):
        focus.set("check")


    def requests(focus = "request lstep:?lstep"):
        DM.request("step:? lstep:?lstep")
        focus.set("step")    

    def ini_variable(focus = 'step', DMbuffer = "step:initialize_variable name1:?name1 name2:?name2 lstep:None" ):
        motor.type(name1 + "= 0")
        motor.type(name2 + "= 0")
        talk.talk("Step: " + name1 + "= 0" + name2 + "= 0") 
        focus.set('request lstep:initialize_variable')

    def ini_list(focus = 'step', DMbuffer = "step:initialize_list name1:?name1 lstep:initialize_variable" ):
        talk.talk("Step: for x in " + name1 + ":")
        motor.type("for x in " + name1 + ":")
        focus.set('request lstep:initialize_list')

    def stop_list(focus = 'step', DMbuffer = "lstep:initialize_list name1:?name1 step:stop_list" ):
        talk.talk('Step: if x == ' + name1 + ':break')
        motor.type('    if x == ' + name1 + ':')
        motor.type('        break')
        focus.set('request lstep:stop_list')

    def track_var(focus = 'step', DMbuffer = "step:track_variables lstep:stop_list name1:?name1 name2:?name2 name3:?name3" ):
        talk.talk('Step: if x ' + name1 + ':'+ name2 + "+=1," + name3 + "+= x")
        motor.type('    if x ' + name1 + ':')
        motor.type('        ' + name2 + "+=1")
        motor.type('        ' + name3 + "+= x")
        focus.set('request lstep:track_variables')


    def calc_ave(focus = 'step', DMbuffer = "step:calculate_average lstep:track_variables name1:?name1 name2:?name2"):
        talk.talk('Step: average = ' + name1 + '/' + name2)
        motor.type('average = ' + name1 + '/' + name2 )
        focus.set('stop')

    def stop_production(focus='stop'):
        self.stop()


tim=MyAgent()
env=Problem_Sheet()
env.agent=tim 
ccm.log_everything(env)

env.run()
ccm.finished()


'''These are associations the agent needs to have in their declarative knowledge in order to parse the text (they represent linguistic associations between problem solving steps as
well as keywords) => basically encountering a keyword in the problem text triggers recall of programming steps associated with that keyword (such as average being a keyword associated
with calculating the average "calculate_average average keywords"). additionally some steps are associated with other steps in that they require each other 
like "initialize_variables track_variables" -change the bespokeness'''