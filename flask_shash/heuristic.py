nrows=8
ncols=12





#Code Chunk from official python priority queue page
from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class PrioritizedItem:
    priority: int
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
class StateWrapper:
    def __init__(self, state, colPick=-1, h=20, moves = 0, cost=0, movesList = []):
        self.state = state
        self.colPick = colPick
        self.h = h
        self.moves = moves
        self.cost = cost
            #of the form [(x1,y1), (x2,y2)]
        self.movesList = movesList

    def __str__(self):
        printState(self.state.ship)
        t=""
        if self.colPick>0:
            t=f"Pick Col: {self.colPick}"
        return t+f"\n\nh: {self.h}\n# of Moves: {self.moves}\nCost: {self.cost}\nMovesList: {self.movesList}"

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
            top.append( np.append(array[h,i,2:4],h) )
        else:
            top.append(np.array(['-99999','NONAME',h]))
    return np.array(top)


def pickable(array, col, nrows=nrows):
    h = stackHeight(array,col,nrows)
    if(array[h,col,3]=="NAN" or h==-1):
        return False
    return True


def moveContainer(array, col, newCol):
    if(col==newCol):
        return -1
    #find where to place container
    h1 = stackHeight(array,col)
    h2 = stackHeight(array,newCol) +1 
        
    newArray = array.copy()
    newArray[h2,newCol,2:4] = newArray[h1,col,2:4]  
    newArray[h1,col,2:4] = ['00000','UNUSED']
    
    return newArray


def costCol(array, curCol, newCol, empty=0):
    hs = heights(array)
    maxHeight = max(hs)
    
    h1 = stackHeight(array,col=curCol) + 1
    h2 = stackHeight(array,col=newCol) + 1
    
    
    if(curCol<newCol):
        localMax = max(hs[curCol+1:newCol]) 
        print(localMax,h1,h2)
        if(h2>=h1 and localMax<h1):
            return abs(0) + abs(curCol-newCol) + abs(localMax-h2-1) - empty
        if(h2>=h1 or localMax>=h1):
            return abs(localMax-h1) + abs(newCol-curCol) + abs(localMax-h2-1) 
        else:
            return abs(h1-localMax) + abs(newCol-curCol) + abs(localMax-h2-1) 
    else:
        localMax = max(hs[newCol+1:curCol]) + 1
#         print(localMax,h1,h2)
        if(h2>=h1 and localMax<h1):
            return abs(localMax-h1) + abs(curCol-newCol) + abs(localMax-h2-1) - empty
        if(h2>=h1 or localMax>=h1):
            return abs(localMax-h1) + abs(curCol-newCol) + abs(localMax-h2-1)
        else:
            return abs(h1-localMax) + abs(curCol-newCol) + abs(localMax-h2-1) 



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
        if (newDef - int(i[2]) > 0):
            newDef -= int(i[2])
            h+=1
            
    #h is amount of containers needed to move to get close to balance
    return h, sortedList


def balanceHeuristicPicked(state, colPick=-1, cols=ncols):
    #Picking from col pickCol, how good is this state?
    #what is the dist needed to drop into col on other side
    
    if(state.colPick >= 0):
        colPick = state.colPick
    array = state.state.ship
    
    side = heavySide(state)
    
    heightsArray = np.array(heights(array))
    
    #check if picking from heavy side    
    if(side==0 and colPick<cols/2):
        if( (heightsArray<nrows-1).all() ):
#             print("side 0, moving to",cols/2)
            return cols/2 - colPick

        #there are full cols
        print("left")
        for i in range(cols/2, cols):
            if(heightsArray[i] < nrows-1):
                return i - colPick
    
    if(side==1 and colPick>=cols/2):
        if( (heightsArray<nrows-1).all() ):
            return colPick - ((cols/2)-1)
        
        #there are full cols
        print("right")
        for i in range((cols/2)-1, -1, -1):
            if(heightsArray[i] < nrows-1):
                return colPick-i
            
    #pulling from side that is lighter
    
    #h is slightly worse than worst case moving from heavier side
    return 1 + cols/2



#when tracking moves, compensate coordinates +1 for dropoff location to match pick up
    #**coordinates start at 1, not 0**

def branchingBalance(testManifestArray=testManifestArray,ncols=ncols,):
    comp = 1

    #initial state:
    initialState = StateWrapper(State(testManifestArray))

    #duplicate states checker
    duplicateState = []

    #legal final states
    finalState = []


    #Create PriorityQueue for queing states
    queueP = PriorityQueue()
    queueD = PriorityQueue()

    #queue.put((0,initialState))

    #Choose which container to move
        #creating and adding those states
        

    queueD.put(PrioritizedItem(1, initialState))
                
    depth = 0

    #Choose where to move the container
        #creating and adding those states
    while True:
        
        if not queueD.empty():
            currentState=queueD.get().item
            if(balanced(currentState)):
                print("Already Balanced")
                finalState.append(currentState)
                break;
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
                        print("extra",extraCost)

                    newPickState = StateWrapper(currentState.state, colPick=w, h=balanceHeuristicPicked(currentState, colPick=w), moves=currentState.moves, cost=currentState.cost + extraCost, movesList=currentState.movesList.copy())

                    if(pickable(newPickState.state.ship, w)):
                        queueP.put(PrioritizedItem(newPickState.h,newPickState))
                    
        
        while not queueP.empty():
            currentState = queueP.get().item
            print("\n\nPick State", currentState.state.ship[stackHeight(currentState.state.ship,col=currentState.colPick), currentState.colPick], "with h =",currentState.h)
            if(balanced(currentState)):
                print("Already Balanced")
                finalState.append(currentState)
                break
            #Create new branch
            for newCol in range(0,ncols):
                #try to place container in each col
                if(stackHeight(currentState.state.ship,currentState.colPick)<nrows and newCol!=currentState.colPick):
                    #does not allow if overflow or where it already was
                    dropH, sortedList = balanceHeuristicDroped(state=currentState)
                    newDropState = StateWrapper(State(moveContainer(currentState.state.ship,currentState.colPick,newCol)), h=dropH, moves=currentState.moves+1, cost=currentState.cost + costCol(currentState.state.ship,curCol=currentState.colPick,newCol=newCol), movesList=currentState.movesList.copy())
                    
                    newDropState.movesList.append([[currentState.state.ship[stackHeight(currentState.state.ship,col=currentState.colPick), currentState.colPick].tolist()],[stackHeight(newDropState.state.ship,col=newCol)+comp,newCol+comp]])
                    
                    if(balanced(newDropState)):
                        print("[BALANCED]Droping container at", newCol, "for h =", newDropState.h)
                        finalState.append(newDropState)
    #                     break;
                    elif((newDropState not in duplicateState)):
                        duplicateState.append(newDropState.state)
                    #add h of currentState (parent) and new Drop
                        queueD.put(PrioritizedItem(currentState.h + newDropState.h,newDropState))
                        print("\t  Droping container at", newCol, "for h =", newDropState.h)
        depth+=1

        if (depth>=20 or len(finalState)>3):
            break
    
    return initialState, duplicateState, finalState