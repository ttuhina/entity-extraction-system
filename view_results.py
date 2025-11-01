"""
Results Viewer and Validator
View and validate extraction results
Generates comprehensive analysis report
"""

import pandas as pd
from pathlib import Path
import json
from datetime import datetime

def view_results(save_report=True):
    """Display extraction results in a readable format and save to file"""
    
    output_dir = Path("output_files")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Prepare report content
    report_lines = []
    
    print("\n" + "="*70)
    print(" " * 20 + "EXTRACTION RESULTS VIEWER")
    print("="*70)
    
    report_lines.append("="*70)
    report_lines.append("ENTITY EXTRACTION - COMPREHENSIVE RESULTS REPORT")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("="*70)
    report_lines.append("")
    
    # Check if files exist
    stats_file = output_dir / "extraction_statistics.json"
    relations_file = output_dir / "extracted_relations.csv"
    entities_file = output_dir / "extracted_entities.csv"
    
    files_found = 0
    
    # Load statistics
    if stats_file.exists():
        files_found += 1
        try:
            with open(stats_file, 'r') as f:
                stats = json.load(f)
            
            print("\n📊 OVERALL STATISTICS:")
            print(f"   Total Pages Processed: {stats.get('total_pages', 0)}")
            print(f"   Total Entities Found: {stats.get('entities_found', 0)}")
            print(f"   Total Relations Found: {stats.get('relations_found', 0)}")
            
            report_lines.append("📊 OVERALL STATISTICS")
            report_lines.append("-" * 70)
            report_lines.append(f"Total Pages Processed: {stats.get('total_pages', 0)}")
            report_lines.append(f"Total Entities Found: {stats.get('entities_found', 0)}")
            report_lines.append(f"Total Relations Found: {stats.get('relations_found', 0)}")
            report_lines.append("")
            
            # Extraction methods
            if 'extraction_methods' in stats:
                report_lines.append("Extraction Methods Used:")
                for method, count in stats['extraction_methods'].items():
                    report_lines.append(f"  - {method}: {count}")
                report_lines.append("")
        except Exception as e:
            print(f"   Warning: Could not read statistics file: {e}")
    else:
        print("\n⚠️  extraction_statistics.json not found")
        report_lines.append("⚠️  Statistics file not found")
        report_lines.append("")
    
    # Load and display relations
    if relations_file.exists():
        files_found += 1
        try:
            df = pd.read_csv(relations_file)
            
            print("\n🔗 EXTRACTED RELATIONS:")
            print(f"   Total Relations: {len(df)}")
            print(f"\n   Sample Relations (Top 10):")
            print("-" * 70)
            
            report_lines.append("🔗 EXTRACTED RELATIONS")
            report_lines.append("-" * 70)
            report_lines.append(f"Total Relations: {len(df)}")
            report_lines.append("")
            report_lines.append("Sample Relations (Top 10):")
            report_lines.append("")
            
            for idx, row in df.head(10).iterrows():
                relation_str = f"{row['entity_pan']} → {row['relation']} → {row['entity_person_org']}"
                detail_str = f"   Confidence: {row['confidence']:.2f} | Method: {row['method']}"
                
                print(f"   {relation_str}")
                print(detail_str)
                print()
                
                report_lines.append(f"  {relation_str}")
                report_lines.append(f"     Confidence: {row['confidence']:.2f} | Method: {row['method']}")
                report_lines.append("")
            
            # Quality analysis
            high_conf = len(df[df['confidence'] >= 0.8])
            medium_conf = len(df[(df['confidence'] >= 0.6) & (df['confidence'] < 0.8)])
            low_conf = len(df[df['confidence'] < 0.6])
            
            print("\n📈 CONFIDENCE DISTRIBUTION:")
            print(f"   High Confidence (≥0.8): {high_conf} ({high_conf/len(df)*100:.1f}%)")
            print(f"   Medium Confidence (0.6-0.8): {medium_conf} ({medium_conf/len(df)*100:.1f}%)")
            print(f"   Low Confidence (<0.6): {low_conf} ({low_conf/len(df)*100:.1f}%)")
            
            report_lines.append("📈 CONFIDENCE DISTRIBUTION")
            report_lines.append("-" * 70)
            report_lines.append(f"High Confidence (≥0.8): {high_conf} ({high_conf/len(df)*100:.1f}%)")
            report_lines.append(f"Medium Confidence (0.6-0.8): {medium_conf} ({medium_conf/len(df)*100:.1f}%)")
            report_lines.append(f"Low Confidence (<0.6): {low_conf} ({low_conf/len(df)*100:.1f}%)")
            report_lines.append("")
            
            # Method breakdown
            method_counts = df['method'].value_counts()
            report_lines.append("Extraction Method Breakdown:")
            for method, count in method_counts.items():
                percentage = (count / len(df)) * 100
                report_lines.append(f"  - {method}: {count} ({percentage:.1f}%)")
            report_lines.append("")
        except Exception as e:
            print(f"   Warning: Could not read relations file: {e}")
    else:
        print("\n⚠️  extracted_relations.csv not found")
        report_lines.append("⚠️  Relations file not found")
        report_lines.append("")
    
    # Load and display entities
    if entities_file.exists():
        files_found += 1
        try:
            df_entities = pd.read_csv(entities_file)
            
            print("\n📋 EXTRACTED ENTITIES BY TYPE:")
            entity_counts = df_entities['entity_type'].value_counts()
            
            report_lines.append("📋 EXTRACTED ENTITIES BY TYPE")
            report_lines.append("-" * 70)
            
            for entity_type, count in entity_counts.items():
                print(f"   {entity_type}: {count}")
                report_lines.append(f"{entity_type}: {count}")
            
            report_lines.append("")
            
            # Sample entities for each type
            report_lines.append("Sample Entities by Type:")
            report_lines.append("")
            for entity_type in entity_counts.index:
                samples = df_entities[df_entities['entity_type'] == entity_type]['entity_value'].head(5).tolist()
                report_lines.append(f"{entity_type}:")
                for sample in samples:
                    report_lines.append(f"  - {sample}")
                report_lines.append("")
        except Exception as e:
            print(f"   Warning: Could not read entities file: {e}")
    else:
        print("\n⚠️  extracted_entities.csv not found")
        report_lines.append("⚠️  Entities file not found")
        report_lines.append("")
    
    print("\n" + "="*70)
    
    # Check if any files were found
    if files_found == 0:
        print("❌ ERROR: No extraction result files found!")
        print("\n💡 Please run 'python extract_entities.py' first to generate results.")
        print("="*70 + "\n")
        return None
    
    # Save report to file
    if save_report:
        try:
            report_file = output_dir / "extraction_report.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            print(f"✅ Detailed report saved to: {report_file}")
            print(f"   File location: {report_file.absolute()}")
        except Exception as e:
            print(f"❌ Error saving report file: {e}")
    
    print("="*70 + "\n")
    
    return report_lines


def validate_pan_format():
    """Validate all extracted PAN numbers and save report"""
    import re
    
    output_dir = Path("output_files")
    output_dir.mkdir(exist_ok=True)
    
    entities_file = output_dir / "extracted_entities.csv"
    
    if not entities_file.exists():
        print("\n❌ ERROR: extracted_entities.csv not found!")
        print("💡 Please run 'python extract_entities.py' first to generate results.\n")
        return None
    
    try:
        df = pd.read_csv(entities_file)
        pans = df[df['entity_type'] == 'PAN']['entity_value'].tolist()
        
        if len(pans) == 0:
            print("\n⚠️  No PAN numbers found in the entities file.")
            return None
        
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
        
        print("\n🔍 PAN FORMAT VALIDATION:")
        print("="*70)
        
        validation_report = []
        validation_report.append("="*70)
        validation_report.append("PAN FORMAT VALIDATION REPORT")
        validation_report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        validation_report.append("="*70)
        validation_report.append("")
        validation_report.append("🔍 PAN FORMAT VALIDATION")
        validation_report.append("-" * 70)
        
        valid_count = 0
        for pan in pans:
            is_valid = bool(re.match(pan_pattern, pan))
            if is_valid:
                valid_count += 1
                status = "✓ VALID"
            else:
                status = "✗ INVALID"
            
            print(f"   {pan}: {status}")
            validation_report.append(f"{pan}: {status}")
        
        print(f"\n📊 Validation Summary:")
        print(f"   Total PANs: {len(pans)}")
        if len(pans) > 0:
            print(f"   Valid PANs: {valid_count} ({valid_count/len(pans)*100:.1f}%)")
            print(f"   Invalid PANs: {len(pans) - valid_count}")
        print("="*70)
        
        validation_report.append("")
        validation_report.append("📊 Validation Summary")
        validation_report.append("-" * 70)
        validation_report.append(f"Total PANs: {len(pans)}")
        if len(pans) > 0:
            validation_report.append(f"Valid PANs: {valid_count} ({valid_count/len(pans)*100:.1f}%)")
            validation_report.append(f"Invalid PANs: {len(pans) - valid_count}")
        validation_report.append("="*70)
        
        # Save validation report
        try:
            report_file = output_dir / "pan_validation_report.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(validation_report))
            print(f"\n✅ PAN validation report saved to: {report_file}")
            print(f"   File location: {report_file.absolute()}\n")
        except Exception as e:
            print(f"\n❌ Error saving validation report: {e}\n")
        
        return validation_report
        
    except Exception as e:
        print(f"\n❌ Error reading entities file: {e}\n")
        return None


if __name__ == "__main__":
    print("\n" + "🔍 Starting comprehensive results analysis...")
    print("=" * 70)
    
    # Check if output directory exists
    output_dir = Path("output_files")
    if not output_dir.exists():
        print("\n❌ ERROR: 'output_files' directory not found!")
        print("\n💡 Please run 'python extract_entities.py' first to:")
        print("   1. Create the output_files directory")
        print("   2. Generate extraction results")
        print("\nThen run this script again.\n")
        exit(1)
    
    # View and save main results report
    result = view_results(save_report=True)
    
    if result is not None:
        # Validate and save PAN validation report
        validate_pan_format()
        
        print("\n" + "="*70)
        print("✅ ALL REPORTS GENERATED SUCCESSFULLY!")
        print("="*70)
        print("\n📂 Check output_files/ for:")
        print("   ✓ extraction_report.txt (Comprehensive analysis)")
        print("   ✓ pan_validation_report.txt (PAN format validation)")
        print("   ✓ extracted_relations.csv (Main results)")
        print("   ✓ extracted_entities.csv (All entities)")
        print("   ✓ extraction_statistics.json (Metrics)")
        print("\n" + "="*70 + "\n")
    else:
        print("\n" + "="*70)
        print("⚠️  Could not generate reports - extraction results not found")
        print("="*70 + "\n")