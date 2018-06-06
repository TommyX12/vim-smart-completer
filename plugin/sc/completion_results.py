#  import vim

import heapq

class UniqueValuedMaxHeap(object):

    """
    A priority queue where all values are unique.
    Data format: (value, priority)
    """

    def __init__ (self, max_entries = 0):
        self.data = []
        self.indices = {}
        self.max_entries = max_entries
    
    def set_max_entries(self, max_entries):
        self.max_entries = max_entries
    
    def clear (self):
        """
        Clears the heap.
        """
        
        self.data = []
        self.indices = {}
    
    def update (self, value, priority, take_max = False):
        """
        Updates a certain value with given priority.
        If take_max is True, only update when priority is greater than previous.
        """
        
        if value in self.indices:
            old_priority = self.data[self.indices[value]][1]
            if take_max and priority <= old_priority:
                return
            
            self.data[self.indices[value]] = (self.data[self.indices[value]][0], priority)
            
            if priority > old_priority:
                self.float_up(self.indices[value])
            
            else:
                self.float_down(self.indices[value])
        
        else:
            if self.max_entries > 0 and len(self.data) >= self.max_entries:
                del self.indices[self.data[len(self.data) - 1][0]]
                self.data[len(self.data) - 1] = (value, priority)
            
            else:
                self.data.append((value, priority))
            
            self.indices[value] = len(self.data) - 1
            
            self.float_up(len(self.data) - 1)
    
    def float_down (self, i):
        """
        Pushes the i-th entry downward on the heap when necessary.
        """
        
        i_value = self.data[i][0]
        i_priority = self.data[i][1]
        j = i
        
        while j < len(self.data) - 1:
            l = 2 * i + 1
            r = 2 * i + 2
            
            if l < len(self.data) and self.data[l][1] > self.data[j][1]:
                j = l
                
            if r < len(self.data) and self.data[r][1] > self.data[j][1]:
                j = r
            
            if j == i:
                break
            
            self.indices[self.data[j][0]] = i
            self.indices[i_value] = j
            self.data[i], self.data[j] = self.data[j], self.data[i]
            
            i = j
        
    def float_up (self, i):
        """
        Pushes the i-th entry upward on the heap when necessary.
        """
        i_value = self.data[i][0]
        i_priority = self.data[i][1]
        j = i
        
        while j > 0:
            j = (i - 1) // 2
            
            if i_priority <= self.data[j][1]:
                break
            
            self.indices[self.data[j][0]] = i
            self.indices[i_value] = j
            self.data[i], self.data[j] = self.data[j], self.data[i]
            
            i = j
        

class CompletionResults(object):
    """
    Container and helpers for completion candidates.
    """
    def __init__ (self, max_entries = None):
        super(CompletionResults, self).__init__()
        
        self.heap = UniqueValuedMaxHeap(max_entries)
    
    def set_max_entries(self, max_entries):
        self.heap.set_max_entries(max_entries)
    
    def clear (self):
        """
        Clears the results.
        """
        
        self.heap.clear()
        
    def add (self, text, priority, take_max = True):
        """
        Add a single result.
        If take_max is True, only update when priority is greater than previous.
        """
        
        self.heap.update(text, priority, take_max)
        
    def get_strings (self):
        """
        Returns the data array as strings.
        """
        
        return [item[0] for item in self.heap.data]
    
    def is_empty(self):
        """
        Returns True iff there are no results.
        """
        
        return len(self.heap.data) == 0


if __name__ == "__main__":
    cr = CompletionResults(3)
    
    cr.add('a', 4)
    print(cr.heap.data)
    cr.add('b', 1)
    print(cr.heap.data)
    cr.add('d', 6)
    print(cr.heap.data)
    cr.add('w', 2)
    print(cr.heap.data)
    cr.add('t', 9)
    print(cr.heap.data)
    cr.add('s', 54)
    print(cr.heap.data)
    cr.add('s', 0)
    print(cr.heap.data)
    cr.add('b', 34)
    print(cr.heap.data)
