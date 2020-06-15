from functools import wraps

import pymel.core as pm


# ------------------------------------------------------------------------------
class ContextDecorator(object):

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class UndoChunk(ContextDecorator):

    # --------------------------------------------------------------------------
    def __init__(self):
        self._closed = False

    # --------------------------------------------------------------------------
    def __enter__(self):
        pm.undoInfo(openChunk=True)
        return self

    # --------------------------------------------------------------------------
    def __exit__(self, *exc_info):
        if not self._closed:
            pm.undoInfo(closeChunk=True)

    # --------------------------------------------------------------------------
    def restore(self):
        pm.undoInfo(closeChunk=True)
        self._closed = True

        try:
            pm.undo()

        except StandardError:
            pass


# ------------------------------------------------------------------------------
class RestoredTime(ContextDecorator):

    # --------------------------------------------------------------------------
    def __init__(self):
        # -- Cast to iterable
        self._time = pm.currentTime()

    # --------------------------------------------------------------------------
    def __enter__(self):
        pass

    # --------------------------------------------------------------------------
    def __exit__(self, *exc_info):
        pm.setCurrentTime(self._time)


# ------------------------------------------------------------------------------
class RestoredSelection(ContextDecorator):
    """
    Cache selection on entering and re-select on exit
    """

    # --------------------------------------------------------------------------
    def __enter__(self):
        self._selection = pm.selected()

    # --------------------------------------------------------------------------
    def __exit__(self, *exc_info):
        if self._selection:
            pm.select(self._selection)
