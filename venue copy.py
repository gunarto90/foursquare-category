
arr = {}
with open('venue_checkina.csv', 'r') as fr:
    for line in fr:
        arr[line.strip()] = 1

with open('venue.csv', 'r') as fr:
    for line in fr:
        split = line.split(',')
        vid = split[0]
        if arr.get(vid) is not None:
            arr[vid] = line

with open('venue_checkin_new.csv', 'w') as fw:
    for key, value in arr.items():
        fw.write(str(value))