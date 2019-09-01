from __future__ import print_function
import os

# Function List:
# 1. netRead: Reading Circuit gate-level netlist file
# 2. gateCalc: function that will work on the logic of each gate
# 3. inputRead: function that will update the circuit dictionary made in netRead to hold the line values
# 4. basic_sim: the actual simulation
# 5. main: The main function


# Defining a function to act as a const variable by returning a list of the LOGIC's
def logicList():
    return ["NOT", "AND", "NAND", "OR", "NOR", "XOR", "XNOR"]


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Reading in the Circuit gate-level netlist file:
def netRead(netName):
    netFile = open(netName, "r")
    # Variables:#
    inputs = []  # array of the input bits
    outputs = []  # array of the output bits
    gates = []   # array of the gate bits
    circuit = {}  # list of all the things in this circuit
    # dest = -999 # the destination bit of the current gate
    # logic = "" # the logic of the current gate
    # terms = [] # the terminals of the current gate
    bitsNeeded = 0 # the number of inputs needed in this given circuit

    for line in netFile:

        # NOT Reading any empty lines
        if (line == "\n"):
            continue

        # Removing spaces and newlines
        line = line.replace(" ","")
        line = line.replace("\n","")

        # NOT Reading any comments
        if (line[0] == "#"):
            continue

        # @ Here it should just be in one of these formats:
        # INPUT(x)
        # OUTPUT(y)
        # z=LOGIC(a,b,c,...)

        # Reading the INPUTS :
        if (line[0:5] == "INPUT"):
            # Removing everything but the numbers
            line = line.replace("INPUT", "")
            line = line.replace("(", "")
            line = line.replace(")", "")

            # Format the variable name to line_*VAR_NAME*
            line = "line_" + line

            # Error detection: line being made already exists
            if line in circuit:
                msg = "NETLIST ERROR: INPUT LINE \"" + line + "\" ALREADY EXISTS PREVIOUSLY IN NETLIST"
                print(msg + "\n")
                return msg
            # Appending the number to the inputs array and update the bitsNeeded
            inputs.append(line)
            circuit[line] = ["INPUT", line, False, 'U']
            bitsNeeded += 1
            continue

        # Reading the OUTPUTS
        if line[0:6] == "OUTPUT":
            # Removing everything but the numbers
            line = line.replace("OUTPUT", "")
            line = line.replace("(", "")
            line = line.replace(")", "")

            # Appending the number to the inputs array
            outputs.append("line_" + line)
            continue

        # Reading the gates
        lineSpliced = line.split("=") # splicing the line at the equals sign to get the destination
        dest = "line_" + lineSpliced[0]

        # Error detection: line being made already exists
        if dest in circuit:
            msg = "NETLIST ERROR: GATE OUTPUT LINE \"" + dest + "\" ALREADY EXISTS PREVIOUSLY IN NETLIST"
            print(msg+"\n")
            return msg

        # Appending the dest name to the gates
        gates.append(dest)

        lineSpliced = lineSpliced[1].split("(") # splicing the line again at the "("  to get the gate logic
        logic = lineSpliced[0].upper()

        # Error detection: logic being called does not exist
        if logic not in logicList():
            msg =  "NETLIST ERROR: LOGIC \"" + logic + "\" DOES NOT EXIST"
            print(msg + "\n")
            return msg

        lineSpliced[1] = lineSpliced[1].replace(")", "")
        terms = lineSpliced[1].split(",")  # Splicing the the line again at each comma to the get the gate terminals
        # Turning each term into an integer before putting it into the circuit dictionary
        terms = ["line_" + x for x in terms]

        # add the dest, logic and terminals to the gates list/table, with the dest as the key
        circuit[dest] = [logic, terms, False, 'U']

    circuit["BITS_NEEDED"] = ["Bits Needed", bitsNeeded]
    circuit["INPUTS"] = ["Inputs", inputs]
    circuit["OUTPUTS"] = ["Outputs", outputs]
    circuit["GATES"] = ["Gates", gates]

    return circuit


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: calculates the logic for each logic/gate
def gateCalc(circuit, node):
    terminals = list(circuit[node][1])

    # If the node is an Inverter gate output, solve and return the output
    if circuit[node][1] == "NOT":
        if circuit[terminals[0]][3] == '0':
            circuit[node][3] = '1'
        elif circuit[terminals[0]][3] == '1':
            circuit[node][3] = '0'
        elif circuit[terminals[0]][3] == "U":
            circuit[node][3] = "U"
        else:  # Should not be able to come here
            return -1
        return circuit

    # If the node is an AND gate output, solve and return the output
    elif circuit[node][0] == "AND":
        # Initialize the output to 1
        circuit[node][3] = '1'
        # Initialize also a flag that detects a U to false
        unknownTerm = False  # This will become True if at least one unknown terminal is found

        # if there is a 0 terminal, AND changes the output to 0. If there is an unknown terminal, mark the flag
        # Otherwise, keep it at 1
        for term in terminals:
            if circuit[term][3] == '0':
                circuit[node][3] = '0'
                break
            if circuit[term][3] == "U":
                unknownTerm = True

        if unknownTerm:
            if circuit[node][3] == '1':
                circuit[node][3] = "U"
        return circuit

    # If the node is a NAND gate output, solve and return the output
    elif circuit[node][0] == "NAND":
        # Initialize the output to 0
        circuit[node][3] = '0'
        # Initialize also a variable that detects a U to false
        unknownTerm = False  # This will become True if at least one unknown terminal is found

        # if there is a 0 terminal, NAND changes the output to 1. If there is an unknown terminal, it
        # changes to "U" Otherwise, keep it at 0
        for term in terminals:
            if circuit[term][3] == '0':
                circuit[node][3] = '1'
                break
            if circuit[term][3] == "U":
                unknownTerm = True
                break

        if unknownTerm:
            if circuit[node][3] == '0':
                circuit[node][3] = "U"
        return circuit

    # If the node is an OR gate output, solve and return the output
    elif circuit[node][0] == "OR":
        # Initialize the output to 0
        circuit[node][3] = '0'
        # Initialize also a variable that detects a U to false
        unknownTerm = False  # This will become True if at least one unknown terminal is found

        # if there is a 1 terminal, OR changes the output to 1. Otherwise, keep it at 0
        for term in terminals:
            print(circuit[term])
            if circuit[term][3] == '1':
                circuit[node][3] = '1'
                break
            if circuit[term][3] == "U":
                unknownTerm = True

        if unknownTerm:
            if circuit[node][3] == '0':
                circuit[node][3] = "U"
        return circuit

    # If the node is an NOR gate output, solve and return the output
    if circuit[node][0] == "NOR":
        # Initialize the output to 1
        circuit[node][3] = '1'
        # Initialize also a variable that detects a U to false
        unknownTerm = False  # This will become True if at least one unknown terminal is found

        # if there is a 1 terminal, NOR changes the output to 0. Otherwise, keep it at 1
        for term in terminals:
            if circuit[term][3] == '1':
                circuit[node][3] = '0'
                break
            if circuit[term][3] == "U":
                unknownTerm = True
        if unknownTerm:
            if circuit[node][3] == '1':
                circuit[node][3] = "U"
        return circuit

    # If the node is an XOR gate output, solve and return the output
    if circuit[node][0] == "XOR":
        # Initialize a variable to zero, to count how many 1's in the terms
        count = 0

        # if there are an odd number of terminals, XOR outputs 1. Otherwise, it should output 0
        for term in terminals:
            if circuit[term][3] == '1':
                count += 1  # For each 1 bit, add one count
            if circuit[term][3] == "U":
                circuit[node][3] = "U"
                return circuit

        # check how many 1's we counted
        if count % 2 == 1:  # if more than one 1, we know it's going to be 0.
            circuit[node][3] = '1'
        else:  # Otherwise, the output is equal to how many 1's there are
            circuit[node][3] = '0'
        return circuit

    # If the node is an XNOR gate output, solve and return the output
    elif circuit[node][0] == "XNOR":
        # Initialize a variable to zero, to count how many 1's in the terms
        count = 0

        # if there is a single 1 terminal, XNOR outputs 0. Otherwise, it outputs 1
        for term in terminals:
            if circuit[term][3] == '1':
                count += 1  # For each 1 bit, add one count
            if circuit[term][3] == "U":
                circuit[node][3] = "U"
                return circuit

        # check how many 1's we counted
        if count % 2 == 1:  # if more than one 1, we know it's going to be 0.
            circuit[node][3] = '1'
        else:  # Otherwise, the output is equal to how many 1's there are
            circuit[node][3] = '0'
        return circuit

    # Error detection... should not be able to get at this point
    return circuit[node][0]


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Updating the circuit dictionary with the input line, and also resetting the gates and output lines
def inputRead(circuit, line):
    # Checking if input bits are enough for the circuit
    if len(line) < circuit["BITS_NEEDED"][1]:
        return -1

    # Getting the proper number of bits:
    line = line[(len(line) - circuit["BITS_NEEDED"][1]):(len(line))]

    # Adding the inputs to the dictionary
    # Since the for loop will start at the most significant bit, we start at bits_needed
    i = circuit["BITS_NEEDED"][1] - 1
    inputs = list(circuit["INPUTS"][1])
    # dictionary item: [(bool) If accessed, (int) the value of each line, (int) layer number, (str) origin of U value]
    for bitVal in line:
        bitVal = bitVal.upper() # in the case user input lower-case u
        circuit[inputs[i]][3] = bitVal # put the bit value as the line value
        circuit[inputs[i]][2] = True  # and make it so that this line is accessed

        # In case the input has an invalid character (i.e. not "0", "1" or "U"), return an error flag
        if bitVal != "0" and bitVal != "1" and bitVal != "U":
            return -2
        i -= 1 # continuing the increments

    return circuit

# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: the actual simulation #
def basic_sim(circuit, debug):
    # QUEUE and DEQUEUE
    # Creating a queue, using a list of the gates
    queue = list(circuit["GATES"][1])
    i = 1
    
    while True:
        i -= 1
        # If there's no more things in queue, no need to work on it
        if len(queue) == 0:
            break

        # Remove the first element of the queue and assign it to a variable for us to use
        curr = queue[0]
        queue.remove(curr)

        # a flag to check if every terminal has been accessed
        term_has_value = True

        # Check if the terminals have been accessed
        for term in circuit[curr][1]:
            if not circuit[term][2]:
                term_has_value = False
                break

        if term_has_value:
            circuit[curr][2] = True

            circuit = gateCalc(circuit, curr)

            # ERROR Detection if LOGIC does not exist
            if isinstance(circuit, str):
                print(circuit)
                return circuit

            print("Progress: " + curr + " = " + str(circuit[curr][3]) + " result of " + circuit[curr][0] + " of:")
            for term in circuit[curr][1]:
                print(term + " = " + str(circuit[term][3]))
            print("\nPress Enter to Continue...")
            raw_input()

        else:
            # If the terminals have not been accessed yet, append the current node at the end of the queue
            queue.append(curr)

    return circuit


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Main Function
def main():
    # **************************************************************************************************************** #
    # NOTE: UI code; Does not contain anything about the actual simulation

    # Used for file access
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in

    print("Circuit Simulator:")

    # Select netlist file
    while True:
        cktFile = "circuit.bench"
        print("\nSelect netlist file:")
        print("Read the " + cktFile + " file?")
        print("If yes, press Enter. Otherwise, type in the filename")
        userInput = raw_input()
        if userInput == "":
            break
        else:
            cktFile = os.path.join(script_dir, userInput)
            if not os.path.isfile(cktFile):
                print("File does not exist, please try again")
            else:
                break

    print("Reading the" + cktFile + " file...")
    circuit = netRead("circuit.bench")
    if isinstance(circuit, str):
        print("\n" + circuit)
        print("\n...PROGRAM EXITS")
        exit()
    print("...Done\n")

    # creating a copy of the circuit for an easy reset
    netList = circuit

    # Select input file
    while True:
        inputName = "input.txt"
        print("\nSelect input file:")
        print("Read the " + inputName + " file?")
        print("If yes, press Enter. Otherwise, type in the filename")
        userInput = raw_input()
        if userInput == "":
            break
        else:
            cktFile = os.path.join(script_dir, userInput)
            if not os.path.isfile(cktFile):
                print("File does not exist, please try again")
            else:
                break

    # Select output file
    while True:
        outputName = "output.txt"
        print("\nSelect output file:")
        print("Read the " + outputName + " file?")
        print("If yes, press Enter. Otherwise, type in the filename" +
              "(This will create a file, if the file does not exist)")
        userInput = raw_input()
        if userInput == "":
            break
        else:
            cktFile = os.path.join(script_dir, userInput)
            if not os.path.isfile(cktFile):
                print("File does not exist, please try again")
            else:
                break

    # Note: UI code;
    # **************************************************************************************************************** #

    print("Simulating the" + inputName + " file and will output in" + outputName + "...")
    inputFile = open(inputName, "r")
    outputFile = open(outputName, "w")

    # Runs the simulator for each line of the input file
    for line in inputFile:
        # Initializing output variable each input line
        output = ""

        # Do nothing else if empty lines, ...
        if (line == "\n"):
            outputFile.write(line)
            continue
        # ... or any comments
        if (line[0] == "#"):
            outputFile.write(line)
            continue

        # Removing the the newlines at the end and then output it to the txt file
        line = line.replace("\n", "")
        outputFile.write(line)

        # Removing spaces
        line = line.replace(" ", "")

        print("For the INPUT: " + line)

        print("Updating circuit dictionary...")
        circuit = inputRead(circuit, line)

        if circuit == -1:
            print("INPUT ERROR: INSUFFICIENT BITS")
            outputFile.write(" -> INPUT ERROR: INSUFFICIENT BITS" + "\n")
            # After each input line is finished, reset the netList
            circuit = netList
            print("...Done\n")
            continue
        elif circuit == -2:
            print("INPUT ERROR: INVALID INPUT VALUE/S")
            outputFile.write(" -> INPUT ERROR: INVALID INPUT VALUE/S" + "\n")
            # After each input line is finished, reset the netList
            circuit = netList
            print("...Done\n")
            continue

        print("...Done\n")

        circuit = basic_sim(circuit, debug)

        for y in circuit["OUTPUTS"][1]:
            if not circuit[y][2]:
                output = "NETLIST ERROR: OUTPUT LINE \"" + y + "\" NOT ACCESSED"
                break
            output = str(circuit[y][3]) + output
        print(line + " -> " + output)
        outputFile.write(" -> " + output + "\n")

        # After each input line is finished, reset the netList
        circuit = netList
    exit()


if __name__ == "__main__":
    main()

