import ccm      
log=ccm.log()
log=ccm.log(html=True)   

from ccm.lib.actr import *  



class Problem_Sheet(ccm.Model):        
    rain_problem=ccm.Model(isa='problem', name='rainfall', status='unsolved', text_exp='Given list, sum positive numbers, stop at first -999 in list')


class MotorModule(ccm.Model):     
    def type_first(self, text):           
        #yield 2
        with open('out1.py', 'w') as out: 
            print (text, file = out)
    def type(self, text):           
        #yield 0.5                    #including yield messes up the agent's ability to use it
        with open('out1.py', 'a') as out: 
            print (text, file = out)


 
class MyAgent(ACTR):
    focus=Buffer()
    motor=MotorModule()
    DMbuffer=Buffer()                           
    DM=Memory(DMbuffer, finst_size=5,finst_time=30.0)  

    '''
    Similar to the production driven one (in that all the steps are already there) but this time they're in the DM and not just productions => productions can then act on these steps
    in the declarative knowledge
    '''

    DM.add("step:initialize_variable name1:sum name2:count lstep:None nstep:initialize_list") 
    DM.add("step:initialize_list name1:x name2:rain lstep:initialize_variable nstep:stop_list") 
    DM.add("step:stop_list name1:x name2:-999 lstep:initialize_list nstep:track_variable") 
    DM.add("step:track_variables name1:x name2:0 name3:count name4:sum lstep:stop_list nstep:initialize_variable_2")
    DM.add("step:calculate_average name1:sum name2:count lstep:track_variables nstep:stop") 
    
                            
    
    def init():        
        focus.set("request lstep:None")
 
    def requests(focus = "request lstep:?lstep"):
        DM.request("step:? lstep:?lstep")
        focus.set("step")    

    def ini_variable(focus = 'step', DMbuffer = "step:initialize_variable name1:?name1 name2:?name2 lstep:None" ):
        motor.type(name1 + "= 0")
        motor.type(name2 + "= 0")
        print('variables initialized') 
        focus.set('request lstep:initialize_variable')

    def ini_list(focus = 'step', DMbuffer = "step:initialize_list name1:?name1 name2:?name2 lstep:initialize_variable" ):
        print('start list')
        motor.type('for ' + name1 + " in " + name2 + ":")
        focus.set('request lstep:initialize_list')

    def stop_list(focus = 'step', DMbuffer = "lstep:initialize_list name1:?name1 name2:?name2 step:stop_list" ):
        print('stop list')
        motor.type('    if ' + name1 + ' == ' + name2 + ':')
        motor.type('        break')
        focus.set('request lstep:stop_list')

    def track_var_ave(focus = 'step', DMbuffer = "step:track_variables lstep:stop_list name1:?name1 name2:?name2 name3:?name3 name4:?name4 " ):
        print('track'+ name3 + "+" + name4)
        motor.type('    if ' + name1 + ' >= ' + name2 + ':')
        motor.type('        ' + name3 + "+=1")
        motor.type('        ' + name4 + "+= " + name1)
        focus.set('request lstep:track_variables')


    def calc_ave(focus = 'step', DMbuffer = "step:calculate_average lstep:track_variables name1:?name1 name2:?name2"):
        print('calc average')
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