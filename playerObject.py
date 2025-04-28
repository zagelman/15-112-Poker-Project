import copy
import itertools
import random
class Player(object):
    def __init__(self,name,hand, handList, switch, turn, playerType, money = 100):
        self.name = name
        self.money = money
        self.hand = hand
        self.handList = handList
        self.turn = turn
        self.playerType = playerType
        self.doneTurn = False
        self.switch = switch
        self.betTotal = 0
        self.allIn = False
        self.fold = False
        self.eV = 0
        self.betCount = 0
        self.checked = False
        self.handWinRateVar = 0
    def deal(self,app,amount, position = 'end'):
        if len(self.handList) < 5:
            for i in range(amount):
                if position == 'end':
                    self.hand.append(app.allCards.pop())
                    self.handList.append(self.hand[-1][0])
                else:
                    self.hand.insert(position,app.allCards.pop())
                    self.handList.insert(position,self.hand[position][0])
    def handScore(self,hand):
        findMax = []
        for c,s in hand:
            findMax.append(c)
        findMax = sorted(findMax)[::-1]
        def inLine(numCount):
            tempnum = 0
            for num in numCount:
                if tempnum != 0:
                    if num-tempnum != 1:
                        return False
                tempnum = num
            return True
        def findCount(numCount, numLooking, notThese = []):
            highestnum = 0
            for n in numCount:
                if numCount[n] == numLooking and n not in notThese:
                    highestnum = n
            return highestnum  
        #Scores: 
        # used https://www.cardplayer.com/rules-of-poker/hand-rankings
        # (0,2-14) basic
        # (1,2-14) pair
        # (2, (2-14,2-14)) double pair
        # (3, 2-14) three of a kind
        # (4, 6-14) straight cards in  sequence(high card)
        # (5, 2-14) flush same suit no sequence
        # (6, 2-14) full house
        # (7,2-14) four of a kind
        # (8, 6-14) straight flush (high card)
        # (9) royal flush
        suitCount = set()
        numCount = dict()
        for i in hand:
            suitCount.add(i[1])
            numCount[i[0]] = numCount.get(i[0],0) + 1
        #GoodFlush
        if len(suitCount) == 1:
            #Royal Flush
            if {10,11,12,13,14}.issubset(numCount):
                return (9,findMax)
            #Straight Flush
            if inLine(numCount):
                return (8, findMax)
        #Four of a Kind
        thisCount = findCount(numCount,4)
        if thisCount != 0:
            for i in findMax:
                if i != thisCount:
                    break
            return (7,thisCount, i)
        #Full House
        threeofkind = findCount(numCount,3)
        if threeofkind != 0:
            pair1 = findCount(numCount,2,notThese = [threeofkind])
            if pair1 != 0:
                return(6, (threeofkind,pair1))
        #Flush
        if len(suitCount) == 1:
            return (5, findMax)
        #Straight
        if inLine(numCount):
            return (4, findMax)
        #three of a kind
        if threeofkind != 0:
            findMax = findMax[:findMax.index(threeofkind)]+findMax[findMax.index(threeofkind)+3:]
            return(3, threeofkind, findMax)
        #double pair
        pair1 = findCount(numCount,2,)
        if pair1 != 0:
            findMax = findMax[:findMax.index(pair1)]+findMax[findMax.index(pair1)+2:]
            pair2 = findCount(numCount,2,notThese = [pair1])
            if pair2 != 0:
                findMax = findMax[:findMax.index(pair2)]+findMax[findMax.index(pair2)+2:]
                return(2,(pair1,pair2),findMax)
            #pair
            else:
                return(1,pair1, findMax)
        #basic
        return (0,findMax)
    def handWinRate(self, app):
        monteNum = 1000
        handScore = self.handScore(self.handList)
        avgWinRate = [0,0,0,0]
        for pRemain in range(1,5):
            for i in range(monteNum):
                lost = False
                for ops in range(pRemain):
                    opHand = []
                    rands = random.sample(range(52), 5)
                    for card in rands:
                        opHand.append(app.allCardsFull[card][0])
                    if self.handScore(opHand) > handScore:
                        lost = True
                        break
                if lost == False:
                    avgWinRate[pRemain-1] += 1
            avgWinRate[pRemain-1] /= monteNum
        self.handWinRateVar = avgWinRate
        print(self.handWinRateVar)
            
    def bet(self, app, amount):
        self.betCount += 1
        if amount == 'f':
            self.fold = True
            nextPlayerSwitch(app)
        else:
            app.bet = min(amount, self.money)
            if app.checkNum == app.bet + self.betTotal or app.bet == 0:
                self.checked = True
            app.checkNum = app.bet + self.betTotal
            self.betTotal += app.bet
            app.pot += app.bet
            self.money -= app.bet
        #might need to fix this
        if len(app.foldList) < 5: 
            app.currentPlayerNum = (app.currentPlayerNum + 1)%5
            print('test', self.name, amount)
            while app.playerList[app.currentPlayerNum] in app.foldList:
                print('test2')
                app.currentPlayerNum = (app.currentPlayerNum + 1)%5
            # print('test3')
        self.doneTurn = True

    def handSwitchAI(self, app):
        bestHs = self.handScore(self.handList)[0]
        #MonteCarlo AI (purely handbased) (cheats a bit)
        monteNum = 100
        #currently tests once
        #improve MC AI by increasing test rate

        #use this:
        #https://datagy.io/python-combinations-of-a-list/
        seqTests = []
        mockHand = copy.deepcopy(self.handList)
        for seq in range(len(self.handList)+1):
            #Found how to do this with https://docs.python.org/3/library/itertools.html
            seqTests +=(itertools.combinations(list(range(len(self.handList))), seq))
        for seq in seqTests:
            getAvg = 0
            for run in range(monteNum):
                bigDeckSwitch = random.sample(range(len(app.allCards)), len(seq))
                for i in seq:
                    mockHand.pop(i)
                    mockHand.insert(i, app.allCards[bigDeckSwitch[seq.index(i)]][0])
                getAvg += self.handScore(mockHand)[0]
                mockHand = copy.deepcopy(self.handList)
            getAvg /= monteNum
            if getAvg > bestHs:
                bestHs = getAvg
                self.switch = seq
        #TODO add something to reduce chance of changing with low diff
        #and high extra num
    #Sources used for AI:
    #https://courses.cs.washington.edu/courses/cse473/11au/slides/cse473au11-adversarial-search.pdf
    #https://www.youtube.com/watch?v=jaFRyzp7yWw  
    #https://idswater.com/2020/08/28/what-is-expectimax-search/
    #https://www.youtube.com/watch?v=4yMvc1Uph-Y
    #https://www.baeldung.com/cs/expectimax-search
    #https://en.wikipedia.org/wiki/Expectiminimax
    def betAI(self, app):
        for player in app.playerList:
            if player.handWinRateVar == 0:
                player.handWinRate(app)
        tree = {}
        tree[('F',self.turn)] = app.pot
        tree[('min',self.turn)] = self.graphCreate(app,app.checkNum - self.betTotal,app.pot,(self.turn+1)%5)
        r = random.randint(1,10)
        tree[('more',self.turn)] = self.graphCreate(app,app.checkNum - self.betTotal + r,app.pot,(self.turn+1)%5)
        playersIn = app.playersIn
        for key in tree:
            if key[0] == 'F':       foldCash = self.expectimax(app,tree[key], pLeft = len(playersIn)-1)
            elif key[0] == 'min':   minCash = self.expectimax(app,tree[key], pLeft = len(playersIn))
            else:                   moreCash = self.expectimax(app,tree[key], pLeft = len(playersIn))
            self.expectimax(app, tree, pLeft = 5)
        print(foldCash,minCash,moreCash)
        if max(foldCash,minCash,moreCash) == foldCash:
            self.fold = True
            app.foldList.append(self)
            app.currentPlayerNum = (app.currentPlayerNum + 1)%5
        elif max(foldCash,minCash,moreCash) == minCash:
            self.bet(app, app.checkNum-self.betTotal)
        else:
            self.bet(app, app.checkNum-self.betTotal + r)

    def graphCreate(self, app, bet, potTotal, player):
        if player == self.turn:
            return potTotal + bet
        if app.playerList[player] in app.foldList:
            return {('F',player):self.graphCreate(app,0,potTotal+bet,(player+1)%5)}
        else:
            r = random.randint(1,10)
            return {('F',player):self.graphCreate(app,0,potTotal+bet,(player+1)%5), 
            ('min',player) : self.graphCreate(app,app.checkNum-self.betTotal, potTotal+bet, (player+1)%5), 
            ('more',player) : self.graphCreate(app,app.checkNum-self.betTotal + r,potTotal+bet, (player+1)%5)}
    def expectimax(self,app, tree, pLeft = 5):
        if len(app.playersIn) > 1:
            if type(tree) == int:
                return (tree * self.handWinRateVar[pLeft - 2])
            player = list(tree.keys())[0][1]
            winOdds = app.playerList[player].handWinRateVar[pLeft - 2]
            if winOdds < 0.1:   calcOdds = [0.4,0.55,0.05]
            elif winOdds < 0.2: calcOdds = [0.2,0.75,0.05]
            elif winOdds < 0.3: calcOdds = [0.1,0.85,0.05]
            elif winOdds < 0.4: calcOdds = [0.05,0.85,0.1]
            elif winOdds < 0.5: calcOdds = [0.05,0.8,0.15]
            elif winOdds < 0.6: calcOdds = [0.05,0.75,0.2]
            else:               calcOdds = [0.05,0.75,0.2]
            #for key in [('F', player), ('min', player), ('more', player)]:

            eV = 0
            for key in tree:
                if key[0] == 'F':       eV += calcOdds[0]*self.expectimax(app,tree[key], pLeft-1)
                elif key[0] == 'min':   eV += calcOdds[1]*self.expectimax(app,tree[key])
                else:                   eV += calcOdds[2]*self.expectimax(app,tree[key])
            return eV

def nextPlayerSwitch(app):
    print(app.goToNextRealPerson, 'realpersstart')
    if len(app.playerPeopleIn) > 1:
        print('test1')
        app.goToNextRealPerson = (app.goToNextRealPerson + 1)%len(app.Players)
        while app.playerList[app.goToNextRealPerson] in app.foldList:
            app.goToNextRealPerson = (app.goToNextRealPerson + 1)%len(app.Players)
    print(app.goToNextRealPerson,'realpersend')