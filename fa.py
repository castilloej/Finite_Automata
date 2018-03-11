

class FiniteAutomaton:

    def __init__(self, inputStructure = 'dfa.txt'):

        self._faFiles = {}
        self._loadFiles(inputStructure)

        self._finalStates = self._startingState = self._States = self._Alphabet = None
        self._transitionRules = {}
        self._processStructure()

    def __del__(self):

        for currentFile in self._faFiles:
            self._faFiles[currentFile].close()

    def _loadFiles(self, inputStructure):

        self._faFiles['structure'] = open(inputStructure, 'r')

    def _processStructure(self):

        fileLines = self._faFiles['structure'].read().splitlines()

        self._States = fileLines[0].split(',')
        self._Alphabet = fileLines[1].split(',')
        self._startingState = fileLines[2]
        self._finalStates = set(fileLines[3].split(','))

        for line in fileLines[4:]:
            a, b, c = line.split(',')

            if a not in self._transitionRules:
                self._transitionRules[a] = {}

            if b not in self._transitionRules[a]:
                self._transitionRules[a][b] = set()

            self._transitionRules[a][b].add(c)

    def addFile(self, nickname, file, mode):
        self._faFiles[nickname] = open(file, mode)

    def getFile(self, requestedFile):
        return self._faFiles[requestedFile]

    def getTransitions(self):
        return self._transitionRules

    def getFinalStates(self):
        return self._finalStates

    def getStartingState(self):
        return self._startingState

    def getStates(self):
        return self._States

    def getAlphabet(self):
        return self._Alphabet


class SimulateFA:

    def __init__(self, inputStructure = 'dfa.txt', inputInput = 'input.txt', inputOutput = 'output.txt'):

        self._FA = FiniteAutomaton(inputStructure=inputStructure)
        self._FA.addFile('input', inputInput, 'r')
        self._FA.addFile('output', inputOutput, 'w')

        self._results = []
        self._runTests()

        self._dumpOutput()

    def _runTests(self):

        fileLines = self._FA.getFile('input').read().splitlines()

        for test in fileLines:
            simulationResult = 'accept' if self._simulate(test) in self._FA.getFinalStates() else 'reject'
            self._results.append(simulationResult)

    def _simulate(self, test):

        raise NotImplementedError

    def _dumpOutput(self):

        self._FA.getFile('output').write('\n'.join(self._results))


class SimulateDFA(SimulateFA):

    def _simulate(self, test):

        transitionRules = self._FA.getTransitions()
        currentState = self._FA.getStartingState()

        for transition in test:
            here = [element for element in transitionRules[currentState][transition]]
            currentState = here[0]

        return currentState


class SimulateNFA(SimulateFA):

    def _simulate(self, test):

        transitionRules = self._FA.getTransitions()
        finalStates = self._FA.getFinalStates()
        queue = {(self._FA.getStartingState(), test)}
        knowledge = set()

        while queue:

            currentState, stringTest = queue.pop()
            knowledge.add((currentState, stringTest))

            if currentState in transitionRules:

                processMoves = {}

                if '$' in transitionRules[currentState]:
                    processMoves['$'] = stringTest

                if stringTest:
                    processMoves[stringTest[0]] = stringTest[1:]

                for move in processMoves:

                    if move in transitionRules[currentState]:

                        for newState in transitionRules[currentState][move]:

                            if newState == '$':
                                continue

                            if not processMoves[move] and newState in finalStates:
                                return newState

                            if (newState, processMoves[move]) not in knowledge:
                                queue.add((newState, processMoves[move]))

        return None


def NFAtoDFA(finiteAutomata, outputFile='dfa.txt'):

    alphabet = finiteAutomata.getAlphabet()
    currentTransitions = finiteAutomata.getTransitions()

    newTransitions = {}
    newStates = []
    newfinalStates = []

    # TODO: Use reachKnowledge for dynamic programming.
    # TODO: Code has to be optimized and cleaned.
    reachKnowledge = set()

    process = {tuple([finiteAutomata.getStartingState()])}

    while process:

        currentlyProcessing = process.pop()

        for letter in alphabet:

            sCurrentlyProcessing = set(currentlyProcessing)

            thisReaches = set()

            visited = set()
            while sCurrentlyProcessing:

                useThis = sCurrentlyProcessing.pop()
                visited.add(useThis)

                if useThis in currentTransitions and letter in currentTransitions[useThis]:
                    thisReaches = thisReaches.union(currentTransitions[useThis][letter])

                if useThis in currentTransitions and '$' in currentTransitions[useThis]:
                    sCurrentlyProcessing = sCurrentlyProcessing.union(currentTransitions[useThis]['$'])

            yas = ''.join(currentlyProcessing)
            if yas not in newTransitions:
                newTransitions[yas] = {}

            thisReaches = thisReaches if thisReaches else {'uniqueDeadElement'}

            theTuple = tuple(thisReaches)
            maybe = ''.join(theTuple)

            if thisReaches.intersection(finiteAutomata.getFinalStates()) and maybe not in newfinalStates:
                newfinalStates.append(maybe)

            newTransitions[yas][letter] = maybe

            if yas not in newStates:
                newStates.append(yas)

            if maybe not in newTransitions:
                process.add(theTuple)

    finiteAutomata.addFile('newDFA', outputFile, 'w')

    prepare = list()

    prepare.append(','.join(newStates))
    prepare.append(','.join(alphabet))
    prepare.append(finiteAutomata.getStartingState())
    prepare.append(','.join(newfinalStates))

    prepare2 = []
    for k, v in newTransitions.items():

        for letter in alphabet:
            prepare2.append(k + ',' + letter + ',' + newTransitions[k][letter])

    prepare.append('\n'.join(prepare2))

    finiteAutomata.getFile('newDFA').write('\n'.join(prepare))


