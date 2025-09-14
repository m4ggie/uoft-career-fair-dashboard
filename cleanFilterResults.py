'''
level of study:
Graduate, Graduate Full-time --> Graduate
Recent Graduate, Recent Graduates --> Recent Graduates

hiring for:
Co-op, Co-ops -->  Co-op
Full-Time, Full-time --> Full-time
Internship, Internships --> Internship
Part-Time, Part-time --> Part-time

Target Programs:
All Programs, All programs --> All Programs
Arts & Science, Arts and Sciences --> Arts & Sciences
Engineering & Technology, Engineering and Technology --> Engineering & Technology
'''

import pandas as pd
import re

df = pd.read_csv("uoft_career_fair_employers.csv")

def clean_level_of_study(value):
    value = re.sub(r'Graduate Full-time', 'Graduate', str(value), flags=re.IGNORECASE)
    value = re.sub(r'Recent Graduate', 'Recent Graduates', str(value), flags=re.IGNORECASE)
    return value

def clean_hiring_for(value):
    value = re.sub(r'Co-ops', 'Co-op', str(value), flags=re.IGNORECASE)
    value = re.sub(r'Full-Time', 'Full-time', str(value), flags=re.IGNORECASE)
    value = re.sub(r'Part-Time', 'Part-time', str(value), flags=re.IGNORECASE)
    value = re.sub(r'Internships', 'Internship', str(value), flags=re.IGNORECASE)
    return value
    
def clean_target_programs(value):
    value = re.sub(r'All programs', 'All Programs', str(value), flags=re.IGNORECASE)
    value = re.sub(r'Arts and Sciences', 'Arts & Science', str(value), flags=re.IGNORECASE)
    value = re.sub(r'Engineering and Technology', 'Engineering & Technology', str(value), flags=re.IGNORECASE)
    return value



df["Level of Study"] = df["Level of Study"].apply(clean_level_of_study)
df["Hiring For"] = df["Hiring For"].apply(clean_hiring_for)
df["Target Programs"] = df["Target Programs"].apply(clean_target_programs)

df.to_csv("uoft_career_fair_employers_cleaned.csv", index=False)
print("done")
