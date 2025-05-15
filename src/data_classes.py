from typing import List, Dict, Union
from pydantic import BaseModel, Field


class FAQ(BaseModel):
    """
    Represents the data structure of the FAQ file.
    """
    type: str = Field(default="faq")
    question: str = Field(default="N/A")
    answer: str = Field(default="N/A")
    category: str = Field(default="N/A")

class ProductDetails(BaseModel):
    """
    Represents the data structure of the Insurance Product.
    """
    type: str
    product_id: str = Field(default="N/A")
    name: str = Field(default="N/A")
    description: str = Field(default="N/A")
    target_industries: List[str] = Field(default=[])
    coverage_options: List[str] = Field(default=[])
    premium_range: Dict = Field(default={'min':0, 'max':0, 'currency': 'N/A'})
    excess_range: Dict = Field(default={'min':0, 'max':0, 'currency': 'N/A'})
    key_features: List[str] = Field(default=[])
    exclusions: List[str] = Field(default=[])
    unique_selling_points: List[str] = Field(default=[])
    required_documents: List[str] = Field(default=[])
    
class OccupationDetails(BaseModel):
    """
    Represents the data structure of the Occupation.
    """
    type: str = Field(default="N/A")
    industry: str = Field(default="N/A")
    occupation: str = Field(default="N/A")
    risk_level: str = Field(default="N/A")
    recommended_products: List[str] = Field(default=[])
    claim_likelihood: Union[float, str] = Field(default=1)
