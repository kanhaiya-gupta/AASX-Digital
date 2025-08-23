"""
Utilities & Integration Demo for Physics Modeling
Demonstrates the usage of all utility components and integrations

This demo showcases:
1. Physics Utilities - Common physics calculations and unit conversions
2. Mesh Quality Tools - Comprehensive mesh quality assessment
3. Twin Registry Integration - Digital twin data retrieval and management
4. AASX Integration - AASX file processing and physics mapping
"""

import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path

# Import utility components
from .physics_utilities import PhysicsUtilities, UnitSystem, PhysicsDomain
from .mesh_quality_tools import MeshQualityTools, QualityThresholds
from .twin_registry_integration import TwinRegistryIntegration, TwinQuery
from .aasx_integration import AASXIntegration

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UtilitiesDemo:
    """Comprehensive demo of all utilities and integration components"""
    
    def __init__(self):
        self.physics_utils = PhysicsUtilities()
        self.mesh_tools = MeshQualityTools()
        self.twin_integration = TwinRegistryIntegration()
        self.aasx_integration = AASXIntegration()
        
        logger.info("🚀 Utilities Demo initialized")

    async def run_comprehensive_demo(self):
        """Run the complete utilities and integration demo"""
        logger.info("🎯 Starting Comprehensive Utilities & Integration Demo")
        
        try:
            # 1. Physics Utilities Demo
            await self.demo_physics_utilities()
            
            # 2. Mesh Quality Tools Demo
            await self.demo_mesh_quality_tools()
            
            # 3. Twin Registry Integration Demo
            await self.demo_twin_registry_integration()
            
            # 4. AASX Integration Demo
            await self.demo_aasx_integration()
            
            # 5. Integrated Workflow Demo
            await self.demo_integrated_workflow()
            
            logger.info("✅ Comprehensive demo completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {str(e)}")
            raise

    async def demo_physics_utilities(self):
        """Demonstrate physics utilities functionality"""
        logger.info("\n🔬 === PHYSICS UTILITIES DEMO ===")
        
        # Unit conversions
        logger.info("📏 Unit Conversions:")
        length_m = await self.physics_utils.convert_units(1.0, "m", "cm", "length")
        logger.info(f"  1 meter = {length_m} centimeters")
        
        temp_c = await self.physics_utils.convert_units(25.0, "C", "F", "temperature")
        logger.info(f"  25°C = {temp_c}°F")
        
        # Physics calculations
        logger.info("🧮 Physics Calculations:")
        stress = await self.physics_utils.calculate_stress(force=1000, area=0.01)
        logger.info(f"  Stress: {stress} Pa")
        
        strain = await self.physics_utils.calculate_strain(original_length=1.0, deformed_length=1.001)
        logger.info(f"  Strain: {strain}")
        
        thermal_expansion = await self.physics_utils.calculate_thermal_expansion(
            original_length=1.0, coefficient=23e-6, temperature_change=100
        )
        logger.info(f"  Thermal expansion: {thermal_expansion} m")
        
        # Fluid dynamics
        logger.info("🌊 Fluid Dynamics:")
        reynolds = await self.physics_utils.calculate_fluid_dynamics(
            velocity=5.0, characteristic_length=0.1, kinematic_viscosity=1e-6
        )
        logger.info(f"  Reynolds number: {reynolds}")
        
        # Physics constraints validation
        logger.info("✅ Physics Constraints Validation:")
        constraints = {
            'temperature': {'min': -273.15, 'max': 1000, 'unit': 'C'},
            'pressure': {'min': 0, 'max': 1e6, 'unit': 'Pa'},
            'velocity': {'min': 0, 'max': 100, 'unit': 'm/s'}
        }
        
        validation_result = await self.physics_utils.validate_physics_constraints(
            values={'temperature': 25, 'pressure': 101325, 'velocity': 10},
            constraints=constraints
        )
        logger.info(f"  Constraints validation: {validation_result}")
        
        # Get physical constants
        constants = await self.physics_utils.get_physical_constants()
        logger.info(f"  Available constants: {list(constants.keys())}")

    async def demo_mesh_quality_tools(self):
        """Demonstrate mesh quality tools functionality"""
        logger.info("\n🔍 === MESH QUALITY TOOLS DEMO ===")
        
        # Create sample mesh data
        sample_mesh = {
            'nodes': [
                [0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0],
                [0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1]
            ],
            'elements': [
                {'type': 'hexahedron', 'nodes': [0, 1, 2, 3, 4, 5, 6, 7]},
                {'type': 'tetrahedron', 'nodes': [0, 1, 2, 4]},
                {'type': 'wedge', 'nodes': [1, 2, 3, 5, 6, 7]}
            ],
            'mesh_type': 'hybrid',
            'dimension': 3
        }
        
        # Assess mesh quality
        logger.info("📊 Mesh Quality Assessment:")
        quality_report = await self.mesh_tools.assess_mesh_quality(sample_mesh)
        
        logger.info(f"  Overall quality: {quality_report.overall_quality.value}")
        logger.info(f"  Quality score: {quality_report.quality_score:.2f}")
        logger.info(f"  Element count: {quality_report.element_count}")
        logger.info(f"  Critical issues: {len(quality_report.critical_issues)}")
        logger.info(f"  Optimization suggestions: {len(quality_report.optimization_suggestions)}")
        
        # Show quality distribution
        logger.info("📈 Quality Distribution:")
        for level, count in quality_report.quality_distribution.items():
            logger.info(f"  {level.value}: {count} elements")
        
        # Show critical issues
        if quality_report.critical_issues:
            logger.info("⚠️ Critical Issues:")
            for issue in quality_report.critical_issues[:3]:  # Show first 3
                logger.info(f"  - {issue}")
        
        # Show optimization suggestions
        if quality_report.optimization_suggestions:
            logger.info("💡 Optimization Suggestions:")
            for suggestion in quality_report.optimization_suggestions[:3]:  # Show first 3
                logger.info(f"  - {suggestion}")
        
        # Update quality thresholds
        logger.info("⚙️ Updating Quality Thresholds:")
        new_thresholds = QualityThresholds(
            min_aspect_ratio=0.1,
            max_skewness=0.8,
            min_orthogonality=0.3,
            min_jacobian=0.1
        )
        await self.mesh_tools.update_thresholds(new_thresholds)
        logger.info("  Thresholds updated successfully")

    async def demo_twin_registry_integration(self):
        """Demonstrate twin registry integration functionality"""
        logger.info("\n🔄 === TWIN REGISTRY INTEGRATION DEMO ===")
        
        # Get available twins
        logger.info("🔍 Querying Available Twins:")
        twins = await self.twin_integration.get_available_twins()
        logger.info(f"  Found {len(twins)} available twins")
        
        if twins:
            # Show first twin details
            first_twin = twins[0]
            logger.info(f"  First twin: {first_twin.twin_id} ({first_twin.twin_type})")
            logger.info(f"    Status: {first_twin.status}")
            logger.info(f"    Created: {first_twin.created_at}")
        
        # Search for specific twin types
        logger.info("🔎 Searching for Specific Twin Types:")
        structural_twins = await self.twin_integration.get_twins_by_type("structural")
        logger.info(f"  Structural twins: {len(structural_twins)}")
        
        thermal_twins = await self.twin_integration.get_twins_by_type("thermal")
        logger.info(f"  Thermal twins: {len(thermal_twins)}")
        
        # Get simulation data for a twin
        if twins:
            logger.info("📊 Getting Twin Simulation Data:")
            twin_id = twins[0].twin_id
            simulation_data = await self.twin_integration.get_twin_simulation_data(twin_id)
            
            if simulation_data:
                logger.info(f"  Physical constraints: {len(simulation_data.get('physical_constraints', []))}")
                logger.info(f"  Mesh requirements: {len(simulation_data.get('mesh_requirements', []))}")
                logger.info(f"  Solver recommendations: {len(simulation_data.get('solver_recommendations', []))}")
                logger.info(f"  Validation criteria: {len(simulation_data.get('validation_criteria', []))}")
            else:
                logger.info("  No simulation data available")
        
        # Get integration statistics
        logger.info("📈 Integration Statistics:")
        stats = await self.twin_integration.get_twin_statistics()
        logger.info(f"  Total twins: {stats.get('total_twins', 0)}")
        logger.info(f"  Active twins: {stats.get('active_twins', 0)}")
        logger.info(f"  Twin types: {stats.get('twin_types', [])}")

    async def demo_aasx_integration(self):
        """Demonstrate AASX integration functionality"""
        logger.info("\n📦 === AASX INTEGRATION DEMO ===")
        
        # Create a mock AASX file path for demonstration
        mock_aasx_path = "sample_physics_model.aasx"
        
        # Validate AASX file (this will show warnings since file doesn't exist)
        logger.info("✅ AASX File Validation:")
        try:
            validation_result = await self.aasx_integration.validate_aasx_file(mock_aasx_path)
            logger.info(f"  File valid: {validation_result.is_valid}")
            if validation_result.errors:
                logger.info(f"  Errors: {validation_result.errors}")
            if validation_result.warnings:
                logger.info(f"  Warnings: {validation_result.warnings}")
        except Exception as e:
            logger.info(f"  Validation error (expected for mock file): {str(e)}")
        
        # Process AASX file (this will create a placeholder since file doesn't exist)
        logger.info("📋 AASX File Processing:")
        try:
            aasx_file = await self.aasx_integration.process_aasx_file(mock_aasx_path)
            logger.info(f"  Processed file: {aasx_file.file_name}")
            logger.info(f"  File size: {aasx_file.file_size} bytes")
            logger.info(f"  Submodels: {len(aasx_file.submodels)}")
            logger.info(f"  Assets: {len(aasx_file.assets)}")
            logger.info(f"  Relationships: {len(aasx_file.relationships)}")
            
            # Create physics modeling mapping
            logger.info("🗺️ Creating Physics Modeling Mapping:")
            mapping = await self.aasx_integration.create_physics_modeling_mapping(aasx_file)
            logger.info(f"  Mapping ID: {mapping.mapping_id}")
            logger.info(f"  Physics constraints: {len(mapping.physics_constraints)}")
            logger.info(f"  Mesh requirements: {len(mapping.mesh_requirements)}")
            logger.info(f"  Solver recommendations: {len(mapping.solver_recommendations)}")
            logger.info(f"  Validation criteria: {len(mapping.validation_criteria)}")
            
        except Exception as e:
            logger.info(f"  Processing error (expected for mock file): {str(e)}")
        
        # Show integration history
        logger.info("📚 Integration History:")
        processed_files = await self.aasx_integration.get_processed_files()
        logger.info(f"  Processed files: {len(processed_files)}")
        
        validation_history = await self.aasx_integration.get_validation_history()
        logger.info(f"  Validation history: {len(validation_history)}")
        
        mapping_history = await self.aasx_integration.get_mapping_history()
        logger.info(f"  Mapping history: {len(mapping_history)}")

    async def demo_integrated_workflow(self):
        """Demonstrate integrated workflow using all utilities together"""
        logger.info("\n🔄 === INTEGRATED WORKFLOW DEMO ===")
        
        # Simulate a complete physics modeling workflow
        logger.info("🎯 Simulating Complete Physics Modeling Workflow:")
        
        # 1. Get twin data for simulation
        logger.info("1️⃣ Retrieving Digital Twin Data:")
        twins = await self.twin_integration.get_available_twins()
        if twins:
            twin_id = twins[0].twin_id
            simulation_data = await self.twin_integration.get_twin_simulation_data(twin_id)
            logger.info(f"   Retrieved data for twin: {twin_id}")
        else:
            simulation_data = {}
            logger.info("   Using mock simulation data")
        
        # 2. Process AASX file for additional constraints
        logger.info("2️⃣ Processing AASX File for Constraints:")
        mock_aasx_path = "workflow_model.aasx"
        try:
            aasx_file = await self.aasx_integration.process_aasx_file(mock_aasx_path)
            mapping = await self.aasx_integration.create_physics_modeling_mapping(aasx_file)
            logger.info(f"   Created mapping: {mapping.mapping_id}")
        except Exception as e:
            logger.info(f"   AASX processing: {str(e)} (expected for mock)")
            mapping = None
        
        # 3. Generate mesh and assess quality
        logger.info("3️⃣ Mesh Generation and Quality Assessment:")
        sample_mesh = {
            'nodes': [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]],
            'elements': [{'type': 'quad', 'nodes': [0, 1, 2, 3]}],
            'mesh_type': 'structured',
            'dimension': 2
        }
        
        quality_report = await self.mesh_tools.assess_mesh_quality(sample_mesh)
        logger.info(f"   Mesh quality: {quality_report.overall_quality.value}")
        
        # 4. Apply physics calculations
        logger.info("4️⃣ Applying Physics Calculations:")
        # Convert units for simulation
        length_cm = await self.physics_utils.convert_units(1.0, "m", "cm", "length")
        force_n = await self.physics_utils.convert_units(1000, "N", "kN", "force")
        
        # Calculate physics properties
        stress = await self.physics_utils.calculate_stress(force=force_n * 1000, area=0.01)
        logger.info(f"   Calculated stress: {stress:.2f} Pa")
        
        # 5. Validate physics constraints
        logger.info("5️⃣ Validating Physics Constraints:")
        constraints = {
            'stress': {'max': 1e6, 'unit': 'Pa'},
            'temperature': {'min': -50, 'max': 150, 'unit': 'C'}
        }
        
        validation_result = await self.physics_utils.validate_physics_constraints(
            values={'stress': stress, 'temperature': 25},
            constraints=constraints
        )
        logger.info(f"   Constraints validation: {validation_result}")
        
        # 6. Generate workflow report
        logger.info("6️⃣ Generating Workflow Report:")
        workflow_report = {
            'timestamp': datetime.now().isoformat(),
            'twin_id': twin_id if twins else 'mock',
            'mesh_quality': quality_report.overall_quality.value,
            'physics_validation': validation_result,
            'aasx_mapping': mapping.mapping_id if mapping else 'none',
            'calculated_stress': stress,
            'status': 'completed'
        }
        
        logger.info("   Workflow completed successfully!")
        logger.info(f"   Report: {json.dumps(workflow_report, indent=2)}")

async def main():
    """Main demo execution"""
    demo = UtilitiesDemo()
    await demo.run_comprehensive_demo()

if __name__ == "__main__":
    asyncio.run(main())
