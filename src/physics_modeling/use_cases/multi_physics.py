"""
Multi-Physics Use Cases

This module contains famous real-world multi-physics use cases including:
- Fluid-structure interaction (FSI)
- Thermal-structural coupling
- Electromagnetic-thermal coupling
- Electrochemical systems
- Biomechanical systems
"""

import numpy as np
from typing import Dict, Any, List
from ..core import Material, Geometry, BoundaryConditions
from ..core.material import MaterialTemplates
from ..core.geometry import GeometryUtils
from ..core.constraints import BoundaryConditionTemplates, PhysicsType, BoundaryType

class MultiPhysicsUseCases:
    """Collection of famous multi-physics use cases"""
    
    @staticmethod
    def fluid_structure_interaction() -> Dict[str, Any]:
        """
        Fluid-Structure Interaction (FSI) - Critical for many engineering applications
        
        This represents the coupled analysis of fluid flow and structural deformation,
        essential for aircraft wings, heart valves, and many other applications.
        """
        use_case = {
            "name": "Fluid-Structure Interaction Analysis",
            "description": "Coupled analysis of fluid flow and structural deformation",
            "industry": "Multi-Industry",
            "famous_examples": ["Aircraft Wing Flutter", "Heart Valve Dynamics", "Wind Turbine Blades"],
            "challenge": "Accurately modeling the two-way coupling between fluid forces and structural response",
            "physics_focus": "Fluid-structure coupling, dynamic response, stability analysis"
        }
        
        # Materials
        materials = {
            "air": MaterialTemplates.air(),
            "flexible_membrane": Material(
                name="Flexible Membrane",
                material_type="polymer",
                density=1200.0,
                youngs_modulus=1e6,  # Flexible material
                poissons_ratio=0.4,
                yield_strength=10e6
            ),
            "rigid_support": MaterialTemplates.steel()
        }
        
        # Geometry
        fluid_domain = GeometryUtils.create_cube("fluid_domain", size=10.0)
        
        # Flexible structure (e.g., membrane or wing)
        flexible_structure = GeometryUtils.create_cube("flexible_structure", size=2.0)
        flexible_structure.scale(np.array([1.0, 0.1, 0.01]))  # Thin, flexible structure
        
        # Rigid support
        rigid_support = GeometryUtils.create_cube("rigid_support", size=0.5)
        rigid_support.translate(np.array([0, 0, -1.0]))
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="fsi_bc",
            physics_type=PhysicsType.MULTI_PHYSICS
        )
        
        # Fluid inlet
        fluid_inlet = BoundaryConditionTemplates.fluid_inlet_velocity(velocity=20.0)  # 20 m/s flow
        fluid_inlet.geometry_entities = ["fluid_inlet"]
        boundary_conditions.add_condition(fluid_inlet)
        
        # Fluid outlet
        fluid_outlet = BoundaryConditionTemplates.fluid_outlet_pressure(pressure=101325.0)
        fluid_outlet.geometry_entities = ["fluid_outlet"]
        boundary_conditions.add_condition(fluid_outlet)
        
        # Structural support
        structural_support = BoundaryConditionTemplates.structural_fixed_support()
        structural_support.geometry_entities = ["rigid_support"]
        boundary_conditions.add_condition(structural_support)
        
        # Interface coupling
        fsi_interface = BoundaryConditionTemplates.fsi_interface_condition()
        fsi_interface.geometry_entities = ["fluid_structure_interface"]
        boundary_conditions.add_condition(fsi_interface)
        
        use_case.update({
            "materials": materials,
            "geometry": {
                "fluid_domain": fluid_domain,
                "flexible_structure": flexible_structure,
                "rigid_support": rigid_support
            },
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "max_displacement": "1-10 mm",
                "natural_frequency": "5-50 Hz",
                "flutter_speed": "30-100 m/s",
                "coupling_strength": "Strong/Weak"
            },
            "optimization_targets": [
                "Prevent flutter instability",
                "Maximize energy efficiency",
                "Optimize structural response",
                "Ensure computational stability"
            ]
        })
        
        return use_case
    
    @staticmethod
    def thermal_structural_coupling() -> Dict[str, Any]:
        """
        Thermal-Structural Coupling - Critical for thermal expansion and stress analysis
        
        This represents the coupled analysis of thermal and structural effects,
        essential for electronic packaging, nuclear reactors, and many other applications.
        """
        use_case = {
            "name": "Thermal-Structural Coupling Analysis",
            "description": "Coupled analysis of thermal expansion and structural stress",
            "industry": "Multi-Industry",
            "famous_examples": ["Electronic Packaging", "Nuclear Reactor Components", "Aircraft Engines"],
            "challenge": "Modeling thermal expansion effects and resulting structural stresses",
            "physics_focus": "Thermal expansion, thermal stress, creep effects"
        }
        
        # Materials
        materials = {
            "silicon_chip": Material(
                name="Silicon Chip",
                material_type="semiconductor",
                density=2330.0,
                youngs_modulus=130e9,
                poissons_ratio=0.28,
                thermal_expansion_coefficient=2.6e-6,
                thermal_conductivity=148.0
            ),
            "copper_heat_sink": Material(
                name="Copper Heat Sink",
                material_type="metal",
                density=8960.0,
                youngs_modulus=110e9,
                poissons_ratio=0.34,
                thermal_expansion_coefficient=17e-6,
                thermal_conductivity=400.0
            ),
            "thermal_interface": Material(
                name="Thermal Interface Material",
                material_type="thermal_interface",
                density=2000.0,
                youngs_modulus=1e6,
                poissons_ratio=0.4,
                thermal_conductivity=5.0
            )
        }
        
        # Geometry
        silicon_chip = GeometryUtils.create_cube("silicon_chip", size=0.02)  # 20mm chip
        heat_sink = GeometryUtils.create_cube("heat_sink", size=0.05)  # 50mm heat sink
        heat_sink.translate(np.array([0, 0, 0.01]))  # Position above chip
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="thermal_structural_bc",
            physics_type=PhysicsType.MULTI_PHYSICS
        )
        
        # Heat generation in chip
        heat_generation = BoundaryConditionTemplates.thermal_heat_source(heat_flux=1e6)  # 1 MW/m²
        heat_generation.geometry_entities = ["silicon_chip"]
        boundary_conditions.add_condition(heat_generation)
        
        # Heat sink convection
        heat_sink_convection = BoundaryConditionTemplates.thermal_convection(
            ambient_temp=25.0, h_coeff=100.0  # Forced convection
        )
        heat_sink_convection.geometry_entities = ["heat_sink"]
        boundary_conditions.add_condition(heat_sink_convection)
        
        # Structural constraints
        structural_constraint = BoundaryConditionTemplates.structural_fixed_support()
        structural_constraint.geometry_entities = ["heat_sink_base"]
        boundary_conditions.add_condition(structural_constraint)
        
        # Thermal-structural coupling
        thermal_structural_coupling = BoundaryConditionTemplates.thermal_structural_coupling()
        thermal_structural_coupling.geometry_entities = ["all_materials"]
        boundary_conditions.add_condition(thermal_structural_coupling)
        
        use_case.update({
            "materials": materials,
            "geometry": {"silicon_chip": silicon_chip, "heat_sink": heat_sink},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "max_temperature": "80-120°C",
                "thermal_stress": "50-200 MPa",
                "thermal_displacement": "1-10 μm",
                "fatigue_life": "10,000+ cycles"
            },
            "optimization_targets": [
                "Minimize thermal resistance",
                "Reduce thermal stress",
                "Optimize material selection",
                "Ensure reliability"
            ]
        })
        
        return use_case
    
    @staticmethod
    def electromagnetic_thermal_coupling() -> Dict[str, Any]:
        """
        Electromagnetic-Thermal Coupling - Critical for electrical systems
        
        This represents the coupled analysis of electromagnetic and thermal effects,
        essential for electric motors, transformers, and power electronics.
        """
        use_case = {
            "name": "Electromagnetic-Thermal Coupling Analysis",
            "description": "Coupled analysis of electromagnetic losses and thermal effects",
            "industry": "Electrical Engineering",
            "famous_examples": ["Electric Motors", "Transformers", "Power Electronics"],
            "challenge": "Modeling joule heating and its effects on electrical performance",
            "physics_focus": "Joule heating, temperature-dependent resistivity, thermal management"
        }
        
        # Materials
        materials = {
            "copper_winding": Material(
                name="Copper Winding",
                material_type="metal",
                density=8960.0,
                electrical_conductivity=58e6,
                thermal_conductivity=400.0,
                thermal_expansion_coefficient=17e-6
            ),
            "iron_core": Material(
                name="Electrical Steel",
                material_type="steel",
                density=7850.0,
                electrical_conductivity=2e6,
                thermal_conductivity=50.0,
                relative_permeability=1000.0
            ),
            "insulation": Material(
                name="Electrical Insulation",
                material_type="polymer",
                density=1200.0,
                electrical_conductivity=1e-12,
                thermal_conductivity=0.2
            )
        }
        
        # Geometry (simplified transformer)
        core = GeometryUtils.create_cube("iron_core", size=0.2)  # 200mm core
        winding = GeometryUtils.create_cylinder("copper_winding", radius=0.05, height=0.15)
        winding.translate(np.array([0, 0, 0.025]))
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="electromagnetic_thermal_bc",
            physics_type=PhysicsType.MULTI_PHYSICS
        )
        
        # Electrical current
        electrical_current = BoundaryConditionTemplates.electromagnetic_current_density(
            current_density=1e6  # 1 MA/m²
        )
        electrical_current.geometry_entities = ["copper_winding"]
        boundary_conditions.add_condition(electrical_current)
        
        # Magnetic field
        magnetic_field = BoundaryConditionTemplates.electromagnetic_magnetic_field(
            magnetic_flux_density=1.5  # 1.5 Tesla
        )
        magnetic_field.geometry_entities = ["iron_core"]
        boundary_conditions.add_condition(magnetic_field)
        
        # Thermal convection
        thermal_convection = BoundaryConditionTemplates.thermal_convection(
            ambient_temp=25.0, h_coeff=20.0
        )
        thermal_convection.geometry_entities = ["external_surfaces"]
        boundary_conditions.add_condition(thermal_convection)
        
        # Electromagnetic-thermal coupling
        em_thermal_coupling = BoundaryConditionTemplates.electromagnetic_thermal_coupling()
        em_thermal_coupling.geometry_entities = ["copper_winding", "iron_core"]
        boundary_conditions.add_condition(em_thermal_coupling)
        
        use_case.update({
            "materials": materials,
            "geometry": {"core": core, "winding": winding},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "joule_losses": "100-1000 W",
                "max_temperature": "60-120°C",
                "efficiency": "95-99%",
                "thermal_resistance": "0.1-1.0°C/W"
            },
            "optimization_targets": [
                "Minimize electrical losses",
                "Maximize efficiency",
                "Optimize thermal management",
                "Ensure temperature limits"
            ]
        })
        
        return use_case
    
    @staticmethod
    def electrochemical_system() -> Dict[str, Any]:
        """
        Electrochemical System - Critical for batteries and fuel cells
        
        This represents the coupled analysis of electrochemical, thermal, and structural effects,
        essential for lithium-ion batteries, fuel cells, and electrolyzers.
        """
        use_case = {
            "name": "Electrochemical System Analysis",
            "description": "Coupled analysis of electrochemical, thermal, and structural effects",
            "industry": "Energy Storage",
            "famous_examples": ["Lithium-ion Batteries", "Fuel Cells", "Electrolyzers"],
            "challenge": "Modeling complex interactions between electrochemical reactions, heat generation, and structural changes",
            "physics_focus": "Electrochemical reactions, thermal management, structural evolution"
        }
        
        # Materials
        materials = {
            "lithium_ion": Material(
                name="Lithium-ion Electrode",
                material_type="battery",
                density=2300.0,
                electrical_conductivity=1e3,
                thermal_conductivity=1.0,
                specific_heat=1200.0
            ),
            "electrolyte": Material(
                name="Lithium Electrolyte",
                material_type="electrolyte",
                density=1200.0,
                electrical_conductivity=1e-3,
                thermal_conductivity=0.2,
                ionic_conductivity=1e-2
            ),
            "separator": Material(
                name="Battery Separator",
                material_type="polymer",
                density=1000.0,
                electrical_conductivity=1e-12,
                thermal_conductivity=0.1
            )
        }
        
        # Geometry (simplified battery cell)
        positive_electrode = GeometryUtils.create_cube("positive_electrode", size=0.1)
        negative_electrode = GeometryUtils.create_cube("negative_electrode", size=0.1)
        negative_electrode.translate(np.array([0, 0, 0.06]))
        separator = GeometryUtils.create_cube("separator", size=0.1)
        separator.scale(np.array([1.0, 1.0, 0.02]))  # Thin separator
        separator.translate(np.array([0, 0, 0.05]))
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="electrochemical_bc",
            physics_type=PhysicsType.MULTI_PHYSICS
        )
        
        # Electrical current
        electrical_current = BoundaryConditionTemplates.electrochemical_current_density(
            current_density=1000.0  # 1 kA/m²
        )
        electrical_current.geometry_entities = ["electrodes"]
        boundary_conditions.add_condition(electrical_current)
        
        # Electrochemical reactions
        electrochemical_reaction = BoundaryConditionTemplates.electrochemical_reaction(
            reaction_rate=1e-6  # mol/(m²·s)
        )
        electrochemical_reaction.geometry_entities = ["electrode_interfaces"]
        boundary_conditions.add_condition(electrochemical_reaction)
        
        # Heat generation
        heat_generation = BoundaryConditionTemplates.thermal_heat_source(heat_flux=1000.0)  # 1 kW/m²
        heat_generation.geometry_entities = ["electrodes"]
        boundary_conditions.add_condition(heat_generation)
        
        # Thermal convection
        thermal_convection = BoundaryConditionTemplates.thermal_convection(
            ambient_temp=25.0, h_coeff=10.0
        )
        thermal_convection.geometry_entities = ["external_surfaces"]
        boundary_conditions.add_condition(thermal_convection)
        
        use_case.update({
            "materials": materials,
            "geometry": {
                "positive_electrode": positive_electrode,
                "negative_electrode": negative_electrode,
                "separator": separator
            },
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "cell_voltage": "3.0-4.2 V",
                "capacity": "100-300 Ah",
                "max_temperature": "40-60°C",
                "efficiency": "85-95%"
            },
            "optimization_targets": [
                "Maximize energy density",
                "Minimize thermal runaway risk",
                "Optimize cycle life",
                "Ensure safety margins"
            ]
        })
        
        return use_case
    
    @staticmethod
    def biomechanical_system() -> Dict[str, Any]:
        """
        Biomechanical System - Critical for medical devices and implants
        
        This represents the coupled analysis of biological, mechanical, and fluid effects,
        essential for medical devices, implants, and tissue engineering.
        """
        use_case = {
            "name": "Biomechanical System Analysis",
            "description": "Coupled analysis of biological, mechanical, and fluid effects",
            "industry": "Medical Devices",
            "famous_examples": ["Heart Valves", "Hip Implants", "Stents"],
            "challenge": "Modeling complex interactions between biological tissues, mechanical loads, and fluid flow",
            "physics_focus": "Tissue mechanics, fluid-structure interaction, biological response"
        }
        
        # Materials
        materials = {
            "biological_tissue": Material(
                name="Biological Tissue",
                material_type="biological",
                density=1000.0,
                youngs_modulus=1e6,  # Soft tissue
                poissons_ratio=0.45,
                thermal_conductivity=0.5
            ),
            "blood": Material(
                name="Blood",
                material_type="fluid",
                density=1060.0,
                viscosity=3e-3,
                thermal_conductivity=0.5
            ),
            "implant_material": Material(
                name="Titanium Alloy",
                material_type="metal",
                density=4500.0,
                youngs_modulus=110e9,
                poissons_ratio=0.34,
                yield_strength=900e6
            )
        }
        
        # Geometry (simplified heart valve)
        valve_leaflet = GeometryUtils.create_cube("valve_leaflet", size=0.02)
        valve_leaflet.scale(np.array([1.0, 0.5, 0.001]))  # Thin, flexible leaflet
        
        blood_vessel = GeometryUtils.create_cylinder("blood_vessel", radius=0.01, height=0.1)
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="biomechanical_bc",
            physics_type=PhysicsType.MULTI_PHYSICS
        )
        
        # Blood flow
        blood_flow = BoundaryConditionTemplates.fluid_inlet_velocity(velocity=0.5)  # 0.5 m/s blood flow
        blood_flow.geometry_entities = ["blood_inlet"]
        boundary_conditions.add_condition(blood_flow)
        
        # Blood pressure
        blood_pressure = BoundaryConditionTemplates.fluid_pressure_load(pressure=12000.0)  # 12 kPa
        blood_pressure.geometry_entities = ["blood_vessel"]
        boundary_conditions.add_condition(blood_pressure)
        
        # Tissue constraints
        tissue_constraint = BoundaryConditionTemplates.structural_fixed_support()
        tissue_constraint.geometry_entities = ["tissue_attachment"]
        boundary_conditions.add_condition(tissue_constraint)
        
        # Fluid-structure interaction
        fsi_interface = BoundaryConditionTemplates.fsi_interface_condition()
        fsi_interface.geometry_entities = ["blood_tissue_interface"]
        boundary_conditions.add_condition(fsi_interface)
        
        use_case.update({
            "materials": materials,
            "geometry": {"valve_leaflet": valve_leaflet, "blood_vessel": blood_vessel},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "max_displacement": "1-5 mm",
                "blood_flow_rate": "5-10 L/min",
                "pressure_drop": "1-5 mmHg",
                "tissue_stress": "10-100 kPa"
            },
            "optimization_targets": [
                "Minimize pressure drop",
                "Maximize flow efficiency",
                "Ensure tissue compatibility",
                "Prevent mechanical failure"
            ]
        })
        
        return use_case
    
    @classmethod
    def get_all_use_cases(cls) -> List[Dict[str, Any]]:
        """Get all multi-physics use cases"""
        return [
            cls.fluid_structure_interaction(),
            cls.thermal_structural_coupling(),
            cls.electromagnetic_thermal_coupling(),
            cls.electrochemical_system(),
            cls.biomechanical_system()
        ]
    
    @classmethod
    def get_use_case_by_name(cls, name: str) -> Dict[str, Any]:
        """Get a specific use case by name"""
        use_cases = cls.get_all_use_cases()
        for use_case in use_cases:
            if use_case["name"].lower() == name.lower():
                return use_case
        raise ValueError(f"Use case '{name}' not found")