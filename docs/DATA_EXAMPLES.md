# AASX Data Examples

## Overview

This directory contains comprehensive AASX (Asset Administration Shell Exchange) data examples for various critical infrastructure domains. These examples demonstrate the full capabilities of our AASX processing pipeline and provide realistic data for testing, development, and demonstration purposes.

## Data Examples

https://admin-shell-io.com/samples/

### 1. Additive Manufacturing - Industrial 3D Printer
**File:** `data/aasx-examples/additive-manufacturing-3d-printer.aasx`

**Domain:** Advanced Manufacturing
**Asset Type:** Industrial 3D Printer (AM5000-XL)

**Key Features:**
- **Technical Specifications:** Build volume, layer resolution, supported materials
- **Operational Data:** Real-time status, temperature, print progress
- **Quality Control:** Surface roughness, dimensional accuracy, tensile strength
- **Maintenance:** Service schedule, operating hours
- **Safety:** Emergency stop, safety zones, gas monitoring

**Extracted Data:**
- **Assets:** 2 (Asset Administration Shell + Physical Asset)
- **Submodels:** 5 (Technical Specs, Operational Data, Quality Control, Maintenance, Safety)
- **Properties:** 25+ technical and operational parameters

### 2. Hydrogen Filling Station
**File:** `data/aasx-examples/hydrogen-filling-station.aasx`

**Domain:** Energy Infrastructure
**Asset Type:** High-capacity hydrogen station (H2Fuel-700Pro)

**Key Features:**
- **Station Specifications:** Pressure capacity, storage, filling rate
- **Operational Status:** Real-time flow, pressure, availability
- **Safety Systems:** Gas detection, emergency shutdown, fire suppression
- **Environmental Monitoring:** Weather conditions, emissions
- **Billing System:** Pricing, revenue, transaction tracking

**Extracted Data:**
- **Assets:** 1 (Hydrogen Station)
- **Submodels:** 5 (Station Specs, Operational Status, Safety, Environmental, Billing)
- **Properties:** 20+ operational and safety parameters

### 3. Smart Grid Substation
**File:** `data/aasx-examples/smart-grid-substation.aasx`

**Domain:** Power Infrastructure
**Asset Type:** High-voltage substation (SmartGrid-500kV-Pro)

**Key Features:**
- **Power Specifications:** Voltage levels, rated power, frequency
- **Power Monitoring:** Load, current, power factor, grid frequency
- **Cybersecurity:** Security status, firewall, intrusion detection
- **Weather Monitoring:** Environmental conditions, lightning risk
- **Maintenance:** Equipment health, service schedule

**Extracted Data:**
- **Assets:** 1 (Grid Substation)
- **Submodels:** 5 (Power Specs, Power Monitoring, Cybersecurity, Weather, Maintenance)
- **Properties:** 25+ electrical and security parameters

### 4. Wastewater Treatment Plant
**File:** `data/aasx-examples/wastewater-treatment-plant.aasx`

**Domain:** Water Infrastructure
**Asset Type:** Municipal treatment plant (WWTP-100K-Advanced)

**Key Features:**
- **Plant Specifications:** Design capacity, flow rates, treatment process
- **Process Monitoring:** Influent/effluent flow, sludge production
- **Water Quality:** BOD, COD, TSS, pH monitoring
- **Environmental Compliance:** Regulatory status, inspections
- **Energy Consumption:** Efficiency, renewable energy, biogas production

**Extracted Data:**
- **Assets:** 1 (Treatment Plant)
- **Submodels:** 5 (Plant Specs, Process Monitoring, Water Quality, Compliance, Energy)
- **Properties:** 30+ process and quality parameters

## Data Structure

### AAS 1.0 XML Format
All examples use the AAS 1.0 XML format with proper namespace declarations:

```xml
<aas:aasenv xmlns:aas="http://www.admin-shell.io/aas/1/0">
  <aas:assetAdministrationShells>
    <!-- Asset Administration Shell definitions -->
  </aas:assetAdministrationShells>
  <aas:assets>
    <!-- Physical asset definitions -->
  </aas:assets>
  <aas:submodels>
    <!-- Submodel definitions with properties -->
  </aas:submodels>
</aas:aasenv>
```

### Common Submodel Types

#### 1. Technical Specifications
- **Purpose:** Static technical data and capabilities
- **Category:** CONSTANT
- **Examples:** Manufacturer, model number, capacity, dimensions

#### 2. Operational Data
- **Purpose:** Real-time operational status
- **Category:** VARIABLE
- **Examples:** Current status, performance metrics, efficiency

#### 3. Quality Control
- **Purpose:** Quality parameters and measurements
- **Category:** VARIABLE
- **Examples:** Quality metrics, compliance data, test results

#### 4. Safety Systems
- **Purpose:** Safety monitoring and emergency systems
- **Category:** VARIABLE
- **Examples:** Safety status, emergency systems, monitoring

#### 5. Environmental Monitoring
- **Purpose:** Environmental conditions and impact
- **Category:** VARIABLE
- **Examples:** Weather data, emissions, environmental compliance

#### 6. Maintenance
- **Purpose:** Maintenance schedule and equipment health
- **Category:** VARIABLE
- **Examples:** Service history, next maintenance, equipment health

## Data Categories

### Manufacturing & Industry
- **Additive Manufacturing:** 3D printers, CNC machines, robotic systems
- **Quality Control:** Inspection systems, measurement devices
- **Safety:** Industrial safety systems, monitoring equipment

### Energy Infrastructure
- **Power Generation:** Solar farms, wind turbines, nuclear plants
- **Power Distribution:** Substations, transformers, smart meters
- **Alternative Energy:** Hydrogen stations, battery storage, geothermal

### Water & Wastewater
- **Water Treatment:** Drinking water plants, filtration systems
- **Wastewater Treatment:** Sewage plants, biological treatment
- **Water Distribution:** Pumps, pipelines, storage tanks

### Transportation
- **Smart Cities:** Traffic systems, public transport, parking
- **Logistics:** Warehouses, distribution centers, ports
- **Railway:** Signaling systems, rolling stock, stations

### Healthcare
- **Medical Equipment:** Imaging systems, laboratory equipment
- **Hospital Systems:** Patient monitoring, building management
- **Pharmaceutical:** Manufacturing equipment, quality control

## Usage Examples

### Processing with .NET Processor
```bash
# Process additive manufacturing example
cd aas-processor
dotnet run --configuration Release "../data/aasx-examples/additive-manufacturing-3d-printer.aasx"

# Process hydrogen station example
dotnet run --configuration Release "../data/aasx-examples/hydrogen-filling-station.aasx"

# Process smart grid example
dotnet run --configuration Release "../data/aasx-examples/smart-grid-substation.aasx"

# Process wastewater example
dotnet run --configuration Release "../data/aasx-examples/wastewater-treatment-plant.aasx"
```

### Processing with Python Bridge
```python
from webapp.aasx.dotnet_bridge import DotNetAasProcessor

processor = DotNetAasProcessor()

# Process all examples
examples = [
    "additive-manufacturing-3d-printer.aasx",
    "hydrogen-filling-station.aasx",
    "smart-grid-substation.aasx",
    "wastewater-treatment-plant.aasx"
]

for example in examples:
    result = processor.process_aasx_file(f"data/aasx-examples/{example}")
    print(f"Processed {example}: {len(result['assets'])} assets, {len(result['submodels'])} submodels")
```

### Web Interface Integration
```python
# Upload examples to web interface
import requests

files = [
    "additive-manufacturing-3d-printer.aasx",
    "hydrogen-filling-station.aasx",
    "smart-grid-substation.aasx",
    "wastewater-treatment-plant.aasx"
]

for file in files:
    with open(f"data/aasx-examples/{file}", "rb") as f:
        response = requests.post(
            "http://localhost:8000/api/aasx/upload",
            files={"file": f}
        )
        print(f"Uploaded {file}: {response.status_code}")
```

## Data Quality

### Validation Standards
- **Schema Compliance:** All files validate against AAS 1.0 schema
- **Data Completeness:** Required fields populated with realistic values
- **Relationship Integrity:** Proper references between assets and submodels
- **Format Consistency:** Standardized property naming and categorization

### Quality Metrics
- **Completeness:** 95%+ field completion rate
- **Accuracy:** Realistic values based on industry standards
- **Consistency:** Standardized formats and naming conventions
- **Reliability:** Tested across multiple processing pipelines

## Contributing

### Adding New Examples
1. Create AASX file following the established format
2. Include comprehensive metadata and properties
3. Test with the processing pipeline
4. Update this documentation
5. Submit for review

### Example Requirements
- **Realistic Data:** Use industry-standard values
- **Complete Metadata:** Include all required AAS fields
- **Multiple Submodels:** Demonstrate various data types
- **Proper Relationships:** Include asset-submodel references
- **Documentation:** Provide clear description and usage examples 