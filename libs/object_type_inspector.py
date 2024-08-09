import logging

class ObjectInspector:
    def __init__(self, include_attributes=True, max_depth=None, logger=None):
        self.include_attributes = include_attributes
        self.max_depth = max_depth
        self.logger = logger or logging.getLogger(__name__)
        self.seen_objects = set()

    def check_object_types(self, obj, depth=0):
        """
        Recursively inspects and returns a list of the types of the given object and any nested objects.

        Parameters:
        obj: The object to inspect.
        depth: Current recursion depth.

        Returns:
        List[type]: A flattened list of types detected in the object.
        """
        if self._exceeds_max_depth(depth):
            return []

        obj_id = id(obj)
        if obj_id in self.seen_objects:
            self.logger.warning(f"Circular reference detected for object: {obj}")
            return []
        self.seen_objects.add(obj_id)

        types_list = [type(obj)]
        self.logger.debug(f"Detected type: {type(obj)} at depth {depth}.")

        iterable_items = self._get_iterable_items(obj)

        if iterable_items:
            types_list.extend(self._process_iterable(iterable_items, depth))
        elif self._should_include_attributes(obj):
            types_list.extend(self._process_attributes(obj, depth))

        return types_list

    def reset(self):
        """Clears the state of the inspector, allowing for fresh inspections."""
        self.seen_objects.clear()

    def _exceeds_max_depth(self, depth):
        if self.max_depth is not None and depth > self.max_depth:
            self.logger.debug(f"Max depth of {self.max_depth} reached, stopping recursion.")
            return True
        return False

    def _get_iterable_items(self, obj):
        if isinstance(obj, dict):
            return obj.items()
        elif isinstance(obj, (list, tuple, set, frozenset)):
            return obj
        return None

    def _process_iterable(self, iterable, depth):
        return [
            self.check_object_types(item, depth + 1)
            for item in iterable
            for item in (item if isinstance(item, tuple) else (item,))
        ]

    def _should_include_attributes(self, obj):
        return hasattr(obj, '__dict__') and self.include_attributes

    def _process_attributes(self, obj, depth):
        return [
            self.check_object_types(attr_value, depth + 1)
            for attr_value in obj.__dict__.values()
        ]
