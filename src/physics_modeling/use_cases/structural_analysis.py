"""
Structural Analysis Use Cases

This module contains famous real-world structural analysis use cases including:
- Bridge and infrastructure design
- Aircraft and automotive structures
- Building and construction
- Wind turbine design
- Pressure vessel analysis
"""

import numpy as np
from typing import Dict, Any, List
from ..core import Material, Geometry, BoundaryConditions
from ..core.material import MaterialTemplates
from ..core.geometry import GeometryUtils
from ..core.constraints import BoundaryConditionTemplates, PhysicsType, BoundaryType

class StructuralAnalysisUseCases:
    """Collection of famous structural analysis use cases"""
    
    @staticmethod
    def suspension_bridge_analysis() -> Dict[str, Any]:
        """
        Suspension Bridge Analysis - Famous engineering marvels
        
        This represents the structural analysis of suspension bridges,
        similar to Golden Gate Bridge, Brooklyn Bridge, or modern cable-stayed bridges.
        """
        use_case = {
            "name": "Suspension Bridge Structural Analysis",
            "description": "Structural analysis of suspension bridge under various loading conditions",
            "industry": "Civil Engineering",
            "famous_examples": ["Golden Gate Bridge", "Brooklyn Bridge", "Akashi Kaikyō Bridge"],
            "challenge": "Designing long-span bridges to withstand wind, seismic, and traffic loads",
            "physics_focus": "Large-scale structural dynamics, wind loading, seismic response"
        }
        
        # Materials
        materials = {
            "steel_cable": Material(
                name="High-Strength Steel Cable",
                material_type="steel",
                density=7850.0,
                youngs_modulus=200e9,
                poissons_ratio=0.3,
                yield_strength=1800e6  # High-strength steel
            ),
            "concrete_deck": Material(
                name="Reinforced Concrete",
                material_type="concrete",
                density=2400.0,
                youngs_modulus=30e9,
                poissons_ratio=0.2,
                yield_strength=30e6
            ),
            "steel_tower": MaterialTemplates.steel()
        }
        
        # Geometry (simplified bridge)
        main_span = GeometryUtils.create_cube("main_span", size=1000.0)  # 1000m main span
        main_span.scale(np.array([1.0, 0.1, 0.02]))  # Thin deck
        
        # Cable geometry (simplified)
        cable = GeometryUtils.create_cylinder("main_cable", radius=0.5, height=1000.0)
        cable.translate(np.array([0, 0, 50.0]))  # 50m above deck
        
        # Tower geometry
        tower = GeometryUtils.create_cube("tower", size=200.0)  # 200m tower
        tower.scale(np.array([0.1, 0.1, 1.0]))  # Tall, thin tower
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="bridge_structural_bc",
            physics_type=PhysicsType.STRUCTURAL
        )
        
        # Dead load (self-weight)
        dead_load = BoundaryConditionTemplates.structural_gravity_load()
        dead_load.geometry_entities = ["main_span", "cable", "tower"]
        boundary_conditions.add_condition(dead_load)
        
        # Live load (traffic)
        live_load = BoundaryConditionTemplates.structural_uniform_load(pressure=5000.0)  # 5 kPa traffic
        live_load.geometry_entities = ["main_span"]
        boundary_conditions.add_condition(live_load)
        
        # Wind load
        wind_load = BoundaryConditionTemplates.structural_pressure_load(pressure=2000.0)  # 2 kPa wind
        wind_load.geometry_entities = ["main_span", "tower"]
        boundary_conditions.add_condition(wind_load)
        
        # Foundation support
        foundation_support = BoundaryConditionTemplates.structural_fixed_support()
        foundation_support.geometry_entities = ["tower_base"]
        boundary_conditions.add_condition(foundation_support)
        
        use_case.update({
            "materials": materials,
            "geometry": {"main_span": main_span, "cable": cable, "tower": tower},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "max_deflection": "2-5m at mid-span",
                "cable_tension": "50-100 MN",
                "tower_compression": "200-500 MN",
                "natural_frequency": "0.1-0.5 Hz"
            },
            "optimization_targets": [
                "Minimize deflection under load",
                "Maximize structural stability",
                "Optimize cable tension distribution",
                "Ensure aerodynamic stability"
            ]
        })
        
        return use_case
    
    @staticmethod
    def aircraft_wing_analysis() -> Dict[str, Any]:
        """
        Aircraft Wing Analysis - Critical for aviation safety
        
        This represents the structural analysis of aircraft wings,
        essential for Boeing, Airbus, and other aircraft manufacturers.
        """
        use_case = {
            "name": "Aircraft Wing Structural Analysis",
            "description": "Structural analysis of aircraft wing under aerodynamic and inertial loads",
            "industry": "Aerospace",
            "famous_examples": ["Boeing 787 Dreamliner", "Airbus A350", "F-35 Lightning II"],
            "challenge": "Designing lightweight, strong wings that can withstand extreme flight loads",
            "physics_focus": "Aerodynamic loading, fatigue analysis, composite materials"
        }
        
        # Materials
        materials = {
            "composite_skin": Material(
                name="Carbon Fiber Composite",
                material_type="composite",
                density=1600.0,
                youngs_modulus=70e9,  # Anisotropic in practice
                poissons_ratio=0.3,
                yield_strength=600e6
            ),
            "aluminum_spar": MaterialTemplates.aluminum(),
            "titanium_fasteners": Material(
                name="Titanium Alloy",
                material_type="metal",
                density=4500.0,
                youngs_modulus=110e9,
                poissons_ratio=0.34,
                yield_strength=900e6
            )
        }
        
        # Geometry (simplified wing)
        wing_span = 30.0  # 30m wing span
        wing_chord = 3.0   # 3m chord length
        
        # Create wing geometry (simplified as thin plate)
        wing = GeometryUtils.create_cube("wing", size=wing_span)
        wing.scale(np.array([1.0, wing_chord/wing_span, 0.01]))  # Thin wing
        
        # Spar geometry
        spar = GeometryUtils.create_cube("spar", size=wing_span)
        spar.scale(np.array([1.0, 0.1, 0.2]))  # Long, thin spar
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="aircraft_wing_bc",
            physics_type=PhysicsType.STRUCTURAL
        )
        
        # Aerodynamic lift (varies with flight conditions)
        lift_load = BoundaryConditionTemplates.structural_pressure_load(pressure=15000.0)  # 15 kPa lift
        lift_load.geometry_entities = ["wing"]
        boundary_conditions.add_condition(lift_load)
        
        # Inertial loads (maneuvering)
        inertial_load = BoundaryConditionTemplates.structural_acceleration_load(acceleration=3.0)  # 3g load
        inertial_load.geometry_entities = ["wing"]
        boundary_conditions.add_condition(inertial_load)
        
        # Fuselage attachment (fixed support)
        fuselage_support = BoundaryConditionTemplates.structural_fixed_support()
        fuselage_support.geometry_entities = ["wing_root"]
        boundary_conditions.add_condition(fuselage_support)
        
        # Fuel weight (distributed load)
        fuel_load = BoundaryConditionTemplates.structural_uniform_load(pressure=2000.0)  # 2 kPa fuel weight
        fuel_load.geometry_entities = ["wing"]
        boundary_conditions.add_condition(fuel_load)
        
        use_case.update({
            "materials": materials,
            "geometry": {"wing": wing, "spar": spar},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "wing_tip_deflection": "1-3m",
                "spar_stress": "200-400 MPa",
                "natural_frequency": "2-5 Hz",
                "fatigue_life": "50,000+ cycles"
            },
            "optimization_targets": [
                "Minimize weight while maintaining strength",
                "Maximize fatigue resistance",
                "Optimize aerodynamic efficiency",
                "Ensure damage tolerance"
            ]
        })
        
        return use_case
    
    @staticmethod
    def wind_turbine_blade_analysis() -> Dict[str, Any]:
        """
        Wind Turbine Blade Analysis - Critical for renewable energy
        
        This represents the structural analysis of wind turbine blades,
        essential for companies like Vestas, GE, and Siemens Gamesa.
        """
        use_case = {
            "name": "Wind Turbine Blade Structural Analysis",
            "description": "Structural analysis of wind turbine blade under aerodynamic and gravitational loads",
            "industry": "Renewable Energy",
            "famous_examples": ["Vestas V164", "GE Haliade-X", "Siemens Gamesa SG 14-222"],
            "challenge": "Designing long, lightweight blades that can withstand extreme wind conditions",
            "physics_focus": "Aerodynamic loading, fatigue, composite materials, large-scale structures"
        }
        
        # Materials
        materials = {
            "glass_fiber_composite": Material(
                name="Glass Fiber Reinforced Polymer",
                material_type="composite",
                density=1800.0,
                youngs_modulus=25e9,
                poissons_ratio=0.3,
                yield_strength=300e6
            ),
            "carbon_fiber_composite": Material(
                name="Carbon Fiber Reinforced Polymer",
                material_type="composite",
                density=1600.0,
                youngs_modulus=70e9,
                poissons_ratio=0.3,
                yield_strength=600e6
            ),
            "foam_core": Material(
                name="Structural Foam",
                material_type="foam",
                density=100.0,
                youngs_modulus=50e6,
                poissons_ratio=0.3
            )
        }
        
        # Geometry (simplified blade)
        blade_length = 80.0  # 80m blade length
        blade_chord = 5.0    # 5m max chord
        
        # Create blade geometry (simplified as tapered beam)
        blade = GeometryUtils.create_cube("blade", size=blade_length)
        blade.scale(np.array([1.0, blade_chord/blade_length, 0.1]))  # Tapered blade
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="wind_turbine_blade_bc",
            physics_type=PhysicsType.STRUCTURAL
        )
        
        # Aerodynamic loads (varies with wind speed)
        aerodynamic_load = BoundaryConditionTemplates.structural_pressure_load(pressure=8000.0)  # 8 kPa
        aerodynamic_load.geometry_entities = ["blade"]
        boundary_conditions.add_condition(aerodynamic_load)
        
        # Centrifugal loads (rotation)
        centrifugal_load = BoundaryConditionTemplates.structural_centrifugal_load(
            angular_velocity=1.0, radius=blade_length/2  # 1 rad/s, 40m radius
        )
        centrifugal_load.geometry_entities = ["blade"]
        boundary_conditions.add_condition(centrifugal_load)
        
        # Gravity loads
        gravity_load = BoundaryConditionTemplates.structural_gravity_load()
        gravity_load.geometry_entities = ["blade"]
        boundary_conditions.add_condition(gravity_load)
        
        # Hub connection (fixed support)
        hub_support = BoundaryConditionTemplates.structural_fixed_support()
        hub_support.geometry_entities = ["blade_root"]
        boundary_conditions.add_condition(hub_support)
        
        use_case.update({
            "materials": materials,
            "geometry": {"blade": blade},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "blade_tip_deflection": "5-15m",
                "root_bending_moment": "10-50 MN·m",
                "natural_frequency": "0.5-2 Hz",
                "fatigue_life": "20+ years"
            },
            "optimization_targets": [
                "Maximize energy capture efficiency",
                "Minimize weight and cost",
                "Ensure structural integrity",
                "Optimize for manufacturing"
            ]
        })
        
        return use_case
    
    @staticmethod
    def pressure_vessel_analysis() -> Dict[str, Any]:
        """
        Pressure Vessel Analysis - Critical for industrial safety
        
        This represents the structural analysis of pressure vessels,
        essential for chemical plants, oil refineries, and nuclear power.
        """
        use_case = {
            "name": "Pressure Vessel Structural Analysis",
            "description": "Structural analysis of pressure vessel under internal pressure and thermal loads",
            "industry": "Industrial Manufacturing",
            "famous_examples": ["Nuclear Reactor Vessels", "Chemical Storage Tanks", "Boiler Systems"],
            "challenge": "Designing vessels that can safely contain high-pressure fluids at elevated temperatures",
            "physics_focus": "Pressure loading, thermal stresses, fatigue, fracture mechanics"
        }
        
        # Materials
        materials = {
            "steel_vessel": MaterialTemplates.steel(),
            "stainless_steel": Material(
                name="Stainless Steel 316",
                material_type="steel",
                density=8000.0,
                youngs_modulus=193e9,
                poissons_ratio=0.3,
                yield_strength=250e6
            ),
            "carbon_steel": Material(
                name="Carbon Steel A516",
                material_type="steel",
                density=7850.0,
                youngs_modulus=200e9,
                poissons_ratio=0.3,
                yield_strength=250e6
            )
        }
        
        # Geometry
        vessel_radius = 2.0  # 2m radius
        vessel_height = 8.0  # 8m height
        wall_thickness = 0.05  # 50mm wall thickness
        
        # Create vessel geometry
        vessel = GeometryUtils.create_cylinder("pressure_vessel", radius=vessel_radius, height=vessel_height)
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="pressure_vessel_bc",
            physics_type=PhysicsType.STRUCTURAL
        )
        
        # Internal pressure
        internal_pressure = BoundaryConditionTemplates.structural_pressure_load(pressure=10e6)  # 10 MPa
        internal_pressure.geometry_entities = ["vessel_inner"]
        boundary_conditions.add_condition(internal_pressure)
        
        # Thermal loads (temperature difference)
        thermal_load = BoundaryConditionTemplates.structural_thermal_load(
            temperature_difference=200.0  # 200°C temperature difference
        )
        thermal_load.geometry_entities = ["vessel"]
        boundary_conditions.add_condition(thermal_load)
        
        # Support conditions (fixed base)
        base_support = BoundaryConditionTemplates.structural_fixed_support()
        base_support.geometry_entities = ["vessel_base"]
        boundary_conditions.add_condition(base_support)
        
        # External pressure (atmospheric)
        external_pressure = BoundaryConditionTemplates.structural_pressure_load(pressure=101325.0)  # 1 atm
        external_pressure.geometry_entities = ["vessel_outer"]
        boundary_conditions.add_condition(external_pressure)
        
        use_case.update({
            "materials": materials,
            "geometry": {"vessel": vessel},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "hoop_stress": "80-120 MPa",
                "longitudinal_stress": "40-60 MPa",
                "max_deflection": "1-5 mm",
                "safety_factor": "2-4"
            },
            "optimization_targets": [
                "Maximize pressure capacity",
                "Minimize material usage",
                "Ensure safety margins",
                "Optimize for manufacturing"
            ]
        })
        
        return use_case
    
    @staticmethod
    def automotive_chassis_analysis() -> Dict[str, Any]:
        """
        Automotive Chassis Analysis - Critical for vehicle safety and performance
        
        This represents the structural analysis of automotive chassis and body structures,
        essential for crash safety and vehicle performance.
        """
        use_case = {
            "name": "Automotive Chassis Structural Analysis",
            "description": "Structural analysis of automotive chassis under crash and normal loading conditions",
            "industry": "Automotive",
            "famous_examples": ["Tesla Model S", "BMW i3", "Volvo XC90"],
            "challenge": "Designing lightweight, strong chassis that provides excellent crash protection",
            "physics_focus": "Crash analysis, impact loading, energy absorption, lightweight design"
        }
        
        # Materials
        materials = {
            "high_strength_steel": Material(
                name="High Strength Steel",
                material_type="steel",
                density=7850.0,
                youngs_modulus=200e9,
                poissons_ratio=0.3,
                yield_strength=800e6
            ),
            "aluminum_chassis": MaterialTemplates.aluminum(),
            "carbon_fiber": Material(
                name="Carbon Fiber Composite",
                material_type="composite",
                density=1600.0,
                youngs_modulus=70e9,
                poissons_ratio=0.3,
                yield_strength=600e6
            )
        }
        
        # Geometry (simplified chassis)
        chassis_length = 4.5  # 4.5m vehicle length
        chassis_width = 1.8   # 1.8m vehicle width
        chassis_height = 1.4  # 1.4m vehicle height
        
        # Create chassis geometry
        chassis = GeometryUtils.create_cube("chassis", size=chassis_length)
        chassis.scale(np.array([1.0, chassis_width/chassis_length, chassis_height/chassis_length]))
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="automotive_chassis_bc",
            physics_type=PhysicsType.STRUCTURAL
        )
        
        # Crash impact load (frontal collision)
        crash_load = BoundaryConditionTemplates.structural_impact_load(
            velocity=15.0,  # 15 m/s impact velocity
            duration=0.1    # 100ms impact duration
        )
        crash_load.geometry_entities = ["front_crash_zone"]
        boundary_conditions.add_condition(crash_load)
        
        # Normal driving loads
        driving_load = BoundaryConditionTemplates.structural_gravity_load()
        driving_load.geometry_entities = ["chassis"]
        boundary_conditions.add_condition(driving_load)
        
        # Suspension loads
        suspension_load = BoundaryConditionTemplates.structural_point_load(force=5000.0)  # 5 kN per wheel
        suspension_load.geometry_entities = ["suspension_points"]
        boundary_conditions.add_condition(suspension_load)
        
        # Rollover protection
        rollover_load = BoundaryConditionTemplates.structural_pressure_load(pressure=50000.0)  # 50 kPa
        rollover_load.geometry_entities = ["roof_structure"]
        boundary_conditions.add_condition(rollover_load)
        
        use_case.update({
            "materials": materials,
            "geometry": {"chassis": chassis},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "crash_deformation": "200-500 mm",
                "energy_absorption": "50-100 kJ",
                "passenger_compartment_integrity": "Maintained",
                "weight": "300-800 kg"
            },
            "optimization_targets": [
                "Maximize crash safety",
                "Minimize vehicle weight",
                "Optimize energy absorption",
                "Ensure passenger protection"
            ]
        })
        
        return use_case
    
    @classmethod
    def get_all_use_cases(cls) -> List[Dict[str, Any]]:
        """Get all structural analysis use cases"""
        return [
            cls.suspension_bridge_analysis(),
            cls.aircraft_wing_analysis(),
            cls.wind_turbine_blade_analysis(),
            cls.pressure_vessel_analysis(),
            cls.automotive_chassis_analysis()
        ]
    
    @classmethod
    def get_use_case_by_name(cls, name: str) -> Dict[str, Any]:
        """Get a specific use case by name"""
        use_cases = cls.get_all_use_cases()
        for use_case in use_cases:
            if use_case["name"].lower() == name.lower():
                return use_case
        raise ValueError(f"Use case '{name}' not found")