# Metadata Extraction Tool

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python extract_metadata.py <input_file>
```

## Supported formats
- SPSS (.sav)
- Excel (.xlsx, .xls)
- CSV (.csv)

## Output
JSON file saved to `Output/` directory with extracted metadata:
- Question codes (SPSS variables)
- Question text (labels)
- Variable type (numeric/string)
- Possible values (ranges, categories, or freetext indicator)

## Examples
```bash
python extract_metadata.py Data/AutoClaims/autoclaims.sav
python extract_metadata.py Data/Bill/NX_bill_direct_1_data.xlsx
```
