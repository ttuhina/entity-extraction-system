"""
Results Viewer and Validator
View and validate extraction results
"""

import pandas as pd
from pathlib import Path
import json

def view_results():
    """Display extraction results in a readable format"""
    
    output_dir = Path("output_files")
    
    print("\n" + "="*70)
    print(" " * 20 + "EXTRACTION RESULTS VIEWER")
    print("="*70)
    
    # Load statistics
    stats_file = output_dir / "extraction_statistics.json"
    if stats_file.exists():
        with open(stats_file, 'r') as f:
            stats = json.load(f)
        
        print("\n📊 OVERALL STATISTICS:")
        print(f"   Total Pages Processed: {stats.get('total_pages', 0)}")
        print(f"   Total Entities Found: {stats.get('entities_found', 0)}")
        print(f"   Total Relations Found: {stats.get('relations_found', 0)}")
    
    # Load and display relations
    relations_file = output_dir / "extracted_relations.csv"
    if relations_file.exists():
        df = pd.read_csv(relations_file)
        
        print("\n🔗 EXTRACTED RELATIONS:")
        print(f"   Total Relations: {len(df)}")
        print(f"\n   Sample Relations (Top 10):")
        print("-" * 70)
        
        for idx, row in df.head(10).iterrows():
            print(f"   {row['entity_pan']} → {row['relation']} → {row['entity_person_org']}")
            print(f"      Confidence: {row['confidence']:.2f} | Method: {row['method']}")
            print()
        
        # Quality analysis
        high_conf = len(df[df['confidence'] >= 0.8])
        medium_conf = len(df[(df['confidence'] >= 0.6) & (df['confidence'] < 0.8)])
        low_conf = len(df[df['confidence'] < 0.6])
        
        print("\n📈 CONFIDENCE DISTRIBUTION:")
        print(f"   High Confidence (≥0.8): {high_conf} ({high_conf/len(df)*100:.1f}%)")
        print(f"   Medium Confidence (0.6-0.8): {medium_conf} ({medium_conf/len(df)*100:.1f}%)")
        print(f"   Low Confidence (<0.6): {low_conf} ({low_conf/len(df)*100:.1f}%)")
    
    # Load and display entities
    entities_file = output_dir / "extracted_entities.csv"
    if entities_file.exists():
        df_entities = pd.read_csv(entities_file)
        
        print("\n📋 EXTRACTED ENTITIES BY TYPE:")
        entity_counts = df_entities['entity_type'].value_counts()
        for entity_type, count in entity_counts.items():
            print(f"   {entity_type}: {count}")
    
    print("\n" + "="*70)
    print("✅ Review complete! Check the CSV files for full results.")
    print("="*70 + "\n")


def validate_pan_format():
    """Validate all extracted PAN numbers"""
    import re
    
    entities_file = Path("output_files/extracted_entities.csv")
    if not entities_file.exists():
        print("No entities file found!")
        return
    
    df = pd.read_csv(entities_file)
    pans = df[df['entity_type'] == 'PAN']['entity_value'].tolist()
    
    pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    
    print("\n🔍 PAN FORMAT VALIDATION:")
    print("="*70)
    
    valid_count = 0
    for pan in pans:
        is_valid = bool(re.match(pan_pattern, pan))
        if is_valid:
            valid_count += 1
            status = "✓ VALID"
        else:
            status = "✗ INVALID"
        
        print(f"   {pan}: {status}")
    
    print(f"\n📊 Validation Summary:")
    print(f"   Total PANs: {len(pans)}")
    print(f"   Valid PANs: {valid_count} ({valid_count/len(pans)*100:.1f}%)")
    print(f"   Invalid PANs: {len(pans) - valid_count}")
    print("="*70 + "\n")


if __name__ == "__main__":
    view_results()
    validate_pan_format()