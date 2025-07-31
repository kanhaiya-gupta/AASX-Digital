"""
Fluid Dynamics Use Cases

This module contains famous real-world fluid dynamics use cases including:
- Aircraft aerodynamics
- Automotive aerodynamics
- Marine hydrodynamics
- Wind turbine aerodynamics
- HVAC systems
"""

import numpy as np
from typing import Dict, Any, List
from ..core import Material, Geometry, BoundaryConditions
from ..core.material import MaterialTemplates
from ..core.geometry import GeometryUtils
from ..core.constraints import BoundaryConditionTemplates, PhysicsType, BoundaryType

class FluidDynamicsUseCases:
    """Collection of famous fluid dynamics use cases"""
    
    @staticmethod
    def aircraft_aerodynamics() -> Dict[str, Any]:
        """
        Aircraft Aerodynamics - Critical for aviation performance and efficiency
        
        This represents the aerodynamic analysis of aircraft,
        essential for Boeing, Airbus, and other aircraft manufacturers.
        """
        use_case = {
            "name": "Aircraft Aerodynamic Analysis",
            "description": "Computational fluid dynamics analysis of aircraft aerodynamics",
            "industry": "Aerospace",
            "famous_examples": ["Boeing 787 Dreamliner", "Airbus A350", "F-35 Lightning II"],
            "challenge": "Optimizing lift, drag, and stability across all flight regimes",
            "physics_focus": "Compressible flow, boundary layer effects, transonic aerodynamics"
        }
        
        # Materials (fluids)
        materials = {
            "air": MaterialTemplates.air(),
            "fuel": Material(
                name="Aviation Fuel",
                material_type="fluid",
                density=800.0,
                viscosity=2e-3,
                thermal_conductivity=0.15
            )
        }
        
        # Geometry (simplified aircraft)
        fuselage = GeometryUtils.create_cylinder("fuselage", radius=2.0, height=40.0)
        
        # Wing geometry (simplified)
        wing = GeometryUtils.create_cube("wing", size=30.0)
        wing.scale(np.array([1.0, 0.2, 0.01]))  # Thin wing
        wing.translate(np.array([0, 0, 0.5]))
        
        # Tail surfaces
        horizontal_tail = GeometryUtils.create_cube("horizontal_tail", size=8.0)
        horizontal_tail.scale(np.array([1.0, 0.15, 0.01]))
        horizontal_tail.translate(np.array([15, 0, 2.0]))
        
        vertical_tail = GeometryUtils.create_cube("vertical_tail", size=6.0)
        vertical_tail.scale(np.array([0.1, 1.0, 0.01]))
        vertical_tail.translate(np.array([15, 0, 1.0]))
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="aircraft_aero_bc",
            physics_type=PhysicsType.FLUID
        )
        
        # Free stream conditions (cruise)
        freestream = BoundaryConditionTemplates.fluid_inlet_velocity(velocity=250.0)  # 250 m/s cruise
        freestream.geometry_entities = ["inlet_boundary"]
        boundary_conditions.add_condition(freestream)
        
        # Outlet pressure
        outlet_pressure = BoundaryConditionTemplates.fluid_outlet_pressure(pressure=101325.0)  # 1 atm
        outlet_pressure.geometry_entities = ["outlet_boundary"]
        boundary_conditions.add_condition(outlet_pressure)
        
        # Wall boundary conditions (no-slip)
        wall_condition = BoundaryConditionTemplates.fluid_wall_condition()
        wall_condition.geometry_entities = ["aircraft_surface"]
        boundary_conditions.add_condition(wall_condition)
        
        # Symmetry plane
        symmetry = BoundaryConditionTemplates.fluid_symmetry_condition()
        symmetry.geometry_entities = ["symmetry_plane"]
        boundary_conditions.add_condition(symmetry)
        
        use_case.update({
            "materials": materials,
            "geometry": {
                "fuselage": fuselage,
                "wing": wing,
                "horizontal_tail": horizontal_tail,
                "vertical_tail": vertical_tail
            },
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "lift_coefficient": "0.3-0.6",
                "drag_coefficient": "0.02-0.04",
                "lift_to_drag_ratio": "15-25",
                "stall_angle": "12-18 degrees"
            },
            "optimization_targets": [
                "Maximize lift-to-drag ratio",
                "Minimize drag coefficient",
                "Optimize stability characteristics",
                "Ensure safe stall behavior"
            ]
        })
        
        return use_case
    
    @staticmethod
    def automotive_aerodynamics() -> Dict[str, Any]:
        """
        Automotive Aerodynamics - Critical for fuel efficiency and performance
        
        This represents the aerodynamic analysis of vehicles,
        essential for Tesla, BMW, Mercedes, and other automotive manufacturers.
        """
        use_case = {
            "name": "Automotive Aerodynamic Analysis",
            "description": "Computational fluid dynamics analysis of vehicle aerodynamics",
            "industry": "Automotive",
            "famous_examples": ["Tesla Model S", "BMW i8", "Mercedes EQS"],
            "challenge": "Balancing aerodynamic efficiency with design aesthetics and functionality",
            "physics_focus": "Ground effects, wake analysis, drag reduction"
        }
        
        # Materials
        materials = {
            "air": MaterialTemplates.air(),
            "road_surface": Material(
                name="Asphalt Road",
                material_type="solid",
                density=2300.0,
                thermal_conductivity=0.7
            )
        }
        
        # Geometry (simplified vehicle)
        vehicle_body = GeometryUtils.create_cube("vehicle_body", size=4.5)
        vehicle_body.scale(np.array([1.0, 0.4, 0.3]))  # Car proportions
        
        # Wheels
        wheels = []
        wheel_positions = [(-1.5, -0.8), (-1.5, 0.8), (1.5, -0.8), (1.5, 0.8)]
        for i, (x, y) in enumerate(wheel_positions):
            wheel = GeometryUtils.create_cylinder(f"wheel_{i}", radius=0.3, height=0.2)
            wheel.translate(np.array([x, y, 0.3]))
            wheels.append(wheel)
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="automotive_aero_bc",
            physics_type=PhysicsType.FLUID
        )
        
        # Free stream conditions (highway speed)
        freestream = BoundaryConditionTemplates.fluid_inlet_velocity(velocity=30.0)  # 30 m/s (108 km/h)
        freestream.geometry_entities = ["inlet_boundary"]
        boundary_conditions.add_condition(freestream)
        
        # Outlet pressure
        outlet_pressure = BoundaryConditionTemplates.fluid_outlet_pressure(pressure=101325.0)
        outlet_pressure.geometry_entities = ["outlet_boundary"]
        boundary_conditions.add_condition(outlet_pressure)
        
        # Ground plane (moving ground)
        ground_condition = BoundaryConditionTemplates.fluid_moving_wall(velocity=30.0)
        ground_condition.geometry_entities = ["ground_plane"]
        boundary_conditions.add_condition(ground_condition)
        
        # Vehicle surface (no-slip)
        vehicle_wall = BoundaryConditionTemplates.fluid_wall_condition()
        vehicle_wall.geometry_entities = ["vehicle_surface"]
        boundary_conditions.add_condition(vehicle_wall)
        
        use_case.update({
            "materials": materials,
            "geometry": {"vehicle_body": vehicle_body, "wheels": wheels},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "drag_coefficient": "0.25-0.35",
                "lift_coefficient": "-0.1 to 0.1",
                "downforce": "0-500 N",
                "wake_size": "2-4 vehicle lengths"
            },
            "optimization_targets": [
                "Minimize drag coefficient",
                "Optimize lift/downforce balance",
                "Reduce wake turbulence",
                "Improve cooling airflow"
            ]
        })
        
        return use_case
    
    @staticmethod
    def wind_turbine_aerodynamics() -> Dict[str, Any]:
        """
        Wind Turbine Aerodynamics - Critical for renewable energy efficiency
        
        This represents the aerodynamic analysis of wind turbine blades,
        essential for Vestas, GE, Siemens Gamesa, and other wind energy companies.
        """
        use_case = {
            "name": "Wind Turbine Aerodynamic Analysis",
            "description": "Computational fluid dynamics analysis of wind turbine blade aerodynamics",
            "industry": "Renewable Energy",
            "famous_examples": ["Vestas V164", "GE Haliade-X", "Siemens Gamesa SG 14-222"],
            "challenge": "Maximizing energy capture while minimizing loads and noise",
            "physics_focus": "Rotating aerodynamics, tip effects, stall behavior"
        }
        
        # Materials
        materials = {
            "air": MaterialTemplates.air(),
            "blade_surface": Material(
                name="Blade Coating",
                material_type="coating",
                density=1200.0,
                thermal_conductivity=0.2
            )
        }
        
        # Geometry (simplified blade)
        blade_length = 80.0  # 80m blade
        blade_chord = 5.0    # 5m max chord
        
        # Create blade geometry (simplified airfoil)
        blade = GeometryUtils.create_cube("blade", size=blade_length)
        blade.scale(np.array([1.0, blade_chord/blade_length, 0.1]))  # Tapered blade
        
        # Hub geometry
        hub = GeometryUtils.create_cylinder("hub", radius=2.0, height=4.0)
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="wind_turbine_aero_bc",
            physics_type=PhysicsType.FLUID
        )
        
        # Wind inlet (varies with wind speed)
        wind_inlet = BoundaryConditionTemplates.fluid_inlet_velocity(velocity=12.0)  # 12 m/s wind
        wind_inlet.geometry_entities = ["wind_inlet"]
        boundary_conditions.add_condition(wind_inlet)
        
        # Outlet pressure
        outlet_pressure = BoundaryConditionTemplates.fluid_outlet_pressure(pressure=101325.0)
        outlet_pressure.geometry_entities = ["outlet_boundary"]
        boundary_conditions.add_condition(outlet_pressure)
        
        # Rotating blade surface
        rotating_wall = BoundaryConditionTemplates.fluid_rotating_wall(
            angular_velocity=1.0,  # 1 rad/s rotation
            axis_origin=np.array([0, 0, 0]),
            axis_direction=np.array([0, 0, 1])
        )
        rotating_wall.geometry_entities = ["blade_surface"]
        boundary_conditions.add_condition(rotating_wall)
        
        # Hub surface (rotating)
        hub_wall = BoundaryConditionTemplates.fluid_rotating_wall(
            angular_velocity=1.0,
            axis_origin=np.array([0, 0, 0]),
            axis_direction=np.array([0, 0, 1])
        )
        hub_wall.geometry_entities = ["hub_surface"]
        boundary_conditions.add_condition(hub_wall)
        
        use_case.update({
            "materials": materials,
            "geometry": {"blade": blade, "hub": hub},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "power_coefficient": "0.4-0.5",
                "thrust_coefficient": "0.7-0.9",
                "tip_speed_ratio": "7-10",
                "blade_efficiency": "85-95%"
            },
            "optimization_targets": [
                "Maximize power coefficient",
                "Minimize blade loads",
                "Optimize tip speed ratio",
                "Reduce noise generation"
            ]
        })
        
        return use_case
    
    @staticmethod
    def marine_hydrodynamics() -> Dict[str, Any]:
        """
        Marine Hydrodynamics - Critical for ship design and performance
        
        This represents the hydrodynamic analysis of ships and marine vessels,
        essential for naval architecture and marine engineering.
        """
        use_case = {
            "name": "Marine Hydrodynamic Analysis",
            "description": "Computational fluid dynamics analysis of ship hydrodynamics",
            "industry": "Marine Engineering",
            "famous_examples": ["Container Ships", "Oil Tankers", "Naval Vessels"],
            "challenge": "Optimizing hull design for resistance, propulsion, and seakeeping",
            "physics_focus": "Free surface effects, wave resistance, propeller interaction"
        }
        
        # Materials
        materials = {
            "water": MaterialTemplates.water(),
            "air": MaterialTemplates.air(),
            "hull_steel": MaterialTemplates.steel()
        }
        
        # Geometry (simplified ship)
        hull_length = 300.0  # 300m ship length
        hull_width = 40.0    # 40m beam
        hull_height = 25.0   # 25m draft
        
        # Create hull geometry (simplified)
        hull = GeometryUtils.create_cube("hull", size=hull_length)
        hull.scale(np.array([1.0, hull_width/hull_length, hull_height/hull_length]))
        
        # Propeller geometry
        propeller = GeometryUtils.create_cylinder("propeller", radius=3.0, height=0.5)
        propeller.translate(np.array([-hull_length/2, 0, 0]))
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="marine_hydro_bc",
            physics_type=PhysicsType.FLUID
        )
        
        # Water inlet (ship speed)
        water_inlet = BoundaryConditionTemplates.fluid_inlet_velocity(velocity=15.0)  # 15 m/s (30 knots)
        water_inlet.geometry_entities = ["water_inlet"]
        boundary_conditions.add_condition(water_inlet)
        
        # Air inlet (atmosphere)
        air_inlet = BoundaryConditionTemplates.fluid_inlet_velocity(velocity=0.0)  # Still air
        air_inlet.geometry_entities = ["air_inlet"]
        boundary_conditions.add_condition(air_inlet)
        
        # Outlet pressure
        outlet_pressure = BoundaryConditionTemplates.fluid_outlet_pressure(pressure=101325.0)
        outlet_pressure.geometry_entities = ["outlet_boundary"]
        boundary_conditions.add_condition(outlet_pressure)
        
        # Free surface (water-air interface)
        free_surface = BoundaryConditionTemplates.fluid_free_surface()
        free_surface.geometry_entities = ["water_air_interface"]
        boundary_conditions.add_condition(free_surface)
        
        # Hull wall (no-slip)
        hull_wall = BoundaryConditionTemplates.fluid_wall_condition()
        hull_wall.geometry_entities = ["hull_surface"]
        boundary_conditions.add_condition(hull_wall)
        
        # Rotating propeller
        propeller_wall = BoundaryConditionTemplates.fluid_rotating_wall(
            angular_velocity=10.0,  # 10 rad/s propeller rotation
            axis_origin=np.array([-hull_length/2, 0, 0]),
            axis_direction=np.array([1, 0, 0])
        )
        propeller_wall.geometry_entities = ["propeller_surface"]
        boundary_conditions.add_condition(propeller_wall)
        
        use_case.update({
            "materials": materials,
            "geometry": {"hull": hull, "propeller": propeller},
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "resistance_coefficient": "0.002-0.004",
                "propulsive_efficiency": "60-75%",
                "wave_resistance": "30-50% of total",
                "wake_fraction": "0.2-0.4"
            },
            "optimization_targets": [
                "Minimize total resistance",
                "Maximize propulsive efficiency",
                "Optimize hull form",
                "Reduce wave making"
            ]
        })
        
        return use_case
    
    @staticmethod
    def hvac_system_analysis() -> Dict[str, Any]:
        """
        HVAC System Analysis - Critical for building comfort and energy efficiency
        
        This represents the fluid dynamics analysis of heating, ventilation, and air conditioning systems,
        essential for building design and energy efficiency.
        """
        use_case = {
            "name": "HVAC System Fluid Analysis",
            "description": "Computational fluid dynamics analysis of HVAC system airflow",
            "industry": "Building Services",
            "famous_examples": ["Office Buildings", "Data Centers", "Hospitals"],
            "challenge": "Optimizing airflow distribution for comfort and energy efficiency",
            "physics_focus": "Turbulent flow, thermal mixing, pressure distribution"
        }
        
        # Materials
        materials = {
            "air": MaterialTemplates.air(),
            "duct_material": Material(
                name="Galvanized Steel",
                material_type="steel",
                density=7850.0,
                thermal_conductivity=50.0
            )
        }
        
        # Geometry (simplified HVAC system)
        main_duct = GeometryUtils.create_cube("main_duct", size=20.0)
        main_duct.scale(np.array([1.0, 0.5, 0.5]))  # Rectangular duct
        
        # Branch ducts
        branch_ducts = []
        for i in range(5):
            branch = GeometryUtils.create_cube(f"branch_duct_{i}", size=5.0)
            branch.scale(np.array([1.0, 0.3, 0.3]))
            branch.translate(np.array([0, 0, i * 3.0]))
            branch_ducts.append(branch)
        
        # Room geometry
        room = GeometryUtils.create_cube("room", size=10.0)
        room.translate(np.array([0, 0, 15.0]))
        
        # Boundary conditions
        boundary_conditions = BoundaryConditions(
            name="hvac_fluid_bc",
            physics_type=PhysicsType.FLUID
        )
        
        # Air inlet (supply air)
        supply_inlet = BoundaryConditionTemplates.fluid_inlet_velocity(velocity=5.0)  # 5 m/s supply air
        supply_inlet.geometry_entities = ["supply_inlet"]
        boundary_conditions.add_condition(supply_inlet)
        
        # Temperature boundary condition
        supply_temp = BoundaryConditionTemplates.fluid_inlet_temperature(temperature=15.0)  # 15°C supply
        supply_temp.geometry_entities = ["supply_inlet"]
        boundary_conditions.add_condition(supply_temp)
        
        # Return air outlet
        return_outlet = BoundaryConditionTemplates.fluid_outlet_pressure(pressure=101325.0)
        return_outlet.geometry_entities = ["return_outlet"]
        boundary_conditions.add_condition(return_outlet)
        
        # Wall boundary conditions
        wall_condition = BoundaryConditionTemplates.fluid_wall_condition()
        wall_condition.geometry_entities = ["duct_walls", "room_walls"]
        boundary_conditions.add_condition(wall_condition)
        
        # Heat sources (occupants, equipment)
        heat_source = BoundaryConditionTemplates.fluid_heat_source(heat_flux=100.0)  # 100 W/m²
        heat_source.geometry_entities = ["room_heat_sources"]
        boundary_conditions.add_condition(heat_source)
        
        use_case.update({
            "materials": materials,
            "geometry": {
                "main_duct": main_duct,
                "branch_ducts": branch_ducts,
                "room": room
            },
            "boundary_conditions": boundary_conditions,
            "expected_results": {
                "air_distribution_efficiency": "80-95%",
                "temperature_uniformity": "±2°C",
                "pressure_drop": "50-200 Pa",
                "energy_efficiency": "70-85%"
            },
            "optimization_targets": [
                "Maximize air distribution efficiency",
                "Minimize pressure drop",
                "Optimize thermal comfort",
                "Reduce energy consumption"
            ]
        })
        
        return use_case
    
    @classmethod
    def get_all_use_cases(cls) -> List[Dict[str, Any]]:
        """Get all fluid dynamics use cases"""
        return [
            cls.aircraft_aerodynamics(),
            cls.automotive_aerodynamics(),
            cls.wind_turbine_aerodynamics(),
            cls.marine_hydrodynamics(),
            cls.hvac_system_analysis()
        ]
    
    @classmethod
    def get_use_case_by_name(cls, name: str) -> Dict[str, Any]:
        """Get a specific use case by name"""
        use_cases = cls.get_all_use_cases()
        for use_case in use_cases:
            if use_case["name"].lower() == name.lower():
                return use_case
        raise ValueError(f"Use case '{name}' not found")