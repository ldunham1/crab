from string import Formatter
import re

import pymel.core as pm


# ------------------------------------------------------------------------------
# -- This is a list of Component types. These are used in META nodes
# -- to define the type of component (such as guide, skeleton etc)
COMPONENT_MARKER = 'crabComponent'


# ------------------------------------------------------------------------------
# -- This is a list of names which define attributes on meta nodes.
META_IDENTIFIER = 'Identifier'
META_VERSION = 'Version'
META_OPTIONS = 'Options'

# ------------------------------------------------------------------------------
# -- This is a list of attribute names used by the internals of
# -- crab to resolve relationships between objects
BOUND = 'crabBinding'
BEHAVIOUR_DATA = 'crabBehaviours'

# ------------------------------------------------------------------------------
RIG_ROOT_LINK_ATTR = 'crabRigHost'
CONNECTION_PREFIX = 'crabRootConnection'
SKELETON_ROOT_LINK_ATTR = '%sSkeleton' % CONNECTION_PREFIX
CONTROL_ROOT_LINK_ATTR = '%sControls' % CONNECTION_PREFIX
GUIDE_ROOT_LINK_ATTR = '%sGuide' % CONNECTION_PREFIX


# ------------------------------------------------------------------------------
# -- This is a group of layer names
HIDDEN_LAYER = 'Hidden'
CONTROL_LAYER = 'Controls'
SKELETON_LAYER = 'Skeleton'
GEOMETRY_LAYER = 'Geometry'

# ------------------------------------------------------------------------------
# -- This is a list of name prefixes for structural objects created
# -- within a crab rig hierarchy
RIG_ROOT = 'RIG'
RIG_COMPONENT = 'CMP'
GUIDE_COMPONENT = 'GCM'
META = 'META'

# ------------------------------------------------------------------------------
# -- This is a list of pre-fixes for general use within a crab plugin
# -- in order to keep naming consistent
ORG = 'ORG'
CONTROL = 'CTL'
ZERO = 'ZRO'
OFFSET = 'OFF'
SKELETON = 'SKL'
MECHANICAL = 'MEC'
MATH = 'MATH'
MARKER = 'LOC'
GUIDE = 'GDE'
PIVOT = 'PIV'
LOGIC = 'LGC'
SNAP = 'SNP'
IK = 'IKH'
EFFECTOR = 'EFF'
CLUSTER = 'CLS'
UPVECTOR = 'UPV'
SPLINE = 'CRV'

PREFIXES = [
    ORG,
    CONTROL,
    ZERO,
    OFFSET,
    SKELETON,
    MECHANICAL,
    MATH,
    MARKER,
    GUIDE,
    PIVOT,
    LOGIC,
    SNAP,
    IK,
    EFFECTOR,
    CLUSTER,
    UPVECTOR,
    SPLINE,
]

# ------------------------------------------------------------------------------
# -- This is a list of suffixes for general use within a crab plugin
# -- in order to keep naming consistent
# -- Sides and Locations
LEFT = 'LF'
RIGHT = 'RT'
MIDDLE = 'MD'
FRONT = 'FR'
BACK = 'BK'
TOP = 'TP'
BOTTOM = 'BT'
SIDELESS = 'NA'

LOCATIONS = [
    LEFT,
    RIGHT,
    MIDDLE,
    FRONT,
    BACK,
    TOP,
    BOTTOM,
    SIDELESS,
]

# ------------------------------------------------------------------------------
# -- Define colours based on categories
LEFT_COLOR = [252, 48, 1]
RIGHT_COLOR = [0, 162, 254]
MIDDLE_COLOR = [254, 209, 0]
NON_ANIMATABLE_COLOUR = [150, 150, 150]
GUIDE_COLOR = [162, 222, 0]

# ------------------------------------------------------------------------------
# -- Defines attribute defaults
DEFAULT_CONTROL_ROTATION_ORDER = 5


# ------------------------------------------------------------------------------
# Determine a readable naming pattern and regex patterns for matching each group.
NAME_PATTERN = '{category}_{description}_{counter}_{side}'
NAME_PATTERN_GROUPS = {
    'category': '[A-Z]+',
    'counter': '[0-9]+',
    'description': '[a-zA-Z0-9_]+',
    'side': '[A-Z_]+',
}

# Generate a compiled pattern using each group as a named group.
COMPILED_NAME_PATTERN = re.compile(
    NAME_PATTERN.format(
        **{
            group: '(?P<{}>{})'.format(group, pattern)
            for group, pattern in NAME_PATTERN_GROUPS.items()
        }
    )
)


# ------------------------------------------------------------------------------
def validate_name(given_name):
    """
    Return True if the given name matches the current name pattern.

    :param given_name: Name to validate.
    :type given_name: str / pm.nt.DependNode

    :return: True if the given name matches the current name pattern.
    :rtype: bool
    """
    try:
        match = COMPILED_NAME_PATTERN.match(str(given_name))

    except AttributeError:
        return False

    # Build a set of all group names identified in the NAME_PATTERN
    used_groups = set(
        data[1]
        for data in Formatter().parse(NAME_PATTERN)
        if data[1]
    )

    # -- Ensure all identified groups are found in the match
    return all(
        grp in used_groups
        for grp in match.groupdict()
    )


# ------------------------------------------------------------------------------
def get_group(given_name, group):
    """
    Assuming the given name adheres to the naming convention of crab this
    will extract the named group of the name.

    :param given_name: Name to extract from.
    :type given_name: str / pm.nt.DependNode

    :param group: Group to extract.
    :type group: str

    :return: str / None
    """
    try:
        return COMPILED_NAME_PATTERN.match(str(given_name)).group(group)

    except AttributeError:
        return None


def replace_group(given_name, replace, group):
    """
    Replace a grouped section of the given name with the replace string
    and name of the group.

    .. code-block:: python

        >>> NAME_PATTERN = '{category}_{description}_{counter}_{side}'
        >>> original_name = NAME_PATTERN.format(
        ...     category='CTRL',
        ...     description='test_object_01',
        ...     counter=0,
        ...     side='LT',
        ... )
        # 'CTRL_test_object_01_0_LT'
        >>> # We replace the "description".
        >>> replace_group(original_name, 'new_test_obj', 'description')
        # 'CTRL_new_test_obj_0_LT'

    :param given_name: Name to use.
    :type given_name: str

    :param replace: Replace string to use.
    :type replace: str

    :param group: Group to identify in the given_name and replace.
    :type group: str

    :return: New replaced name.
    :rtype: str
    """
    replace_dict = {
        key: '\\g<{}>'.format(key)
        for key in NAME_PATTERN_GROUPS
    }
    replace_dict[group] = replace
    replace_pattern = NAME_PATTERN.format(
        **replace_dict
    )

    return COMPILED_NAME_PATTERN.sub(
        replace_pattern,
        given_name,
    )


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
def name(prefix, description, side, counter=1):
    """
    Generates a unique name with the given naming parts

    :param prefix: Typically this is used to denote usage type. Note that this
        should not be 'node type' but should be representative of what the node
        is actually being used for in the rig.
    :type prefix: str

    :param description: This is the descriptive element of the rig and should
        ideally be upper camel case.
    :type description: str

    :param side: This is the location of the element, such as LF, RT  or MD etc
    :type side: str

    :param counter: To ensure all names are unique we use a counter. By default
        all counters start at 1, but you may override this.
    :type counter: int

    :return:
    """
    prefix = prefix.upper()
    side = side.upper()

    while True:
        candidate = NAME_PATTERN.format(
            category=prefix,
            description=description,
            counter=counter,
            side=side,
        )

        # -- If the name is unique, return it
        if not pm.objExists(candidate):
            return candidate

        # -- The name already exists, so increment our
        # -- counter
        counter += 1


# ------------------------------------------------------------------------------
def get_category(given_name):
    """
    Assuming the given name adheres to the naming convention of crab this
    will extract the category element of the name.

    :param given_name: Name to extract from.
    :type given_name: str or pm.nt.DependNode

    :return: str
    """
    return get_group(given_name, group='category')


# ------------------------------------------------------------------------------
def get_description(given_name):
    """
    Assuming the given name adheres to the naming convention of crab this
    will extract the descriptive element of the name.

    :param given_name: Name to extract from.
    :type given_name: str or pm.nt.DependNode

    :return: str
    """
    return get_group(given_name, group='description')


# ------------------------------------------------------------------------------
def get_counter(given_name):
    """
    Assuming the given name adheres to the naming convention of crab this
    will extract the counter element of the name.

    :param given_name: Name to extract from.
    :type given_name: str or pm.nt.DependNode

    :return: int / None
    """
    try:
        return int(get_group(given_name, group='counter'))

    except TypeError:
        return None


# ------------------------------------------------------------------------------
def get_side(given_name):
    """
    Assuming the given name adheres to the naming convention of crab this
    will extract the side/location element of the name.

    :param given_name: Name to extract from.
    :type given_name: str or pm.nt.DependNode

    :return: str
    """
    return get_group(given_name, group='side') or ''
