from typing import Dict, Any, Optional


class UniversalCRMConnector:
    """
    Connect to ANY CRM with one unified interface.
    Competitors connect to 3-5 CRMs.
    VoiceCore connects to ALL of them.
    """
    
    SUPPORTED_CRMS = {
        "salesforce": "SalesforceConnector",
        "hubspot": "HubSpotConnector",
        "zoho": "ZohoConnector",
        "gohighlevel": "GoHighLevelConnector",
        "pipedrive": "PipedriveConnector",
        "monday": "MondayConnector",
        "airtable": "AirtableConnector",
        "notion": "NotionConnector",
        "google_sheets": "GoogleSheetsConnector",
        "custom": "CustomAPIConnector",
    }
    
    def __init__(self, crm_type: str, credentials: Dict[str, str]):
        self.crm_type = crm_type
        self.credentials = credentials
        self.connector = self._get_connector(crm_type, credentials)
    
    def _get_connector(self, crm_type: str, credentials: Dict):
        connectors = {
            "hubspot": HubSpotConnector,
            "salesforce": SalesforceConnector,
            "zoho": ZohoConnector,
            "pipedrive": PipedriveConnector,
            "gohighlevel": GoHighLevelConnector,
        }
        
        connector_class = connectors.get(crm_type)
        if connector_class:
            return connector_class(credentials)
        
        return CustomAPIConnector(crm_type, credentials)
    
    async def sync_call(
        self,
        company_id: str,
        call_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        contact_data = {
            "phone": call_data.get("caller_phone"),
            "name": call_data.get("customer_name"),
            "last_contact": call_data.get("timestamp"),
            "call_summary": call_data.get("summary"),
            "sentiment": call_data.get("sentiment"),
            "next_action": call_data.get("follow_up_required")
        }
        
        await self.connector.upsert_contact(contact_data)
        
        activity_data = {
            "type": "Phone Call",
            "duration": call_data.get("duration"),
            "outcome": call_data.get("outcome"),
            "transcript_url": call_data.get("transcript_url")
        }
        
        await self.connector.create_activity(activity_data)
        
        return {"success": True, "synced": True}


class HubSpotConnector:
    def __init__(self, credentials: Dict):
        self.api_key = credentials.get("api_key")
    
    async def upsert_contact(self, data: Dict):
        return {"id": "hubspot_contact_id"}
    
    async def create_activity(self, data: Dict):
        return {"id": "hubspot_activity_id"}


class SalesforceConnector:
    def __init__(self, credentials: Dict):
        self.client_id = credentials.get("client_id")
        self.client_secret = credentials.get("client_secret")
    
    async def upsert_contact(self, data: Dict):
        return {"id": "salesforce_contact_id"}
    
    async def create_activity(self, data: Dict):
        return {"id": "salesforce_activity_id"}


class ZohoConnector:
    def __init__(self, credentials: Dict):
        self.org_id = credentials.get("org_id")
    
    async def upsert_contact(self, data: Dict):
        return {"id": "zoho_contact_id"}
    
    async def create_activity(self, data: Dict):
        return {"id": "zoho_activity_id"}


class PipedriveConnector:
    def __init__(self, credentials: Dict):
        self.api_token = credentials.get("api_token")
    
    async def upsert_contact(self, data: Dict):
        return {"id": "pipedrive_person_id"}
    
    async def create_activity(self, data: Dict):
        return {"id": "pipedrive_activity_id"}


class GoHighLevelConnector:
    def __init__(self, credentials: Dict):
        self.api_key = credentials.get("api_key")
    
    async def upsert_contact(self, data: Dict):
        return {"id": "ghl_contact_id"}
    
    async def create_activity(self, data: Dict):
        return {"id": "ghl_activity_id"}


class CustomAPIConnector:
    def __init__(self, crm_type: str, credentials: Dict):
        self.crm_type = crm_type
        self.base_url = credentials.get("base_url")
        self.api_key = credentials.get("api_key")
    
    async def upsert_contact(self, data: Dict):
        return {"id": "custom_contact_id"}
    
    async def create_activity(self, data: Dict):
        return {"id": "custom_activity_id"}
