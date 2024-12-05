from mpi4py import MPI

# Initialize the MPI environment if not already initialized
if not MPI.Is_initialized():
    MPI.Init()

# Get the communicator and the rank of the process
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Ensure we have exactly 2 processes
if size != 2:
    if rank == 0:
        print("This program requires exactly 2 processes.")
    if not MPI.Is_finalized():
        MPI.Finalize()
    exit()

# Number of ping-pong iterations
num_iterations = 10
message = "ping-pong"

for i in range(num_iterations):
    if rank == 0:
        # Rank 0 sends the message and then receives it back
        comm.send(message, dest=1, tag=i)
        print(f"Rank 0 sent '{message}' in iteration {i}", flush=True)
        received_message = comm.recv(source=1, tag=i)
        print(f"Rank 0 received '{received_message}' in iteration {i}", flush=True)
    elif rank == 1:
        # Rank 1 receives the message and then sends it back
        received_message = comm.recv(source=0, tag=i)
        print(f"Rank 1 received '{received_message}' in iteration {i}", flush=True)
        comm.send(received_message, dest=0, tag=i)
        print(f"Rank 1 sent '{received_message}' in iteration {i}", flush=True)

# Finalize the MPI environment if not already finalized
if not MPI.Is_finalized():
    MPI.Finalize()
