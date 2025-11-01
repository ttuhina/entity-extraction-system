"""
Entity Extraction System for Organizations, Names, and PAN Numbers
Author: [Your Name]
Date: November 2025

This system uses multiple extraction methods:
1. Regex pattern matching for PAN numbers
2. NLP-based entity recognition using transformer models
3. Context-aware relation extraction
4. Validation and quality scoring
"""

import re
import pandas as pd
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict
import json
from datetime import datetime

# For NER (Named Entity Recognition)
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("Warning: transformers not installed. Will use regex-only mode.")

class EntityExtractor:
    """Main class for extracting entities and relations from PDF documents"""
    
    def __init__(self, pdf_path: str, output_dir: str = "output_files"):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Storage for extracted entities
        self.organizations = set()
        self.persons = set()
        self.pan_numbers = set()
        self.relations = []
        
        # Statistics
        self.stats = {
            'total_pages': 0,
            'entities_found': 0,
            'relations_found': 0,
            'extraction_methods': defaultdict(int)
        }
        
        # Initialize NER pipeline if available
        self.ner_pipeline = None
        if HAS_TRANSFORMERS:
            self.initialize_ner()
    
    def initialize_ner(self):
        """Initialize the Named Entity Recognition pipeline"""
        try:
            print("Loading NER model... This may take a few minutes on first run.")
            # Using a lightweight model suitable for beginners
            model_name = "dslim/bert-base-NER"
            self.ner_pipeline = pipeline(
                "ner", 
                model=model_name, 
                aggregation_strategy="simple"
            )
            print("✓ NER model loaded successfully!")
        except Exception as e:
            print(f"Warning: Could not load NER model: {e}")
            print("Continuing with regex-based extraction only.")
            self.ner_pipeline = None
    
    def extract_text_from_pdf(self) -> List[Dict]:
        """Extract text from PDF with page information"""
        print(f"\n📄 Reading PDF: {self.pdf_path.name}")
        
        try:
            doc = fitz.open(self.pdf_path)
            self.stats['total_pages'] = len(doc)
            
            pages_data = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                pages_data.append({
                    'page_num': page_num + 1,
                    'text': text,
                    'char_count': len(text)
                })
                
                if (page_num + 1) % 10 == 0:
                    print(f"  Processed {page_num + 1}/{len(doc)} pages...")
            
            doc.close()
            print(f"✓ Successfully extracted text from {len(pages_data)} pages")
            return pages_data
            
        except Exception as e:
            print(f"✗ Error reading PDF: {e}")
            return []
    
    def extract_pan_with_regex(self, text: str) -> List[Dict]:
        """
        Extract PAN numbers using regex pattern matching
        PAN Format: ABCDE1234F
        - First 5 characters: Letters
        - Next 4 characters: Numbers
        - Last character: Letter
        """
        pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'
        pans = []
        
        for match in re.finditer(pan_pattern, text):
            pan = match.group()
            position = match.start()
            
            # Extract context around PAN (for finding associated names)
            context_start = max(0, position - 100)
            context_end = min(len(text), position + 100)
            context = text[context_start:context_end]
            
            pans.append({
                'pan': pan,
                'context': context,
                'position': position,
                'method': 'regex'
            })
            
            self.pan_numbers.add(pan)
            self.stats['extraction_methods']['regex_pan'] += 1
        
        return pans
    
    def extract_names_near_pan(self, pan_info: Dict) -> List[str]:
        """Extract potential names near a PAN number"""
        context = pan_info['context']
        pan = pan_info['pan']
        
        # Common prefixes before names
        name_patterns = [
            r'(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Prof\.?|Shri|Smt\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'Name[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*[-–—]\s*' + re.escape(pan),
            r'' + re.escape(pan) + r'\s*[-–—]\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        
        names = []
        for pattern in name_patterns:
            matches = re.finditer(pattern, context, re.IGNORECASE)
            for match in matches:
                name = match.group(1).strip()
                # Validate name (at least 2 words, reasonable length)
                if len(name.split()) >= 2 and 4 <= len(name) <= 50:
                    names.append(name)
        
        return list(set(names))  # Remove duplicates
    
    def extract_organizations_with_regex(self, text: str) -> List[str]:
        """Extract organization names using pattern matching"""
        org_patterns = [
            r'\b([A-Z][A-Za-z&\s]+(?:Ltd|Limited|Pvt|Private|Corporation|Corp|Inc|LLC|LLP|Company|Co\.))',
            r'\b([A-Z][A-Za-z\s]+(?:Bank|Insurance|Industries|Systems|Solutions|Technologies|Services))',
        ]
        
        organizations = []
        for pattern in org_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                org = match.group(1).strip()
                if 5 <= len(org) <= 100:  # Reasonable organization name length
                    organizations.append(org)
                    self.organizations.add(org)
                    self.stats['extraction_methods']['regex_org'] += 1
        
        return list(set(organizations))
    
    def extract_entities_with_ner(self, text: str) -> Dict:
        """Extract entities using NER model"""
        if not self.ner_pipeline:
            return {'persons': [], 'organizations': []}
        
        try:
            # Split text into chunks (models have token limits)
            max_chunk = 512
            chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
            
            all_persons = []
            all_orgs = []
            
            for chunk in chunks:
                if len(chunk.strip()) < 10:
                    continue
                    
                entities = self.ner_pipeline(chunk)
                
                for entity in entities:
                    entity_text = entity['word'].strip()
                    
                    if entity['entity_group'] == 'PER' and len(entity_text) > 3:
                        all_persons.append(entity_text)
                        self.persons.add(entity_text)
                        self.stats['extraction_methods']['ner_person'] += 1
                    
                    elif entity['entity_group'] == 'ORG' and len(entity_text) > 3:
                        all_orgs.append(entity_text)
                        self.organizations.add(entity_text)
                        self.stats['extraction_methods']['ner_org'] += 1
            
            return {
                'persons': list(set(all_persons)),
                'organizations': list(set(all_orgs))
            }
        
        except Exception as e:
            print(f"Warning: NER extraction failed: {e}")
            return {'persons': [], 'organizations': []}
    
    def create_relations(self, pans: List[Dict], page_entities: Dict):
        """Create PAN_Of relations between PANs and persons/organizations"""
        for pan_info in pans:
            pan = pan_info['pan']
            
            # Try to find names near this PAN
            nearby_names = self.extract_names_near_pan(pan_info)
            
            # Create relations with nearby names
            for name in nearby_names:
                self.relations.append({
                    'entity_pan': pan,
                    'relation': 'PAN_Of',
                    'entity_person_org': name,
                    'confidence': 0.9,
                    'method': 'context_proximity'
                })
                self.persons.add(name)
                self.stats['relations_found'] += 1
            
            # If no nearby names found, try NER entities
            if not nearby_names and page_entities:
                # Use persons from NER
                for person in page_entities.get('persons', [])[:3]:  # Top 3
                    self.relations.append({
                        'entity_pan': pan,
                        'relation': 'PAN_Of',
                        'entity_person_org': person,
                        'confidence': 0.6,
                        'method': 'ner_fallback'
                    })
                    self.stats['relations_found'] += 1
    
    def process_document(self):
        """Main processing pipeline"""
        print("\n" + "="*60)
        print("ENTITY EXTRACTION SYSTEM - STARTING")
        print("="*60)
        
        # Step 1: Extract text from PDF
        pages_data = self.extract_text_from_pdf()
        if not pages_data:
            print("✗ Failed to extract text from PDF")
            return
        
        # Step 2: Process each page
        print(f"\n🔍 Analyzing {len(pages_data)} pages for entities...")
        
        for page_data in pages_data:
            page_num = page_data['page_num']
            text = page_data['text']
            
            # Extract PANs with regex
            pans = self.extract_pan_with_regex(text)
            
            # Extract organizations with regex
            orgs = self.extract_organizations_with_regex(text)
            
            # Extract entities with NER
            page_entities = self.extract_entities_with_ner(text)
            
            # Create relations
            self.create_relations(pans, page_entities)
            
            if (page_num) % 10 == 0:
                print(f"  Analyzed page {page_num}...")
        
        # Step 3: Calculate statistics
        self.stats['entities_found'] = (
            len(self.pan_numbers) + 
            len(self.persons) + 
            len(self.organizations)
        )
        
        # Print summary
        print("\n" + "="*60)
        print("EXTRACTION COMPLETE - SUMMARY")
        print("="*60)
        print(f"📊 Total Pages Processed: {self.stats['total_pages']}")
        print(f"🔢 PAN Numbers Found: {len(self.pan_numbers)}")
        print(f"👤 Persons Found: {len(self.persons)}")
        print(f"🏢 Organizations Found: {len(self.organizations)}")
        print(f"🔗 Relations Created: {self.stats['relations_found']}")
        print(f"📈 Total Entities: {self.stats['entities_found']}")
        print("\n💡 Extraction Methods Used:")
        for method, count in self.stats['extraction_methods'].items():
            print(f"   - {method}: {count}")
    
    def save_results(self):
        """Save extraction results to CSV files"""
        print("\n💾 Saving results...")
        
        # Save Relations CSV
        relations_df = pd.DataFrame(self.relations)
        if not relations_df.empty:
            relations_df = relations_df.sort_values('confidence', ascending=False)
            relations_file = self.output_dir / 'extracted_relations.csv'
            relations_df.to_csv(relations_file, index=False)
            print(f"✓ Relations saved to: {relations_file}")
        
        # Save All Entities CSV
        entities_data = []
        
        for pan in self.pan_numbers:
            entities_data.append({
                'entity_type': 'PAN',
                'entity_value': pan,
                'extraction_method': 'regex'
            })
        
        for person in self.persons:
            entities_data.append({
                'entity_type': 'Person',
                'entity_value': person,
                'extraction_method': 'multiple'
            })
        
        for org in self.organizations:
            entities_data.append({
                'entity_type': 'Organization',
                'entity_value': org,
                'extraction_method': 'multiple'
            })
        
        entities_df = pd.DataFrame(entities_data)
        if not entities_df.empty:
            entities_file = self.output_dir / 'extracted_entities.csv'
            entities_df.to_csv(entities_file, index=False)
            print(f"✓ Entities saved to: {entities_file}")
        
        # Save Statistics JSON
        stats_file = self.output_dir / 'extraction_statistics.json'
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2, default=str)
        print(f"✓ Statistics saved to: {stats_file}")
        
        print("\n✅ All results saved successfully!")
        return relations_file, entities_file


def main():
    """Main execution function"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          ENTITY & RELATION EXTRACTION SYSTEM                 ║
║                                                              ║
║  Extracting: Organizations, Names, PAN Numbers               ║
║  Relations: PAN_Of                                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Configuration
    PDF_PATH = "input_files/document.pdf"  # Change this to your PDF filename
    OUTPUT_DIR = "output_files"
    
    # Check if PDF exists
    if not Path(PDF_PATH).exists():
        print(f"✗ Error: PDF file not found at '{PDF_PATH}'")
        print(f"\n📝 Please ensure your PDF file is in the 'input_files' folder")
        print(f"   and update the PDF_PATH variable in the code if needed.")
        return
    
    # Create extractor and process
    extractor = EntityExtractor(PDF_PATH, OUTPUT_DIR)
    extractor.process_document()
    extractor.save_results()
    
    print("\n" + "="*60)
    print("🎉 PROCESSING COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📂 Check the '{OUTPUT_DIR}' folder for your results:")
    print("   - extracted_relations.csv (Main deliverable)")
    print("   - extracted_entities.csv (All entities)")
    print("   - extraction_statistics.json (Quality metrics)")
    print("\n")


if __name__ == "__main__":
    main()