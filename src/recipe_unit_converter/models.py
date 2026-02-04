from typing import List, Optional, Dict
from pydantic import BaseModel

# --- Data Loading Models ---

class UnitDetail(BaseModel):
    factor: float
    aliases: List[str]


class TemperatureUnitDetail(BaseModel):
    aliases: List[str]


class VolumeDefinition(BaseModel):
    base: str
    units: Dict[str, UnitDetail]


class WeightDefinition(BaseModel):
    base: str
    units: Dict[str, UnitDetail]


class TempDefinition(BaseModel):
    units: Dict[str, TemperatureUnitDetail]


class UnitsDb(BaseModel):
    volume: VolumeDefinition
    weight: WeightDefinition
    temperature: TempDefinition


class IngredientEntry(BaseModel):
    id: str
    names: List[str]
    density: Optional[float] = None
    source: Optional[List[Dict[str, str]]] = None

# --- Application Models ---

class ParsedQuery(BaseModel):
    quantity: float
    unit: str
    ingredient: Optional[str] = None


class ConversionResult(BaseModel):
    original_query: str
    source_unit: str
    target_unit: str
    result_value: float
    result_unit: str
    ingredient: str | None
    explanation: str
