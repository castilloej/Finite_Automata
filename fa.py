

class SimulateFA:

    def __init__(self, inputStructure = 'dfa.txt', inputInput = 'input.txt', inputOutput = 'output.txt'):

        self._faFiles = {}
        self._loadFiles(inputStructure, inputInput, inputOutput)

        self._finalStates = self._startingState = self._States = self._Alphabet = None
        self._transitionRules = {}
        self._processStructure()

        self._results = []
        self._runTests()

        self._dumpOutput()

    def __del__(self):

        for currentFile in self._faFiles:
            self._faFiles[currentFile].close()

    def _loadFiles(self, inputStructure, inputInput, inputOutput):

        self._faFiles['structure'] = open(inputStructure, 'r')
        self._faFiles['input'] = open(inputInput, 'r')
        self._faFiles['output'] = open(inputOutput, 'w')

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

    def _runTests(self):

        fileLines = self._faFiles['input'].read().splitlines()

        for test in fileLines:
            simulationResult = 'accept' if self._simulate(test) in self._finalStates else 'reject'
            self._results.append(simulationResult)

    def _simulate(self, test):

        raise NotImplementedError

    def _dumpOutput(self):

        self._faFiles['output'].write('\n'.join(self._results))


class SimulateDFA(SimulateFA):

    def _simulate(self, test):

        currentState = self._startingState
        for transition in test:
            here = [element for element in self._transitionRules[currentState][transition]]
            currentState = here[0]

        return currentState


class SimulateNFA(SimulateFA):

    def _simulate(self, test):

        queue = {(self._startingState, test)}
        knowledge = set()

        while queue:

            currentState, stringTest = queue.pop()
            knowledge.add((currentState, stringTest))

            if currentState in self._transitionRules:

                processMoves = {}

                if '$' in self._transitionRules[currentState]:
                    processMoves['$'] = stringTest

                if stringTest:
                    processMoves[stringTest[0]] = stringTest[1:]

                for move in processMoves:

                    if move in self._transitionRules[currentState]:

                        for newState in self._transitionRules[currentState][move]:

                            if newState == '$':
                                continue

                            if not processMoves[move] and newState in self._finalStates:
                                return newState

                            if (newState, processMoves[move]) not in knowledge:
                                queue.add((newState, processMoves[move]))

        return None


SimulateNFA(inputStructure='nfa.txt')
