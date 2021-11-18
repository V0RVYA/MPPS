import ccm      
log=ccm.log()
log=ccm.log(html=True)   

from ccm.lib.actr import *  
'''
This model has the agent 
'''


class Problem_Sheet(ccm.Model):        # items in the environment look and act like chunks - but note the syntactic differences
    rain_problem=ccm.Model(isa='problem', name='rainfall', status='unsolved', text_exp='calculate average of positive numbers in list , rains , stop at first -999 in list', variable = 'rains')
#text_exp represents the problem description text, I've basically put in the simplest description of the problem.

class MotorModule(ccm.Model):     # motor module handles typing actions
    def type_first(self, text):           # note that technically the motor module is outside the agent
        #yield 2
        with open('piecemeal.py', 'w') as out: 
            print (text, file = out)
    def type(self, text):           
        #yield 0.5                    #including yield messes up the agent's ability to use it
        with open('piecemeal.py', 'a') as out: 
            print (text, file = out)

class Chronotrans(ccm.Model):     # tracks cognitive and programming steps taken by the agent
    def talk(self, text):           
        #yield 0.5                    
        with open('piecemeal-talk.txt', 'a') as chrono: 
            print (text, file = chrono) 
 
class MyAgent(ACTR): #This is the class defining the agent
    #These are the buffers which the agent uses to manage information between modules (DM, Motor, etc) and the agent
    focus=Buffer()
    motor=MotorModule()
    DMbuffer=Buffer()
    plan_step = Buffer()
    talk=Chronotrans()
    
                               
    DM=Memory(DMbuffer, finst_size=5,finst_time=30.0) #settings for the declarative memory - refer to the Python ACT-R documentation 

      



    text_list = [] #holds the text of the problem being read

    def init():
        # The Goal Expansion model is initialized with keyword associations for goals and associated variables
        #Keyword associations for the goals provide some information through the following slots: (a) step - is the step which would resolve the goal chunk; 
        # (b) keyword - the keyword associated with the goal; (c) request - identifies the information the goal needs to implement the step; 
        # (d) costeps - states if the goal requires the resolution of anyother goals; (e) costep - states the goal that requires the current goal to resolve
        
        DM.add("step:calculate_average keyword:average request:variables costeps:Yes stop:No")
        DM.add('step:loop_iterate keyword:list request:variables costeps:No stop:No')
        DM.add('step:stop_loop_iterate keyword:stop request:variables costeps:No stop:Yes')

        DM.add('step:initialize_variables keyword:costep request:variables costeps:No costep:calculate_average stop:No')
        DM.add("step:track_variables keyword:positive request:variables costeps:No stop:No")


        DM.add("keyword:average request:step variable1:total variable2:count variable3:None variable4:None")
        DM.add("keyword:average request:step variable1:sum variable2:count variable3:None variable4:None")
        DM.add('keyword:list request:step variable1:None variable2:None variable3:x variable4:rains')
        DM.add('keyword:positive request:step variable1:sum variable2:count variable3:x variable4:>=0')
        DM.add('keyword:stop request:when variable1:None variable2:None variable3:x variable4:None')
        
        #plan_variables.set("variable1:none variable2:none variable3:none variable4:none")
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
                DM.add('keyword:stop request:step variable1:None variable2:None variable3:x variable4:?i') #this adds any number values to the declarative memory as a keyword
                self.focus.set('special') #if the word is a number sets the focus buffer to special -> helps agent identify stop signal in provided list
            except ValueError:
                DM.request("keyword:?i request:variables") #checks the DM for the current list word (if it is a keyword)
                self.focus.set("understand")
        else:
            self.focus.set("stop")

    def variable_request_special_stop(focus = "special", plan_step = "keyword:?word request:variables step:?step fire:Yes stop:Yes"):
        DM.request("keyword:?word request:!variables")
        focus.set("variable")

    def variable_request(focus = "understand", DMbuffer = "keyword:?keyword request:variables step:?step costeps:?costep stop:No"):
        plan_step.set("keyword:?keyword request:variables step:?step fire:Yes costeps:?costep")
        DM.request("keyword:?keyword request:!variables")
        focus.set("variable")
    
    def goal_initialize(focus = "variable", DMbuffer = "keyword:?word request:step variable1:?A variable2:?B variable3:?C variable4:?D", plan_step = "keyword:?word request:variables step:?step fire:Yes"):
        DM.add("step:?step name1:?A name2:?B name3:?C name4:?D fire:Yes")
        talk.talk("I need to:" + step)        
        focus.set("recall step")

    def variable_request_stop(focus = "understand", DMbuffer = "keyword:?keyword request:variables step:?step costeps:?costep stop:Yes"):
        plan_step.set("keyword:?keyword request:variables step:?step fire:Yes costeps:?costep stop:Yes")
        focus.set("check")
    

    def variable_request_costep(focus = "understand_costep", DMbuffer = "keyword:?keyword request:variables step:?step2", plan_step = "keyword:?keyword step:?step fire:Yes costeps:?costeps" ):
        DM.request("keyword:?keyword request:!variables")
        focus.set("variable")





    
    def request_costep_yes(plan_step = "keyword:?word request:variables step:?step fire:Yes costeps:Yes", focus = "request costeps"):
        DM.request("step:? keyword:costep costep:?step")
        focus.set("costep")

    def request_costep_no(plan_step = "keyword:?word request:variables step:?step fire:Yes costeps:No", focus = "request costeps"):
        plan_step.set("")
        focus.set("check")

    def ID_costep(plan_step = "keyword:?word request:variables step:?step fire:Yes costeps:Yes", focus = "costep", DMbuffer = "step:?step2 keyword:costep costep:?step costeps:?costeps" ):
        plan_step.set("keyword:?word step:?step2 fire:Yes costeps:?costeps request:variables")
        DM.request("keyword:?word request:variables")
        focus.set("understand_costep")





    def step_recall(focus = "recall step", plan_step = "keyword:?word request:variables step:?step fire:Yes"):
        DM.request("step:?step fire:Yes")        
        focus.set("step")



    def ini_variable(focus = 'step', DMbuffer = "step:initialize_variables name1:?name1 name2:?name2 fire:Yes" ):
        talk.talk("Step: " + name1 + "= 0, " + name2 + "= 0") 
        motor.type(name1 + "= 0")
        motor.type(name2 + "= 0")
        focus.set('request costeps')   

    def calc_ave(focus = 'step', DMbuffer = "step:calculate_average name1:?name1 name2:?name2 fire:Yes"):    
        talk.talk('Step: average = ' + name1 + '/' + name2)
        motor.type('average = ' + name1 + '/' + name2 )
        focus.set('request costeps')

    def loop_iterate(focus = 'step', DMbuffer = "step:loop_iterate name3:?name1 name4:?name2 fire:Yes" ):
        talk.talk("Step: for" + name1 + "in " + name2 + ":")
        motor.type("for " + name1 + " in " + name2 + ":")
        focus.set('request costeps')
    
    def track_var(focus = 'step', DMbuffer = "step:track_variables name1:?name1 name2:?name2 name3:?name3 name4:?name4 fire:Yes" ):
        talk.talk('Step: if '+ name3 + ' ' + name4 + ':'+ name2 + "+=1," + name1 + "+= x")
        motor.type('    if ' + name3 +'  ' + name4 + ':')
        motor.type('        ' + name2 + "+=1")
        motor.type('        ' + name1 + "+= x")
        focus.set('request costeps')

    def stop_loop(focus = 'step', DMbuffer = "step:stop_loop_iterate name1:? name2:? name3:?name2 name4:?name1 fire:Yes" ):
        talk.talk('Step: if' + name2 + '== ' + name1 + ':break')
        motor.type('    if '+ name2 +' == ' + name1 + ':')
        motor.type('        break')
        focus.set('request costep')


    
    def no_id(focus = "understand", DM = 'error:True'):
        focus.set("check")

    def no_var(focus = "variable", DM = 'error:True'):
        focus.set("check")

    def no_step(focus = "step", DM = 'error:True'):
        focus.set("check")

    def no_costep(focus = "costep", DM = 'error:True'):
        focus.set("check")   


    def stop_production(focus='stop'):
        self.stop()


tim=MyAgent()
env=Problem_Sheet()
env.agent=tim 
ccm.log_everything(env)

env.run()
ccm.finished()



