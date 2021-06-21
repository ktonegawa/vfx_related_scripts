#include "blendMeshDeformer.h"
#include <iostream>

MTypeId BlendMesh::id(0x00000233);
MObject BlendMesh::aNoiseValue;

BlendMesh::BlendMesh()
{
}

BlendMesh::~BlendMesh()
{
}

void* BlendMesh::creator()
{
	return new BlendMesh();
}

MStatus BlendMesh::deform(MDataBlock& data, MItGeometry& itGeo,
	const MMatrix& localToWorldMatrix, unsigned int geomIndex)
{
	MStatus status;

	MDataHandle envelopeData = data.inputValue(envelope, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	float envelope = envelopeData.asFloat();

	float bulgeAmount = data.inputValue(aNoiseValue).asFloat();

	MPoint point;
	for (; !itGeo.isDone(); itGeo.next())
	{
		point = itGeo.position();

		std::cerr << "position: " << point << endl;
		itGeo.setPosition(point);
	}

	return MS::kSuccess;
}

MStatus BlendMesh::initialize()
{
	MStatus status;

	MFnNumericAttribute nAttr;

	aNoiseValue = nAttr.create("noiseValue", "noiseValue", MFnNumericData::kFloat);
	nAttr.setKeyable(true);
	nAttr.setMin(0.0);
	nAttr.setMax(10.0);
	addAttribute(aNoiseValue);
	attributeAffects(aNoiseValue, outputGeom);

	MGlobal::executeCommand("makePaintable -attrType multiFloat -sm deformer blendMeshTestNode weights;");

	return MS::kSuccess;
}