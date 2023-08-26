from .base_strategy import BaseStrategy


class RemoveTempDocSitesStrategy(BaseStrategy):
    def compute(self, context):
        """
        Compute function that checks if all "doc_sites" have paths in the
        temporary directory.
        If so, it removes those sites and sets "disable_docs" to True.
        """
        temp_sites = []
        for site_key, site in context.get("doc_sites", {}).items():
            if "/tmp/" in site.get("path", ""):
                temp_sites.append(site_key)

        for site_key in temp_sites:
            del context["doc_sites"][site_key]

        # If all sites were temporary
        if not context.get("doc_sites"):
            context["disable_docs"] = True
