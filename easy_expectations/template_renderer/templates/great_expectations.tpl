{% import 'macros/azure_options.j2' as azure_options_macro %}
{% import 'macros/generate_backend.j2' as backend_macro %}

config_version: 3.0
datasources:
  {{ data_connector.name }}:
    module_name: great_expectations.datasource
    class_name: Datasource
    execution_engine:
      module_name: great_expectations.execution_engine
      class_name: {{ data_connector.execution_engine }}
      {% if "_database" in data_connector.type %}
      connection_string: {{ data_connector.path }}
      {% endif %}
      {{ azure_options_macro.azure_data_connector_options(data_connector) }}
    data_connectors:
      default_runtime_data_connector_name:
          class_name: RuntimeDataConnector
          batch_identifiers:
            {% for identifier in batch_identifiers.keys() %}
            - {{ identifier }}
            {% endfor %}
{% if data_connector.type != "in_memory" %}
      default_inferred_data_connector_name:
          class_name: {{ data_connector.inferred_connector }}
          {% if data_connector.type in ["local", "dbfs"] %}
          base_directory: {{ data_connector.base_dir }}
          {% elif data_connector.type == "s3" %}
          bucket: {{ data_connector.bucket }}
          {% elif data_connector.type == "gcs" %}
          bucket_or_name: {{ data_connector.bucket }}
          {% endif %}
          {% if  data_connector.type in ["gcs" , "s3"] %}
          prefix: {{ data_connector.prefix | default('') }}
          {% elif data_connector.type == "azure" %}
          container: {{ data_connector.container }}
          name_starts_with: {{ data_connector.prefix | default('') }}
          {% endif %}
          {% if "_database" not in data_connector.type %}
          default_regex:
              pattern: {{ data_connector.pattern }}
              group_names:
              - data_asset_name
          {% else %}
          include_schema_name: true
          {% endif %}
{% endif %}



{% if custom_expectations_path %}
plugins_directory: {{ custom_expectations_path }}
{% endif %}

{% if checkpoint_store or expectations_store or validations_store %}
stores:
  {% if expectations_store %}
  {{ expectations_store.name }}:
    class_name: ExpectationsStore
    store_backend:
    {{ backend_macro.store_backend(expectations_store) }}
  {% endif %}
  {% if validations_store %}
  {{ validations_store.name }}:
    class_name: ValidationsStore
    store_backend:
    {{ backend_macro.store_backend(validations_store) }}
  {% endif %}

  {% if evaluation_parameter_store %}
  {{ evaluation_parameter_store.name }}:
    class_name: EvaluationParameterStore
  {% endif %}

  {% if checkpoint_store %}
  {{ checkpoint_store.name }}:
    class_name: CheckpointStore
    store_backend:
    {{ backend_macro.store_backend(checkpoint_store) }}
  {% endif %}

{%if expectations_store %}
expectations_store_name: {{ expectations_store.name }}
{% endif %}
{%if validations_store %}
validations_store_name: {{ validations_store.name }}
{% endif %}
{%if checkpoint_store %}
evaluation_parameter_store_name: {{ evaluation_parameter_store.name }}
checkpoint_store_name: {{ checkpoint_store.name }}
{% endif %}
{% endif %}


{% if disable_docs != True %}
data_docs_sites:
  {% for site_key, site in doc_sites.items() %}
  {{ site_key }}:
    class_name: SiteBuilder
    show_how_to_buttons: {{ site.tutorial | default(false) }}
    store_backend:
    {{ backend_macro.store_backend(site) }}
    site_index_builder:
      class_name: DefaultSiteIndexBuilder
  {% endfor %}
{% endif %}




{% if enable_usage_statistic %}
anonymous_usage_statistics:
  enabled: {{ enable_usage_statistic }}
{% endif %}