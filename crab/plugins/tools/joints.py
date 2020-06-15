import pymel.core as pm

import crab


# ------------------------------------------------------------------------------
class MirrorJointsAcrossTool(crab.RigTool):

    identifier = 'Joints: Mirror Across'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(MirrorJointsAcrossTool, self).__init__()

        self.options.mirror_plane = ''
        self.options.translation_only = False

    # --------------------------------------------------------------------------
    def run(self):
        crab.utils.maths.global_mirror(
            pm.selected(),
            across=self.options.mirror_plane or None,
            remap=MirrorJointsAcrossTool.remap,
            translation_only=self.options.translation_only,
        )

    # --------------------------------------------------------------------------
    @classmethod
    def remap(cls, node):
        if crab.config.LEFT in node.name():
            return pm.PyNode(
                node.name().replace(
                    crab.config.LEFT,
                    crab.config.RIGHT,
                )
            )

        return pm.PyNode(
            node.name().replace(
                crab.config.RIGHT,
                crab.config.LEFT,
            )
        )


# ------------------------------------------------------------------------------
class MirrorJointsTool(crab.RigTool):

    identifier = 'Joints: Mirror'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(MirrorJointsTool, self).__init__()

        self.options.mirror_plane = ''

    # --------------------------------------------------------------------------
    def run(self):
        crab.utils.maths.global_mirror(
            pm.selected(),
            across=self.options.mirror_plane or None,
        )


# ------------------------------------------------------------------------------
class ToggleJointStyleTool(crab.RigTool):

    identifier = 'Joints: Toggle Draw'

    # --------------------------------------------------------------------------
    def run(self):
        selected = pm.selected()
        if not selected:
            return

        if not isinstance(selected[0], pm.nt.Joint):
            return

        current_value = selected[0].drawStyle.get()

        value = 2 if not current_value else 0

        for joint in pm.selected():
            if isinstance(joint, pm.nt.Joint):
                joint.drawStyle.set(value)


# ------------------------------------------------------------------------------
class MoveRotationsToOrientsTool(crab.RigTool):

    identifier = 'Joints: Move Rotations to Orients'

    # --------------------------------------------------------------------------
    def run(self):
        for node in pm.selected():
            crab.utils.joints.move_rotations_to_joint_orients(node)


# ------------------------------------------------------------------------------
class MoveOrientsToRotationsTool(crab.RigTool):

    identifier = 'Joints: Move Orients to Rotations'

    # --------------------------------------------------------------------------
    def run(self):
        for node in pm.selected():
            crab.utils.joints.move_joint_orients_to_rotations(node)


# ------------------------------------------------------------------------------
class SingulizeSelected(crab.RigTool):

    identifier = 'Singulize : Selected'

    # --------------------------------------------------------------------------
    def run(self):
        rig = crab.Rig(node=pm.selected()[0])

        for node in pm.selected():
            rig.add_component('Singular', pre_existing_joint=node.name())


# ------------------------------------------------------------------------------
class SingulizeAll(crab.RigTool):
    identifier = 'Singulize : All'

    # --------------------------------------------------------------------------
    def run(self):

        # -- Get the currently active rig
        rig = crab.Rig.all()[0]

        # -- Find all teh joints in the rig so we can check which
        # -- require singulizing
        all_joints = rig.skeleton_org().getChildren(
            allDescendents=True,
            type='joint',
        )

        for joint in all_joints:

            # -- Assume the joint will need singulizing unless
            # -- we find otherwise.
            requires_singulizing = True

            # -- If the joint has crab meta attached, then we do not
            # -- want to singulize it
            for possible_meta in joint.outputs(type='network'):
                if possible_meta.hasAttr('crabComponent'):
                    requires_singulizing = False
                    break

            # -- Singulize if required
            if requires_singulizing:
                rig.add_component('Singular', pre_existing_joint=joint.name())
