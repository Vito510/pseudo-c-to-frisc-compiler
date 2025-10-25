# Step 1: Run GLA.py
python3 "GLA.py" < "./tests/19_ppjLang_laksi/test.lan"

# Step 2: Run LA.py
(cd "./analizator" && python3 LA.py < "../tests/19_ppjLang_laksi/test.in")
