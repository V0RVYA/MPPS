sum = 0
count = 0
for x in list:
    if x == -999:
        break
    if x>= 0:
        sum += x
        count += 1
average = sum/count
print (average)
