#include "blendMeshDeformer.h"

#include <maya/MFnPlugin.h>

MStatus initializePlugin( MObject obj )
{
    MStatus status;
    
    MFnPlugin fnPlugin( obj, "Kazuma Tonegawa", "1.0", "Any" );
    
    status = fnPlugin.registerNode( "blendMeshTestNode", 
                                    BlendMesh::id, 
                                    BlendMesh::creator, 
                                    BlendMesh::initialize, 
                                    MPxNode::kDeformerNode );
    CHECK_MSTATUS_AND_RETURN_IT( status );
    
    return MS::kSuccess;
}

MStatus uninitializePlugin( MObject obj )
{
    MStatus status;
    
    MFnPlugin fnPlugin( obj );
    
    status = fnPlugin.deregisterNode(BlendMesh::id );
    CHECK_MSTATUS_AND_RETURN_IT( status );
    
    return MS::kSuccess;
}