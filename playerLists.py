from playerObject import *
def createPlayers(app,numPlayers):
    if numPlayers >= 1:
        app.P1 = Player('P1',[],[],set(),0,'p')
        app.P2 = Player('CPU1',[],[],set(),1,'b')
        app.P3 = Player('CPU2',[],[],set(),2,'b')
        app.P4 = Player('CPU3',[],[],set(),3,'b')
        app.P5 = Player('CPU4',[],[],set(),4,'b')
    if numPlayers >= 2:
        app.P2 = Player('P2',[],[],set(),1,'p')
        app.P3 = Player('CPU1',[],[],set(),2,'b')
        app.P4 = Player('CPU2',[],[],set(),3,'b')
        app.P5 = Player('CPU3',[],[],set(),4,'b')
    if numPlayers >= 3:
        app.P3 = Player('P3',[],[],set(),2,'p')
        app.P4 = Player('CPU1',[],[],set(),3,'b')
        app.P5 = Player('CPU2',[],[],set(),4,'b')
    if numPlayers >= 4:
        app.P4 = Player('P4',[],[],set(),3,'p')
        app.P5 = Player('CPU1',[],[],set(),4,'b')
    if numPlayers == 5:
        app.P5 = Player('P5',[],[],set(),4,'p')
    app.playerList = [app.P1,app.P2,app.P3,app.P4,app.P5]
    onlyBots(app)
    onlyPlayers(app)
    app.currentPlayerPers = app.playerList[app.currentPlayerNum]
    app.destroyedPlayers = []
def onlyBots(app):
    app.Bots = []
    app.botTurns = []
    for bot in app.playerList:
        if bot.playerType == 'b':
            app.Bots.append(bot)
            app.botTurns.append(bot.turn)

def onlyPlayers(app):
    app.Players = []
    app.playerTurns = []
    for player in app.playerList:
        if player.playerType == 'p':
            app.Players.append(player)
            app.playerTurns.append(player.turn)

def cleanUpBet(app):
    app.round += 1
    app.bettingFlag = False
    app.checkNum = 0
    for player in app.playerList:
        player.doneTurn = False
        player.betTotal = 0
        player.checked = False
        player.betCount = 0
    app.goToNextRealPerson = 0

def getWinner(app):
    greatestScore = [(0,[0]),None]
    for player in app.playersIn:
        print(player.handScore(player.handList) , greatestScore[0])
        if player.handScore(player.handList) > greatestScore[0]:
            greatestScore[0] = player.handScore(player.handList)
            greatestScore[1] = player
        elif player.handScore(player.handList) == greatestScore:
            pass
    app.pWin = greatestScore[1]
    greatestScore[1].money += app.pot
    app.victoryAmount = app.pot
    app.pot = 0