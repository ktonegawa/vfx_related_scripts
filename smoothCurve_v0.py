from PySide import QtCore, QtGui

import maya.cmds as cmds
from functools import partial
import maya.mel as mel

class Window(QtGui.QWidget):
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('Smooth Curves')
        self.setMinimumSize(150, 100)
        self.setMaximumSize(150, 100)
        position = QtGui.QCursor.pos()
        self.move(position)
        self.uiWidget = QtGui.QWidget()
        
        self.verticalLayout = QtGui.QVBoxLayout(self.uiWidget)
        
        self.horizontalLayout = QtGui.QHBoxLayout(self.uiWidget)
        
        self.strengthLabel = QtGui.QLabel(self.uiWidget)
        self.strengthLabel.setText('Strength')
        self.horizontalLayout.addWidget(self.strengthLabel)
        
        self.strengthSpinBox = QtGui.QDoubleSpinBox(self.uiWidget)
        self.horizontalLayout.addWidget(self.strengthSpinBox)
        
        self.verticalLayout.addLayout(self.horizontalLayout)
        
        self.smoothPushButton = QtGui.QPushButton(self.uiWidget)
        self.smoothPushButton.setText('Smooth')
        self.smoothPushButton.clicked.connect(self.smoothCurve)
        self.verticalLayout.addWidget(self.smoothPushButton)
        
        self.lyt = QtGui.QVBoxLayout()
        self.lyt.addWidget(self.uiWidget)
        self.setLayout(self.lyt)
    
    #provided by user Tim Pietzcker on stackoverflow (his profile: http://stackoverflow.com/users/20670/tim-pietzcker)
    #https://stackoverflow.com/questions/23976988/python-plotting-numbers-as-a-custom-range
    #based on this page: http://www.vb-helper.com/howto_find_quadratic_curve.html
    #other recourses: http://en.wikipedia.org/wiki/Curve_fitting
    #http://www.maths.qmul.ac.uk/~lms/research/curvefitting.html
    def fit(self, p1, p2, p3):
        """Return the quadratic function that fits the three points p1, p2, p3,
        each defined as a tuple of (x,y) coordinates"""
        a = ((p2[1]-p1[1])*(p1[0]-p3[0]) + (p3[1]-p1[1])*(p2[0]-p1[0])) / \
        ((p1[0]-p3[0])*(p2[0]**2-p1[0]**2) + (p2[0]-p1[0])*(p3[0]**2-p1[0]**2))
        b = ((p2[1]-p1[1]) - a*(p2[0]**2 - p1[0]**2)) / (p2[0]-p1[0])
        c = p1[1] - a*p1[0]**2 - b*p1[0]
        return lambda x: a*x**2 + b*x + c
        
    def smoothCurve(self):
        curves = cmds.keyframe( query = True, selected = True, name = True )
        if len(curves) == 0:
            cmds.error("Select at least 1 curve in the Graph Editor.")
            return
            
        for curve in curves:
            keys = cmds.keyframe( curve, query = True, selected = True, timeChange = True )
            sizeOfKeys = len(keys)
            duplicateCurve = cmds.duplicate( curve )
            
            if not sizeOfKeys >= 3:
                cmds.error("Select at least 3 keys in the Graph Editor.")
                return
                
            for i in range(1, sizeOfKeys - 1, 1):
                previousValue = cmds.keyframe( curve, query = True, time = ( keys[i-1], keys[i-1]), valueChange = True )
                currentValue = cmds.keyframe( curve, query = True, time = ( keys[i], keys[i] ), valueChange = True )
                nextValue = cmds.keyframe( curve, query = True, time = ( keys[i+1], keys[i+1] ), valueChange = True )
                
                medianValue = ( previousValue[0] + nextValue[0] ) / 2.0
                averageValue = ( previousValue[0] + currentValue[0] + nextValue[0] ) / 3.0
                
                f = self.fit((0.0,currentValue[0]), (5.0,averageValue), (10.0,medianValue))
                strength = f(float(self.strengthSpinBox.value()))
                
                cmds.keyframe( duplicateCurve[0], time = ( keys[i], keys[i] ), absolute = True, valueChange = strength )
                i += 1
            
            for i in range(1, sizeOfKeys - 1, 1):
                duplicateCurveValue = cmds.keyframe( duplicateCurve[0], query = True, time = ( keys[i], keys[i]), valueChange = True )
                cmds.keyframe( curve, time = ( keys[i], keys[i] ), absolute = True, valueChange = duplicateCurveValue[0] )
                i += 1
                
            cmds.delete( duplicateCurve[0] )

window = Window()
window.show()