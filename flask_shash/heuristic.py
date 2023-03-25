nrows=8
ncols=12





#Code Chunk from official python priority queue page
from dataclasses import dataclass, field
from typing import Any
import numpy as np
from queue import PriorityQueue

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    cost: int
    item: Any=field(compare=False)



def printState(array):
    for j in range(7,-1,-1):
        print("")
        for i in array[j]:
            if(i[3]=="UNUSED"):
                print("[  ]", end="\t")
            else:
                print(i[3], end="\t")
#printState(testManifestArray)


#Need Matrix of Ship Containers
#Need Matrix of Buffer Zone
#Need Col # the Crane is picking from

testBuffer = np.zeros(4*24).reshape(4,24)

class State:
    def __init__(self, ship, topLayer=[], buffer=testBuffer):
        self.ship = ship
        self.buffer = buffer
        self.topLayer = topLayer

    def __str__(self):
        printState(self.ship)
        #return f"\n\nPick Col: {self.colPos}"
        return ""


#decorator clas for use with branching
#decorator clas for use with branching
#decorator clas for use with branching
class StateWrapper:
    def __init__(self, state, colPick=-1, h=40, moves = 0, cost=0, movesList = [], load=[], unload=[], status=0):
        self.state = state
        self.colPick = colPick
        self.h = h
        self.moves = moves
        self.cost = cost
        self.movesList = movesList #of the form [(x1,y1), (x2,y2)]
        self.load = load
        self.unload = unload
        self.status = status

    def __str__(self):
        printState(self.state.ship)
        t=""
        if self.colPick>0:
            t=f"\n\nPick Col: {self.colPick}"
        return t+f"\nh: {self.h}\n# of Moves: {self.moves}\nCost: {self.cost}\nMovesList: {self.movesList}\nload{self.load}\nunload{self.unload}"
    
def stackHeight(array, col, nrows=nrows):
    for row in range(nrows-1,-1,-1):
        if(array[row,col,3] != "UNUSED"):
            return row
    return(-1)
    #-1 means no containers/blocked spaces in col

def heights(array, cols=ncols):
    h = []
    for col in range(0,cols):
        h.append(stackHeight(array,col) + 1)
    return h


def updateTop(array, cols=ncols):
    top = []
    for i in range(0,cols):
        h = stackHeight(array,i)
        if(h!=-1):
#             top.append( np.append(array[h,i,2:4],h) )
            top.append( (array[h,i]) )
        else:
#             top.append(np.array(['-99999','NONAME',h]))
            top.append(np.array(['00','00','-99999','NONAME']))
    return np.array(top)

def removeEmpty(array, pos = 3):
    filterArray = ((array[:,:,pos] != 'UNUSED') == (array[:,:,pos] != 'NAN'))
    return (array[filterArray])

def pickable(array, col, nrows=nrows):
    h = stackHeight(array,col,nrows)
    if(array[h,col,3]=="NAN" or h==-1):
        return False
    return True


def moveContainer(array, col, newCol, unload=0):
    # if(col==newCol):
    #     return -1
    #find where to place container
    h1 = stackHeight(array,col)
    h2 = stackHeight(array,newCol) +1 
        
    newArray = array.copy()
    if(unload == 0):
        newArray[h2,newCol,2:4] = newArray[h1,col,2:4]  
    newArray[h1,col,2:4] = ['00000','UNUSED']
    
    return newArray


def costCol(array, curCol, newCol, empty=0, h1=-1, h2=-1):
    hs = heights(array)    
    
    if(h1<0):
        h1 = hs[curCol]
    if(h2<0):
        h2 = hs[newCol]
    
    #check if there exists in between area
    localMax=h2
    if(abs(curCol-newCol) > 1):
        localMax = max(hs[min(curCol,newCol)+1:max(curCol,newCol)+1]) - empty
    
    if(h1>=localMax):
        return 0 + abs(curCol-newCol) + abs(localMax-h2)
    else:
        return abs(localMax-h1) + abs(curCol-newCol) + abs(localMax-h2)
    

#-----------------------------------------------
#---------------LOAD/UNLOAD---------------------
#-----------------------------------------------

def unloadTop(state, unload, cols=ncols):
    #Shows us cols of states to pick from which have exposed unload container
    top = np.array((updateTop(state.state.ship, cols=cols)))
    
    filterTop = top[((top[:,3] != 'NONAME') == (top[:,3] != 'NAN'))]
#     print(filterTop)
    
    unloadable = []
    for i in filterTop:
        for w in unload:
            if(i[3]==w):
                unloadable.append(int(i[1])-1)
    
    return unloadable

def countUnload(state, cols=ncols):
    array = (state.state.ship)
    unload = state.unload
    unloadable=[]
    for i in range(cols):
        num = 0
        for w in range(len(array[:,0])):
            if (array[w,i,3] in unload):
                num+=1
        unloadable.append(num)
    
    return np.array(unloadable)
    

#find nearest col to load from left
def nearestLoad(unloadable, col=0):
    #expecting np.array
    left = right = col

    while( left >=0 or right < len(unloadable)):
        if(left >=0 and unloadable[left]==0):
            return left
        left-=1
        if(right < len(unloadable) and unloadable[right]==0):
            return right
        right+=1
    return -1

#distance to pink block (to ship/buffer)
def distToPink(row,col):
    return (nrows-row)+(col)

#create container at location
def createContainer(array, col, container):
    h = stackHeight(array,col)
    tmp = array.copy()
    tmp[h+1,col,2:4] = container
    return tmp

def loadHeuristic(state):
    load = state.load
    unload = state.unload
    return len(load)+len(unload)

def LoadingBranch(testManifestArray, unloadIn, load):

    # unloadIn = []
    # load = []

    #tracking how many duplicate states
    old=100

    #cost of going to truck
    costBetweenPink = 2

    #duplicate states checker
    duplicateState = []

    #legal final states
    finalState = []

    #Create PriorityQueue for queing states
    queueMain = PriorityQueue()

                
    depth = 0
    minCost = 10000



    #when tracking moves, compensate coordinates +1 for dropoff location to match pick up
    #**coordinates start at 1, not 0**
    comp = 1

    #cleanup unload data
    unloadT = []
    unload = []
    for i in unloadIn:
        unloadT.append(np.array(testManifestArray[i[0]-comp,i[1]-comp, 3]))
    unloadT = np.array(unloadT)

    if(len(unloadT)):
        unload = np.array(unloadT[(unloadT[:] != 'UNUSED') == (unloadT[:] != 'NAN')])

    #using colPick attribute of class to show previous col
        #-1 means previous cell was buffer

    #initial state:
    initialState = StateWrapper(State(testManifestArray),h=0,load=load,unload=unload, colPick=-1)
    queueMain.put(PrioritizedItem(1, 1, initialState))

    while not queueMain.empty():
        currentState=queueMain.get().item
    #     if(len(currentState.load)==0 and len(currentState.unload)==0):
    #             print("no more states")    
    #             break
        
        #At Each state we have 3 choices
            #unload available container                           (high priority)
            #load container from truck                            (high priority if crane empty)
            #move container on ship from on place to another      (low priority, only do if cant do prev 2)
        
        #first always attempt to unload container
        
        #first we find cols where there is a container we can pick right away
        unloadable = unloadTop(currentState, currentState.unload, cols=ncols)
        
        #we can branch here by choosing to pick each one and calculating h()
        if(len(unloadable)>0):
            
            ind=0
            for i in range(len(unloadable)):
                #unload item
                # if len(currentState.unload) > i:
                removedShip = moveContainer(array=currentState.state.ship,col=unloadable[i],newCol=0,unload=1)
                    #find row removed from to calc h
                removedRow = stackHeight(currentState.state.ship,col=unloadable[i])
                    #create new unloadlist
                removedUnload = np.delete(currentState.unload,i)
                    
                extraCost= 2*(costBetweenPink)
                if(currentState.colPick==-1):
                    extraCost = distToPink(removedRow,unloadable[i]) + 2*(costBetweenPink)
                else:
                    extraCost = costCol(currentState.state.ship, curCol=currentState.colPick, newCol=unloadable[i], empty=1)
                    
                newRemovedState = StateWrapper(State(removedShip),cost=extraCost + currentState.cost + distToPink(removedRow,unloadable[i]),movesList=currentState.movesList.copy(), load=currentState.load, unload=removedUnload, colPick=-1, moves=currentState.moves+1, status=0)
                newRemovedState.h = loadHeuristic(newRemovedState)
                newRemovedState.movesList.append([[currentState.state.ship[stackHeight(currentState.state.ship,col=unloadable[i]), unloadable[i]].tolist()],[9,1], newRemovedState.status])

                    
                    
                if(len(newRemovedState.load)==0 and len(newRemovedState.unload)==0):
                    # print("cost was", newRemovedState.cost)
                    newRemovedState.cost += costBetweenPink
                    # print("cost is", newRemovedState.cost)
                    if(minCost >= newRemovedState.cost) :
                        minCost=newRemovedState.cost
                        print("[FINAL]New Min Cost:", minCost)
                        finalState.append(newRemovedState)
                
                elif((newRemovedState.state not in duplicateState) and newRemovedState.cost < minCost):
                    duplicateState.append(newRemovedState)
                    queueMain.put(PrioritizedItem(newRemovedState.h,newRemovedState.cost, newRemovedState))
                    
                # ind +=1
    #     else:
    #         print("Nothing available to UNLOAD")
        
        #shows which cols have unloadable
        cntUnload = countUnload(currentState)
        
        if(len(currentState.load)>0):
            #starting point is pink
            #we do not care which is loaded first so we can just pop off
            
            #we should try loading into cheaper col without something to be unloaded from
            
            
            
            
            for i in range(ncols):
                if(cntUnload[i]==0 and stackHeight(currentState.state.ship, i) < 7):
                    
                    loadedShip = createContainer(currentState.state.ship,col=i, container=currentState.load[0])
    #                 print("converting \t", currentState.load)
                    removedLoad = currentState.load[1:]
    #                 print("to \t", removedLoad)
                    removedRow = stackHeight(currentState.state.ship,col=i)+1
            
                    extraCost=2*(costBetweenPink)
                    if(currentState.colPick==-1):
                        extraCost = 2*(costBetweenPink)
                    else:
                        extraCost = distToPink(removedRow,i)
                                    
                    newLoadState = StateWrapper(State(loadedShip), cost=extraCost + currentState.cost + distToPink(removedRow,i),movesList=currentState.movesList.copy(), load=removedLoad, unload=currentState.unload, colPick=i, moves=currentState.moves+1, status=1)
                    newLoadState.h = loadHeuristic(newLoadState)
                    newLoadState.movesList.append([[np.append(['09','01'], currentState.load[0])],[stackHeight(newLoadState.state.ship,col=i)+comp,i+comp], newLoadState.status])
                
                    if(len(newLoadState.load)==0 and len(newLoadState.unload)==0):
                        if(minCost >= newLoadState.cost) :
                            minCost=newLoadState.cost
                            print("[FINAL]New Min Cost:", minCost)
                            finalState.append(newLoadState)

                    elif((newLoadState.state not in duplicateState) and newLoadState.cost < minCost):
                        duplicateState.append(newLoadState)
                        queueMain.put(PrioritizedItem(newLoadState.h,newLoadState.cost, newLoadState))

    #     else:
    #         print("Nothing available to LOAD")
            
        if(len(unloadable)<=0):
            #try picking from col that has unload
            
            for i in range(ncols):
                if(cntUnload[i]!=0):
                    movedCol = nearestLoad(countUnload(currentState),i)
                    
                    movedShip = moveContainer(currentState.state.ship,col=i,newCol= movedCol)
                    movedCost = costCol(currentState.state.ship,curCol=i, newCol=movedCol)
                    
                    extraCost=2*(costBetweenPink)
                    if(currentState.colPick==-1 and len(currentState.movesList) > 0):
                        extraCost = distToPink(currentState.movesList[-1][1][0]-1,i) + 2*(costBetweenPink)
                    else:
                        if(currentState.colPick != -1):
                            extraCost = distToPink(stackHeight(currentState.state.ship, col=i),i) + 2*(costBetweenPink)
                        else:
                            extraCost = costCol(currentState.state.ship, curCol=currentState.colPick, newCol=i, empty=1)
                        
                    newMoveState = StateWrapper(State(movedShip), cost=extraCost + currentState.cost + movedCost ,movesList=currentState.movesList.copy(), load=currentState.load, unload=currentState.unload, colPick=movedCol, moves=currentState.moves+1, status=2)
                    newMoveState.h = loadHeuristic(newMoveState)
                    newMoveState.movesList.append([[currentState.state.ship[stackHeight(currentState.state.ship,col=i), i].tolist()],[stackHeight(newMoveState.state.ship,col=movedCol)+comp,movedCol+comp], newMoveState.status])
                    
                    if((newMoveState.state not in duplicateState) and newMoveState.cost < minCost):
                        duplicateState.append(newMoveState)
                        queueMain.put(PrioritizedItem(newMoveState.h,newMoveState.cost, newMoveState))

    #         #Stopping conditions

        depth+=1
        if((( depth>=1000 or len(finalState)>40) and len(finalState)!=0) or (queueMain.empty() and len(duplicateState)==old )):
            print("Exited at depth",depth, " and ", len(finalState), "final states", old,"=?",len(duplicateState))
            if(queueMain.empty()):
                print("No More states to branch from!")
            break
        else:
            old = len(duplicateState)

    best = sorted(finalState,key=lambda x: x.cost)[0]

    return initialState, best, duplicateState, finalState

#Function for testing balance
def balanceScore(array, cols=ncols):
    split=cols/2
    left = sum(((array[:,:int(split),2]).flatten()).astype(int))
    #print(left)
    right = sum(((array[:,int(split):,2]).flatten()).astype(int))
    #print(right)
    
    if(left==right):
        return 1
    if(left==0 or right==0):
        return 0
    
    return min(left,right)/max(left,right)

#Function for accepting balance
#default threshold of 10% 
def balanced(state, cols=ncols, thresh=.1):
    array = state.state.ship
    if(balanceScore(array, cols) > (1-thresh)):
        return True
    return False



def totalWeight(array):
    return sum(((array[:,:,2]).flatten()).astype(int))

def leftWeight(array, cols=ncols):
    split=cols/2
    return sum(((array[:,:int(split),2]).flatten()).astype(int))

def rightWeight(array, cols=ncols):
    split=cols/2
    return sum(((array[:,int(split):,2]).flatten()).astype(int))

def removeEmpty(array):
    filterArray = ((array[:,:,3] != 'UNUSED') == (array[:,:,3] != 'NAN'))
    return (array[filterArray])

def heavySide(state, cols=ncols):
    array = state.state.ship
    left = leftWeight(array,cols)
    right = rightWeight(array,cols)
    if(left < right):
        return 1
    return 0


def balanceHeuristicDroped(state, cols=ncols):
    #Given state, how balanced is it and what potential does it have?
    
    array = state.state.ship

    balanceMass = totalWeight(array)/2
    split = cols/2
    
    #which side is heavier
    side = heavySide(state)
        
    left = leftWeight(array,cols)
    right = rightWeight(array,cols)
    
    deficit = abs(balanceMass - max(left, right))

    if(side==0):
        weights = removeEmpty((array[:,:int(split)]))
    else:
        weights = removeEmpty((array[:,int(split):]))
    
    #list of cells sorted by weight
    sortedList = sorted(weights, key=lambda x: x[2], reverse=True)
    newDef = deficit
    h = 0
    for i in sortedList:
#         print("\ndef", newDef, "\n-")
#         print(i[2])

        if (newDef - int(i[2]) > 0):
            newDef -= int(i[2])
            h+=1
    
            
    #h is amount of containers needed to move to get close to balance
    return h, sortedList



def balanceHeuristicPicked(state, colPick=-1, cols=ncols):
    #Picking from col pickCol, how good is this state?
    #what is the dist needed to drop into col on other side
        

    colPick = state.colPick
    array = state.state.ship
    
    side = heavySide(state)
    
    heightsArray = np.array(heights(array))
    
    #check if picking from heavy side    
    if(side==0 and colPick<cols/2):
        if( (heightsArray[int(cols/2):cols]<nrows-1).all() ):
#             print("side 0, moving to",cols/2)
            return cols/2 - colPick

        #there are full cols
#         print("left")
        for i in range(int(cols/2), cols):
            print(i)
            if(heightsArray[i] < nrows-1):
                return i - colPick
    
    if(side==1 and colPick>=cols/2):
        if( (heightsArray[int(cols/2)-1:-1]<nrows-1).all() ):
            return colPick - ((cols/2)-1)
        
        #there are full cols
#         print("right")
        for i in range(int(cols/2)-1, -1, -1):
            if(heightsArray[i] < nrows-1):
                return colPick-i
            
    #pulling from side that is lighter
    
    #h is slightly worse than worst case moving from heavier side
    return int(1 + cols/2)

def sift(array, sortedList=0, cols = ncols):
    tmpArray = array.copy()
    cont= removeEmpty(array)
    containers = cont.copy()
    cont[:,2:4] = ['00000','UNUSED']
    
    
    filterArray = ((array[:,:,3] != 'UNUSED') == (array[:,:,3] != 'NAN'))    
    
    (tmpArray[filterArray]) = cont
    #make empty ship while keeping NAN's
    
    if(sortedList==0):
        sortedList = sorted(containers, key=lambda x: x[2], reverse=True)
    
    
    #Place all containers 1 by 1
    
    for i in range(len(sortedList)):
        height = (heights(tmpArray))        
        if(i%2 == 0):
            #every other time
            minRow = min(height[0:int(cols/2)])
            #place on left side
            for w in range(int(cols/2)-1,-1,-1):
                
                h = stackHeight(tmpArray,w)+1
                if(h == minRow):
                    #we can place container here
#                     print("\nwas", tmpArray[h,w])
                    tmpArray[h,w,2:4] = sortedList[i][2:4]
#                     print("\tchanged to ", tmpArray[h,w])
                    break
                    
        else:
            #every other time
            minRow = min(height[int(cols/2):cols+1])
            #place on right side
            for w in range(int(cols/2), cols+1):
                
                h = stackHeight(tmpArray,w)+1
                if(h == minRow):
                    #we can place container here
#                     print("\nwas", tmpArray[h,w])
                    tmpArray[h,w,2:4] = sortedList[i][2:4]
#                     print("\tchanged to ", tmpArray[h,w])
                    break
    
    return tmpArray



def balancePossible(state) :
    array = state.state.ship
    cont = removeEmpty(array)
    sortedList = np.array(sorted(cont, key=lambda x: x[2], reverse=True))
    
    big = int(sortedList[0][2])
    other = sum((sortedList[1:,2].flatten()).astype(int))
#     print(big)
#     print(other)
    
    if((big>(big+other)/2) and (other/big <.9)):
        return False
    return True


def siftDrop(state, siftState=[]):
    if(siftState==[]):
        siftState = sift(state.state.ship)
    array = np.array(removeEmpty(state.state.ship))
    cont = np.array(removeEmpty(siftState))
    
    h=0
    
    for i in array:
        for w in cont:
            if((i==w).all()):
                h+=1
    
#     print(h)
    return len(array) - h

def siftPick(state, col, siftState=[]):
    array = state.state.ship
    
    if(siftState==[]):
        siftState = sift(array)
    
    h = stackHeight(array,col)
    chosen = array[h,col]
    if((chosen == siftState[h,col])).all():
        return(20)

    for i in removeEmpty(siftState):
#         print((chosen, "vs", i))
        if((i[2:4] == chosen[2:4]).all()):
#             return abs(int(i[1])-int(chosen[1]))
            return(len(array))


def branchingBalance(testManifestArray,ncols=ncols):
    #when tracking moves, compensate coordinates +1 for dropoff location to match pick up
    #**coordinates start at 1, not 0**
    comp = 1

    #checking if duplicateState changes in size
    old = 100

    #initial state:
    initialState = StateWrapper(State(testManifestArray))

    #duplicate states checker
    duplicateState = []

    #legal final states
    finalState = []

    #create sift state if branched to
    siftState = sift(testManifestArray)


    #Create PriorityQueue for queing states
    queueP = PriorityQueue()
    queueD = PriorityQueue()

    queueD.put(PrioritizedItem(1, 1, initialState))
                
    depth = 0
    minCost = 10000


    if(balancePossible(initialState)):

        #Choose where to move the container
            #creating and adding those states
        while True:

            if not queueD.empty():
                currentState=queueD.get().item

            #Choose which container to move
                #creating and adding those states
                for w in range(0,ncols):
                    dropped=-1
                    if len(currentState.movesList) > 0:
                            #cost of moving crane from dropped to new pickup
                            dropped = currentState.movesList[-1][1][1]-1

                    if(w!=dropped):
                        extraCost=0
                        if len(currentState.movesList) > 0:
                            extraCost = costCol(currentState.state.ship,currentState.movesList[-1][1][1]-1,w,empty=1)

                        newPickState = StateWrapper(currentState.state, colPick=w, h=balanceHeuristicPicked(currentState, colPick=w), moves=currentState.moves, cost=currentState.cost + extraCost, movesList=currentState.movesList.copy())

                        if(pickable(newPickState.state.ship, w) and (newPickState.cost < minCost)):
                            queueP.put(PrioritizedItem(newPickState.h, newPickState.cost, newPickState))


            while not queueP.empty():
                currentState = queueP.get().item
        #         print("\nPick State", currentState.state.ship[stackHeight(currentState.state.ship,col=currentState.colPick), currentState.colPick], "with h =",currentState.h)
                #Create new branch
                for newCol in range(0,ncols):
                    #try to place container in each col
                    if(stackHeight(currentState.state.ship,currentState.colPick)<nrows and newCol!=currentState.colPick):
                        #does not allow if overflow or where it already was
                        dropH, sortedList = balanceHeuristicDroped(state=currentState)
                        newDropState = StateWrapper(State(moveContainer(currentState.state.ship,currentState.colPick,newCol)), h=dropH, moves=currentState.moves+1, cost=currentState.cost + costCol(currentState.state.ship,curCol=currentState.colPick,newCol=newCol), movesList=currentState.movesList.copy())

                        newDropState.movesList.append([[currentState.state.ship[stackHeight(currentState.state.ship,col=currentState.colPick), currentState.colPick].tolist()],[stackHeight(newDropState.state.ship,col=newCol)+comp,newCol+comp]])

                        if((balanced(newDropState)) and (newDropState.cost < minCost) or (newDropState.state.ship == siftState).all()):
        #                     print("[BALANCED]Droping container at", newCol, "for h =", newDropState.h)
                            finalState.append(newDropState)

                            if(minCost >= newDropState.cost) :
                                minCost=newDropState.cost
                                print("[BALANCED]New Min Cost:", minCost)
                            if((newDropState.state.ship==siftState)).all():
                                #sift state
                                print("USING SIFT")

                        elif((newDropState.state not in duplicateState) and (newDropState.cost < minCost) ):
                            duplicateState.append(newDropState.state)
                        #add h of currentState (parent) and new Drop
                            queueD.put(PrioritizedItem(currentState.h + newDropState.h, newDropState.cost, newDropState))
        #                     print("\t  Droping container at", newCol, "for h =", newDropState.h)

            #Stopping conditions

            depth+=1
            if((( depth>=1000 or len(finalState)>20) and len(finalState)!=0) or (queueD.empty() and len(duplicateState)==old )):
                print("Exited at depth",depth, " and ", len(finalState), "final states", old,"=?",len(duplicateState))
                if(queueD.empty()):
                    print("No More states to branch from!")
                break
            else:
                old = len(duplicateState)
    else:
        print("need to sift")
        while(True):
            if not queueD.empty():
                    currentState=queueD.get().item

                #Choose which container to move
                    #creating and adding those states
                    for w in range(0,ncols):
                        dropped=-1
                        if len(currentState.movesList) > 0:
                                #where we dropped
                                dropped = currentState.movesList[-1][1][1]-1

                        if(w!=dropped):
                            extraCost=0
                            if len(currentState.movesList) > 0:
                                #cost of moving crane from dropped to new pickup
                                extraCost = costCol(currentState.state.ship,currentState.movesList[-1][1][1]-1,w,empty=1)

                            newPickState = StateWrapper(currentState.state, colPick=w, h=siftPick(currentState,siftState=siftState,col=w), moves=currentState.moves, cost=currentState.cost + extraCost, movesList=currentState.movesList.copy())

                            if(pickable(newPickState.state.ship, w) and (newPickState.cost < minCost)):
                                queueP.put(PrioritizedItem(newPickState.h, newPickState.cost, newPickState))


            while not queueP.empty():
                currentState = queueP.get().item
    #             print("\nPick State", currentState.state.ship[stackHeight(currentState.state.ship,col=currentState.colPick), currentState.colPick], "with h =",currentState.h)
                #Create new branch
                for newCol in range(0,ncols):
                    #try to place container in each col
                    if(stackHeight(currentState.state.ship,currentState.colPick)<nrows and newCol!=currentState.colPick):
                        #does not allow if overflow or where it already was
                        dropH = siftDrop(currentState,siftState=siftState)
                        newDropState = StateWrapper(State(moveContainer(currentState.state.ship,currentState.colPick,newCol)), h=dropH, moves=currentState.moves+1, cost=currentState.cost + costCol(currentState.state.ship,curCol=currentState.colPick,newCol=newCol), movesList=currentState.movesList.copy())

                        newDropState.movesList.append([[currentState.state.ship[stackHeight(currentState.state.ship,col=currentState.colPick), currentState.colPick].tolist()],[stackHeight(newDropState.state.ship,col=newCol)+comp,newCol+comp]])

                        if((newDropState.state.ship == siftState).all()):
        #                     print("[BALANCED]Droping container at", newCol, "for h =", newDropState.h)
                            finalState.append(newDropState)

                            if(minCost >= newDropState.cost) :
                                minCost=newDropState.cost
                                print("USING SIFT\n[BALANCED]New Min Cost:", minCost)

                        elif((newDropState.state not in duplicateState) and (newDropState.cost < minCost) ):
                            duplicateState.append(newDropState.state)
                        #add h of currentState (parent) and new Drop
                            queueD.put(PrioritizedItem(currentState.h + newDropState.h, newDropState.cost, newDropState))
    #                         print("\t  Droping container at", newCol, "for h =", newDropState.h)

            #Stopping conditions
            depth+=1
            if((( depth>=3000 or len(finalState)>20) and len(finalState)!=0) or (queueD.empty() and len(duplicateState)==old )):
                print("Exited at depth",depth, " and ", len(finalState), "final states", old,"=?",len(duplicateState))
                if(queueD.empty()):
                    print("No More states to branch from!")
                break
            else:
                old = len(duplicateState)

    best = sorted(finalState,key=lambda x: x.cost)[0]
        
    return initialState, best, duplicateState, finalState


