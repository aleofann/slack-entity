from dataclasses import dataclass
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
