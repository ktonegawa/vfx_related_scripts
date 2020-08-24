import re
import copy
import nuke

def collectFileLineCounts(fileRead):
    lineCountList = list()

    for index, line in enumerate(fileRead):
        lineCount = len(line.split(' '))
        lineCountList.append('%s: %s' % (index+1, lineCount))
    return lineCountList

def separateTrackLineInfo(lineCountList):
    listCountListStr = ', '.join(lineCountList)
    searchResults = re.findall(r'\d+: 5, \d+: 9|\d+: 5, \d+: 3, \d+: 11', listCountListStr)
    listCountListStr2 = ', '.join(lineCountList)
    
    for result in searchResults:
        listCountListStr2 = listCountListStr2.replace(result, '\n%s' % result)

    listOfTrack = listCountListStr2.split('\n')
    
    return listOfTrack

def cleanUpTrackInfoStep1(listOfTrack):
    listOfTrackCopy = copy.copy(listOfTrack)
    for i, track in enumerate(listOfTrack):
        if not re.match(r'\d+: 5, \d+: 3, \d+: 11', track):
            continue
        trackKeyLinesList = track.split(', ')
        trackKeyLinesListCopy = track.split(', ')
        refFrameIndex = None
        refFramePos = None
        for j, key in enumerate(trackKeyLinesList):
            if re.match(r'\d+: 11', key) and refFrameIndex == None:
                refFrameIndex = j
                continue
            if re.match(r'\d+: 9', key) and refFrameIndex != None:
                refFramePos = j + 1
                trackKeyLinesListCopy.pop(refFrameIndex)
                trackKeyLinesListCopy.insert(j, trackKeyLinesList[refFrameIndex])
                trackKeyLinesListCopyCombined = ', '.join(trackKeyLinesListCopy).replace('\[', '')
                newTrackSeq = re.sub(r'\[|\]', '', trackKeyLinesListCopyCombined)
                listOfTrackCopy.pop(i)
                listOfTrackCopy.insert(i, newTrackSeq)
                break

    listOfTrackCopyCombined = '\n'.join(listOfTrackCopy)
    return listOfTrackCopy

def cleanUpTrackInfoStep2(listOfTrack):
    listOfTrackCopy = list()
    for trackBlock in listOfTrack:
        matches = re.findall(r'(\d+: )(\d+)', trackBlock)
        newStr = trackBlock
        for i in range(len(matches)-1):
            match1 = matches[i]
            match1Str = ''.join(match1)
            match2 = matches[i+1]
            match2Str = ''.join(match2)
            matchFullString = '%s, %s' % (match1Str, match2Str)
            if int(match1[1]) >= 15 and int(match2[1]) == 5:
                replaceStr = '%s\n%s' % (match1Str, match2Str)
                newStr =  newStr.replace(matchFullString, replaceStr)
        newBlockList = newStr.split('\n')
        for newBlock in newBlockList:
            listOfTrackCopy.append(newBlock)
    return listOfTrackCopy

def cleanUpTrackInfoStep3(listOfTrack):
    firstItem = listOfTrack.pop(0)
    frameInfoRemoved = ', '.join(firstItem.split(', ')[2:])
    listOfTrack.insert(0, frameInfoRemoved)
    listOfTrackCopy = list()
    for trackBlock in listOfTrack:
        trackBlockList = trackBlock.split(', ')
        trackBlockList.pop(1)
        if trackBlockList[-1] == '':
            trackBlockList.pop(-1)
        newTrackBlock = ', '.join(trackBlockList)
        listOfTrackCopy.append(newTrackBlock)
    return listOfTrackCopy

def getStartingInfo(line):
    get_info = line.split(' ')
    startFrame = int(get_info[3])
    res_width, res_height = int(get_info[9])+1, int(get_info[11])+1
    return startFrame, res_width, res_height
    
def isLineFrameType(line):
    if re.match(r'\d+ 0 1(?:\s[\d\.]+){4} %s %s' % (maxX, maxY), line):
        return True
    else:
        return False

def startFrameAdjust(line):
    global startFrame
    match = re.match(r'(\d+ 0 1 )([\d\.]+)', line)
    if not match:
        return
    newStartFrame = int(match.group(2))
    startFrame = newStartFrame

def processTrack(line, firstFrame=False):
    match = re.match(r'((?:[\d\.]+ ){2})([\d\.]+)( )([\d\.]+)', line)
    if firstFrame:
        match = re.match(r'((?:[\d\.]+ ){4})([\d\.]+)( )([\d\.]+)', line)
    if not match:
        return
    xPos = match.group(2)
    yPos = match.group(4)
    return xPos, yPos

def buildTracker(fileRead, trackerBlock):
    firstFrame = startFrame
    trackerData = list()
    trackerBlockSplit = trackerBlock.split(', ')
    for index, trackData in enumerate(trackerBlockSplit):
        lineNumberStr, lineCountStr = trackData.split(': ')
        lineIndex = int(lineNumberStr) - 1
        lineCount = int(lineCountStr)
        lineData = fileRead[lineIndex]
        if isLineFrameType(lineData):
            startFrameAdjust(lineData)
            continue
        try:
            if lineCount == 9 and index == 0:
                xPos, yPos = processTrack(lineData, firstFrame=True)
            else:
                xPos, yPos = processTrack(lineData)
        except TypeError:
            print 'lineData: %s' % lineData
            print 'current trackerData: %s' % trackerData
            raise TypeError('Unrecognized format')
        resultingData = '%s: %s, %s' % (firstFrame, xPos, yPos)
        firstFrame += 1
        trackerData.append(resultingData)
    return trackerData

def run(toWriteFile):
    node = nuke.selectedNode()
    nukeScriptText = node.__str__()
    scriptMatch = re.match(r'(\n.*\nserializeKnob \")([^\"]+)(\")', nukeScriptText)
    if not scriptMatch:
        return
    fileRead = scriptMatch.group(2).split('\n')

    line_count = len(fileRead)

    startFrame, res_width, res_height = getStartingInfo(fileRead[1])
    maxX = res_width - 1
    maxY = res_height - 1

    lineCountList = collectFileLineCounts(fileRead)
    listOfTrack = separateTrackLineInfo(lineCountList)
    listOfTrackCleaned1 = cleanUpTrackInfoStep1(listOfTrack)
    listOfTrackCleaned2 = cleanUpTrackInfoStep2(listOfTrackCleaned1)
    listOfTrackCleaned3 = cleanUpTrackInfoStep3(listOfTrackCleaned2)

    allTrackerList = list()
    indexCounter = 0

    for trackerBlock in listOfTrackCleaned3:
        trackerData = buildTracker(fileRead, trackerBlock)
        allTrackerList.append(trackerData)

    with open(toWriteFile, 'w') as writeFile:
        for index, item in enumerate(allTrackerList):
            newIndex = index + 1
            writeFile.write('TrackName autoTrack%s\n' % newIndex)
            writeFile.write('   Frame             X             Y   Correlation\n')
            for frameBlock in item:
                frameStr, coordsStr = frameBlock.split(': ')
                xPosStr, yPosStr = coordsStr.split(', ')
                frame = "%.2f" % float(frameStr)
                if len(str(frame)) < 8:
                    frameRemainingSpace = 8 - len(str(frame))
                else:
                    frameRemainingSpace = 0
                xPos = "%.3f" % float(xPosStr)
                xPosSpacing = 14 - len(str(xPos))
                yPos = "%.3f" % float(yPosStr)
                yPosSpacing = 14 - len(str(yPos))
                formattedLine = '{prespacing}{frame}{spacing1}{xPos}{spacing2}{yPos}{spacing3}1.000\n'.format(prespacing=' '*frameRemainingSpace, frame=frame, spacing1=' '*xPosSpacing, xPos=xPos, spacing2=' '*yPosSpacing, yPos=yPos, spacing3=' '*9)
                writeFile.write(formattedLine)
            writeFile.write('\n')

run('C:/Users/Desktop02/Documents/pythonDevFiles/output_nuke_trackers_script03.txt')
