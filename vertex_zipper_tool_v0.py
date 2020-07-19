# OpenMaya api 2.0
import maya.api.OpenMaya as om
import maya.cmds as cmds

# set up some class objects
class OmEdgeObject(object):
    def __init__(self, edgeIterator):
        self.id = int(edgeIterator.index())
        self.vtx0_id = int(edgeIterator.vertexId(0))
        self.vtx0_pos = edgeIterator.point(0)
        self.vtx1_id = int(edgeIterator.vertexId(1))
        self.vtx1_pos = edgeIterator.point(1)
        self.vtx_list = [self.vtx0_id, self.vtx1_id]
        self.connectedEdges = list(edgeIterator.getConnectedEdges())
        self.edgePos = edgeIterator.center()
    
    def reverseVertData(self):
        old_vtx0_id = int(self.vtx0_id)
        old_vtx0_pos = om.MPoint(self.vtx0_pos)
        old_vtx1_id = int(self.vtx1_id)
        old_vtx1_pos = om.MPoint(self.vtx1_pos)
        self.vtx0_id = old_vtx1_id
        self.vtx0_pos = old_vtx1_pos
        self.vtx1_id = old_vtx0_id
        self.vtx1_pos = old_vtx0_pos
        self.vtx_list.reverse()
    
class OmVertexObject(object):
    def __init__(self, vertexIterator):
        self.vtx_id = int(vertexIterator.index())
        self.vtx_pos = vertexIterator.position()
        self.connectedEdges = list(vertexIterator.getConnectedEdges())
        self.connectedVerts = list(vertexIterator.getConnectedVertices())

def arrayRotate(array, step):
    length = len(array)
    if step < 0:
        for i in range(abs(step)):
            leftRotatebyOne(array, length)
    else:
        for i in range(step): 
            rightRotatebyOne(array, length)
  
# Function to left Rotate arr[] of size n by 1*/  
def leftRotatebyOne(array, length):
    temp = array[0]
    for i in range(length-1):
        array[i] = array[i + 1]
    array[length-1] = temp
    
# Function to right Rotate arr[] of size n by 1*/  
def rightRotatebyOne(array, length):
    temp = array[-1]
    for i in range(length-1, 0, -1):
        array[i] = array[i - 1]
    array[0] = temp

def queryEdgeChain(startEdgeID, desiredEdgeDict, desiredCount, attempts):
    loopList = list()
    chainCount = 0
    startEdgeObj = desiredEdgeDict[startEdgeID]
    connectedEdgeObj = None
    connectedVert = startEdgeObj.vtx_list[1]
    if attempts > 4:
        connectedVert = startEdgeObj.vtx_list[0]
        startEdgeObj.reverseVertData()
    loopList.append(startEdgeObj)
    while chainCount != desiredCount:
        chainCount += 1
        reversed = False
        foundEdgeId = None
        for edgeID, edgeObj in desiredEdgeDict.iteritems():
            if edgeObj.vtx_list[0] == connectedVert and edgeObj not in loopList:
                foundEdgeId = edgeID
                break
            if attempts > 2:
                if edgeObj.vtx_list[1] == connectedVert and edgeObj not in loopList:
                    foundEdgeId = edgeID
                    reversed = True
                    break
        if foundEdgeId == None:
            if chainCount == desiredCount - 1 and attempts > 0:
                if not connectedEdgeObj:
                    connectedEdgeObj = startEdgeObj
                for edgeID, edgeObj in desiredEdgeDict.iteritems():
                    if edgeObj.vtx_list[1] == connectedVert and edgeObj != connectedEdgeObj:
                        foundEdgeId = edgeID
                        break
                    if attempts > 2 and edgeObj.vtx_list[0] == connectedVert and edgeObj != connectedEdgeObj:
                        foundEdgeId = edgeID
                        reversed = True
                        break
                if foundEdgeId != None:
                    lastEdgeObj = desiredEdgeDict[foundEdgeId]
                    if not reversed:
                        lastEdgeObj.reverseVertData()
                    loopList.append(lastEdgeObj)
                loopFound = True
                continue
            else:
                break
        if len(loopList) == desiredCount:
            break
        connectedEdgeObj = desiredEdgeDict[foundEdgeId]
        if reversed:
            connectedEdgeObj.reverseVertData()
        loopList.append(connectedEdgeObj)
        connectedVert = connectedEdgeObj.vtx_list[1]
    return loopList

def getLoopList(desiredEdgeDict, inputEdgeList, firstLoopList=None):
    if firstLoopList:
        edgesToRemove = list()
        for e in firstLoopList:
            if e.id in inputEdgeList:
                edgesToRemove.append(e.id)
        for e in edgesToRemove:
            inputEdgeList.remove(e)
    desiredCount = len(desiredEdgeDict.keys()) / 2
    loopFound = False
    attempts = 0
    while not loopFound:
        for index, startEdgeID in enumerate(inputEdgeList):
            loopList = queryEdgeChain(startEdgeID, desiredEdgeDict, desiredCount, attempts)
            if len(loopList) == desiredCount:
                loopFound = True
                break
        attempts += 1
    return loopList

def assessComponents():
    desiredEdgeDict = dict()
    sel = om.MGlobal.getActiveSelectionList()
    dag, component = sel.getComponent(0)

    # assess selected components
    if component.apiType() == om.MFn.kMeshVertComponent:
        vertEdgeDict = dict()
        selectedVertsList = list()
        sel2 = om.MSelectionList()
        vert_itr = om.MItMeshVertex(dag, component)
        if vert_itr.count() % 2 != 0:
            raise ValueError('Please select matching number of vertices/edges')
        while not vert_itr.isDone():
            vertID = int(vert_itr.index())
            selectedVertsList.append(vertID)
            for vertEdge_id in list(vert_itr.getConnectedEdges()):
                sel2.add('%s.e[%s]' % (dag.fullPathName(), vertEdge_id))
            vert_itr.next()
        dag, vertEdge_component = sel2.getComponent(0)
        vertEdge_itr = om.MItMeshEdge(dag, vertEdge_component)
        while not vertEdge_itr.isDone():
            connectedVertices = [vertEdge_itr.vertexId(0), vertEdge_itr.vertexId(1)]
            if all(x in selectedVertsList for x in connectedVertices):
                desiredEdgeDict[int(vertEdge_itr.index())] = OmEdgeObject(vertEdge_itr)
            vertEdge_itr.next()

    elif component.apiType() == om.MFn.kMeshEdgeComponent:
        edgeDict = dict()
        edge_itr = om.MItMeshEdge(dag, component)
        if edge_itr.count() % 2 != 0:
            raise ValueError('Please select matching number of vertices/edges')
        while not edge_itr.isDone():
            desiredEdgeDict[int(edge_itr.index())] = OmEdgeObject(edge_itr)
            edge_itr.next()

    else:
        raise ValueError('Select either vertices or edges')
    
    return desiredEdgeDict, dag

def cleanUpDictData(desiredEdgeDict, selectedEdgeList):
    for edge in desiredEdgeDict:
        edgeObj = desiredEdgeDict[edge]
        edgesToRemove = list()
        for connectedEdge in edgeObj.connectedEdges:
            if connectedEdge not in selectedEdgeList:
                edgesToRemove.append(connectedEdge)
        for y in edgesToRemove:
            edgeObj.connectedEdges.remove(y)
    return desiredEdgeDict

def buildDistanceData(firstLoopList, secondLoopList):
    edgeDistanceDict = dict()
    for edgeObj1 in firstLoopList:
        edge1_pos = edgeObj1.edgePos
        for edgeObj2 in secondLoopList:
            edge2_pos = edgeObj2.edgePos
            distance = edge1_pos.distanceTo(edge2_pos)
            edgeDistanceDict[distance] = (edgeObj1, edgeObj2)
    return edgeDistanceDict

def assessDistance(edgeDistanceDict):
    minEdgeDistance = min(edgeDistanceDict.keys())

    matchingEdgeObj1 = edgeDistanceDict[minEdgeDistance][0]
    matchingEdgeObj2 = edgeDistanceDict[minEdgeDistance][1]

    vertexPairList = [
                    (0, 0),
                    (0, 1),
                    (1, 0),
                    (1, 1)
                ]

    distanceList = [
                    matchingEdgeObj1.vtx0_pos.distanceTo(matchingEdgeObj2.vtx0_pos),
                    matchingEdgeObj1.vtx0_pos.distanceTo(matchingEdgeObj2.vtx1_pos),
                    matchingEdgeObj1.vtx1_pos.distanceTo(matchingEdgeObj2.vtx0_pos),
                    matchingEdgeObj1.vtx1_pos.distanceTo(matchingEdgeObj2.vtx1_pos)
                ]

    pairResult = vertexPairList[distanceList.index(min(distanceList))]
    
    return pairResult, matchingEdgeObj1, matchingEdgeObj2

def buildVertList(firstLoopList, secondLoopList):
    vertexComponentsDict = dict()
    firstVerticesList = list()
    secondVerticesList = list()

    for a in range(len(firstLoopList)):
        e1 = firstLoopList[a]
        e2 = secondLoopList[a]
        if e1.vtx0_id not in firstVerticesList:
            firstVerticesList.append(e1.vtx0_id)
            vertexComponentsDict[e1.vtx0_id] = e1.vtx0_pos
        if e2.vtx0_id not in secondVerticesList:
            secondVerticesList.append(e2.vtx0_id)
            vertexComponentsDict[e2.vtx0_id] = e2.vtx0_pos
        if e1.vtx1_id not in firstVerticesList:
            firstVerticesList.append(e1.vtx1_id)
            vertexComponentsDict[e1.vtx1_id] = e1.vtx1_pos
        if e2.vtx1_id not in secondVerticesList:
            secondVerticesList.append(e2.vtx1_id)
            vertexComponentsDict[e2.vtx1_id] = e2.vtx1_pos
    return vertexComponentsDict, firstVerticesList, secondVerticesList

def centerMergeVerts(dag, firstVerticesList, secondVerticesList):
    vertsToSelectSet = set()
    vertsProcessed = list()
    
    for a in range(len(firstVerticesList)):
        if firstVerticesList[a] in vertsProcessed:
            continue
        v1_path = '%s.vtx[%s]' % (dag.fullPathName(), firstVerticesList[a])
        v2_path = '%s.vtx[%s]' % (dag.fullPathName(), secondVerticesList[a])
        if v1_path == v2_path:
            continue
        vertsToSelectSet.add(v1_path)
        vertsToSelectSet.add(v2_path)
        v1_pos = cmds.xform(v1_path, query=True, translation=True, worldSpace=True)
        v2_pos = cmds.xform(v2_path, query=True, translation=True, worldSpace=True)
        vAvg_pos = [((v1_pos[0] + v2_pos[0]) / 2.0), ((v1_pos[1] + v2_pos[1]) / 2.0), ((v1_pos[2] + v2_pos[2]) / 2.0)]
        vertsProcessed.append(firstVerticesList[a])
        cmds.xform(v1_path, translation=vAvg_pos, worldSpace=True)
        cmds.xform(v2_path, translation=vAvg_pos, worldSpace=True)

    cmds.select(list(vertsToSelectSet), replace=True)
    cmds.polyMergeVertex()

def run():
    desiredEdgeDict, dag = assessComponents()
    selectedEdgeList = desiredEdgeDict.keys()

    desiredEdgeDict = cleanUpDictData(desiredEdgeDict, selectedEdgeList)

    # dealing with edge loops
    firstLoopList = getLoopList(desiredEdgeDict, selectedEdgeList)
    secondLoopList = getLoopList(desiredEdgeDict, selectedEdgeList, firstLoopList=firstLoopList)

    if len(firstLoopList) != len(secondLoopList):
        raise ValueError('Loop counts do not match')

    edgeDistanceDict = buildDistanceData(firstLoopList, secondLoopList)
    
    pairResult, matchingEdgeObj1, matchingEdgeObj2 = assessDistance(edgeDistanceDict)
    
    # determine if the other loop needs to be reversed
    isReversed = False
    if pairResult[0] != pairResult[1]:
        secondLoopList.reverse()
        for z in secondLoopList:
            z.reverseVertData()
    firstListShift = firstLoopList.index(matchingEdgeObj1) * -1
    secondListShift = secondLoopList.index(matchingEdgeObj2) * -1
    arrayRotate(firstLoopList, firstListShift)
    arrayRotate(secondLoopList, secondListShift)

    vertexComponentsDict, firstVerticesList, secondVerticesList = buildVertList(firstLoopList, secondLoopList)
    
    centerMergeVerts(dag, firstVerticesList, secondVerticesList)

run()