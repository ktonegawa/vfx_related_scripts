#include "blendMeshDeformer.h"

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

	MArrayDataHandle hInput = data.outputArrayValue(input, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	status = hInput.jumpToElement(geomIndex);
	MDataHandle hInputElement = hInput.outputValue(&status);
	MObject oInputGeom = hInputElement.child(inputGeom).asMesh();

	MFnMesh fnMesh(oInputGeom, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	MFloatVectorArray normals;
	fnMesh.getVertexNormals(false, normals);

	float bulgeAmount = data.inputValue(aNoiseValue).asFloat();
	float env = data.inputValue(envelope).asFloat();

	MPoint point;
	for (; !itGeo.isDone(); itGeo.next())
	{
		point = itGeo.position();
		double data_array[4];
		point.get(data_array);
		int i;
		MString str = "";
		for (i = 0; i < 4; i++) {
			str = str + ", ";
			str = str + data_array[i];
		}
		MGlobal::displayInfo("position: " + str);
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