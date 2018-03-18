import time
import os
import pickle

n_bytes = 2**31
max_bytes = 2**31 - 1
    
def load_pickle(file_path):

    bytes_in = bytearray(0)
    input_size = os.path.getsize(file_path)
    with open(file_path, 'rb') as f_in:
        for _ in range(0, input_size, max_bytes):
            bytes_in += f_in.read(max_bytes)
    
    return pickle.loads(bytes_in)

def calc_m_pdf(train_payprice, laplace=1):
    m_counter = [ train_payprice.count(i) for i in range(0, max(train_payprice)+1)]
    m_pdf = [ (i+laplace)/(len(train_payprice) + len(m_counter)*laplace) for i in m_counter ]
    return m_pdf

class Time_Tracking():
    
    start_time = None
    
    def start_tracking(self):
        
        self.start_time = time.time()
    
    def stop_tracking(self):
        
        print("Time used:", round(((time.time() - self.start_time)/60),2), ' minutes')


