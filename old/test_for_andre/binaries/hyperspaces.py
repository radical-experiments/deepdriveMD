# script to create hyperspaces 

from hyperspace.space import create_hyperspace
import pickle

def get_hyperspaces(parameters = None):

    hyperspaces = create_hyperspace(hyperparameters)
    with open('/home/dakka/spaces.txt', 'wb') as fp: # add the location an argument save known place
        pickle.dump(hyperspaces, fp)
    return hyperspaces


if __name__ == '__main__':
  
    get_hyperspaces(parameters = int(sys.argv[1]))
    




