from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Compliance:
    country: str
    localAuthority: str
    licenseNumber: str
    licenseLink: str
    registeredName: str
    dates: dict
    status: str
    licenseType: str

@dataclass
class Contacts:
    contactName: str
    position: str
    emailAddress: str
    contactLinks: List[str]

@dataclass
class Departments:
    departmentName: str
    departmentLinks: List[str]

@dataclass
class PaymentSystem:
    systemName: str
    website: Optional[str] = None
    paymentTypes: Optional[List[str]] = field(default_factory=list)
    paymentMethods: Optional[List[str]] = field(default_factory=list)
    registrationGeography: Optional[str] = None