"""Provides models for regions and region variations.
"""


# System imports
import re
from copy import deepcopy

# owls-data imports
from owls_data.expression import multiplied


class Variation(object):
    """Represents a variation which can be applied to a region.
    """

    def __hash__(self):
        """Returns a unique hash for the patch.

        This method should not be overridden.
        """
        # Grab the variation type
        variation_type = type(self)

        # Extract hashable components
        module = variation_type.__module__
        name = variation_type.__name__
        state = self.state()

        # Create a unique hash
        return hash((module, name, state))

    def state(self):
        """Returns a representation of the variation's internal state, if any.

        This method is used to generate a unique hash for the variation for the
        purposes of caching.  If a variation has no internal state, and it's
        behavior is determined entirely by its type, then the implementer need
        not override this method.  However, if a variation contains state which
        affects its patching behavior, this method needs to be overridden.  A
        simple tuple may be returned containing the state of the variation.

        Returns:
            A hashable object representing the internal state of the variation.
        """
        return ()

    def __call__(self, weight, selection):
        """Applies a variation to a region's weight and selection.

        Implementers must override this method.

        Args:
            weight: The existing weight expression
            selection: The existing selection expression

        Returns:
            A tuple of the form (varied_weight, varied_selection).
        """
        raise NotImplementedError('abstract method')


class Region(object):
    """Represents a region (a selection and weight) in which processes can be
    evaluated.
    """

    def __init__(self, name, weight, selection, label, blinded = False):
        """Initialized a new instance of the Region class.

        Args:
            name: A name by which to refer to the region
            weight: A string representing the weight for the region
            selection: A string representing selection for the region
            label: The ROOT TLatex label string to use when rendering the
                region
            blinded: Whether or not the region is marked as blinded
        """
        # Store parameters
        self._name = name
        self._weight = weight
        self._selection = selection
        self._label = label
        self._blinded = blinded

        # Create initial variations container
        self._variations = ()

    def __hash__(self):
        """Returns a hash for the region.
        """
        # Hash only weight, selection, and variations since those are all that
        # really matter for evaluation
        return hash((self._weight, self._selection, self._variations))

    def name(self):
        """Returns the region name.
        """
        return self._name

    def blinded(self):
        """Returns whether or not the region is blinded.
        """
        return self._blinded

    def varied(self, variation):
        """Creates a copy of the region with the specified variation applied.

        Args:
            variation: The variation to apply

        Returns:
            A duplicate region, but with the specified variation applied.
        """
        # Create the copy
        result = deepcopy(self)

        # Add the variation
        result._variations += (variation,)

        # All done
        return result

    def weighted_selection(self):
        """Returns the weighted-selection expression for the region (after
        applying all variations).
        """
        # Grab resultant weight/selection
        weight, selection = self._weight, self._selection

        # Apply any variations
        for v in self._variations:
            weight, selection = v(weight, selection)

        # Compute the combined expression
        return multiplied(weight, selection)
