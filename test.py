
import time
#print the processing message gets two arguments: 1. the max number of iterations and 2. the current iteration
def print_processing_message(current_file: str,max_iter: int, current_iter: int):
    print(f"Processing file: {current_file} - {current_iter}/{max_iter}...", end='\r')

print_processing_message("file1", 10, 5)
time.sleep(1)
print_processing_message("file2", 10, 6)
time.sleep(1)
print_processing_message("file3", 10, 7)
time.sleep(1)
print_processing_message("file4", 10, 8)