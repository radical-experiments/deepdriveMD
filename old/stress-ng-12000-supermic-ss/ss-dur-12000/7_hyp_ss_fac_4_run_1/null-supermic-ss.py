from radical.entk import Pipeline, Stage, Task, AppManager
import os
import traceback
import sys
import pickle # change the pickle to json load and dump 
from glob import glob
import radical.utils as ru
import shutil


# convert tabs to spaces (no tabs)


# ------------------------------------------------------------------------------
# Set default verbosity

if os.environ.get('RADICAL_ENTK_VERBOSE') == None:
    os.environ['RADICAL_ENTK_VERBOSE'] = 'INFO'

cur_dir = os.path.dirname(os.path.abspath(__file__))
hostname = os.environ.get('RMQ_HOSTNAME','localhost')
port = int(os.environ.get('RMQ_PORT',5672))

logger = ru.Logger(__name__, level='DEBUG')

class HyperSpacePipeline(Pipeline):
    def __init__(self, name):
        super(HyperSpacePipeline, self).__init__()
        self.name = name 

class HyperSpaceStage(Stage):
    def __init__(self, name):
        super(HyperSpaceStage, self).__init__()
        self.name = name
        

class HyperSpaceTask(Task):
    def __init__(self, name, hyperparameters):

        # this task will generate hyperspaces
        # takes input hyperparameters that are defined by user 
        # and uses HyperSpace function create_hyperspace to generate a list of 
        # hyperspaces 

        super(HyperSpaceTask, self).__init__()
        self.name = name  
        # self.pre_exec = ['source activate ve_hyperspace'] 
        self.pre_exec = ['export PATH=/home/jdakka/stress-ng-0.09.40:$PATH']
        self.executable = ['stress-ng'] 
        self.arguments = ['-c', '1', '-t', '5'] 
        self.copy_input_data = ['$SHARED/hyperspaces.py']
        self.cpu_reqs = {'processes': 1, 'thread_type': None, 'threads_per_process': 1, 'process_type': None}


class OptimizationStage(Stage):
    def __init__(self, name):
        super(OptimizationStage, self).__init__()
        self.name = name    

class OptimizationTask(Task):
    def __init__(self, name, hyperspace_index, duration):

        # this task will execute a Bayesian optimization
        # each task takes a unique hyperspace input  
        
        super(OptimizationTask, self).__init__()
        self.name = name
        self.copy_input_data = ['$SHARED/optimization.py']
        self.pre_exec = ['export PATH=/home/jdakka/stress-ng-0.09.40:$PATH']
        # self.pre_exec += ['python optimization.py {}'.format(hyperspace_index)]
        self.executable = ['stress-ng'] 
        self.arguments = ['-c', '20', '-t', '{}'.format(duration)]
        self.cpu_reqs = {'processes': 1, 'thread_type': None, 'threads_per_process': 20, 'process_type': None}


if __name__ == '__main__':

    # arguments for AppManager


    stress_ng_duration = int(sys.argv[1]) 

    number_of_hyperparameters = int(sys.argv[2])

    walltime = int(sys.argv[3])
    
    strong_scaling = int(sys.argv[4])
    
    # user defines the global search space bounds for each search dimension

    initial_hparams = [(0,7)] 

    final_hparams = list()

    final_hparams += number_of_hyperparameters * [initial_hparams[0]]


    # EnTK single pipeline of two stages 

    # pipelines = set()
    
    # Stage 1: generate all combinations of search subspaces (hyperspaces)

    p = HyperSpacePipeline(name = 'hyperspace_pipeline')

    # s1 = HyperSpaceStage(name = 'hyperspace_stage' )
    
    #t1 = HyperSpaceTask(name = 'hyperspace_generator_task', hyperparameters = final_hparams)  
        
    # Add the Task to the Stage
    # s1.add_tasks(t1)

    # Add Stage to the Pipeline
    # p.add_stages(s1)

    # logger.info('adding stage {} with {} tasks'.format(s1.name, s1._task_count))

    # Stage 2: bag-of-tasks for Bayesian optimizations (2**H tasks) 

    s2 = OptimizationStage(name = 'optimizations') 
    for i in range(2**len(final_hparams)): 
    
        # run Bayesian optimization in parallel
        # each optimization runs for n_iterations

        t = OptimizationTask(name = 'optimization_{}'.format(i), hyperspace_index = i,
                            duration = stress_ng_duration)
        s2.add_tasks(t)
        
    p.add_stages(s2)
        

    # logger.info('adding stage {} with {} tasks'.format(s.name, s._task_count))
    # logger.info('adding pipeline {} with {} stages'.format(p.name, p._stage_count))

    # Create Application Manager
    appman = AppManager(hostname=hostname, port=port)
    
    res_dict = {

        'resource': 'xsede.supermic',
        'project' : 'TG-MCB090174',
        'queue' : 'workq',
        'walltime': walltime,
        'cpus': (2**len(final_hparams)*20)/strong_scaling,
        'access_schema': 'gsissh'
    }


    # Assign resource manager to the Application Manager
    appman.resource_desc = res_dict
    appman.shared_data = ['%s/binaries/hyperspaces.py' %cur_dir, '%s/binaries/optimization.py' %cur_dir]

    
    # Assign the workflow as a set of Pipelines to the Application Manager
    appman.workflow = [p]

    # Run the Application Manager
    appman.run()

