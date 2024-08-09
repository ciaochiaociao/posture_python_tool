from multiprocessing import shared_memory
import numpy as np

def read_from_shared_memory(shm_name):
    # Attach to the existing shared memory block
    existing_shm = shared_memory.SharedMemory(name=shm_name)
    
    # Create a NumPy array using the shared memory buffer
    # shared_array = np.ndarray((10,), dtype=np.int32, buffer=existing_shm.buf)
    
    # print(f"Reader: Shared array: {shared_array}")
    print("Reader: Shared memory data: ", existing_shm.buf[:13].tobytes().decode())
    
    # Modify the shared data
    # shared_array[0] = 100
    # print(f"Reader: Modified shared array: {shared_array}")
    
    # Clean up
    existing_shm.close()

if __name__ == "__main__":
    # shm_name = input("Enter the shared memory name: ")
    read_from_shared_memory("C:\\Users\\550030\\Documents\\test_nodejs_shm\\shared_memory_file")