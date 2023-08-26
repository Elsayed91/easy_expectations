{% set include_action_list = email_alerting or opsgenie_alerting or pagerduty_alerting or slack_alerting or sns_alerting or teams_alerting or datahub_integration or openlineage_integration or evaluation_parameter_store or metric_store or validations_store or (disable_docs == false and doc_sites) %}

{#
{% set selected_expectation_suite = expectations_suite_name %}
{% if tests and tests|length > 0 %}
{% elif not tests and expectations_file %}
  {% set selected_expectation_suite = expectations_file %}
{% elif contract_tests and contract_tests|length > 0 %}
  {% set selected_expectation_suite = contract_suite_name %}
{% endif %} #}
name: {{ checkpoint_name }}
config_version: 1
class_name: Checkpoint
run_name_template: "{{ run_name_template }}"
validations:
  - batch_request:
      datasource_name: {{ data_connector.name }}
      data_connector_name: {{ data_connector.checkpoint_connector }}
      data_asset_name: {% if "_database" in data_connector.type and data_connector.table != None %}{{ data_connector.table }}{% else %}data_asset_name{% endif %}
      
      {% if connector_query_index %}
      data_connector_query:
        index: {{ connector_query_index }}
      {% endif %}
      {% if data_connector.checkpoint_connector == "default_runtime_data_connector_name" %}
      batch_identifiers:
      {% for identifier, value in batch_identifiers.items() %}
        {{ identifier }}: {{ value }}
      {% endfor %}
      {% endif %}
      {% if evaluation_parameters %}
      evaluation_parameters:
      {% for param, value in evaluation_parameters.items() %}
        {{ param }}: {{ value }}
      {% endfor %}
      {% endif %}
      {% if batch_limit %}
      limit: {{ batch_limit }} 
      {% endif %}
    expectation_suite_name: {{ expectations_suite_name }}
{% if include_action_list %}
    action_list:
      {% if email_alerting %}
      - name: send_email_on_validation_result
        action:
          class_name: EmailAction
          notify_on: {{ notify_on }}
          {% if notify_with %}
          notify_with: {{ notify_with | join(", ") }}
          {% endif %}
          renderer:
            module_name: great_expectations.render.renderer.email_renderer
            class_name: EmailRenderer
          smtp_address: {{ smtp_address }}
          smtp_port: {{ smtp_port }}
          sender_login: {{ sender_login }}
          sender_password: {{ sender_password }}
          {% if sender_alias %}
          sender_alias: {{ sender_alias }}
          {% endif %}
          receiver_emails: {{ receiver_emails }}
          {% if use_tls is not none %}
          use_tls: {{ use_tls }}
          {% endif %}
          {% if use_ssl is not none %}
          use_ssl: {{ use_ssl }}
          {% endif %}
      {% endif %}

      {% if opsgenie_alerting %}
      - name: send_opsgenie_alert_on_validation_result
        action:
          class_name: OpsgenieAlertAction
          notify_on: {{ notify_on }}
          api_key: {{ api_key }}
          priority: {{ priority }}
          renderer:
            module_name: great_expectations.render.renderer.opsgenie_renderer
            class_name: OpsgenieRenderer
          {% if region %}
          region: {{ region }}
          {% endif %}
          {% if tags %}
          tags:
            {% for tag in tags %}
            - {{ tag }}
            {% endfor %}
          {% endif %}
      {% endif %}

      {% if pagerduty_alerting %}
      - name: send_pagerduty_alert_on_validation_result
        action:
          class_name: PagerdutyAlertAction
          api_key: {{ api_key }}
          routing_key: {{ routing_key }}
          notify_on: {{ notify_on }}
      {% endif %}

      {% if slack_alerting %}
      - name: send_slack_notification_on_validation_result
        action:
          class_name: SlackNotificationAction
          {% if webhook %}
          slack_webhook: {{ webhook }}
          {% endif %}
          {% if token %}
          slack_token: {{ token }}
          {% endif %}
          {% if channel %}
          slack_channel: {{ channel }}
          {% endif %}
          notify_on: {{ notify_on }}
          {% if reference_sites %}
          notify_with: {{ reference_sites | join(", ") }}
          {% endif %}
          renderer:
            module_name: great_expectations.render.renderer.slack_renderer
            class_name: SlackRenderer
          {% if show_failed_expectations %}
          show_failed_expectations: {{ show_failed_expectations }}
          {% endif %}
      {% endif %}

      {% if sns_alerting %}
      - name: send_sns_notification_on_validation_result
        action:
          class_name: SNSNotificationAction
          sns_topic_arn: {{ topic_arn }}
          {% if message_subject %}
          sns_subject: {{ message_subject }}
          {% endif %}
      {% endif %}

      {% if teams_alerting %}
      - name: send_microsoft_teams_notification_on_validation_result
        action:
          class_name: MicrosoftTeamsNotificationAction
          microsoft_teams_webhook: {{ webhook }}
          notify_on: {{ notify_on }}
          renderer:
            module_name: great_expectations.render.renderer.microsoft_teams_renderer
            class_name: MicrosoftTeamsRenderer
      {% endif %}

      {% if datahub_integration %}
      - name: datahub_action
        action:
          module_name: datahub.integrations.great_expectations.action
          class_name: DataHubValidationAction
          server_url: {{ url }}
      {% endif %}

      {% if openlineage_integration %}
      - name: openlineage
        action:
          class_name: OpenLineageValidationAction
          module_name: openlineage.common.provider.great_expectations
          openlineage_host: {{ host }}
          openlineage_apiKey: {{ api_key }}
          job_name: {{ job_name }}
          openlineage_namespace: {{ namespace }}
      {% endif %}

      {% if evaluation_parameter_store.name %}
      - name: store_evaluation_parameters
        action:
          class_name: StoreEvaluationParametersAction
      {% endif %}

      {% if metric_store %}
      - name: store_evaluation_params
        action:
          class_name: StoreMetricsAction
          target_store_name: 
      {% endif %}

      {% if validations_store %}
      - name: save_validation_results
        action:
          class_name: StoreValidationResultAction 
      {% endif %}

      {% if disable_docs == false and doc_sites %}
      - name: update_documentation
        action:
          class_name: UpdateDataDocsAction
      {% endif %}
{% endif %}

    runtime_configuration:
      result_format:
        result_format: {{ result_format | default('COMPLETE') }}
      
        # include_unexpected_rows: 
        # unexpected_index_column_names: Defines columns that can be used to identify unexpected results, for example primary key (PK) column(s) or other columns with unique identifiers. Supports multiple column names as a list.
        # return_unexpected_index_query: When running validations, a query (or a set of indices) will be returned that will allow you to retrieve the full set of unexpected results including any columns identified in unexpected_index_column_names. Setting this value to False will suppress the output (default is True).
        # partial_unexpected_count: Sets the number of results to include in partial_unexpected_count, if applicable. If set to 0, this will suppress the unexpected counts.
        # include_unexpected_rows: When running validations, this will return the entire row for each unexpected value in dictionary form
        # https://docs.greatexpectations.io/docs/reference/expectations/result_format/#column-map-expectations-eg-columnmapexpectation-columnpairmapexpectation-multicolumnmapexpectation