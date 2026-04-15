import threading

class GameState:
    '''
        Inherit from this class for each game to create a game-specific state class that can be used to track 
        the state of the game in a thread-safe way
    '''
    def __init__(self):
        # Create a lock for thread safety
        self._lock = threading.Lock()
        
    # Getter for any attribute
    def get(self, attr):
        with self._lock:
            return getattr(self, attr)
        
    # Setter for any attribute
    def set(self, attr, value):
        with self._lock:
            return setattr(self, attr, value)
        
    def detectStates(self):
        '''
            This function should be overridden in the child class to detect the state of the game and set variables accordingly
        '''
        pass 