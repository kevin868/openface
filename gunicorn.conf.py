import multiprocessing

timeout = 90
num_cores = multiprocessing.cpu_count()
print("Number of CPU cores: {}".format(num_cores))
workers = num_cores * 2 + 1
# workers = max(3, workers)
workers = min(3, workers)

# workers = 4
