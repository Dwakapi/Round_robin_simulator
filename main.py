from math import pow


# Recursive formula to create a tree from an array
def create_tree(arr, nxt, it, no):
    if it < no:
        temp = Match(arr[it])
        nxt = temp

        nxt.left = create_tree(arr, nxt.left, 2 * it + 1, no)

        nxt.right = create_tree(arr, nxt.right, 2 * it + 2, no)
    return nxt


# Recursive formula to find all root-to-leaf paths
def path_finder(root, match_path, prob_path, match_paths, prob_paths, trn):

    # Append match id
    match_path.append(root.match_id)
    # Append associated probability
    prob_path.append(root.probability(trn))

    if root.left:
        path_finder(root.left, match_path, prob_path, match_paths, prob_paths, trn)
    if root.right:
        path_finder(root.right, match_path, prob_path, match_paths, prob_paths, trn)
    if not root.left and not root.right:
        # store the copy of list to avoid referencing older list
        match_paths.append(match_path.copy())
        prob_paths.append(prob_path.copy())

    # remove last node to backtrack
    match_path.pop()
    prob_path.pop()


# Helper formula to make a list of zeros of a given length
def zerolistmaker(n):
    listofzeros = [0] * n
    return listofzeros


# Main class containing a given simulated tournament
class Tournament:
    def __init__(self, size):
        self.size = size            # No of players in the tournament
        self.table = []             # Round robin table with all matchups
        self.nodes = ['start']      # List of nodes for a tree of outcomes
        self.tree = None            # Tree of outcomes
        self.players = []           # List of players
        self.match_paths = []       # List of all permutations of outcomes
        self.prob_paths = []        # List of all probabilities of the permutations
        self.cumul_probs = []       # Cumulative probabilities of each ppath
        self.path_tables = []       # Score tables of each path
        self.uniquetables = []      # Unique score tables
        self.uniqueprobs = []       # Cumulative probabilities of each table

    # Private method to create a list of round robin matchups
    def __create_matchups(self):

        p = []
        for i in range(self.size):
            p.append(i + 1)

        # 0 = BYE
        if len(p) % 2:
            p.append(0)

        # Parameters
        n = len(p)  # Number of players
        r = n - 1  # Number of rounds
        g = int(n / 2)  # Number of games per round

        # Creating rotating columns
        A = p[:g]
        B = p[g:]
        B.reverse()
        # fixed = B[0]

        for i in range(r):
            rnd = []
            for j in range(g):
                rnd.append((str(A[j]) + 'v' + str(B[j])))

            self.table.append(rnd)

            # Circle method
            A.insert(1, B.pop(0))
            B.insert(g, A.pop())

    # Private method to generate nodes for the tree based on the matches
    def __create_nodes(self):
        flat_table = [matchid for rnd in self.table for matchid in rnd]
        for i in flat_table:
            count = 2 ** flat_table.index(i)
            for j in range(count):
                self.nodes.append(i + '_W' + i[0])
                self.nodes.append(i + '_W' + i[2])

    def __create_tournament_tree(self):
        self.tree = create_tree(self.nodes, self.tree, 0, len(self.nodes))

    def __generate_paths(self):
        path_finder(self.tree, [], [], self.match_paths, self.prob_paths, self)

    def __get_cumulative_probabilities(self):
        for path in self.prob_paths:
            result = 1
            for prob in path:
                result = result * prob
            self.cumul_probs.append(result)

    def __generate_path_tables(self):
        for path in self.match_paths:
            helpertable = zerolistmaker(self.size)
            for match in path:
                if match != 'start':
                    helpertable[int(match[5]) - 1] += 1
            self.path_tables.append(helpertable)

    def add_player(self, player):
        self.players.append(player)

    def simulate(self):
        if len(self.players) != self.size:
            print('Wrong number of players' + '\n'
                  + 'Tournament size:' + self.size + '\n'
                  + 'Players added:' + str(len(self.players)) + '\n')

        else:
            self.__create_matchups()
            self.__create_nodes()
            self.__create_tournament_tree()
            self.__generate_paths()

    def aggregate(self):
        self.__get_cumulative_probabilities()
        self.__generate_path_tables()
        counter = 0
        for table in self.path_tables:
            if table in self.uniquetables:
                self.uniqueprobs[self.uniquetables.index(table)] += self.cumul_probs[counter]
            elif table not in self.uniquetables:
                self.uniquetables.append(table)
                self.uniqueprobs.append(self.cumul_probs[counter])
            counter += 1


# Class containing a player and their elo score
class Player:
    def __init__(self, name, elo):
        self.name = name
        self.elo = elo

# Class containing a single match as a tree node and associated methods
class Match:
    def __init__(self, match_id, left=None, right=None):
        self.match_id = match_id
        self.left = left
        self.right = right

    # Method to get the depth of this node, currently unused
    def depth(self):
        left_depth = self.left.depth() if self.left else 0
        right_depth = self.right.depth() if self.right else 0
        return max(left_depth, right_depth) + 1

    # Method to get the probability of getting from a parent node to this node
    def probability(self, tournament):
        if self.match_id == 'start':
            return 1

        else:
            # Getting elos of the players participating in this match
            pleftelo = tournament.players[int(self.match_id[0])-1].elo
            prightelo = tournament.players[int(self.match_id[2])-1].elo

            # Elo formula
            rightwin = 1.0/(1.0 + 1.0 * pow(10.0, (pleftelo - prightelo)/400))

            # Checking which player won the match
            if self.match_id[0] == self.match_id[5]:
                return 1.0 - rightwin
            elif self.match_id[2] == self.match_id[5]:
                return rightwin
            else:
                return 0


# Creating all of the players, assigning elos and adding them to the tournament
p1 = Player("Adam", 1493)
p2 = Player("Bartek", 1601)
p3 = Player("Cledzban", 966)
p4 = Player("Dagmara", 1558)
p5 = Player("Edwin", 1249)
p6 = Player("F for respect", 1822)

my_tournament = Tournament(6)
my_tournament.add_player(p1)
my_tournament.add_player(p2)
my_tournament.add_player(p3)
my_tournament.add_player(p4)
my_tournament.add_player(p5)
my_tournament.add_player(p6)

# Running the simulation
my_tournament.simulate()
my_tournament.aggregate()

# print(my_tournament.path_tables)
# print(my_tournament.cumul_probs)
print(len(my_tournament.path_tables))
print(len(my_tournament.cumul_probs))
print(my_tournament.uniqueprobs)
print(my_tournament.uniquetables)
print(len(my_tournament.uniqueprobs))
print(len(my_tournament.uniquetables))
