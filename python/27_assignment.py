marks = {"Maths": 78, "Physics": 35, "Chemistry": 60, "English": 45}
total = 0   #Let current total be 0. 

for i in marks:
    if marks[i] < 50:
        print(f"Marks obtained in {i} are {marks[i]}")

option = int(input("Do you want the total of all the marks and their average? Type 1 for yes and 2 for no: \n"))

if option == 1:
    for i in marks:
        total += marks[i]   #Adding values of marks
    print(f"The total of all marks combined is: {total} and the average of all marks is: {total / len(marks)}")
elif option == 2:
    print("Okay, the total and average won't be printed, as requested.")
else:
    print("Enter the correct option....")