"""
Industrial Applications Use Cases

This module contains famous real-world industrial applications use cases including:
- Manufacturing processes
- Chemical processing
- Oil and gas applications
- Power generation
- Mining and materials processing
"""

import numpy as np
from typing import Dict, Any, List
from ..core import Material, Geometry, BoundaryConditions
from ..core.material import MaterialTemplates
from ..core.geometry import GeometryUtils
from ..core.constraints import BoundaryConditionTemplates, PhysicsType, BoundaryType

class IndustrialUseCases:
    """Collection of famous industrial applications use cases"""
    
    @staticmethod
    def additive_manufacturing() -> Dict[str, Any]:
        """
        Additive Manufacturing (3D Printing) - Revolutionary manufacturing technology
        
        This represents the physics modeling of additive manufacturing processes,
        essential for companies like 3D Systems, Stratasys, and industrial 3D printing.
        """
        use_case = {
            "name": "Additive Manufacturing Process Analysis",
            "description": "Multi-physics analysis of 3D printing processes including thermal, structural, and fluid effects",
            "industry": "Manufacturing",
            "famous_examples": ["3D Systems", "Stratasys", "EOS", "GE Additive"],
            "challenge": "Optimizing process parameters for quality, speed, and material properties",
            "physics_focus": "Thermal management, residual stress, material properties, process optimization"
        }
        
        # Materials
        materials = {
            "titanium_powder": Material(
                name="Titanium Alloy Powder",
                material_type="metal_powder",
                density=4500.0,
                thermal_conductivity=7.0,
                specific_heat=523.0,
                melting_point=1668.0
            ),
            "support_material": Material(
                name="Support Material",
                material_type="polymer",
                density=1200.0,
                thermal_conductivity=0.2,
                specific_heat=1500.0
            ),
            "build_plate": MaterialTemplates.steel()
        }
        
        # Geometry
        build_volume = GeometryUtils.create_cube("build_volume", size=0.3)  # 300mm build volume
        laser_spot = GeometryUtils.create_sphere("laser_spot", radius=0.001)  # 1mm laser spot
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="additive_manufacturing_bc",
            physics_type=PhysicsType.MULTI_PHYSICS
        )
        
        # Laser heat source
        laser_heat = BoundaryConditionTemplates.thermal_heat_source(heat_flux=1e9)  # 1 GW/m² laser power
        laser_heat.geometry_entities = ["laser_spot"]
        boundary_conditions.add_condition(laser_heat)
        
        # Build plate heating
        build_plate_heating = BoundaryConditionTemplates.thermal_fixed_temperature(temperature=200.0)  # 200°C
        build_plate_heating.geometry_entities = ["build_plate"]
        boundary_conditions.add_condition(build_plate_heating)
        
        # Ambient cooling
        ambient_cooling = BoundaryConditionTemplates.thermal_convection(
            ambient_temp=25.0, h_coeff=10.0
        )
        ambient_cooling.geometry_entities = ["build_volume"]
        boundary_conditions.add_condition(ambient_cooling)
        
        # Structural constraints
        structural_constraint = BoundaryConditionTemplates.structural_fixed_support()
        structural_constraint.geometry_entities = ["build_plate"]
        boundary_conditions.add_condition(structural_constraint)
        
        use_case.update({
            "materials": materials,
            "geometry": {"build_volume": build_volume, "laser_spot": laser_spot},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "max_temperature": "1500-2000°C",
                "cooling_rate": "100-1000°C/s",
                "residual_stress": "100-500 MPa",
                "build_speed": "10-100 mm³/s"
            },
            "optimization_targets": [
                "Minimize residual stress",
                "Maximize build speed",
                "Optimize material properties",
                "Reduce support material usage"
            ]
        })
        
        return use_case
    
    @staticmethod
    def chemical_reactor_design() -> Dict[str, Any]:
        """
        Chemical Reactor Design - Critical for chemical processing industry
        
        This represents the physics modeling of chemical reactors,
        essential for companies like BASF, Dow, and chemical processing plants.
        """
        use_case = {
            "name": "Chemical Reactor Design Analysis",
            "description": "Multi-physics analysis of chemical reactors including fluid flow, heat transfer, and reactions",
            "industry": "Chemical Processing",
            "famous_examples": ["BASF", "Dow Chemical", "DuPont", "ExxonMobil"],
            "challenge": "Optimizing reactor design for conversion efficiency, heat management, and safety",
            "physics_focus": "Fluid dynamics, heat transfer, chemical kinetics, mixing"
        }
        
        # Materials
        materials = {
            "reactant_fluid": Material(
                name="Reactant Fluid",
                material_type="fluid",
                density=800.0,
                viscosity=1e-3,
                thermal_conductivity=0.15,
                specific_heat=2000.0
            ),
            "catalyst": Material(
                name="Catalyst Material",
                material_type="catalyst",
                density=2000.0,
                thermal_conductivity=10.0,
                specific_heat=800.0
            ),
            "reactor_wall": MaterialTemplates.steel()
        }
        
        # Geometry
        reactor_vessel = GeometryUtils.create_cylinder("reactor_vessel", radius=1.0, height=5.0)
        catalyst_bed = GeometryUtils.create_cylinder("catalyst_bed", radius=0.8, height=3.0)
        catalyst_bed.translate(np.array([0, 0, 1.0]))
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="chemical_reactor_bc",
            physics_type=PhysicsType.MULTI_PHYSICS
        )
        
        # Fluid inlet
        fluid_inlet = BoundaryConditionTemplates.fluid_inlet_velocity(velocity=0.1)  # 0.1 m/s flow
        fluid_inlet.geometry_entities = ["reactor_inlet"]
        boundary_conditions.add_condition(fluid_inlet)
        
        # Temperature inlet
        temperature_inlet = BoundaryConditionTemplates.fluid_inlet_temperature(temperature=300.0)  # 300°C
        temperature_inlet.geometry_entities = ["reactor_inlet"]
        boundary_conditions.add_condition(temperature_inlet)
        
        # Chemical reaction
        chemical_reaction = BoundaryConditionTemplates.chemical_reaction(
            reaction_rate=1e-3,  # mol/(m³·s)
            activation_energy=50000.0  # J/mol
        )
        chemical_reaction.geometry_entities = ["catalyst_bed"]
        boundary_conditions.add_condition(chemical_reaction)
        
        # Heat transfer
        heat_transfer = BoundaryConditionTemplates.thermal_convection(
            ambient_temp=25.0, h_coeff=50.0
        )
        heat_transfer.geometry_entities = ["reactor_wall"]
        boundary_conditions.add_condition(heat_transfer)
        
        use_case.update({
            "materials": materials,
            "geometry": {"reactor_vessel": reactor_vessel, "catalyst_bed": catalyst_bed},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "conversion_efficiency": "80-95%",
                "temperature_rise": "50-200°C",
                "pressure_drop": "10-100 kPa",
                "residence_time": "10-1000 s"
            },
            "optimization_targets": [
                "Maximize conversion efficiency",
                "Optimize heat management",
                "Minimize pressure drop",
                "Ensure safety margins"
            ]
        })
        
        return use_case
    
    @staticmethod
    def oil_gas_pipeline() -> Dict[str, Any]:
        """
        Oil & Gas Pipeline - Critical for energy transportation
        
        This represents the physics modeling of oil and gas pipelines,
        essential for companies like TransCanada, Kinder Morgan, and energy transportation.
        """
        use_case = {
            "name": "Oil & Gas Pipeline Analysis",
            "description": "Multi-physics analysis of pipeline systems including fluid flow, thermal effects, and structural integrity",
            "industry": "Oil & Gas",
            "famous_examples": ["TransCanada", "Kinder Morgan", "Enbridge", "Keystone XL"],
            "challenge": "Ensuring safe and efficient transportation of hydrocarbons over long distances",
            "physics_focus": "Fluid dynamics, thermal management, structural integrity, corrosion"
        }
        
        # Materials
        materials = {
            "crude_oil": Material(
                name="Crude Oil",
                material_type="fluid",
                density=850.0,
                viscosity=5e-3,
                thermal_conductivity=0.15,
                specific_heat=2000.0
            ),
            "natural_gas": Material(
                name="Natural Gas",
                material_type="fluid",
                density=0.7,
                viscosity=1e-5,
                thermal_conductivity=0.03,
                specific_heat=2000.0
            ),
            "pipeline_steel": MaterialTemplates.steel()
        }
        
        # Geometry
        pipeline = GeometryUtils.create_cylinder("pipeline", radius=0.3, height=1000.0)  # 1km pipeline
        pipeline_wall = GeometryUtils.create_cylinder("pipeline_wall", radius=0.3, height=1000.0)
        pipeline_wall.scale(np.array([1.0, 1.0, 0.01]))  # Thin wall
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="pipeline_bc",
            physics_type=PhysicsType.MULTI_PHYSICS
        )
        
        # Fluid inlet (pump station)
        fluid_inlet = BoundaryConditionTemplates.fluid_inlet_velocity(velocity=2.0)  # 2 m/s flow
        fluid_inlet.geometry_entities = ["pipeline_inlet"]
        boundary_conditions.add_condition(fluid_inlet)
        
        # Pressure outlet
        pressure_outlet = BoundaryConditionTemplates.fluid_outlet_pressure(pressure=5e6)  # 5 MPa
        pressure_outlet.geometry_entities = ["pipeline_outlet"]
        boundary_conditions.add_condition(pressure_outlet)
        
        # Ground temperature
        ground_temperature = BoundaryConditionTemplates.thermal_fixed_temperature(temperature=10.0)  # 10°C
        ground_temperature.geometry_entities = ["ground_contact"]
        boundary_conditions.add_condition(ground_temperature)
        
        # Structural support
        structural_support = BoundaryConditionTemplates.structural_fixed_support()
        structural_support.geometry_entities = ["pipeline_supports"]
        boundary_conditions.add_condition(structural_support)
        
        use_case.update({
            "materials": materials,
            "geometry": {"pipeline": pipeline, "pipeline_wall": pipeline_wall},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "flow_rate": "1000-10000 m³/day",
                "pressure_drop": "1-10 MPa",
                "temperature_change": "±20°C",
                "pipeline_stress": "50-200 MPa"
            },
            "optimization_targets": [
                "Maximize flow capacity",
                "Minimize pressure drop",
                "Ensure structural integrity",
                "Prevent corrosion and leaks"
            ]
        })
        
        return use_case
    
    @staticmethod
    def power_plant_thermal_cycle() -> Dict[str, Any]:
        """
        Power Plant Thermal Cycle - Critical for electricity generation
        
        This represents the physics modeling of power plant thermal cycles,
        essential for companies like GE, Siemens, and power generation facilities.
        """
        use_case = {
            "name": "Power Plant Thermal Cycle Analysis",
            "description": "Multi-physics analysis of power plant thermal cycles including steam generation, expansion, and condensation",
            "industry": "Power Generation",
            "famous_examples": ["GE Power", "Siemens Energy", "Westinghouse", "Nuclear Power Plants"],
            "challenge": "Optimizing thermal efficiency while ensuring safety and reliability",
            "physics_focus": "Thermodynamics, heat transfer, fluid dynamics, structural integrity"
        }
        
        # Materials
        materials = {
            "steam": Material(
                name="Steam",
                material_type="fluid",
                density=10.0,  # Superheated steam
                viscosity=2e-5,
                thermal_conductivity=0.05,
                specific_heat=2000.0
            ),
            "water": MaterialTemplates.water(),
            "steel_turbine": MaterialTemplates.steel(),
            "concrete_foundation": Material(
                name="Concrete",
                material_type="concrete",
                density=2400.0,
                thermal_conductivity=1.4,
                specific_heat=880.0
            )
        }
        
        # Geometry
        boiler = GeometryUtils.create_cube("boiler", size=10.0)
        turbine = GeometryUtils.create_cylinder("turbine", radius=2.0, height=8.0)
        turbine.translate(np.array([0, 0, 5.0]))
        condenser = GeometryUtils.create_cube("condenser", size=8.0)
        condenser.translate(np.array([0, 0, 15.0]))
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="power_plant_bc",
            physics_type=PhysicsType.MULTI_PHYSICS
        )
        
        # Heat input (combustion or nuclear)
        heat_input = BoundaryConditionTemplates.thermal_heat_source(heat_flux=1e6)  # 1 MW/m²
        heat_input.geometry_entities = ["boiler"]
        boundary_conditions.add_condition(heat_input)
        
        # Steam flow
        steam_flow = BoundaryConditionTemplates.fluid_inlet_velocity(velocity=100.0)  # 100 m/s steam
        steam_flow.geometry_entities = ["turbine_inlet"]
        boundary_conditions.add_condition(steam_flow)
        
        # Condenser cooling
        condenser_cooling = BoundaryConditionTemplates.thermal_convection(
            ambient_temp=15.0, h_coeff=1000.0  # Water cooling
        )
        condenser_cooling.geometry_entities = ["condenser"]
        boundary_conditions.add_condition(condenser_cooling)
        
        # Structural support
        structural_support = BoundaryConditionTemplates.structural_fixed_support()
        structural_support.geometry_entities = ["foundation"]
        boundary_conditions.add_condition(structural_support)
        
        use_case.update({
            "materials": materials,
            "geometry": {"boiler": boiler, "turbine": turbine, "condenser": condenser},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "thermal_efficiency": "30-45%",
                "power_output": "100-1000 MW",
                "steam_temperature": "500-600°C",
                "steam_pressure": "10-25 MPa"
            },
            "optimization_targets": [
                "Maximize thermal efficiency",
                "Minimize fuel consumption",
                "Ensure operational safety",
                "Optimize maintenance cycles"
            ]
        })
        
        return use_case
    
    @staticmethod
    def mining_processing_plant() -> Dict[str, Any]:
        """
        Mining Processing Plant - Critical for mineral extraction and processing
        
        This represents the physics modeling of mining processing plants,
        essential for companies like BHP, Rio Tinto, and mineral processing operations.
        """
        use_case = {
            "name": "Mining Processing Plant Analysis",
            "description": "Multi-physics analysis of mineral processing including crushing, grinding, and separation",
            "industry": "Mining & Materials",
            "famous_examples": ["BHP", "Rio Tinto", "Vale", "Freeport-McMoRan"],
            "challenge": "Optimizing processing efficiency while minimizing energy consumption and environmental impact",
            "physics_focus": "Particle dynamics, fluid-solid interaction, heat transfer, mechanical wear"
        }
        
        # Materials
        materials = {
            "ore_particles": Material(
                name="Ore Particles",
                material_type="solid_particles",
                density=3000.0,
                thermal_conductivity=3.0,
                specific_heat=800.0
            ),
            "water_slurry": Material(
                name="Water Slurry",
                material_type="fluid",
                density=1200.0,
                viscosity=5e-3,
                thermal_conductivity=0.6
            ),
            "steel_equipment": MaterialTemplates.steel()
        }
        
        # Geometry
        crusher = GeometryUtils.create_cylinder("crusher", radius=1.0, height=3.0)
        ball_mill = GeometryUtils.create_cylinder("ball_mill", radius=2.0, height=4.0)
        ball_mill.translate(np.array([0, 0, 4.0]))
        separator = GeometryUtils.create_cube("separator", size=5.0)
        separator.translate(np.array([0, 0, 10.0]))
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="mining_processing_bc",
            physics_type=PhysicsType.MULTI_PHYSICS
        )
        
        # Ore feed
        ore_feed = BoundaryConditionTemplates.fluid_solid_inlet(
            velocity=1.0,  # 1 m/s
            particle_concentration=0.3  # 30% solids
        )
        ore_feed.geometry_entities = ["crusher_inlet"]
        boundary_conditions.add_condition(ore_feed)
        
        # Mechanical crushing
        crushing_force = BoundaryConditionTemplates.structural_force_load(force=1e6)  # 1 MN
        crushing_force.geometry_entities = ["crusher_jaws"]
        boundary_conditions.add_condition(crushing_force)
        
        # Ball mill rotation
        mill_rotation = BoundaryConditionTemplates.structural_rotational_load(
            angular_velocity=10.0  # 10 rad/s
        )
        mill_rotation.geometry_entities = ["ball_mill"]
        boundary_conditions.add_condition(mill_rotation)
        
        # Heat generation
        heat_generation = BoundaryConditionTemplates.thermal_heat_source(heat_flux=10000.0)  # 10 kW/m²
        heat_generation.geometry_entities = ["grinding_media"]
        boundary_conditions.add_condition(heat_generation)
        
        use_case.update({
            "materials": materials,
            "geometry": {"crusher": crusher, "ball_mill": ball_mill, "separator": separator},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "processing_capacity": "1000-10000 t/day",
                "particle_size_reduction": "90-99%",
                "energy_consumption": "10-50 kWh/t",
                "recovery_rate": "80-95%"
            },
            "optimization_targets": [
                "Maximize processing capacity",
                "Minimize energy consumption",
                "Optimize particle size distribution",
                "Maximize mineral recovery"
            ]
        })
        
        return use_case
    
    @staticmethod
    def hydrogen_economy() -> Dict[str, Any]:
        """
        Hydrogen Economy - Critical for Germany's energy transition
        
        This represents the physics modeling of hydrogen production, storage, and distribution systems,
        essential for Germany's National Hydrogen Strategy and companies like Siemens Energy, 
        Linde, and hydrogen infrastructure development.
        """
        use_case = {
            "name": "Hydrogen Economy Infrastructure Analysis",
            "description": "Multi-physics analysis of hydrogen production (electrolysis), storage, and distribution systems",
            "industry": "Energy & Infrastructure",
            "famous_examples": ["Siemens Energy", "Linde", "Air Liquide", "German National Hydrogen Strategy"],
            "challenge": "Optimizing hydrogen infrastructure for efficiency, safety, and cost-effectiveness in Germany's energy transition",
            "physics_focus": "Electrochemistry, fluid dynamics, thermal management, structural integrity, safety"
        }
        
        # Materials
        materials = {
            "hydrogen_gas": Material(
                name="Hydrogen Gas",
                material_type="gas",
                density=0.08988,  # kg/m³ at STP
                viscosity=8.9e-6,
                thermal_conductivity=0.18,
                specific_heat=14300.0,
                molecular_weight=2.016
            ),
            "oxygen_gas": Material(
                name="Oxygen Gas",
                material_type="gas",
                density=1.429,  # kg/m³ at STP
                viscosity=2.0e-5,
                thermal_conductivity=0.026,
                specific_heat=920.0
            ),
            "water": MaterialTemplates.water(),
            "electrolyte": Material(
                name="Alkaline Electrolyte",
                material_type="liquid",
                density=1200.0,
                viscosity=1e-3,
                thermal_conductivity=0.6,
                specific_heat=4200.0,
                electrical_conductivity=100.0  # S/m
            ),
            "pem_membrane": Material(
                name="PEM Membrane",
                material_type="polymer",
                density=2000.0,
                thermal_conductivity=0.2,
                specific_heat=1500.0,
                electrical_conductivity=10.0  # S/m for proton conduction
            ),
            "hydrogen_storage_tank": Material(
                name="Composite Hydrogen Tank",
                material_type="composite",
                density=1800.0,
                thermal_conductivity=0.5,
                specific_heat=1000.0,
                tensile_strength=800e6,  # 800 MPa
                max_pressure=70e6  # 70 MPa
            ),
            "pipeline_steel": MaterialTemplates.steel()
        }
        
        # Geometry
        electrolyzer = GeometryUtils.create_cube("electrolyzer", size=2.0)
        hydrogen_storage = GeometryUtils.create_cylinder("hydrogen_storage", radius=1.5, height=6.0)
        hydrogen_storage.translate(np.array([0, 0, 4.0]))
        distribution_pipeline = GeometryUtils.create_cylinder("distribution_pipeline", radius=0.2, height=100.0)
        distribution_pipeline.translate(np.array([0, 0, 10.0]))
        pem_stack = GeometryUtils.create_cube("pem_stack", size=1.5)
        pem_stack.translate(np.array([3.0, 0, 0]))
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="hydrogen_economy_bc",
            physics_type=PhysicsType.MULTI_PHYSICS
        )
        
        # Electrolysis electrical input
        electrolysis_current = BoundaryConditionTemplates.electrical_current_density(
            current_density=2000.0  # 2000 A/m²
        )
        electrolysis_current.geometry_entities = ["electrolyzer_electrodes"]
        boundary_conditions.add_condition(electrolysis_current)
        
        # Water feed
        water_feed = BoundaryConditionTemplates.fluid_inlet_velocity(velocity=0.01)  # 0.01 m/s
        water_feed.geometry_entities = ["electrolyzer_inlet"]
        boundary_conditions.add_condition(water_feed)
        
        # Hydrogen production reaction
        hydrogen_reaction = BoundaryConditionTemplates.electrochemical_reaction(
            reaction_rate=1e-3,  # mol/(m²·s)
            faradaic_efficiency=0.95,  # 95% efficiency
            cell_voltage=1.8  # V
        )
        hydrogen_reaction.geometry_entities = ["electrolyzer"]
        boundary_conditions.add_condition(hydrogen_reaction)
        
        # Hydrogen compression and storage
        hydrogen_compression = BoundaryConditionTemplates.fluid_pressure_load(pressure=70e6)  # 70 MPa
        hydrogen_compression.geometry_entities = ["hydrogen_storage"]
        boundary_conditions.add_condition(hydrogen_compression)
        
        # Thermal management
        thermal_cooling = BoundaryConditionTemplates.thermal_convection(
            ambient_temp=25.0, h_coeff=50.0
        )
        thermal_cooling.geometry_entities = ["electrolyzer", "hydrogen_storage"]
        boundary_conditions.add_condition(thermal_cooling)
        
        # Hydrogen distribution flow
        distribution_flow = BoundaryConditionTemplates.fluid_inlet_velocity(velocity=5.0)  # 5 m/s
        distribution_flow.geometry_entities = ["distribution_pipeline_inlet"]
        boundary_conditions.add_condition(distribution_flow)
        
        # Structural support for infrastructure
        structural_support = BoundaryConditionTemplates.structural_fixed_support()
        structural_support.geometry_entities = ["foundation", "pipeline_supports"]
        boundary_conditions.add_condition(structural_support)
        
        # Safety monitoring (hydrogen leak detection)
        safety_monitoring = BoundaryConditionTemplates.sensor_monitoring(
            sensor_type="hydrogen_concentration",
            threshold=4.0  # 4% hydrogen concentration (LEL)
        )
        safety_monitoring.geometry_entities = ["electrolyzer", "hydrogen_storage", "distribution_pipeline"]
        boundary_conditions.add_condition(safety_monitoring)
        
        use_case.update({
            "materials": materials,
            "geometry": {
                "electrolyzer": electrolyzer,
                "hydrogen_storage": hydrogen_storage,
                "distribution_pipeline": distribution_pipeline,
                "pem_stack": pem_stack
            },
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "hydrogen_production_rate": "100-1000 kg/day",
                "electrolysis_efficiency": "70-85%",
                "storage_pressure": "35-70 MPa",
                "distribution_flow_rate": "100-1000 m³/h",
                "system_efficiency": "60-75%",
                "safety_margin": ">10x LEL threshold"
            },
            "optimization_targets": [
                "Maximize hydrogen production efficiency",
                "Minimize energy consumption per kg H₂",
                "Optimize storage capacity and safety",
                "Reduce infrastructure costs",
                "Ensure grid integration compatibility",
                "Maximize renewable energy utilization"
            ],
            "german_context": {
                "national_strategy": "German National Hydrogen Strategy 2020",
                "target_2030": "5 GW electrolysis capacity",
                "target_2040": "10 GW electrolysis capacity",
                "key_regions": ["North Sea", "Ruhr Valley", "Bavaria"],
                "funding_programs": ["H2Giga", "H2Mare", "TransHyDE"],
                "industrial_partners": ["Siemens Energy", "Linde", "Air Liquide", "Thyssenkrupp"]
            }
        })
        
        return use_case
    
    @classmethod
    def get_all_use_cases(cls) -> List[Dict[str, Any]]:
        """Get all industrial applications use cases"""
        return [
            cls.additive_manufacturing(),
            cls.chemical_reactor_design(),
            cls.oil_gas_pipeline(),
            cls.power_plant_thermal_cycle(),
            cls.mining_processing_plant(),
            cls.hydrogen_economy()
        ]
    
    @classmethod
    def get_use_case_by_name(cls, name: str) -> Dict[str, Any]:
        """Get a specific use case by name"""
        use_cases = cls.get_all_use_cases()
        for use_case in use_cases:
            if use_case["name"].lower() == name.lower():
                return use_case
        raise ValueError(f"Use case '{name}' not found")