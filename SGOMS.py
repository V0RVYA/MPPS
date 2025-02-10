AR = 0, AB = 0, HR = 0, HB = 0, SR = 0, SB = 0
while True:
    faculty = input("Faculty (-1 to end)")
        president = input("President")
        if faculty == -1: break
            if faculty == A and president == R: AR+=1
            if faculty == A and president == B: AB+=1
            if faculty == H and president == R: HR+=1
            if faculty == H and president == B: HB+=1
            if faculty == S and president == R: SR+=1
            if faculty == S and president == B: SB+=1
A = 0, H = 0, S = 0
if AR < AB: A-=1
if AR > AB: A+=1
if SR > SB: S+=1
if SR < SB: S-=1
if HR > HB: H+=1
if HR < HB: H-=1
if A+H+S > 0: print("RED WINS")
if A+H+S < 0: print("BLUE WINS")
