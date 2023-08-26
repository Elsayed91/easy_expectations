# class NotImplementedErrorStrategy(BaseStrategy):
#     def __init__(self):
#         self.key = "data_connector_type"
#         self.unsupported_types = ["azure", "dbfs"]

#     def compute(self, config_dict, context):
#         if context.get(self.key) in self.unsupported_types:
#             print(f"{context.get(self.key)} is not implemented yet.")
#             sys.exit(1)
#         return None

#     def applicable(self, context):
#         return context.get(self.key) in self.unsupported_types
