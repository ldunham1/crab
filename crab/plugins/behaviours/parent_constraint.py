import pymel.core as pm

import crab


# ------------------------------------------------------------------------------
class ParentConstraintBehaviour(crab.Behaviour):
    identifier = 'Parent Constraint'
    version = 1

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(ParentConstraintBehaviour, self).__init__(*args, **kwargs)

        self.options.constrain_this = ''
        self.options.to_this = ''
        self.options.maintain_offset = False

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):
        pm.parentConstraint(
            self.options.to_this,
            self.options.constrain_this,
            maintainOffset=self.options.maintain_offset
        )

        return True
