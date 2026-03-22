from typing import Dict, Any, Optional
from datetime import datetime


class WhiteLabelEngine:
    """
    Agencies and resellers can sell VoiceCore
    under their own brand.
    This multiplies revenue without extra marketing.
    
    Agency pays you $200/month per client.
    They charge their client $500/month.
    Everyone wins.
    """
    
    def __init__(self, db_session, dns_service):
        self.db = db_session
        self.dns = dns_service
    
    async def create_white_label_partner(
        self,
        partner_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        partner = await self.db.create_partner({
            "company_name": partner_data["company_name"],
            "brand_name": partner_data["brand_name"],
            "logo_url": partner_data["logo_url"],
            "primary_color": partner_data["primary_color"],
            "domain": partner_data.get("custom_domain"),
            "revenue_share_percent": partner_data.get("revenue_share_percent", 20),
            "max_clients": partner_data.get("max_clients", 10),
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        })
        
        if partner_data.get("custom_domain"):
            await self.dns.create_cname(
                partner_data["custom_domain"],
                target="voicecore.ai"
            )
        
        return partner
    
    async def add_client_to_partner(
        self,
        partner_id: str,
        client_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        partner = await self.db.get_partner(partner_id)
        
        if partner["current_clients"] >= partner["max_clients"]:
            return {"error": "Client limit reached"}
        
        client = await self.db.create_client({
            "partner_id": partner_id,
            "company_name": client_data["company_name"],
            "subdomain": client_data.get("subdomain"),
            "plan": client_data.get("plan", "standard"),
            "monthly_price": client_data.get("monthly_price", 299)
        })
        
        await self.db.increment_partner_client_count(partner_id)
        
        return client
    
    def apply_branding(
        self,
        partner_id: str,
        template: Dict[str, Any]
    ) -> Dict[str, Any]:
        partner = self.db.get_partner(partner_id)
        
        branded = {
            **template,
            "company_name": partner["brand_name"],
            "logo": partner["logo_url"],
            "primary_color": partner["primary_color"],
            "support_email": partner.get("support_email", "support@voicecore.ai"),
            "footer_text": f"Powered by {partner['brand_name']}",
            "domain": partner.get("domain")
        }
        
        return branded
    
    async def get_partner_revenue_report(
        self,
        partner_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        clients = await self.db.get_partner_clients(partner_id)
        
        total_revenue = 0
        client_details = []
        
        for client in clients:
            revenue = await self.db.get_client_revenue(
                client["id"],
                start_date,
                end_date
            )
            total_revenue += revenue
            client_details.append({
                "client_name": client["company_name"],
                "revenue": revenue
            })
        
        partner = await self.db.get_partner(partner_id)
        revenue_share = total_revenue * (partner["revenue_share_percent"] / 100)
        
        return {
            "partner_id": partner_id,
            "period": f"{start_date} to {end_date}",
            "total_revenue": total_revenue,
            "revenue_share_percent": partner["revenue_share_percent"],
            "partner_payout": revenue_share,
            "client_details": client_details
        }


class PartnerPortal:
    """
    Self-service portal for white-label partners.
    """
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def get_dashboard(self, partner_id: str) -> Dict[str, Any]:
        partner = await self.db.get_partner(partner_id)
        clients = await self.db.get_partner_clients(partner_id)
        
        return {
            "partner_name": partner["brand_name"],
            "total_clients": len(clients),
            "client_limit": partner["max_clients"],
            "revenue_share": partner["revenue_share_percent"],
            "clients": clients
        }
    
    async def update_settings(
        self,
        partner_id: str,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self.db.update_partner(partner_id, settings)
