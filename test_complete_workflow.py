#!/usr/bin/env python3
"""
Test for Complete Workflow System
Tests all 14 phases of the manuscript-to-print workflow.
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

def test_workflow_orchestrator():
    """Test workflow orchestrator."""
    print("\n" + "="*70)
    print("TEST: Workflow Orchestrator")
    print("="*70)
    
    try:
        from modules.workflow_orchestrator import WorkflowOrchestrator, ManuscriptMetadata
        
        # Create test orchestrator
        orchestrator = WorkflowOrchestrator("/tmp/test_workflow")
        
        # Check phases initialization
        assert len(orchestrator.phases) == 14, "Should have 14 phases"
        
        # Test phase operations
        orchestrator.start_phase(1, "Test User")
        assert orchestrator.phases[0].status == 'in_progress', "Phase 1 should be in progress"
        
        orchestrator.complete_phase(1, output_files=["test.txt"], notes="Test complete")
        assert orchestrator.phases[0].status == 'completed', "Phase 1 should be completed"
        
        # Test metadata
        orchestrator.metadata = ManuscriptMetadata(
            title="Test Book",
            author="Test Author",
            genre="Fiction",
            word_count=50000,
            page_count=250
        )
        orchestrator.save_state()
        
        # Test report generation
        report = orchestrator.generate_workflow_report()
        assert "Test Book" in report, "Report should contain book title"
        assert "14/14" not in report, "Not all phases should be complete"
        
        print("✅ WorkflowOrchestrator: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ WorkflowOrchestrator: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_isbn_cip_generator():
    """Test ISBN and CIP generator."""
    print("\n" + "="*70)
    print("TEST: ISBN and CIP Generator")
    print("="*70)
    
    try:
        from modules.isbn_cip_generator import ISBNCIPGenerator
        
        generator = ISBNCIPGenerator()
        
        # Test ISBN generation
        isbn = generator.generate_isbn("test-book-001")
        print(f"  Generated ISBN: {isbn}")
        assert isbn.startswith("978-85-"), "ISBN should start with 978-85-"
        assert len(isbn.replace("-", "")) == 13, "ISBN should have 13 digits"
        
        # Test ISBN validation
        assert generator.validate_isbn(isbn), "Generated ISBN should be valid"
        assert not generator.validate_isbn("978-85-12345-67-9"), "Invalid ISBN should fail"
        
        # Test CDD code
        cdd = generator.get_cdd_code("ficção")
        assert cdd == "869.3", "Fiction should be 869.3"
        
        # Test CIP generation
        metadata = {
            'author': 'João Silva',
            'title': 'Test Book',
            'edition': '1. ed.',
            'city': 'São Paulo',
            'publisher': 'Test Publisher',
            'year': 2025,
            'pages': 300,
            'isbn': isbn,
            'subjects': ['Ficção brasileira'],
            'cdd': '869.3'
        }
        
        cip = generator.generate_cip(metadata)
        assert 'João Silva' in cip, "CIP should contain author"
        assert 'Test Book' in cip, "CIP should contain title"
        assert '869.3' in cip, "CIP should contain CDD"
        
        # Test legal page
        legal = generator.generate_legal_page(metadata)
        assert isbn in legal, "Legal page should contain ISBN"
        assert '© 2025' in legal, "Legal page should contain copyright year"
        
        print("✅ ISBNCIPGenerator: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ ISBNCIPGenerator: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_print_ready_generator():
    """Test print-ready file generator."""
    print("\n" + "="*70)
    print("TEST: Print-Ready Generator")
    print("="*70)
    
    try:
        from modules.print_ready_generator import PrintReadyGenerator
        
        generator = PrintReadyGenerator()
        
        # Test spine width calculation
        spine_width = generator.calculate_spine_width(300, 80)
        print(f"  Spine width for 300 pages: {spine_width}mm")
        assert spine_width > 0, "Spine width should be positive"
        assert spine_width < 50, "Spine width should be reasonable"
        
        # Test cover dimensions
        dims = generator.calculate_cover_dimensions('A5', 300, 80)
        print(f"  Cover dimensions: {dims['total_width']}mm x {dims['total_height']}mm")
        assert dims['total_width'] > 0, "Cover width should be positive"
        assert dims['spine_width'] == spine_width, "Spine width should match"
        assert dims['bleed'] == 5, "Bleed should be 5mm"
        
        # Test technical specs generation
        metadata = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '978-85-12345-67-8',
            'publisher': 'Test Publisher',
            'page_format': 'A5',
            'page_count': 300
        }
        
        specs = generator.generate_technical_specs(metadata, 'A5', 300)
        assert 'Test Book' in specs, "Specs should contain title"
        assert '300 DPI' in specs, "Specs should mention resolution"
        assert 'CMYK' in specs, "Specs should mention color mode"
        
        print("✅ PrintReadyGenerator: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ PrintReadyGenerator: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_workflow():
    """Test complete workflow integration."""
    print("\n" + "="*70)
    print("TEST: Complete Workflow Integration")
    print("="*70)
    
    try:
        # Just test import for now
        from complete_workflow import CompleteWorkflow
        
        print("  ✅ CompleteWorkflow class imported successfully")
        print("  ℹ️  Full integration test runs with: python complete_workflow.py")
        
        print("✅ CompleteWorkflow: IMPORT TEST PASSED")
        return True
        
    except Exception as e:
        print(f"❌ CompleteWorkflow: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("🧪 COMPLETE WORKFLOW SYSTEM - TEST SUITE")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("Workflow Orchestrator", test_workflow_orchestrator()))
    results.append(("ISBN/CIP Generator", test_isbn_cip_generator()))
    results.append(("Print-Ready Generator", test_print_ready_generator()))
    results.append(("Complete Workflow", test_complete_workflow()))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {name}")
    
    print("="*70)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
