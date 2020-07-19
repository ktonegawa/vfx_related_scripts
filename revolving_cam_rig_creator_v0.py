import re
import math

import pymel.core as pm
import maya.cmds as cmds

def getRenderFOVs(cameraShape, filmFitType):
    renderAspectRatio = cmds.getAttr('defaultResolution.deviceAspectRatio')
    focalLength = cameraShape.getAttr('focalLength')
    halfWidth = (cameraShape.getAttr('horizontalFilmAperture') * 25.4) / 2.0
    halfHeight = (cameraShape.getAttr('verticalFilmAperture') * 25.4) / 2.0
    if filmFitType == 0 or filmFitType == 1:
        halfHeight = halfWidth / renderAspectRatio
    elif filmFitType == 2 or filmFitType == 3:
        halfWidth = halfHeight * renderAspectRatio
    hfov_tan_theta = halfWidth / focalLength
    hfov = math.degrees(hfov_tan_theta) * 2.0
    vfov_tan_theta = halfHeight / focalLength
    vfov = math.degrees(vfov_tan_theta) * 2.0
    return hfov, vfov

def getDistanceFromWidth(desiredWidth, angleOfView):
    halfAngle = float(angleOfView) / 2.0
    halfDistance = float(desiredWidth / 2.0)
    tan_theta = math.tan(math.radians(halfAngle))
    distance = halfDistance / tan_theta
    return distance + halfDistance

def getDistanceFromHeight(desiredHeight, angleOfView):
    halfAngle = float(angleOfView) / 2.0
    halfDistance = float(desiredHeight / 2.0)
    tan_theta = math.tan(math.radians(halfAngle))
    distance = halfDistance / tan_theta
    return distance + halfDistance

def run():

    # channel lists
    tAttr = ['translateX', 'translateY', 'translateZ']
    rAttr = ['rotateX', 'rotateY', 'rotateZ']
    sAttr = ['scaleX', 'scaleY', 'scaleZ']

    selection = pm.ls(selection=True)
    
    if not selection:
        cmds.error('Select desired object first')
        return
    
    selectedNode = selection[0]
    
    bbox_xMin, bbox_yMin, bbox_zMin, bbox_xMax, bbox_yMax, bbox_zMax = pm.exactWorldBoundingBox(selectedNode)

    center_x = (bbox_xMax + bbox_xMin) / 2.0
    center_y = (bbox_yMax + bbox_yMin) / 2.0
    center_z = (bbox_zMax + bbox_zMin) / 2.0

    obj_width = max(abs(bbox_xMax - bbox_xMin), abs(bbox_zMax - bbox_zMin))
    obj_height = abs(bbox_yMax - bbox_yMin)

    nurbCircleNode, makeNurbCircleNode = pm.circle(name='camera_path1', normalX=0, normalY=1, normalZ=0)

    revolvingCamGroupNode = pm.group(name='revolvingCam_group1', empty=True)
    aimLocator = pm.spaceLocator(name='aim_locator1')
    cameraParentLocator = pm.spaceLocator(name='camera_parent_locator1')
    cameraLocator = pm.spaceLocator(name='camera_locator1')
    revolvingCameraXformNode, revolvingCameraShapeNode = pm.camera(name='revolving_camera1')
    
    filmFitType = revolvingCameraShapeNode.getAttr('filmFit')
    
    camHFOV, camVFOV = getRenderFOVs(revolvingCameraShapeNode, filmFitType)

    circleScale = max(getDistanceFromWidth(obj_width, camHFOV), getDistanceFromHeight(obj_height, camVFOV))

    nurbCircleNode.setScale(scale=(circleScale,circleScale,circleScale))
    pm.makeIdentity(nurbCircleNode, apply=True)

    pm.move(0.0, 0.0, -10.0, aimLocator, absolute=True)

    pm.parent(nurbCircleNode, revolvingCamGroupNode)
    pm.parent(aimLocator, nurbCircleNode)
    pm.parent(cameraParentLocator, revolvingCamGroupNode)
    pm.parent(cameraLocator, cameraParentLocator)
    pm.parent(revolvingCameraXformNode, cameraLocator)

    nurbCircleNode.addAttr('revolutions', attributeType='double', defaultValue=1.0)
    nurbCircleNode.setAttr('revolutions', channelBox=True)

    for attr in list(tAttr+rAttr+sAttr):
        revolvingCamGroupNode.attr(attr).lock()

    aimConstraint = pm.aimConstraint(aimLocator, cameraLocator, aimVector=(0.0,0.0,-1.0))
    pm.move(0.0, 0.0, 0.0, aimLocator, absolute=True)

    motionPathNodeName = pm.pathAnimation(cameraParentLocator, curve=nurbCircleNode, name='camera_motion_path1', fractionMode=True, follow=True, followAxis='x', upAxis='y', worldUpType='vector', worldUpVector=[0.0,1.0,0.0], inverseUp=False, inverseFront=False, bank=False, startTimeU=pm.playbackOptions(query=True, minTime=True), endTimeU=pm.playbackOptions(query=True, maxTime=True))
    motionPathNode = pm.ls(motionPathNodeName)[0]
    motionPathAnimCurveNode = motionPathNode.listConnections(source=True, destination=False, connections=False, type=pm.nodetypes.AnimCurveTL)[0]
    motionPathAnimCurveNode.setPreInfinityType(infinityType='cycle')
    motionPathAnimCurveNode.setPostInfinityType(infinityType='cycle')

    expressionString = 'global proc setRevolutionSpeed()\n\n' \
                        '{{\n\n' \
                        'float $endFrame = `playbackOptions -query -maxTime`;\n' \
                        'float $result = $endFrame / `getAttr {circleNode}.revolutions`;\n' \
                        'print $result;\n' \
                        'keyframe -option over -index 1 -absolute -timeChange $result {animCurveNode} ;\n\n' \
                        'print "\\n";\n\n' \
                        '}}\n\n' \
                        'scriptJob -attributeChange "{circleNode}.revolutions" "setRevolutionSpeed()";'.format(circleNode=nurbCircleNode.fullPath(), animCurveNode=motionPathAnimCurveNode.__str__())
    expressionNode = pm.expression(name='revolutionExpression1', string=expressionString, object=nurbCircleNode, alwaysEvaluate=True, unitConversion='all')


    pm.move(center_x, center_y, center_z, nurbCircleNode, absolute=True)

run()