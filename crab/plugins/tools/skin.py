import pymel.core as pm

from crab.constants import log
import crab


# ------------------------------------------------------------------------------
class SkinDisconnect(crab.RigTool):

    identifier = 'Skin : Disconnect'

    # --------------------------------------------------------------------------
    def run(self):

        for skin in pm.ls(type='skinCluster'):
            skin.moveJointsMode(True)


# ------------------------------------------------------------------------------
class SkinReconnect(crab.RigTool):

    identifier = 'Skin : Reconnect'

    # --------------------------------------------------------------------------
    def run(self):
        for skin in pm.ls(type='skinCluster'):
            skin.moveJointsMode(False)


# ------------------------------------------------------------------------------
class CopyToUnboundMesh(crab.RigTool):

    identifier = 'Skin : Copy To Unbound Mesh'

    # --------------------------------------------------------------------------
    def run(self, current_skin_host=None, target=None):

        # -- Get our mesh candidates
        current_skin_host = pm.selected()[0]
        target = pm.selected()[1]

        # -- Look for the mesh
        log.debug(current_skin_host.inputs())

        # skin = current_skin_host.inputs(type='skinCluster')[0]
        skin = pm.PyNode(pm.mel.findRelatedSkinCluster(current_skin_host))

        # -- Get a list of the influence objects being used
        # -- by the skin currently
        influences = skin.influenceObjects()

        # -- Apply a new skin cluster
        new_skin = pm.skinCluster(
            influences,
            target,
            toSelectedBones=True,
            maximumInfluences=skin.getMaximumInfluences()
        )

        # -- Copy the skin weights between them
        pm.copySkinWeights(
            sourceSkin=skin,
            destinationSkin=new_skin,
            noMirror=True,
            surfaceAssociation='closestPoint',
            influenceAssociation=['name', 'closestJoint', 'label'],
        )
