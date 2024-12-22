from datetime import datetime, timedelta
from typing import Dict, List
import csv
import re


# Function to read medical records from a file and load into Dictionary
def ReadMedicalRecordsFromFile(RecordsFile: str) -> Dict[str, List[Dict[str, str]]]:
    MedicalRecords = {} #Dictionary 
    
    with open(RecordsFile, 'r') as file:
        for Line in file:
            Line = Line.strip()
            if Line:
                # Split line into parts based on colon and comma separation
                parts = Line.split(': ', 1)
                if len(parts) != 2:
                    continue

                PatientId = parts[0]
                RecordData = parts[1].split(', ')

                record = {
                    "TestName": RecordData[0],
                    "DateTime": RecordData[1],
                    "Result": RecordData[2],
                    "Unit": RecordData[3],
                    "Status": RecordData[4]
                }

                # Add CompletionTime if it exists
                if len(RecordData) == 6:
                    record["CompletionTime"] = RecordData[5]

                # Append to dictionary under corresponding PatientId
                if PatientId not in MedicalRecords:
                    MedicalRecords[PatientId] = []
                MedicalRecords[PatientId].append(record)

    return MedicalRecords

#------------------------------
# Function to parse medical tests file
def ReadMedicalTests(TestsFile):
    MedicalTests = {}
    with open(TestsFile, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                # Extract test name, range, and unit
                parts = line.split(';')
                NamePart = parts[0].split(':')[1].strip()

                # Extract the abbreviation inside the parentheses using regex
                match = re.search(r'\((.*?)\)', NamePart)
                ShortName = match.group(1) if match else NamePart #If no Short name found, the full name is used.

                RangePart = parts[1].split(':')[1].strip()
                UnitPart = parts[2].split(':')[1].strip().split(',')[0]

                # Parse range
                ranges = {}
                if '>' in RangePart and '<' in RangePart:
                    LowRange, HighRange = RangePart.split(',')
                    ranges['low'] = float(LowRange.replace('>', '').strip())
                    ranges['high'] = float(HighRange.replace('<', '').strip())
                elif '>' in RangePart:
                    ranges['low'] = float(RangePart.replace('>', '').strip())
                elif '<' in RangePart:
                    ranges['high'] = float(RangePart.replace('<', '').strip())

                # Store test information
                MedicalTests[ShortName] = {'range': ranges, 'unit': UnitPart}

    return MedicalTests

def UpdateRecord(MedicalRecords: Dict[str, List[Dict[str, str]]], MedicalTestsFile: str, MedicalRecordFile: str):
    # Read the test names from the MedicalTests file
    test_names = set()
    with open(MedicalTestsFile, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split(';')
                name_part = parts[0].split(':')[1].strip()
                # Extract the abbreviation inside the parentheses using regex
                match = re.search(r'\((.*?)\)', name_part)
                short_name = match.group(1) if match else name_part
                test_names.add(short_name)

    # Prompt user for Patient ID
    while True:
        PatientId = input("Enter Patient ID (7 digits) to update records: ").strip()
        if PatientId.isdigit() and len(PatientId) == 7:
            if PatientId in MedicalRecords:
                break
            else:
                print("No records found for this Patient ID.")
                return
        else:
            print("Invalid Patient ID! Please enter a 7-digit ID.")

    # Display all records for the patient
    print(f"Existing records for Patient ID {PatientId}:")
    for index, record in enumerate(MedicalRecords[PatientId], start=1):
        # Format output
        RecordLine = (
            f"\n{index}: TestName: {record['TestName']} \t "
            f"DateTime: {record['DateTime']} \t "
            f"Result: {record['Result']} \t "
            f"Unit: {record['Unit']} \t "
            f"Status: {record['Status']}"
        )
        if 'CompletionTime' in record:
            RecordLine += f"   CompletionTime: {record['CompletionTime']}"
        print(RecordLine)

    # Ask which record to update
    while True:
        try:
            RecordIndex = int(input("\nEnter the record number to update: ").strip()) - 1
            if 0 <= RecordIndex < len(MedicalRecords[PatientId]):
                break
            else:
                print("Invalid record number!")
        except ValueError:
            print("Invalid input! Please enter a valid number.")

    # Selected record to update
    record = MedicalRecords[PatientId][RecordIndex]

    # Menu for updating fields
    print("Choose which field to update:")
    print(" 1: Update Date and Time")
    print(" 2: Update Result")
    print(" 3: Update Status")
    print(" 4: Done Updating.")
    
    while True:
        choice = input("Enter the number of the field to update (1-4): ").strip()
        if choice == '1':  # Update Date and Time
            while True:
                DateTime = input(f" Current Date: {record['DateTime']} \n Enter new Date and Time (YYYY-MM-DD HH:MM: ").strip()
                if DateTime == "":
                    break
                try:
                    datetime.strptime(DateTime, '%Y-%m-%d %H:%M')
                    record['DateTime'] = DateTime
                    break
                except ValueError:
                    print("Invalid Date and Time! Please enter in the format YYYY-MM-DD HH:MM.")
        
        elif choice == '2':  # Update Result
            while True:
                Result = input(f" Current Result: {record['Result']} \n Enter new Result: ").strip()
                if Result == "":
                    break
                try:
                    float(Result)
                    record['Result'] = Result
                    break
                except ValueError:
                    print("Invalid Result! Please enter a numeric value.")
        
        elif choice == '3':  # Update Status
            while True:
                Status = input(f" Current Status: {record['Status']}\n Enter new Status (Pending, Completed, Reviewed): ").strip().capitalize()
                if Status == "":
                    break
                if Status in ['Pending', 'Completed', 'Reviewed']:
                    record['Status'] = Status
                    if Status == "Completed":
                        while True:
                            CompletionTime = input(f"\n Current Date: {record.get('CompletionTime', 'None')} \n Enter new Completion Time (YYYY-MM-DD HH:MM: ").strip()
                            if CompletionTime == "":
                                break
                            try:
                                completion_time_obj = datetime.strptime(CompletionTime, '%Y-%m-%d %H:%M')
                                checkdatetime = datetime.strptime(record['DateTime'], '%Y-%m-%d %H:%M')
                                if completion_time_obj > checkdatetime:
                                    record['CompletionTime'] = CompletionTime
                                    break
                                else:
                                    print("Completion Time must be later than Date and Time!")
                            except ValueError:
                                print("Invalid Completion Time!")
                    else:
                        record.pop('CompletionTime', None)  # Remove CompletionTime if status is not "Completed"
                    break
                else:
                    print("Invalid Status! Please enter a valid status.")
        
        elif choice == '4':  # Done updating
            break
        else:
            print("Invalid choice! Please enter a number between 1 and 4.")

    # Update the MedicalRecordFile with the modified records
    with open(MedicalRecordFile, 'w') as file:
        for PId, records in MedicalRecords.items():
            for record in records:
                RecordLine = f"{PId}: {record['TestName']}, {record['DateTime']}, {record['Result']}, {record['Unit']}, {record['Status']}"
                if 'CompletionTime' in record:
                    RecordLine += f", {record['CompletionTime']}"
                file.write(RecordLine + "\n")

    print("--Record updated successfully!")


###################################

def ValidateRange():
   
    while True:
        print("Enter the Range of the Result:\n Specify the type of range:")
        print("  1. Only Maximum Value")
        print("  2. Only Minimum Value")
        print("  3. Both Maximum and Minimum Values")

        choice = input("Enter your choice: ")
        
        if choice not in {'1', '2', '3'}:
            print(" Invalid choice! Please enter 1, 2, or 3.")
            continue
        
        MinValue = None
        MaxValue = None
        
        if choice in {'1', '3'}:
            while True:
                # Ask for the maximum value
                max_input = input(" Enter the Maximum value: ")
                try:
                    MaxValue = float(max_input)
                    break
                except ValueError:
                    print(" Invalid Value! Please enter a number.")
        
        if choice in {'2', '3'}:
            while True:
                # Ask for the minimum value
                min_input = input(" Enter the Minimum value: ")
                try:
                    MinValue = float(min_input)
                    break
                except ValueError:
                    print(" Invalid Value! Please enter a number.")
        
        if MinValue is not None and MaxValue is not None and MinValue >= MaxValue:
            print(" Minimum value is greater than maximum value! Enter the values again.")
            continue
        
        return MinValue, MaxValue

def ValidateString(value, name):
    
    #Validate if the input value is a non-empty string.
    
    while not value or not value.strip():
        print(f"{name} Cannot Be Empty.")
        value = input(f"Enter a valid {name}: ")
    return value

def ValidateTurnaroundTime(TurnaroundTime):
  
    #Validate the turnaround time in the format DD-hh-mm.
   
    while True:
        # Split the input based on the '-' character
        parts = TurnaroundTime.split('-')
        
        if len(parts) != 3:
            print("Invalid Turnaround Time!")
            TurnaroundTime = input("Enter a valid Turnaround Time (DD-hh-mm): ")
            continue
        
        try:
            days = int(parts[0])
            hours = int(parts[1])
            minutes = int(parts[2])
        except ValueError:
            print("Turnaround time components must be integers.")
            TurnaroundTime = input("Enter a valid Turnaround Time (DD-hh-mm): ")
            continue
        
        if days < 0 or hours < 0 or minutes < 0:
            print("Turnaround time values must be Non-Negative.")
            TurnaroundTime = input("Enter a valid Turnaround Time (DD-hh-mm): ")
            continue
        
        if hours >= 24 or minutes >= 60:
            print("Hours must be less than 24 and minutes must be less than 60.")
            TurnaroundTime = input("Enter a valid Turnaround Time (DD-hh-mm): ")
            continue
        
        return True

#check it, maybe is best
def AddTestToFile(TestsFile):
    # Function to check if a test name or short name already exists
    def TestNameExists(name):
        try:
            with open(TestsFile, 'r') as file:
                for line in file:
                    if f"Name: {name} (" in line:
                        return True
        except FileNotFoundError:
            print(f"File {TestsFile} not found. A new file will be created.")
        return False

    def TestShortNameExists(short_name):
        try:
            with open(TestsFile, 'r') as file:
                for line in file:
                    if f"({short_name})" in line:
                        return True
        except FileNotFoundError:
            print(f"File {TestsFile} not found. A new file will be created.")
        return False

    while True:
        # Prompt for test details
        TestName = input("Enter the Full Test Name: ")
        TestName = ValidateString(TestName, "Test Name")
        
        while TestNameExists(TestName):
            print("  The test name already exists in the file.")
            choice = input("Do you want to enter a new Test Name? (Yes/No): ").strip().lower()
            if choice != 'Yes':
                return
            TestName = input("Enter a new Full Test Name: ")
            TestName = ValidateString(TestName, "Test Name")
        
        ShortName = input("Enter the Short Name: ")
        ShortName = ValidateString(ShortName, "Short Name")
        
        while TestShortNameExists(ShortName):
            print("  The short name already exists in the file.")
            choice = input("Do you want to enter a new short name? (Yes/No): ").strip().lower()
            if choice != 'Yes':
                return
            ShortName = input("Enter a new Short Name: ")
            ShortName = ValidateString(ShortName, "Short Name")
        
        MinValue, MaxValue = ValidateRange()
        if MinValue is None and MaxValue is None:
            print("Invalid Range Values. Please enter valid numerical values.")
            continue
        
        RangeStr = ""
        if MinValue is not None and MaxValue is not None:
            RangeStr = f"> {MinValue}, < {MaxValue}"
        elif MinValue is not None:
            RangeStr = f"> {MinValue}"
        elif MaxValue is not None:
            RangeStr = f"< {MaxValue}"
        
        Unit = input("Enter the Unit (like mg/dL): ")
        Unit = ValidateString(Unit, "Unit")
        
        while True:
            TurnaroundTime = input("Enter the turnaround time (DD-hh-mm): ")
            if ValidateTurnaroundTime(TurnaroundTime):
                break
            else:
                print("Invalid Turnaround Time. Please enter a valid format.")
        
        # Append the new test to the file
        try:
            with open(TestsFile, 'a') as file:
                file.write(f"Name: {TestName} ({ShortName}); Range: {RangeStr}; Unit: {Unit}, {TurnaroundTime}\n")
            print("New test added successfully!")
        except IOError:
            print("Error writing to file. Please check the file path and permissions.")
        
        choice = input("Do you want to Add another Test? (Yes/No): ").strip().lower()
        if choice != 'Yes':
            break

#AddTestToFile('MedicalTests.txt')
def UpdateTest(MedicalTestsFile: str):
    # Read the tests from the MedicalTests file
    MedicalTests = []
    with open(MedicalTestsFile, 'r') as file:
        for line in file:
            MedicalTests.append(line.strip())

    # Display the tests with indexes
    print("Available tests to update:")
    for index, test in enumerate(MedicalTests, start=1):
        print(f"{index}. {test}")

    # Prompt the user to select a test to update
    while True:
        try:
            TestIndex = int(input("\nEnter the number of the test to update: ").strip()) - 1
            if 0 <= TestIndex < len(MedicalTests):
                break
            else:
                print("Invalid test number!")
        except ValueError:
            print("Invalid input! Please enter a valid number.")

    # Selected test to update
    selected_test = MedicalTests[TestIndex]

    # Parse the selected test into components
    parts = selected_test.split(';')
    NamePart = parts[0].split(': ')[1]
    FullName, ShortName = NamePart.split('(')
    ShortName = ShortName.strip(')')
    RangePart = parts[1].split(': ')[1]
    UnitPart, TurnaroundTime = parts[2].split(': ')[1].split(',')

    # Menu for updating fields
    print("\nChoose which field to update:")
    print(" 1: Update Full Name")
    print(" 2: Update Short Name")
    print(" 3: Update Range")
    print(" 4: Update Unit")
    print(" 5: Update Turnaround Time")
    print(" 6: Done Updating.")
    
    while True:
        choice = input("Enter the number of the field to update (1-6): ").strip()
        if choice == '1':  # Update Full Name
            NewFullName = input(f"Current Full Name: {FullName.strip()} \nEnter new Full Name: ").strip()
            if NewFullName:
                FullName = ValidateString(NewFullName, "Full Name")
        
        elif choice == '2':  # Update Short Name
            NewShortName = input(f"Current Short Name: {ShortName} \nEnter new Short Name: ").strip()
            if NewShortName:
                ShortName = ValidateString(NewShortName, "Short Name")
        
        elif choice == '3':  # Update Range
            print("Current Range:", RangePart)
            MinValue, MaxValue = ValidateRange()

            # Update range based on returned values
            if MinValue is not None and MaxValue is not None:
                RangePart = f"> {MinValue}, < {MaxValue}"
            elif MinValue is not None:
                RangePart = f"> {MinValue}"
            elif MaxValue is not None:
                RangePart = f"< {MaxValue}"
            else:
                print("Invalid Range Values. Please enter valid numerical ranges.")
                continue
        
        elif choice == '4':  # Update Unit
            new_unit = input(f"Current Unit: {UnitPart.strip()} \nEnter new Unit: ").strip()
            if new_unit:
                UnitPart = ValidateString(new_unit, "Unit")
        
        elif choice == '5':  # Update Turnaround Time
            NewTurnaroundTime = input(f"Current Turnaround Time: {TurnaroundTime.strip()} \nEnter new Turnaround Time (DD-hh-mm): ").strip()
            if ValidateTurnaroundTime(NewTurnaroundTime):
                TurnaroundTime = NewTurnaroundTime
        
        elif choice == '6':  # Done updating
            break
        else:
            print("Invalid choice! Please enter a number between 1 and 6.")

    # Update the selected test in the list
    UpdatedTest = f"Name: {FullName.strip()} ({ShortName}); Range: {RangePart}; Unit: {UnitPart.strip()}, {TurnaroundTime.strip()}"
    MedicalTests[TestIndex] = UpdatedTest

    # Write the updated tests back to the MedicalTests file
    with open(MedicalTestsFile, 'w') as file:
        for test in MedicalTests:
            file.write(test + "\n")

    print("--Test Updated Successfully!")

# Function to format records
def FormatRecord(PatientId, record):
    FormattedRecord = (f"{PatientId}: {record['TestName']}, "
                        f"{record['DateTime']}, "
                        f"{record['Result']}, "
                        f"{record['Unit']}, "
                        f"{record['Status']}")
    if 'CompletionTime' in record:
        FormattedRecord += f", {record['CompletionTime']}"
    return FormattedRecord

# Function to filter by Patient ID and print formatted records
def FilterByPatientId(MedicalRecords, PatientId):
    return MedicalRecords.get(PatientId, [])


def FilterByTestName(MedicalRecords, TestName):
    FilteredRecords = []
    for PatientId, records in MedicalRecords.items():
        for record in records:
            if record['TestName'] == TestName:
                FilteredRecords.append((PatientId, record))
    return FilteredRecords


# Function to filter by Status
def FilterByStatus(MedicalRecords, status):
    FilteredRecords = []
    for PatientId, records in MedicalRecords.items():
        for record in records:
            if record['Status'] == status:
                FilteredRecords.append((PatientId, record))
    return FilteredRecords


# Function to filter by specific Period
def FilterRecordsByDates(MedicalRecords, StartDate, EndDate):
    FilteredRecords = []
    # Set EndDate to the end of the day
    EndDate = EndDate + timedelta(days=1) - timedelta(seconds=1)

    for PatientId, records in MedicalRecords.items():
        for record in records:
            RecordDate = datetime.strptime(record['DateTime'], "%Y-%m-%d %H:%M")
            if StartDate <= RecordDate <= EndDate:
                FilteredRecords.append((PatientId, record))
    return FilteredRecords


#--------------------------------------------
#Function for filter by specific period
# Function to convert turnaround time to minutes
def TurnaroundTimeToMinutes(TurnaroundTime: str) -> int:
    if TurnaroundTime:
        days, hours, minutes = map(int, TurnaroundTime.split('-'))
        return days * 24 * 60 + hours * 60 + minutes
    return 0

def FilterRecordsByAbnormalTests(MedicalRecords, medical_tests):
    while True:
        FoundAbnormal = False
        
        for PatientId, tests in MedicalRecords.items():
            for test in tests:
                TestName = test['TestName']
                TestResult = float(test['Result'])
                TestStatus = test['Status']

                if TestName in medical_tests:
                    TestRange = medical_tests[TestName]['range']
                    
                    # Check if the test result is abnormal
                    if ('low' in TestRange and TestResult < TestRange['low']) or \
                       ('high' in TestRange and TestResult > TestRange['high']):
                        
                        if not FoundAbnormal:
                            print("\n---------------------------- Abnormal Tests ---------------------------\n")
                            FoundAbnormal = True
                        
                        print(FormatRecord(PatientId, test))
        
        if not FoundAbnormal:
            print("No Abnormal Tests Found.")
        
        break

def FilterRecordsByMultipleCriteria(MedicalRecords, MedicalTests):
    while True:
        # Collect criteria from the user
        criteria = []
        print("\nSelect criteria to filter by:")
        print(" 1: Patient ID")
        print(" 2: Test Name")
        print(" 3: Status")
        print(" 4: Date Range")
        print(" 5: Abnormal Tests")
        print(" 6: Turnaround Time")

        while True:
            choice = input("Enter choice (1-6) or '0' to finish: ")
            if choice == '1':
                criteria.append('Patient ID')
            elif choice == '2':
                criteria.append('Test Name')
            elif choice == '3':
                criteria.append('Status')
            elif choice == '4':
                criteria.append('Date Range')
            elif choice == '5':
                criteria.append('Abnormal Tests')
            elif choice == '6':
                criteria.append('Turnaround Time')
            elif choice == '0':
                break
            else:
                print(" Invalid choice. Please enter a valid option.")

        if not criteria:
            print("No Criteria Selected.")
            break

        # Apply selected criteria
        Records = MedicalRecords.copy()
        
        for criterion in criteria:
            if criterion == 'Patient ID':
                while True:
                    PatientId = input(" Enter Patient ID (7 digit): ").strip()
                    if PatientId.isdigit() and len(PatientId) == 7:
                        if PatientId in MedicalRecords:
                            Records = {pid: records for pid, records in Records.items() if pid == PatientId}
                            break
                        else:
                            print(f"No records found for Patient ID {PatientId}.")
                    else:
                        print("Invalid ID!")

            elif criterion == 'Test Name':
                while True:
                    TestName = input(" Enter Test Name: ").strip()
                    if any(TestName in record['TestName'] for records in MedicalRecords.values() for record in records):
                        Records = {pid: [record for record in records if record['TestName'] == TestName] for pid, records in Records.items()}
                        if not any(Records.values()):
                            print(f"No records found for Test Name '{TestName}'.")
                        break
                    else:
                        print("Invalid Test Name!")
            
            elif criterion == 'Status':
                validStatuses = ['Pending', 'Completed', 'Reviewed']
                status = input(" Enter Status (Pending, Completed, Reviewed): ").capitalize()
                while status not in validStatuses:
                    print("Invalid status!")
                    status = input(" Enter Status (Pending, Completed, Reviewed): ").capitalize()
                Records = {pid: [record for record in records if record['Status'] == status] for pid, records in Records.items()}

            elif criterion == 'Date Range':
                while True:
                    try:
                        InputStartDate = input(" Enter Start Date (YYYY-MM-DD): ")
                        InputEndDate = input(" Enter End Date (YYYY-MM-DD): ")
                        StartDate = datetime.strptime(InputStartDate, "%Y-%m-%d")
                        EndDate = datetime.strptime(InputEndDate, "%Y-%m-%d")
                        EndDate = EndDate + timedelta(days=1) - timedelta(seconds=1)

                        if StartDate > EndDate:
                            print("End date must be after start date. Please re-enter the dates.")
                        else:
                            break

                    except ValueError:
                        print("Invalid date. Please enter dates in YYYY-MM-DD format.")

                Records = {pid: [record for record in records if StartDate <= datetime.strptime(record['DateTime'], "%Y-%m-%d %H:%M") <= EndDate] for pid, records in Records.items()}

            elif criterion == 'Abnormal Tests':
                AbnormalTests = [record for pid, records in MedicalRecords.items() for record in records if
                                  (record['TestName'] in MedicalTests and
                                   (('low' in MedicalTests[record['TestName']]['range'] and float(record['Result']) < MedicalTests[record['TestName']]['range']['low']) or
                                    ('high' in MedicalTests[record['TestName']]['range'] and float(record['Result']) > MedicalTests[record['TestName']]['range']['high'])))]

                Records = {pid: [record for record in records if record in AbnormalTests] for pid, records in Records.items()}

            elif criterion == 'Turnaround Time':
                while True:
                    try:
                        MinTurnaround = input(" Enter Minimum Turnaround Time (DD-HH-MM): ")
                        MaxTurnaround = input(" Enter Maximum Turnaround Time (DD-HH-MM): ")

                        MinTurnaroundMinutes = TurnaroundTimeToMinutes(MinTurnaround)
                        MaxTurnaroundMinutes = TurnaroundTimeToMinutes(MaxTurnaround)

                        if MinTurnaroundMinutes > MaxTurnaroundMinutes:
                            print("Maximum turnaround time must be greater than or equal to minimum turnaround time. Please re-enter.")
                            continue

                        for PatientId, records in Records.items():
                            filtered_records = []
                            for record in records:
                                if record['Status'] == 'Completed' and 'CompletionTime' in record:
                                    TestDateTime = datetime.strptime(record['DateTime'], "%Y-%m-%d %H:%M")
                                    CompletionTime = datetime.strptime(record['CompletionTime'], "%Y-%m-%d %H:%M")
                                    TurnaroundTime = CompletionTime - TestDateTime
                                    TurnaroundTimeMinutes = TurnaroundTime.days * 24 * 60 + TurnaroundTime.seconds // 60
                                    if MinTurnaroundMinutes <= TurnaroundTimeMinutes <= MaxTurnaroundMinutes:
                                        filtered_records.append(record)
                            Records[PatientId] = filtered_records
                        break  # Exit the loop after processing
                    except ValueError:
                        print("Invalid turnaround time format! Please enter the time in DD-HH-MM format.")

        # Print filtered records
        if Records:
            print("\n---------------------------- Filtered Records ---------------------------\n")
            for PatientId, records in Records.items():
                for record in records:
                    print(FormatRecord(PatientId, record))
        else:
            print("No records found based on the selected criteria.")

        break  # End the while loop to avoid repeated prompts

def CalculateTurnaroundTimes(MedicalRecords) -> Dict[str, List[int]]:
    TurnaroundTimes = {}
    
    for PatientId, records in MedicalRecords.items():
        for record in records:
            if 'CompletionTime' in record and record['Status'] == 'Completed':
                TestDateTime = datetime.strptime(record['DateTime'], "%Y-%m-%d %H:%M")
                CompletionTime = datetime.strptime(record['CompletionTime'], "%Y-%m-%d %H:%M")
                TurnaroundTime = CompletionTime - TestDateTime
                TurnaroundTimeMinutes = TurnaroundTime.days * 24 * 60 + TurnaroundTime.seconds // 60
                
                TestName = record['TestName']
                if TestName not in TurnaroundTimes:
                    TurnaroundTimes[TestName] = []
                TurnaroundTimes[TestName].append(TurnaroundTimeMinutes)
                
    return TurnaroundTimes

def GenerateSummaryReport(MedicalRecords):
    TestValues = {}
    TurnaroundTimes = CalculateTurnaroundTimes(MedicalRecords)
    
    for PatientId, records in MedicalRecords.items():
        for record in records:
            TestName = record['TestName']
            Result = float(record['Result'])
            
            if TestName not in TestValues:
                TestValues[TestName] = []
            TestValues[TestName].append(Result)

    for TestName, Results in TestValues.items():
        MinValue = min(Results)
        MaxValue = max(Results)
        AvgValue = sum(Results) / len(Results)
        
        # Calculate turnaround time statistics
        if TestName in TurnaroundTimes:
            Turnaround = TurnaroundTimes[TestName]
            MinTurnaround = min(Turnaround)
            MaxTurnaround = max(Turnaround)
            AvgTurnaround = sum(Turnaround) / len(Turnaround)
        else:
            MinTurnaround = MaxTurnaround = AvgTurnaround = 0
        
        print(f"--------------------------\t{TestName}\t--------------------------")
        print(f" Min Result: {MinValue:.2f}\t Max Result: {MaxValue:.2f}\t Average: {AvgValue:.2f}")
        print(f" Min Turnaround Time: {MinTurnaround} minutes\t Max Turnaround Time: {MaxTurnaround} minutes\t Average Turnaround Time: {AvgTurnaround:.2f} minutes")
        print()

def AddRecord(MedicalRecords: Dict[str, List[Dict[str, str]]], MedicalTestsFile: str, MedicalRecordFile: str):
    # Read the test names from the MedicalTests file
    test_names = set()
    with open(MedicalTestsFile, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split(';')
                name_part = parts[0].split(':')[1].strip()
                # Extract the abbreviation inside the parentheses using regex
                match = re.search(r'\((.*?)\)', name_part)
                short_name = match.group(1) if match else name_part
                test_names.add(short_name)

    # Loop for each input to validate and collect data
    while True:
        # Validate Patient ID
        while True:
            PatientId = input("Enter Patient ID (7 digits): ").strip()
            if PatientId.isdigit() and len(PatientId) == 7:
                break
            else:
                print("Invalid Patient ID! Please enter a 7-digit ID.")

        # Validate Test Name
        while True:
            TestName = input("Enter Test Name: ").strip()
            if TestName in test_names:
                break
            else:
                print("Invalid Test Name! Please enter a valid test name from the list.")

        # Validate Date and Time
        while True:
            DateTime = input("Enter Date and Time (YYYY-MM-DD HH:MM): ").strip()
            try:
                # Parse DateTime input into a datetime object
                checkdatetime = datetime.strptime(DateTime, '%Y-%m-%d %H:%M')
                break
            except ValueError:
                print("Invalid Date and Time!")

        # Validate Result (must be a number)
        while True:
            Result = input("Enter Result : ").strip()
            try:
                float(Result)  # Check if input can be converted to a float
                break
            except ValueError:
                print("Invalid Result! Please enter a numeric value.")

        # Validate Unit
        while True:
            Unit = input("Enter Unit: ").strip()
            if Unit:
                break
            else:
                print("Invalid Unit!")

        # Validate Status
        while True:
            Status = input("Enter Status (Pending, Completed, Reviewed): ").strip().capitalize()
            if Status in ['Pending', 'Completed', 'Reviewed']:
                break
            else:
                print("Invalid Status!")

        # Optional: Validate Completion Time if status is Completed
        CompletionTime = ""
        if Status == "Completed":
            while True:
                CompletionTime = input("Enter Completion Time (YYYY-MM-DD HH:MM): ").strip()
                try:
                    # Parse CompletionTime input into a datetime object
                    checkcompletiontime = datetime.strptime(CompletionTime, '%Y-%m-%d %H:%M')
                    # Check if CompletionTime is after DateTime
                    if checkcompletiontime > checkdatetime:
                        break
                    else:
                        print("Completion Time must be later than Date and Time!")
                except ValueError:
                    print("Invalid Completion Time!")

        # Create record
        record = {
            "TestName": TestName,
            "DateTime": DateTime,
            "Result": Result,
            "Unit": Unit,
            "Status": Status
        }

        if CompletionTime:
            record["CompletionTime"] = CompletionTime

        # Add record to dictionary
        if PatientId not in MedicalRecords:
            MedicalRecords[PatientId] = []
        MedicalRecords[PatientId].append(record)

        # Append the new record to the MedicalRecord file
        with open(MedicalRecordFile, 'a') as file:
            record_line = f"{PatientId}: {TestName}, {DateTime}, {Result}, {Unit}, {Status}"
            if CompletionTime:
                record_line += f", {CompletionTime}"
            file.write(record_line + "\n")

        print("--Record added successfully!")
        break  # Exit loop after adding record


def ExportMedicalRecordsToCSV(MedicalRecords: Dict[str, List[Dict[str, str]]], OutputFile: str) -> None:
   
    # Define the header for the CSV file
    csvHeader = ["PatientID", "TestName", "DateTime", "Result", "Unit", "Status", "CompletionTime"]

    try:
        # Open the output file in write mode
        with open(OutputFile, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Write the header to the CSV file
            writer.writerow(csvHeader)

            # Write each record to the CSV file
            for PatientID, Tests in MedicalRecords.items():
                for Test in Tests:
                    # Extract CompletionTime if status is "Completed"
                    completion_time = Test.get("CompletionTime", "") if Test["Status"] == "Completed" else ""
                    
                    writer.writerow([
                        PatientID,
                        Test["TestName"],
                        Test["DateTime"],
                        Test["Result"],
                        Test["Unit"],
                        Test["Status"],
                        completion_time
                    ])
        print(f"--Medical records successfully exported to {OutputFile}.")

    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")

def ImportCSVToMedicalRecord(CSVFile: str, MedicalRecordFile: str):
   
    try:
        with open(CSVFile, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            RecordsToAppend = []
            
            # Reading the CSV file
            for row in reader:
                try:
                    # Assuming the CSV columns are: Patient ID, Test Name, Test DateTime, Result Value, Results Unit, Status, Results DateTime
                    PatientId = row['Patient ID']
                    TestName = row['Test Name']
                    DateTime = row['Test DateTime']
                    Result = row['Result Value']
                    Unit = row['Results Unit']
                    Status = row['Status']
                    ResultsDateTime = row['Results DateTime']

                    # Validate the date formats
                    try:
                        checkdatetime = datetime.strptime(DateTime, '%Y-%m-%d %H:%M')
                        if ResultsDateTime:
                            checkresultsdatetime = datetime.strptime(ResultsDateTime, '%Y-%m-%d %H:%M')
                    except ValueError:
                        print(f"Invalid date format in record: {row}")
                        continue

                    # Prepare the record for appending
                    RecordLine = f"{PatientId}: {TestName}, {DateTime}, {Result}, {Unit}, {Status}"
                    if ResultsDateTime:
                        RecordLine += f", {ResultsDateTime}"
                    
                    RecordsToAppend.append(RecordLine)

                except KeyError as e:
                    print(f"Missing expected column in CSV: {e}")
                except Exception as e:
                    print(f"Error processing row: {row}, Error: {e}")
        
        # Appending to the MedicalRecord file
        with open(MedicalRecordFile, 'a') as file:
            for record in RecordsToAppend:
                file.write(record + "\n")
        
        print("--Records imported successfully.")
    
    except FileNotFoundError:
        print(f"File not found: {CSVFile}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    
    MedicalTestsFile = 'MedicalTests.txt'
    MedicalRecordFile = 'MedicalRecord.txt'
    MedicalRecords = ReadMedicalRecordsFromFile(MedicalRecordFile)
    MedicalTests = ReadMedicalTests('MedicalTests.txt')
    OutputFile = "medical_records.csv"

    
    print ("\n--------------Medical Record Management System--------------")
    while True:
        choice = input("\n------Hello, Choose one:\n"
                       "  1. Add a Record\n"
                       "  2. Add a new Test\n"
                       "  3. Update Patient Record\n"
                       "  4. Update Medical Test\n"            
                       "  5. Filter Records by Abnormal Tests\n" 
                       "  6: Filter by Multiple Criteria\n"
                       "  7: Generate Summary Report\n"
                       "  8: Export medical records to a comma separated file\n"
                       "  9: Import medical records from a comma separated file\n"
                       "  0: Quit\n"
                       "Enter your choice: ")
        if choice == '1':
            AddRecord(MedicalRecords, MedicalTestsFile, MedicalRecordFile)    
        elif choice == '2':
            AddTestToFile(MedicalTestsFile) 
        elif choice == '3':
            UpdateRecord(MedicalRecords, MedicalTestsFile, MedicalRecordFile)
        elif choice == '4':
            UpdateTest(MedicalTestsFile)        
        elif choice == '5':
            FilterRecordsByAbnormalTests(MedicalRecords, MedicalTests) 
        elif choice == '6':
            FilterRecordsByMultipleCriteria(MedicalRecords, MedicalTests)
        elif choice == '7':
            GenerateSummaryReport(MedicalRecords) 
        elif choice == '8':
            ExportMedicalRecordsToCSV(MedicalRecords, OutputFile)  
        elif choice == '9':
            ImportCSVToMedicalRecord('medicalRecordImport.csv', 'MedicalRecord.txt')       
        elif choice == '0':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please enter a valid option.")