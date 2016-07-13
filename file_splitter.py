def write_to_file(filename, array):
    with open(filename, 'w') as fw:
        for s in array:
            fw.write(s)

### Variable to Changes
chunks = 10
filename = 'venue_checkin'
extension = '.csv'

### Variable for Algorithm
size = 0
chunk_size = 0
chunk_counter = 1
counter = 0

# Measure file size
with open('{}{}'.format(filename, extension), 'r') as f:
    for line in f:
        size += 1

chunk_size = int(size / chunks) + 1

print('Number of rows : {}'.format(size))
print('Chunk size     : {}'.format(chunk_size))

# # Split the file into several files
strs = []
with open('{}{}'.format(filename, extension), 'r') as f:
    for line in f:
        counter += 1
        if counter > (chunk_counter * chunk_size):
            write_to_file('{}{}{}'.format(filename, chunk_counter, extension), strs)
            chunk_counter += 1
            # if chunk_counter < chunks:
            strs.clear()
        strs.append(line)
    # The last data
    write_to_file('{}{}{}'.format(filename, chunk_counter, extension), strs)