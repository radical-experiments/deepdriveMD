# script to run optimizations 

class hyperspaces(self, hyperspace_index): 
    def get_spaces(self):

        # load hyperparameter list

        with open('home/dakka/spaces.txt', 'rb') as fp:
            spaces = pickle.load(fp)
        return spaces[hyperspace_index]


if __name__ == '__main__':
    
    hyperspaces.get_spaces(hyperspace_index = int(sys.argv[1]))
