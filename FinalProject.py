from cmu_cs3_graphics import *
from PIL import Image
import random
from playerObject import *
from playerLists import *
# https://docs.python.org/2/library/random.html
#https://pillow.readthedocs.io/en/stable/reference/Image.html
def setupCards(app):
    app.allCards = []
    app.playerHand = []
    app.handList = []
    for suit in range(4):
        for face in range(13):
            if face == 0:
                blackround = Image.new('RGBA', (228,317), color = 'black')
                cropRatio = (0,23+336*suit,224*(face+1),336*(suit+1))
                basicCard = app.cards.crop(cropRatio)
                whiteround = Image.new('RGBA', (224,313), color = 'white')
                white = Image.alpha_composite(whiteround, basicCard)
                blackround.paste(white,(2,2))
                app.allCards.append([(face+2,suit),(blackround)])
            else:
                blackround = Image.new('RGBA', (228,317), color = 'black')
                cropRatio = (270*face,23+336*suit,270*(face+1)-46, 336*(suit+1))
                basicCard = app.cards.crop(cropRatio)
                whiteround = Image.new('RGBA', (224,313), color = 'white')
                white = Image.alpha_composite(whiteround,basicCard)
                blackround.paste(white,(2,2))
                app.allCards.append([(face+2,suit),(blackround)])
    app.allCardsFull = copy.deepcopy(app.allCards)
    random.shuffle(app.allCards)

def onAppStart(app):  
# Vectorized Playing Cards 3.2
# https://totalnonsense.com/open-source-vector-playing-cards/
# Copyright 2011,2021 – Chris Aguilar – conjurenation@gmail.com
# Licensed under: LGPL 3.0 - https://www.gnu.org/licenses/lgpl-3.0.html
    app.cards = Image.open('52cards.png')
#Source	David's web
#Author	David Bellot - Berkeley, CA, USA 08/12/2005 - David's web
    app.back = Image.open('card_back.png').resize((50,70))
#made myself
    app.drawBackground = Image.open('Background.png')
#made myself
    app.round0back=CMUImage(Image.open('round0back.png'))
    #credit: free cowboy hat clip-art, picture of myself
    app.easter=Image.open('eastercowboy.png').resize((18,25))
    app.easterClock = 0
    app.background = rgb(176,224,230)
    app.checkNum = 0
    app.foldList = []
    app.reveal = False
    app.face = False
    app.screen = 0
    app.bettingFlag = False
    app.currentPlayerNum = 0
    app.typing = ''
    app.goToNextRealPerson = 0
    app.bet = 0
    app.pot = 0
    app.victoryAmount = 0
    app.round = 0
    app.over = [0,0]
    app.offset = 0
    app.show = False
    app.pWin = 0
    app.realPersonNumber = 0
    app.upperRight = ['Deal','Continue','Betting...','Switch Cards','Continue','Betting...','Reveal','Next Round']
    app.stepsPerSecond = 10

def cardSwitch(app,player): #switches selected cards
    for i in player.switch:
        player.hand.pop(i)
        player.handList.pop(i)
        player.deal(app,1,i)
    player.switch = set()

def pBet(app):
    pRn = app.playerList[app.currentPlayerNum]
    print(pRn.name)
    if app.playersIn == [pRn]:
        print('WINNER')
        app.round = 6
        cleanUpBet(app)
        app.reveal = True
        getWinner(app)
        app.goToNextRealPerson = app.currentPlayerNum
        print(app.round)
    elif pRn.fold or pRn in app.destroyedPlayers:
        app.currentPlayerNum = (app.currentPlayerNum + 1)%5
    elif pRn.betTotal == app.checkNum and pRn.betCount > 0:
        if pRn.checked:
            cleanUpBet(app)
            nextPlayerSwitch(app)
        else:
            if pRn in app.Bots:
                #Lets bots check when at satisfactory betting position
                pRn.bet(app,0)
                pRn.checked = True
    else:
        pRn.checked = False
        if pRn in app.Bots:
            print(pRn.betCount, 'betcount')
            #two layered betting optimization
            #keeps overall pot at standard level in case of weird AI edge cases
            if pRn.betCount > 1:
                pRn.bet(app,app.checkNum-pRn.betTotal)
            else:
                #pRn.bet(app,app.checkNum-pRn.betTotal)
                pRn.betAI(app)

def onStep(app):
    if app.face:
        if app.easterClock <= 40:
            app.easterClock += 1
        app.easter=Image.open('eastercowboy.png').resize((int(18*(1+app.easterClock/2)),int(25*(1+app.easterClock/2))))
    if app.screen != 0:
        app.playerList = [app.P1,app.P2,app.P3,app.P4,app.P5]
        #used this: https://stackoverflow.com/questions/3428536/python-list-subtraction-operation
        app.playersIn = [player for player in app.playerList if player not in app.foldList]
        app.playerPeopleIn = [player for player in app.Players if player not in app.foldList]
        if app.round != 7:
            app.currentPlayerPers = app.Players[app.goToNextRealPerson]
        app.foldList += [player for player in app.destroyedPlayers if player not in app.foldList]
        if app.bettingFlag:
            pBet(app)
    if app.round == 3: #gives slight delay for Bots to switch cards, more natural
        if app.offset < 5:
            app.offset += 1
        if app.offset == 5:
            app.offset += 1
            for bot in app.Bots:
                bot.handSwitchAI(app)
                for i in bot.switch:
                    bot.hand.pop(i)
                    bot.handList.pop(i)
                    bot.deal(app,1,i)

def onMouseMove(app,mouseX,mouseY):
    if 300 <= mouseX <= 420 and 600 <= mouseY <= 700:
        app.over = [1,0]
    elif 980 <= mouseX <= 1100 and 600 <= mouseY <= 700:
        app.over = [0,1]
    else:
        app.over = [0,0]

def onKeyHold(app,key):
    if 'tab' in key:
        app.show = True
def onKeyRelease(app,key):
    if key == 'tab':
        app.show = False
def onKeyPress(app,key):
    if key == 'a':
        for player in app.playerList:
            print(player.name, player.handList, player.handScore(player.handList))
    if key == 'space':
        nextPlayerSwitch(app)
    elif app.bettingFlag:
        if key == 'backspace':
            app.typing = app.typing[:-1]
        elif key == 'enter':
            if app.typing == '': 
                bet = 0
            else:
                bet = int(app.typing)
            if bet < app.checkNum - app.currentPlayerPers.betTotal:
                bet = app.checkNum - app.currentPlayerPers.betTotal
            if bet >= app.currentPlayerPers.money:
                app.currentPlayerPers.allIn = True
            app.currentPlayerPers.bet(app, bet)
            app.typing = ''
            nextPlayerSwitch(app)
        elif key.isnumeric():
            app.typing += key

def onMousePress(app,mouseX,mouseY):
    if app.screen == 0:
        app.playerCount = 0
        if 575 <= mouseX <= 830 and 280 <= mouseY <= 315:
            app.face = True
        if 538 <= mouseX < 882 and 431 <= mouseY < 539:
            app.playerCount = 1
        elif mouseX < 530 or mouseX > 889 or mouseY < 425 or mouseY > 554:
            if 388 <= mouseX < 702:
                if 346 <= mouseY < 484:
                    app.playerCount = 2
                elif 496 <= mouseY < 634:
                    app.playerCount = 4
            elif 716 <= mouseX < 1034:
                if 346 <= mouseY < 484:
                    app.playerCount = 3
                elif 496 <= mouseY < 634:
                    app.playerCount = 5
        if app.playerCount != 0:
            app.face = False
            app.easterClock = 0
            createPlayers(app,app.playerCount)                              
            setupCards(app)
            app.screen = 1 #five card draw
            app.pot = 0
            app.round = 0
            app.offset = 0
            app.reveal = False
    elif app.screen == 1:
        if app.round > 0:
            print('touchtest',app.round,app.bettingFlag,app.P1.checked, app.P1.betCount)
        if mouseX < app.width/6 and mouseY < app.height/10:
            cleanUpBet(app)
            app.screen = 0
            app.round = 0
        elif mouseX > app.width*5/6 and mouseY < app.height/10: #continue button
            if app.round == 0:
                setupCards(app)
                app.P1.deal(app,5)
                app.P2.deal(app,5)
                app.P3.deal(app,5)
                app.P4.deal(app,5)
                app.P5.deal(app,5)
                for player in app.playerList:
                    if player not in app.destroyedPlayers:
                        player.money -= 2
                        app.pot += 2
            elif app.round == 1 or app.round == 4:
                app.bettingFlag = True
            elif app.round == 3:
                for player in app.Players:
                    cardSwitch(app,player)
                for bot in app.Bots:
                    bot.switch = set()
            elif app.round == 6:
                app.reveal = True
                getWinner(app)
            elif app.round == 7:
                for player in app.playerList:
                    if player.money <= 2:
                        if player not in app.destroyedPlayers:
                            app.destroyedPlayers.append(player)
                app.reveal = False
                for player in app.playerList:
                    player.hand = []
                    player.handList = []
                    player.fold = False
                    app.foldList = []   
                app.round = -1
                app.goToNextRealPerson = 0
                nextPlayerSwitch(app)
            if app.round not in [2,5]:
                app.round += 1
        if app.round == 3:
            coord = int((mouseX - 450)/100)
            if coord not in app.currentPlayerPers.switch:
                if 581 <= mouseY <= 720:
                    if 450 <= mouseX <= 950:
                        app.currentPlayerPers.switch.add(coord)
            else:
                if 501 <= mouseY <= 640:
                    if 450 <= mouseX <= 950:
                        app.currentPlayerPers.switch.remove(coord)
        if app.bettingFlag:
            if 300 <= mouseX <= 420 and 600 <= mouseY <= 700: #fold
                app.currentPlayerPers.bet(app, 'f')
                app.foldList.append(app.currentPlayerPers)
            elif 980 <= mouseX <= 1100 and 600 <= mouseY <= 700: #check/call
                if app.checkNum-app.currentPlayerPers.betTotal >= app.currentPlayerPers.money:
                    app.currentPlayerPers.allIn = True
                    bet = app.currentPlayerPers.money
                else:
                    bet = app.checkNum-app.currentPlayerPers.betTotal
                    if bet == 0:
                        app.currentPlayerPers.checked = True
                app.currentPlayerPers.bet(app, bet)
                nextPlayerSwitch(app)

def redrawAll(app):
    if app.screen == 0:
        drawImage(CMUImage(app.drawBackground),0,0)
        if app.face:
            drawImage(CMUImage(app.easter),40,40)
    if app.screen == 1:
        if app.round == 0:
            if app.playerCount > 1:
                drawImage(app.round0back,0,0)
        drawLabel(f'{app.currentPlayerPers.name} Money: {app.currentPlayerPers.money}',
            app.width/2, app.height*15/16, size=18)    
        drawRect(0,0,app.width/6, app.height/10, fill = None, border = 'black')
        drawLabel('Back', app.width/12, app.height/20)
        drawRect(app.width*5/6,0,app.width,app.height/10, fill = None, border = 'black')
        drawLabel(app.upperRight[app.round], app.width*11/12, app.height/20)
        if app.round >= 1:
            if app.round != 7:
                drawLabel(f'Pot: {app.pot}', app.width/2,400, size = 18)
            else:
                if len(app.destroyedPlayers) < 4:
                    drawLabel(f'{app.pWin.name} wins {app.victoryAmount} chips',app.width/2, 300, size = 18)
                else:
                    drawLabel(f'{app.pWin.name} beat everyone else in the casino!',app.width/2, 300, size = 18)
            if not app.currentPlayerPers.fold and app.currentPlayerPers not in app.destroyedPlayers:
                for card in range(len(app.currentPlayerPers.hand)):
                    if app.show or app.playerCount == 1 or app.reveal:
                        cardS = CMUImage(app.currentPlayerPers.hand[card][1].resize((100,139)))
                    else:
                        cardS = CMUImage(app.back.resize((100,139)))
                    if card in app.currentPlayerPers.switch:
                        drawImage(cardS,app.width/2+100*card - (50)*(len(app.currentPlayerPers.hand)-1),
                            app.height*8/10, align = 'bottom')
                    else:
                        drawImage(cardS,app.width/2+100*card - (50)*(len(app.currentPlayerPers.hand)-1),
                            app.height*9/10, align = 'bottom')
            back = CMUImage(app.back)
            if app.reveal:
                for next in range(4):
                    nextP = app.playerList[(app.goToNextRealPerson + next + 1)%5]
                    if not nextP.fold and nextP not in app.destroyedPlayers:
                        if next not in [1,2]:
                            drawLabel(f'{nextP.name}: {nextP.money}', 70 + 420*next,550)
                            for card in range(len(nextP.hand)):
                                cardS = CMUImage(nextP.hand[card][1].resize((100,139)))
                                drawImage(cardS,70+420*next,400+50*card - 25*(len(nextP.hand)-1), 
                                    rotateAngle = 90, align = 'bottom')
                        else:
                            drawLabel(f'{nextP.name}: {nextP.money}', 100+400*next,170)
                            for card in range(len(nextP.hand)):
                                cardS = CMUImage(nextP.hand[card][1].resize((100,139)))
                                drawImage(cardS,600*(next-1)+400+50*card - 25*(len(nextP.hand)-1),0, align = 'top')
            else:
                for next in range(4):
                    nextP = app.playerList[(app.goToNextRealPerson + next + 1)%5]
                    if not nextP.fold and nextP not in app.destroyedPlayers:
                        if next not in [1,2]:
                            drawLabel(f'{nextP.name}: {nextP.money}', 70+420*next,550)
                            for card in range(len(nextP.hand)):
                                if card in nextP.switch:
                                    drawImage(back,70+420*next + 40*((-2/3)*next+1),400+50*card - 25*(len(nextP.hand)-1), 
                                        rotateAngle = 90, align = 'bottom')
                                else:
                                    drawImage(back,70+420*next,400+50*card - 25*(len(nextP.hand)-1), 
                                        rotateAngle = 90, align = 'bottom')
                        else:
                            if nextP.switch != set():
                                drawLabel(f'{nextP.name}: {nextP.money}', 100+400*next,140)
                            else:
                                drawLabel(f'{nextP.name}: {nextP.money}', 100+400*next,100)  
                            for card in range(len(nextP.hand)):
                                if card in nextP.switch:
                                    drawImage(back,600*(next-1)+400+50*card - 25*(len(nextP.hand)-1),40, align = 'top')
                                else:
                                    drawImage(back,600*(next-1)+400+50*card - 25*(len(nextP.hand)-1),0, align = 'top')
                                    
    if (app.bettingFlag and not app.currentPlayerPers.checked):
        filled = [None, 'red']
        if app.currentPlayerNum in app.playerTurns:
            drawLabel('Type the amount you would like to bet.', app.width/2 ,500)
            drawLabel(app.typing, app.width/2, 525)
            drawRect(300,600, 120, 100, fill = filled[app.over[0]], border = 'black')
            drawLabel('Fold', 360,650, size = 18)
            drawRect(980,600, 120, 100, fill = filled[app.over[1]], border = 'black')
            if app.checkNum == app.currentPlayerPers.betTotal:
                drawLabel('Check', 1040, 650, size = 18)
            else:
                drawLabel('Call', 1040, 650, size = 18)

def main():
    runApp(width=1400,height=800)
if __name__ == '__main__':
    main()