arr = {}
with open('checkin.csv', 'r') as fr:
    for line in fr:
        split = line.split(',')
        venueid = split[len(split)-1]
        arr[venueid] = 1

with open('venue_checkin.csv', 'w') as fw:
    for key, value in arr.items():
        fw.write(str(key))