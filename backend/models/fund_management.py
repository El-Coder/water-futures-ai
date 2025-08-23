"""
Fund Management Models for Water Futures AI
Ensures proper separation and earmarking of subsidy funds vs trading capital
"""
from datetime import datetime
from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum

class FundSource(str, Enum):
    """Types of fund sources"""
    PERSONAL = "personal"
    SUBSIDY_FEDERAL = "subsidy_federal"
    SUBSIDY_STATE = "subsidy_state"
    SUBSIDY_LOCAL = "subsidy_local"
    DROUGHT_RELIEF = "drought_relief"
    CONSERVATION_GRANT = "conservation_grant"
    CROP_INSURANCE = "crop_insurance"
    TRADING_PROFIT = "trading_profit"
    LOAN = "loan"
    
class FundRestriction(str, Enum):
    """Types of restrictions on fund usage"""
    UNRESTRICTED = "unrestricted"
    INFRASTRUCTURE_ONLY = "infrastructure_only"
    CONSERVATION_ONLY = "conservation_only"
    NO_TRADING = "no_trading"
    EMERGENCY_ONLY = "emergency_only"
    EQUIPMENT_ONLY = "equipment_only"
    WATER_PURCHASE_ONLY = "water_purchase_only"

class EarmarkedFund(BaseModel):
    """Represents earmarked funds with specific restrictions"""
    fund_id: str = Field(..., description="Unique identifier for this fund")
    source: FundSource = Field(..., description="Source of the funds")
    amount: float = Field(..., description="Amount in USD")
    available_amount: float = Field(..., description="Currently available amount")
    restrictions: List[FundRestriction] = Field(default_factory=list)
    
    # Metadata
    received_date: datetime = Field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = Field(None, description="When funds must be used by")
    purpose: str = Field(..., description="Intended purpose of funds")
    
    # Compliance tracking
    requires_reporting: bool = Field(default=True)
    reporting_deadline: Optional[datetime] = None
    documentation_required: List[str] = Field(default_factory=list)
    
    # Usage tracking
    transactions: List[Dict[str, Any]] = Field(default_factory=list)
    compliance_status: Literal["compliant", "pending_report", "non_compliant"] = "compliant"
    
    @validator('available_amount')
    def validate_available_amount(cls, v, values):
        if 'amount' in values and v > values['amount']:
            raise ValueError("Available amount cannot exceed total amount")
        return v
    
    def can_use_for_trading(self) -> bool:
        """Check if these funds can be used for trading"""
        return FundRestriction.NO_TRADING not in self.restrictions
    
    def can_use_for_purpose(self, purpose: str) -> bool:
        """Check if funds can be used for a specific purpose"""
        purpose_map = {
            "infrastructure": FundRestriction.INFRASTRUCTURE_ONLY,
            "conservation": FundRestriction.CONSERVATION_ONLY,
            "equipment": FundRestriction.EQUIPMENT_ONLY,
            "water_purchase": FundRestriction.WATER_PURCHASE_ONLY,
            "emergency": FundRestriction.EMERGENCY_ONLY
        }
        
        if FundRestriction.UNRESTRICTED in self.restrictions:
            return True
            
        required_restriction = purpose_map.get(purpose.lower())
        if required_restriction:
            return required_restriction in self.restrictions
        
        return False

class AccountBalance(BaseModel):
    """Complete account balance with earmarked funds tracking"""
    farmer_id: str = Field(..., description="Farmer identifier")
    
    # Unrestricted funds (can be used for trading)
    trading_balance: float = Field(default=0.0, description="Available for trading")
    personal_funds: float = Field(default=0.0, description="Personal unrestricted funds")
    trading_profits: float = Field(default=0.0, description="Profits from trading")
    
    # Earmarked funds (restricted usage)
    earmarked_funds: List[EarmarkedFund] = Field(default_factory=list)
    
    # Totals
    total_balance: float = Field(default=0.0)
    total_earmarked: float = Field(default=0.0)
    total_available_for_trading: float = Field(default=0.0)
    
    # Compliance
    compliance_warnings: List[str] = Field(default_factory=list)
    last_audit: Optional[datetime] = None
    
    def calculate_totals(self):
        """Recalculate all totals"""
        self.total_earmarked = sum(fund.available_amount for fund in self.earmarked_funds)
        self.total_available_for_trading = self.trading_balance + self.personal_funds + self.trading_profits
        
        # Add tradeable earmarked funds
        for fund in self.earmarked_funds:
            if fund.can_use_for_trading():
                self.total_available_for_trading += fund.available_amount
        
        self.total_balance = self.total_available_for_trading + sum(
            fund.available_amount for fund in self.earmarked_funds 
            if not fund.can_use_for_trading()
        )
    
    def add_subsidy(self, subsidy_type: str, amount: float, restrictions: List[str] = None) -> EarmarkedFund:
        """Add a subsidy with appropriate earmarking"""
        fund_source_map = {
            "drought_relief": FundSource.DROUGHT_RELIEF,
            "conservation_grant": FundSource.CONSERVATION_GRANT,
            "crop_insurance": FundSource.CROP_INSURANCE,
            "federal": FundSource.SUBSIDY_FEDERAL,
            "state": FundSource.SUBSIDY_STATE,
            "local": FundSource.SUBSIDY_LOCAL
        }
        
        # Default restrictions for different subsidy types
        default_restrictions = {
            "drought_relief": [FundRestriction.NO_TRADING, FundRestriction.WATER_PURCHASE_ONLY],
            "conservation_grant": [FundRestriction.NO_TRADING, FundRestriction.CONSERVATION_ONLY],
            "crop_insurance": [FundRestriction.NO_TRADING, FundRestriction.EMERGENCY_ONLY]
        }
        
        fund = EarmarkedFund(
            fund_id=f"{subsidy_type}_{datetime.now().isoformat()}",
            source=fund_source_map.get(subsidy_type, FundSource.SUBSIDY_FEDERAL),
            amount=amount,
            available_amount=amount,
            restrictions=restrictions or default_restrictions.get(subsidy_type, [FundRestriction.NO_TRADING]),
            purpose=f"{subsidy_type.replace('_', ' ').title()} Subsidy",
            requires_reporting=True,
            reporting_deadline=datetime.now().replace(month=12, day=31),
            documentation_required=[
                "Proof of usage",
                "Receipts",
                "Impact assessment"
            ]
        )
        
        self.earmarked_funds.append(fund)
        self.calculate_totals()
        return fund
    
    def get_available_for_purpose(self, purpose: str) -> float:
        """Get total funds available for a specific purpose"""
        total = 0
        
        # Check unrestricted funds
        if purpose.lower() == "trading":
            return self.total_available_for_trading
        
        # Check earmarked funds
        for fund in self.earmarked_funds:
            if fund.can_use_for_purpose(purpose):
                total += fund.available_amount
        
        # Personal funds can be used for anything
        total += self.personal_funds
        
        return total

class FundTransaction(BaseModel):
    """Record of fund usage"""
    transaction_id: str = Field(..., description="Unique transaction ID")
    fund_id: str = Field(..., description="ID of fund being used")
    amount: float = Field(..., description="Transaction amount")
    purpose: str = Field(..., description="Purpose of transaction")
    category: Literal["trading", "infrastructure", "conservation", "equipment", "water", "other"]
    
    # Compliance
    approved: bool = Field(default=False)
    approval_reason: Optional[str] = None
    documentation: List[str] = Field(default_factory=list)
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now)
    description: Optional[str] = None
    recipient: Optional[str] = None
    
    # Result tracking
    status: Literal["pending", "completed", "rejected", "reversed"] = "pending"
    result: Optional[Dict[str, Any]] = None

class FundManagementWarning(BaseModel):
    """Warnings for fund management compliance"""
    warning_type: Literal["restriction_violation", "expiry_approaching", "reporting_due", "insufficient_funds"]
    severity: Literal["info", "warning", "critical"]
    message: str
    fund_id: Optional[str] = None
    action_required: Optional[str] = None
    deadline: Optional[datetime] = None