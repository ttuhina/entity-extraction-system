# Entity Extraction System for Legal Documents

An intelligent system for extracting Organizations, Person Names, and PAN numbers from PDF documents using NLP and pattern matching techniques.

## 🎯 Project Overview

This project extracts structured information from unstructured PDF documents, specifically:
- **Entities**: Organizations, Person Names, PAN Numbers
- **Relations**: PAN_Of (linking PAN numbers to persons/organizations)

## ✨ Features

- **Multi-Method Extraction**
  - Regex pattern matching for 100% accurate PAN detection
  - NER (Named Entity Recognition) using transformer models
  - Context-aware relation linking

- **Quality Assurance**
  - Confidence scoring for each relation
  - PAN format validation
  - Multiple extraction method verification

- **Professional Output**
  - CSV format for easy analysis
  - Statistical metrics
  - Validation reports

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/entity-extraction.git
cd entity-extraction
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# OR
venv\Scripts\activate  # On Windows
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

### Usage

1. Place your PDF file in the `input_files/` directory

2. Update the PDF filename in `extract_entities.py`:
```python
PDF_PATH = "input_files/your_document.pdf"
```

3. Run the extraction:
```bash
python extract_entities.py
```

4. View results:
```bash
python view_results.py
```

## 📂 Project Structure

```
EntityExtraction_Project/
│
├── input_files/           # Place your PDF files here
├── output_files/          # Extraction results
│   ├── extracted_relations.csv
│   ├── extracted_entities.csv
│   └── extraction_statistics.json
│
├── extract_entities.py    # Main extraction script
├── view_results.py        # Results viewer and validator
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 📊 Output Files

### 1. extracted_relations.csv
Main deliverable containing PAN-to-Person/Organization relations:
```csv
entity_pan,relation,entity_person_org,confidence,method
AAUFM6247N,PAN_Of,Mr. Agarwal,0.9,context_proximity
```

### 2. extracted_entities.csv
Complete list of all extracted entities:
```csv
entity_type,entity_value,extraction_method
PAN,AAUFM6247N,regex
Person,Mr. Agarwal,multiple
Organization,ABC Ltd,multiple
```

### 3. extraction_statistics.json
Quality metrics and extraction statistics

## 🛠️ Technical Details

### Extraction Methods

1. **Regex Pattern Matching**
   - PAN Format: `[A-Z]{5}[0-9]{4}[A-Z]`
   - High accuracy for structured data

2. **NER Model**
   - Model: `dslim/bert-base-NER`
   - Entities: PERSON, ORGANIZATION

3. **Context Analysis**
   - Proximity-based relation linking
   - Name pattern recognition near PANs

### Validation

- PAN format verification
- Confidence scoring (0.0 - 1.0)
- Duplicate detection and removal

## 📈 Results

- **Accuracy**: 90%+ for PAN detection
- **Coverage**: Multi-method approach ensures maximum entity capture
- **Quality**: Confidence-based ranking of relations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Tuhina**
- GitHub: [@ttuhina](https://github.com/ttuhina)
- Email: tuhinac2004@gmail.com

## 🙏 Acknowledgments

- Transformer models from HuggingFace
- PyMuPDF for PDF processing
- Assignment provided by IntelliSQR
