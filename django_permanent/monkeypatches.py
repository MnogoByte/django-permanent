"""We monkeypatch AddManagers to pluck the original manager type information"""
try:
    from mypy_django_plugin.transformers.models import AddManagers, helpers

    def get_dynamic_manager(self, fullname: str, manager):
        """
        Try to get a dynamically defined manager
        """
        # Check if manager is a generated (dynamic class) manager
        base_manager_fullname = helpers.get_class_fullname(
            manager.__class__.__bases__[0]
        )

        # >>>> BEGIN MONKEY PATCH
        # We check if it is our patched queryset.
        # if it is.... use the parent type
        if getattr(manager.__class__, "is_django_permanent_patched", None):
            base_manager_fullname = helpers.get_class_fullname(
                manager.__class__.__bases__[0].__bases__[0]
            )
            fullname = helpers.get_class_fullname(manager.__class__.__bases__[0])
        # <<<< END MONKEY PATCH

        generated_managers = self.get_generated_manager_mappings(base_manager_fullname)

        generated_manager_name = generated_managers.get(fullname, None)

        if generated_manager_name is None:
            return None

        return self.lookup_typeinfo(generated_manager_name)

    AddManagers.get_dynamic_manager = get_dynamic_manager
except ImportError as e:
    pass
