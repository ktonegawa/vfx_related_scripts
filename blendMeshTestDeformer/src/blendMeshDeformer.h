#ifndef BLENDMESHDEFORMER_H
#define BLENDMESHDEFORMER_H

#include <maya/MItGeometry.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MPxDeformerNode.h>
#include <maya/MFnMesh.h>
#include <maya/MFloatVectorArray.h>
#include <maya/MPointArray.h>
#include <maya/MGlobal.h>

class BlendMesh : public MPxDeformerNode
{
public:
                            BlendMesh();
    virtual                 ~BlendMesh();
    static  void*           creator();

	virtual	MStatus			deform( MDataBlock& data,
									MItGeometry& itGeo,
									const MMatrix& localToWorldMatrix,
									unsigned int geomIndex );
        
    static  MStatus         initialize();
    
	static  MTypeId id;

	static	MObject aNoiseValue;
};

#endif