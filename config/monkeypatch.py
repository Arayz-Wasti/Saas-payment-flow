import sys
import logging

logger = logging.getLogger(__name__)

def apply_patches():
    """
    Apply global patches for compatibility and stability.
    """
    # 1. Django Python 3.14 Compatibility Patch
    # See: https://code.djangoproject.com/ticket/35844
    if sys.version_info >= (3, 14):
        try:
            from django.template.context import BaseContext
            from copy import copy

            # Original __copy__ in Django 4.2 uses copy(super()), which fails in Python 3.14
            # because super() doesn't have dicts or __dict__.
            def robust_copy(self):
                # We want to copy the dicts list from the current object
                new_copy = self.__class__(dict_() if hasattr(self, 'dict_') else {})
                new_copy.dicts = self.dicts.copy()
                return new_copy

            BaseContext.__copy__ = robust_copy
            logger.info("Successfully applied Python 3.14 compatibility patch to BaseContext.__copy__")
        except Exception as e:
            logger.error(f"Failed to apply Python 3.14 compatibility patch: {e}")

if __name__ == "__main__":
    apply_patches()
