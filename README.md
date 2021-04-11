##Installation

```
git clone https://github.com/solotony/irs-gov-parser.git
pip install -r requirements.txt
```

##Run

```
python demo.py list --numbers "Form W-2"  "Form 1095-C"
python demo.py fetch --number "Form W-2" --min_year 2000 --max_year 2021
```

##Comments

This utilite made as "for myself", not for public usage:
  - no any tests
  - no advanced documentation
  - no advanced errors processing  

It was tested on Python 3.7.3, but i believe thant any Python 3 will run it correctly

Form numbers compared with all non-numbers and non-letters are ignored, **all
numbers and letters must match**:

```
"Form W-2" is equal to "f o r m  w2"
"Form W-2" is equal to "f o-rmw-2"
"Form W-2" is not equal to "Form W-2 P" or "Form W-2VI"
```