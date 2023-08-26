from .backend_strategy import ResolveStoreBackendStrategy
from .checkpoint_connector import DataConnectorCheckpointConnectorStrategy
from .credentials_strategy import ResolveCloudAttributesStrategy
from .default_batch_identifiers import BatchIdentifiersStrategy
from .default_naming_strategy import (
    CheckpointNameStrategy,
    ExpectationsSuiteNameStrategy,
    ResolveDocSiteNamingStrategy,
    ResolveEvaluationParameterStoreNamingStrategy,
    ResolveStoreAndConnectorNamingStrategy,
)
from .execution_engine_strategy import ExecutionEngineStrategy
from .filesystem_enhancement_strategy import (
    CleanupStrategy,
    FileSystemEnhancementStrategy,
)
from .group_entities import GroupEntitiesStrategy
from .inferred_connector_strategy import ResolveDataConnectorInferredConnectorStrategy
from .path_strategy import ResolvePathDefaultsStrategy
from .prepare_docs_strategy import (
    CountDocSitesStrategy,
    FlattenDocSitesStrategy,
    GenerateDefaultDataDocsStrategy,
    ReplaceLocationWithPathStrategy,
)
from .remove_temp_docs_strategy import RemoveTempDocSitesStrategy
from .run_template_strategy import RunNameTemplateStrategy
from .suffix_default_paths import SuffixDefaultPathsStrategy
from .temp_artifacts_strategy import ArtifactsPathStrategy
from .type_strategy import ResolveTypeStrategy

start_strategies = [
    ArtifactsPathStrategy,
    CountDocSitesStrategy,
    FlattenDocSitesStrategy,
    ReplaceLocationWithPathStrategy,
    GenerateDefaultDataDocsStrategy,
    ResolvePathDefaultsStrategy,
    ResolveTypeStrategy,
    ResolveStoreBackendStrategy,
    SuffixDefaultPathsStrategy,
    FileSystemEnhancementStrategy,
    ResolveDocSiteNamingStrategy,
]

end_strategies = [GroupEntitiesStrategy, RemoveTempDocSitesStrategy]


strategy_order_documentation = """

1. CountDocSites:
checks the Doc Sites dict to get a count and add the value to context.
2. FlattenDocSitesStrategy turns Doc Sites lists to a flattened structure.
  From
    doc_sites:
    - Location: local://sss/dd
      Name: local_site
      Tutorial: true
    - Boto Endpoint: wqewqew
      Location: s3://sss/dd
  To
    doc_site_1_location: local://sss/dd
    doc_site_1_name: local_site
    doc_site_1_tutorial: true
    doc_site_2_boto_endpoint: wqewqew
    doc_site_2_location: s3://sss/dd
3. ReplaceLocationWithPathStrategy:
changes doc_site_*_location to doc_site_*_path for naming consistency
4. GenerateDefaultDataDocsStrategy:
If no doc sites are declared, and disable_docs is False, this will generate a default doc site using artifact_path.
5. ResolvePathDefaultsStrategy:
If no path is declared, this will use the artifact_path as a fall back value for all stores and doc entities.


"""
