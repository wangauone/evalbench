from .generator import QueryGenerator
import logging
from google.cloud import geminidataanalytics_v1beta as gda

from google.protobuf import json_format

class QueryDataGenerator(QueryGenerator):
    """
    Generator that calls the Google Cloud Gemini Data Analytics API (Query Data) to get SQL suggestions.
    """
    def __init__(self, querygenerator_config):
        super().__init__(querygenerator_config)
        self.name = "query_data_api"
        
        self.project_id = querygenerator_config.get("project_id")
        self.location = querygenerator_config.get("location", "global")
        
        # Context configuration (nested dict matching QueryDataContext)
        self.context = querygenerator_config.get("context", {})

        if not self.project_id:
            raise ValueError("project_id is required for QueryDataGenerator")
        
        # Initialize the client
        self.client = gda.DataChatServiceClient()

    def generate_internal(self, prompt):
        # prompt is the NL query string.
        parent = f"projects/{self.project_id}/locations/{self.location}"
        
        # Build QueryDataContext from config
        context = None
        if self.context:
            try:
                # Use proto-plus constructor which handles nested dicts
                context = gda.QueryDataContext(**self.context)
            except Exception as e:
                logging.error(f"Error parsing QueryDataContext: {e}")
                # Fallback or re-raise? Logging is safer for now.
            
        # Generation options
        gen_options = gda.GenerationOptions(
            generate_query_result=True,
            generate_natural_language_answer=True,
            generate_explanation=True,
            generate_disambiguation_question=True
        )

        request = gda.QueryDataRequest(
            parent=parent,
            prompt=prompt,
            context=context,
            generation_options=gen_options
        )

        try:
            response = self.client.query_data(request=request, timeout=30)
            return response.generated_query
        except Exception as e:
            logging.error(f"Error calling QueryData API: {e}")
            return ""
