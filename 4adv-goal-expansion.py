import python_actr      
log=python_actr.log()
log=python_actr.log(html=True)   

from python_actr import *  
'''
This model has the agent 
'''


class Problem_Sheet(python_actr.Model):        # items in the environment look and act like chunks - but note the syntactic differences
    ballot_problem=python_actr.Model(isa='problem', name='ballot', status='unsolved', text_exp='create a system that given input tracks ballot votes for a school presidential race. winner is the one who wins in two out of three faculties. A/S/H = faculty. R/B = president. stop when -1')
#text_exp represents the problem description text, I've basically put in the simplest description of the problem.

class MotorModule(python_actr.Model):     # motor module handles typing actions
    def type_first(self, text):           # note that technically the motor module is outside the agent
        #yield 2
        with open('piecemeal.py', 'w') as out: 
            print (text, file = out)
    def type(self, text):           
        #yield 0.5                    #including yield messes up the agent's ability to use it
        with open('piecemeal.py', 'a') as out: 
            print (text, file = out)

class Chronotrans(python_actr.Model):     # tracks cognitive and programming steps taken by the agent
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
        
        DM.add("step:input_req  keyword:input       request:variables   costeps:Yes stop:No")
        DM.add('step:loop_ite   keyword:tracks      request:variables   costeps:Yes stop:No')
        DM.add('step:stop_loop  keyword:stop        request:variables   costeps:No  stop:Yes')
        DM.add("step:compare    keyword:wins        request:variables   costeps:Yes stop:No")
        DM.add("step:pres_win   keyword:winner      request:variables   costeps:No  stop:No")
        
        DM.add('step:ini_var    keyword:costep3     request:variables   costeps:No  costep:input_req    stop:No')
        DM.add('step:ini_dep    keyword:costep2     request:variables   costeps:No  costep:compare      stop:No')
        DM.add('step:ini_loop   keyword:costep1     request:variables   costeps:No  costep:loop_ite     stop:No')

        DM.add("keyword:input       request:step    variable1:president     variable2:faculty   variable3:None     variable4:None       variable5:None")
        DM.add("keyword:tracks      request:step    variable1:A             variable2:H         variable3:S        variable4:R          variable5:B")
        DM.add('keyword:costep3     request:step    variable1:A             variable2:H         variable3:S        variable4:R          variable5:B')
        DM.add('keyword:wins        request:step    variable1:A             variable2:H         variable3:S        variable4:R          variable5:B')
        DM.add('keyword:costep1     request:step    variable1:A             variable2:H         variable3:S        variable4:R          variable5:B')
        DM.add('keyword:costep2     request:step    variable1:A             variable2:H         variable3:S        variable4:Red        variable5:Blue')
        DM.add('keyword:stop        request:step    variable1:None          variable2:None      variable3:None     variable4:None       variable5:None')



        
        #plan_variables.set("variable1:none variable2:none variable3:none variable4:none")
        focus.set("read")

    def textparse(focus = 'read', ballot_problem = "status:unsolved text_exp:?text_exp"):
        self.text_list = text_exp.split()  #converts text to a list of the words      
        focus.set("check")

    def read_list(focus = "check"): #this production looks at the next word in the problem text and looks to see if it can act as a keyword to trigger recollection of the necessary step
        if len(self.text_list) != 0:
            i = self.text_list.pop(0) #looks at the next work in the list
            print(i) 
            try: 
                int(i)
                DM.add('keyword:stop request:step variable1:?i variable2:None variable3:None variable4:None variable5:None') #this adds any number values to the declarative memory as a keyword
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
    
    def goal_initialize(focus = "variable", DMbuffer = "keyword:?word request:step variable1:?A variable2:?B variable3:?C variable4:?D variable5:?E", plan_step = "keyword:?word request:variables step:?step fire:Yes"):
        DM.add("step:?step name1:?A name2:?B name3:?C name4:?D name5:?E fire:Yes")
        talk.talk("I need to:" + step)        
        focus.set("recall step")

    def variable_request_stop(focus = "understand", DMbuffer = "keyword:?keyword request:variables step:?step costeps:?costep stop:Yes"):
        plan_step.set("keyword:?keyword request:variables step:?step fire:Yes costeps:?costep stop:Yes")
        focus.set("check")
    

    def variable_request_costep(focus = "understand_costep", DMbuffer = "keyword:?keyword request:variables step:?step2", plan_step = "keyword:?keyword step:?step fire:Yes costeps:?costeps" ):
        DM.request("keyword:?keyword request:!variables")
        focus.set("variable")





    
    def request_costep_yes(plan_step = "keyword:?word request:variables step:?step fire:Yes costeps:Yes", focus = "request costeps"):
        DM.request("step:? costep:?step")
        focus.set("costep")

    def request_costep_no(plan_step = "keyword:?word request:variables step:?step fire:Yes costeps:No", focus = "request costeps"):
        plan_step.set("")
        focus.set("check")

    def ID_costep(plan_step = "keyword:?word request:variables step:?step fire:Yes costeps:Yes", focus = "costep", DMbuffer = "step:?step2 keyword:!variables?kword costep:?step costeps:?costeps" ):
        plan_step.set("keyword:?word step:?step2 fire:Yes costeps:?costeps request:variables")
        DM.request("keyword:?word request:variables")
        focus.set("understand_costep")

    def fail_ID_costep(plan_step = "keyword:?word request:variables step:?step fire:Yes costeps:Yes", focus = "costep", DMbuffer = "step:?step2 keyword:!variables?kword costep:?step costeps:?costeps" ):
        talk.talk('I dont know where to go from ' + step)
        focus.set("check")





    def step_recall(focus = "recall step", plan_step = "keyword:?word request:variables step:?step fire:Yes"):
        DM.request("step:?step fire:Yes")        
        focus.set("step")

    def ini_var(focus='step',
                DMbuffer = 'step:ini_var name1:?A name2:?H name3:?S name4:?R name5:?B fire:Yes'):
        motor.type(A + R+'= 0, '+A + B+' = 0, '+H + R+' = 0, '+H + B+' = 0, '+S + R+' = 0, '+S + B+' = 0')
        talk.talk('STEP: AR = 0, AB = 0, HR = 0, HB = 0, SR = 0, SB = 0')
        focus.set('request costeps')


    #The following productions handle unit tasks for looping for department and total winners.
    def input(focus='step',
              DMbuffer = 'step:input_req name1:?A name2:?H name3:?S name4:?R name5:?B fire:Yes'):
        motor.type('    '+A+' = input("'+A+' (-1 to end)")')
        motor.type('    if '+A+' != -1: '+H+' = input("'+H+'")')
        talk.talk('STEP:     faculty = input("Faculty (-1 to end)"')
        talk.talk('STEP:     if faculty !=-1: president = input("President")')
        focus.set('request costeps')

    def ini_loop(focus='step',
                 DMbuffer = 'step:ini_loop name1:? name2:? name3:? name4:? name5:? fire:yes'):
        motor.type('while True:')
        talk.talk('STEP: while True:')
        focus.set('request costeps')

        
    def ite_loop(focus='step',
                 DMbuffer = 'step:loop_ite name1:?A name2:?H name3:?S name4:?R name5:?B fire:Yes'):
        motor.type_first('            if faculty == ' + A + ' and president == '+ R +': '+A + R+'+=1')
        motor.type('            if faculty == '+ A +' and president == '+ B +': '+A + B+'+=1')
        motor.type('            if faculty == '+ H +' and president == '+ R +': '+ H + R +'+=1')
        motor.type('            if faculty == '+ H +' and president == '+ B +': '+ H + B +'+=1')
        motor.type('            if faculty == '+ S +' and president == '+ R +': '+ S + R +'+=1')
        motor.type('            if faculty == '+ S +' and president == '+ B +': '+ S + B +'+=1')
        talk.talk('STEP:            if faculty == A and president == R: AR+=1')
        talk.talk('STEP:            if faculty == A and president == B: AB+=1')
        talk.talk('STEP:             if faculty == H and president == R: HR+=1')
        talk.talk('STEP:            if faculty == H and president == B: HB+=1')
        talk.talk('STEP:            if faculty == S and president == R: SR+=1')
        talk.talk('STEP:             if faculty == S and president == B: SB+=1')
        focus.set('request costeps')

    # The stop_loop productions stops the loop
    def stop_loop(DMbuffer='step:stop_loop name1:?num name2:None name3:None name4:None name5:None fire:Yes',
                  focus='step'):
        motor.type('    if faculty == '+ num +': break')
        talk.talk('STEP:      if faculty == ' + num +': break')
        focus.set('request costeps')

    def compare(focus='step',
                DMbuffer = 'step:compare name1:?A name2:?H name3:?S name4:?R name5:?B fire:Yes'):
        motor.type('if '+ A + R +' < '+ A + B +': '+ A +'-=1')
        motor.type('if '+ A + R +' > '+ A + B +': '+ A +'+=1')
        motor.type('if '+ S + R +' > '+ S + B +': '+ S +'+=1')
        motor.type('if SR < SB: S-=1')
        motor.type('if HR > HB: H+=1')
        motor.type('if HR < HB: H-=1')
        talk.talk('if AR < AB: A-=1')
        talk.talk('if AR > AB: A+=1')
        talk.talk('if SR > SB: S+=1')
        talk.talk('if SR < SB: S-=1')
        talk.talk('if HR > HB: H+=1')
        talk.talk('if HR < HB: H-=1')
        focus.set('request costeps')

    def ini_dep(focus='step',
                DMbuffer='step:ini_dep name1:?A name2:?H name3:?S name4:?R name5:?B fire:Yes'):
        motor.type(''+A+' = 0, '+H+' = 0, '+S+' = 0')
        talk.talk('STEP: A = 0, H = 0, S = 0')
        focus.set('request costeps')

    def pres_win(focus='step',
                 DMbuffer='step:pres_win name1:?A name2:?H name3:?S name4:?R name5:?B fire:Yes'):
        motor.type('if '+A+'+'+H+'+'+S+' > 0: print("'+R +' WINS")')
        motor.type('if '+A+'+'+H+'+'+S+' < 0: print("'+B+' WINS")')
        talk.talk('STEP: if A+H+S < 0: print("BLUE WINS")')
        talk.talk('STEP: if A+H+S > 0: print("RED WINS")')
        focus.set('request costeps')

    def struggle_step(focus='step',
                      DMbuffer='step:?step name1:?A name2:?H name3:?S name4:?R name5:?B fire:Yes'):
        talk.talk('I forget how to implement ' + step)
        focus.set('request costeps')

    
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
python_actr.log_everything(env)

env.run()
python_actr.finished()



