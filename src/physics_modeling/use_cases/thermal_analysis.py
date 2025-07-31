"""
Thermal Analysis Use Cases

This module contains famous real-world thermal analysis use cases including:
- Electronics cooling (CPU, GPU, mobile devices)
- Automotive thermal management
- Building HVAC systems
- Industrial heat exchangers
- Aerospace thermal protection
"""

import numpy as np
from typing import Dict, Any, List
from ..core import Material, Geometry, BoundaryConditions
from ..core.material import MaterialTemplates
from ..core.geometry import GeometryUtils
from ..core.constraints import BoundaryConditionTemplates, PhysicsType, BoundaryType

class ThermalAnalysisUseCases:
    """Collection of famous thermal analysis use cases"""
    
    @staticmethod
    def cpu_cooling_analysis() -> Dict[str, Any]:
        """
        CPU Cooling Analysis - Famous use case for electronics thermal management
        
        This represents the thermal analysis of a modern CPU with heat sink,
        similar to Intel i9 or AMD Ryzen processors.
        """
        use_case = {
            "name": "CPU Cooling Analysis",
            "description": "Thermal analysis of a modern CPU with heat sink and fan cooling system",
            "industry": "Electronics",
            "famous_examples": ["Intel i9-13900K", "AMD Ryzen 9 7950X", "Apple M2 Pro"],
            "challenge": "Managing thermal dissipation of 150-250W in a compact package",
            "physics_focus": "Conduction, convection, and heat transfer optimization"
        }
        
        # Materials
        materials = {
            "cpu_silicon": MaterialTemplates.aluminum().copy(),  # Simplified for silicon
            "heat_sink": MaterialTemplates.aluminum(),
            "thermal_paste": Material(
                name="Thermal Paste",
                material_type="thermal_interface",
                thermal_conductivity=8.0,  # W/(m·K)
                specific_heat=1000.0
            ),
            "air": MaterialTemplates.air()
        }
        
        # Geometry (simplified CPU + heat sink)
        cpu_geometry = GeometryUtils.create_cube("cpu_die", size=0.02)  # 20mm CPU die
        heat_sink_geometry = GeometryUtils.create_cube("heat_sink", size=0.08)  # 80mm heat sink
        heat_sink_geometry.translate(np.array([0, 0, 0.01]))  # Position above CPU
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="cpu_cooling_bc",
            physics_type=PhysicsType.THERMAL
        )
        
        # CPU heat generation (150W typical for high-end CPU)
        cpu_heat = BoundaryConditionTemplates.thermal_heat_source(heat_flux=150e6)  # 150W over small area
        cpu_heat.geometry_entities = ["cpu_die"]
        boundary_conditions.add_condition(cpu_heat)
        
        # Heat sink convection
        heat_sink_convection = BoundaryConditionTemplates.thermal_convection(
            ambient_temp=25.0, h_coeff=50.0  # Forced convection with fan
        )
        heat_sink_convection.geometry_entities = ["heat_sink"]
        boundary_conditions.add_condition(heat_sink_convection)
        
        # Ambient temperature at case
        case_ambient = BoundaryConditionTemplates.thermal_fixed_temperature(35.0)  # Case temperature
        case_ambient.geometry_entities = ["case_boundary"]
        boundary_conditions.add_condition(case_ambient)
        
        use_case.update({
            "materials": materials,
            "geometry": {"cpu": cpu_geometry, "heat_sink": heat_sink_geometry},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "max_cpu_temp": "85-95°C",
                "heat_sink_temp": "45-55°C",
                "thermal_resistance": "0.2-0.3°C/W",
                "cooling_efficiency": "85-90%"
            },
            "optimization_targets": [
                "Minimize CPU junction temperature",
                "Maximize heat sink surface area",
                "Optimize thermal paste application",
                "Improve fan airflow design"
            ]
        })
        
        return use_case
    
    @staticmethod
    def electric_vehicle_battery_thermal_management() -> Dict[str, Any]:
        """
        EV Battery Thermal Management - Critical for Tesla, BYD, and other EV manufacturers
        
        This represents the thermal management system of electric vehicle battery packs,
        crucial for performance, safety, and longevity.
        """
        use_case = {
            "name": "EV Battery Thermal Management",
            "description": "Thermal analysis of electric vehicle battery pack cooling system",
            "industry": "Automotive",
            "famous_examples": ["Tesla Model S Plaid", "BYD Blade Battery", "Porsche Taycan"],
            "challenge": "Maintaining battery temperature between 15-35°C for optimal performance and safety",
            "physics_focus": "Thermal management, safety, and performance optimization"
        }
        
        # Materials
        materials = {
            "battery_cells": Material(
                name="Lithium-ion Battery",
                material_type="battery",
                density=2300.0,
                thermal_conductivity=1.0,  # Anisotropic in practice
                specific_heat=1200.0
            ),
            "coolant": Material(
                name="Battery Coolant",
                material_type="fluid",
                density=1000.0,
                thermal_conductivity=0.6,
                specific_heat=4200.0,
                viscosity=1e-3
            ),
            "aluminum_cooling_plate": MaterialTemplates.aluminum()
        }
        
        # Geometry (simplified battery pack)
        battery_pack = GeometryUtils.create_cube("battery_pack", size=1.2)  # 1.2m battery pack
        cooling_plates = []
        for i in range(8):  # 8 cooling plates
            plate = GeometryUtils.create_cube(f"cooling_plate_{i}", size=1.0)
            plate.translate(np.array([0, 0, 0.1 * i]))
            cooling_plates.append(plate)
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="ev_battery_bc",
            physics_type=PhysicsType.THERMAL
        )
        
        # Battery heat generation (varies with load)
        battery_heat = BoundaryConditionTemplates.thermal_heat_source(heat_flux=5000.0)  # 5kW heat generation
        battery_heat.geometry_entities = ["battery_pack"]
        boundary_conditions.add_condition(battery_heat)
        
        # Coolant flow
        coolant_inlet = BoundaryConditionTemplates.thermal_fixed_temperature(15.0)  # Coolant inlet
        coolant_inlet.geometry_entities = ["coolant_inlet"]
        boundary_conditions.add_condition(coolant_inlet)
        
        # Ambient heat transfer
        ambient_convection = BoundaryConditionTemplates.thermal_convection(
            ambient_temp=25.0, h_coeff=10.0  # Natural convection
        )
        ambient_convection.geometry_entities = ["battery_pack"]
        boundary_conditions.add_condition(ambient_convection)
        
        use_case.update({
            "materials": materials,
            "geometry": {"battery_pack": battery_pack, "cooling_plates": cooling_plates},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "battery_temp_range": "15-35°C",
                "cooling_power": "3-8 kW",
                "thermal_efficiency": "90-95%",
                "safety_margin": "10-15°C below thermal runaway"
            },
            "optimization_targets": [
                "Maintain uniform temperature distribution",
                "Minimize thermal gradients",
                "Optimize coolant flow rate",
                "Prevent thermal runaway conditions"
            ]
        })
        
        return use_case
    
    @staticmethod
    def data_center_cooling() -> Dict[str, Any]:
        """
        Data Center Cooling - Critical for Google, Amazon, Microsoft cloud infrastructure
        
        This represents the thermal management of large-scale data centers,
        essential for cloud computing and AI infrastructure.
        """
        use_case = {
            "name": "Data Center Cooling Analysis",
            "description": "Thermal analysis of large-scale data center cooling systems",
            "industry": "Information Technology",
            "famous_examples": ["Google Data Centers", "AWS Cloud Infrastructure", "Microsoft Azure"],
            "challenge": "Cooling thousands of servers while minimizing energy consumption and PUE",
            "physics_focus": "Large-scale thermal management, energy efficiency, and sustainability"
        }
        
        # Materials
        materials = {
            "server_rack": MaterialTemplates.aluminum(),
            "cooling_air": MaterialTemplates.air(),
            "chilled_water": Material(
                name="Chilled Water",
                material_type="fluid",
                density=1000.0,
                thermal_conductivity=0.6,
                specific_heat=4200.0
            ),
            "concrete_floor": Material(
                name="Concrete Floor",
                material_type="construction",
                density=2400.0,
                thermal_conductivity=1.4,
                specific_heat=880.0
            )
        }
        
        # Geometry (data center layout)
        server_rack = GeometryUtils.create_cube("server_rack", size=0.6)  # Standard 19" rack
        data_center_floor = GeometryUtils.create_cube("data_center", size=50.0)  # 50m data center
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="data_center_bc",
            physics_type=PhysicsType.THERMAL
        )
        
        # Server heat generation (typical 3-5kW per rack)
        server_heat = BoundaryConditionTemplates.thermal_heat_source(heat_flux=4000.0)  # 4kW per rack
        server_heat.geometry_entities = ["server_rack"]
        boundary_conditions.add_condition(server_heat)
        
        # Cold aisle temperature
        cold_aisle = BoundaryConditionTemplates.thermal_fixed_temperature(18.0)  # Cold aisle
        cold_aisle.geometry_entities = ["cold_aisle"]
        boundary_conditions.add_condition(cold_aisle)
        
        # Hot aisle return
        hot_aisle = BoundaryConditionTemplates.thermal_convection(
            ambient_temp=35.0, h_coeff=20.0  # Hot aisle return
        )
        hot_aisle.geometry_entities = ["hot_aisle"]
        boundary_conditions.add_condition(hot_aisle)
        
        use_case.update({
            "materials": materials,
            "geometry": {"server_rack": server_rack, "data_center": data_center_floor},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "pue_ratio": "1.1-1.3",
                "cooling_efficiency": "85-95%",
                "energy_savings": "20-40% vs traditional cooling",
                "temperature_uniformity": "±2°C"
            },
            "optimization_targets": [
                "Minimize Power Usage Effectiveness (PUE)",
                "Optimize airflow patterns",
                "Implement hot/cold aisle containment",
                "Use free cooling when possible"
            ]
        })
        
        return use_case
    
    @staticmethod
    def solar_panel_thermal_analysis() -> Dict[str, Any]:
        """
        Solar Panel Thermal Analysis - Important for renewable energy systems
        
        This represents the thermal analysis of solar photovoltaic panels,
        crucial for efficiency optimization and thermal management.
        """
        use_case = {
            "name": "Solar Panel Thermal Analysis",
            "description": "Thermal analysis of solar photovoltaic panels and thermal management",
            "industry": "Renewable Energy",
            "famous_examples": ["Tesla Solar Roof", "First Solar Panels", "SunPower Modules"],
            "challenge": "Managing panel temperature to maintain optimal electrical efficiency",
            "physics_focus": "Solar thermal effects, electrical-thermal coupling, efficiency optimization"
        }
        
        # Materials
        materials = {
            "solar_cell": Material(
                name="Silicon Solar Cell",
                material_type="semiconductor",
                density=2330.0,
                thermal_conductivity=148.0,  # Silicon
                specific_heat=700.0
            ),
            "glass_cover": Material(
                name="Solar Glass",
                material_type="glass",
                density=2500.0,
                thermal_conductivity=1.0,
                specific_heat=840.0
            ),
            "aluminum_frame": MaterialTemplates.aluminum(),
            "backsheet": Material(
                name="Polymer Backsheet",
                material_type="polymer",
                density=1200.0,
                thermal_conductivity=0.2,
                specific_heat=1500.0
            )
        }
        
        # Geometry
        solar_panel = GeometryUtils.create_cube("solar_panel", size=1.6)  # 1.6m x 1.6m panel
        solar_panel.scale(np.array([1.0, 1.0, 0.01]))  # Thin panel
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="solar_panel_bc",
            physics_type=PhysicsType.THERMAL
        )
        
        # Solar radiation absorption (1000 W/m² typical)
        solar_radiation = BoundaryConditionTemplates.thermal_heat_source(heat_flux=1000.0)
        solar_radiation.geometry_entities = ["solar_panel"]
        boundary_conditions.add_condition(solar_radiation)
        
        # Ambient convection
        ambient_convection = BoundaryConditionTemplates.thermal_convection(
            ambient_temp=25.0, h_coeff=15.0  # Wind-dependent
        )
        ambient_convection.geometry_entities = ["solar_panel"]
        boundary_conditions.add_condition(ambient_convection)
        
        # Radiative cooling to sky
        sky_radiation = BoundaryConditionTemplates.thermal_radiation(
            emissivity=0.9, sky_temp=10.0
        )
        sky_radiation.geometry_entities = ["solar_panel"]
        boundary_conditions.add_condition(sky_radiation)
        
        use_case.update({
            "materials": materials,
            "geometry": {"solar_panel": solar_panel},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "panel_temp": "45-75°C",
                "efficiency_degradation": "0.3-0.5%/°C",
                "thermal_efficiency": "15-20%",
                "electrical_efficiency": "15-22%"
            },
            "optimization_targets": [
                "Minimize temperature rise",
                "Maximize electrical efficiency",
                "Optimize thermal management",
                "Improve heat dissipation"
            ]
        })
        
        return use_case
    
    @staticmethod
    def aerospace_thermal_protection() -> Dict[str, Any]:
        """
        Aerospace Thermal Protection - Critical for spacecraft and re-entry vehicles
        
        This represents the thermal protection systems used in spacecraft,
        satellites, and re-entry vehicles.
        """
        use_case = {
            "name": "Aerospace Thermal Protection System",
            "description": "Thermal analysis of spacecraft thermal protection and heat shield systems",
            "industry": "Aerospace",
            "famous_examples": ["Space Shuttle TPS", "Dragon Capsule", "Mars Perseverance"],
            "challenge": "Protecting spacecraft from extreme temperatures during re-entry and space operations",
            "physics_focus": "High-temperature materials, ablation, thermal insulation"
        }
        
        # Materials
        materials = {
            "heat_shield": Material(
                name="Carbon-Carbon Composite",
                material_type="composite",
                density=1500.0,
                thermal_conductivity=50.0,
                specific_heat=800.0,
                emissivity=0.8
            ),
            "thermal_insulation": Material(
                name="Aerogel Insulation",
                material_type="insulation",
                density=100.0,
                thermal_conductivity=0.02,  # Very low thermal conductivity
                specific_heat=1000.0
            ),
            "aluminum_structure": MaterialTemplates.aluminum()
        }
        
        # Geometry
        heat_shield = GeometryUtils.create_sphere("heat_shield", radius=2.0)  # 2m radius heat shield
        spacecraft_body = GeometryUtils.create_cylinder("spacecraft", radius=1.5, height=3.0)
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="aerospace_tps_bc",
            physics_type=PhysicsType.THERMAL
        )
        
        # Re-entry heating (extreme conditions)
        reentry_heating = BoundaryConditionTemplates.thermal_heat_source(heat_flux=1e6)  # 1 MW/m²
        reentry_heating.geometry_entities = ["heat_shield"]
        boundary_conditions.add_condition(reentry_heating)
        
        # Space environment (cold)
        space_cooling = BoundaryConditionTemplates.thermal_radiation(
            emissivity=0.8, sky_temp=3.0  # Deep space temperature
        )
        space_cooling.geometry_entities = ["spacecraft_body"]
        boundary_conditions.add_condition(space_cooling)
        
        # Internal heat sources
        internal_heat = BoundaryConditionTemplates.thermal_heat_source(heat_flux=1000.0)  # Internal systems
        internal_heat.geometry_entities = ["spacecraft_body"]
        boundary_conditions.add_condition(internal_heat)
        
        use_case.update({
            "materials": materials,
            "geometry": {"heat_shield": heat_shield, "spacecraft": spacecraft_body},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "max_surface_temp": "1500-2000°C",
                "internal_temp": "20-25°C",
                "thermal_protection": "99.9% effective",
                "mass_efficiency": "High strength-to-weight ratio"
            },
            "optimization_targets": [
                "Minimize heat shield mass",
                "Maximize thermal protection",
                "Ensure structural integrity",
                "Optimize for multiple re-entries"
            ]
        })
        
        return use_case
    
    @classmethod
    def get_all_use_cases(cls) -> List[Dict[str, Any]]:
        """Get all thermal analysis use cases"""
        return [
            cls.cpu_cooling_analysis(),
            cls.electric_vehicle_battery_thermal_management(),
            cls.data_center_cooling(),
            cls.solar_panel_thermal_analysis(),
            cls.aerospace_thermal_protection()
        ]
    
    @classmethod
    def get_use_case_by_name(cls, name: str) -> Dict[str, Any]:
        """Get a specific use case by name"""
        use_cases = cls.get_all_use_cases()
        for use_case in use_cases:
            if use_case["name"].lower() == name.lower():
                return use_case
        raise ValueError(f"Use case '{name}' not found")