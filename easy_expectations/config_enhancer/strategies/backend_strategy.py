from easy_expectations.config_enhancer.system_config import ConstantsConfig

from .base_strategy import BaseStrategy


class ResolveStoreBackendStrategy(BaseStrategy):
    BACKEND_MAPPING = ConstantsConfig().get_backend_mapping()

    def compute(self, context):
        """
        Compute function that maps standard stores and document site stores.
        """
        self.map_standard_stores(context)
        self.map_doc_site_stores(context)

    def map_standard_stores(self, context):
        """
        Maps standard stores to their corresponding backends based on the given context.

        Parameters:
            context (dict): The context object containing information about the mapping.

        Returns:
            None
        """
        stores = ["validations", "expectations", "checkpoint"]
        for store in stores:
            store_type_key = f"{store}_store_type"
            backend_key = f"{store}_store_backend"
            self.map_store_backend(context, store_type_key, backend_key)

    def map_doc_site_stores(self, context):
        """
        Maps the document site stores based on the provided context.

        Args:
            context (dict): The context containing information about the document sites.

        Returns:
            None
        """
        doc_sites_count = context.get("doc_sites_count", 0)
        for i in range(1, doc_sites_count + 1):
            store_type_key = f"doc_site_{i}_type"
            backend_key = f"doc_site_{i}_backend"
            self.map_store_backend(context, store_type_key, backend_key)

    def map_store_backend(self, context, store_type_key, backend_key):
        """
        Maps a store backend based on the provided store type.

        Args:
            context (dict): The context containing information about the stores.
            store_type_key (str): The key for the store type in the context.
            backend_key (str): The key for the store backend in the context.

        Returns:
            None
        """
        store_type = context.get(store_type_key)
        backend_system = self.BACKEND_MAPPING.get(store_type)
        if backend_system:
            context[backend_key] = backend_system
