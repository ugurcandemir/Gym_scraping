import pandas as pd

df = pd.read_excel("macfit_gyms.xlsx")


# Step 1: Clean slashes and create address2
df['address2'] = df['Address'].apply(
    lambda x: '/'.join([part.strip() for part in str(x).split('/')])
)

# Step 2: Get the last word from address2 and create address3
df['address3'] = df['address2'].apply(lambda x: str(x).split()[-1])

# Step 3: Split address3 by the rightmost slash into District and Province, handle no-slash case
def split_district_province(addr):
    parts = addr.rsplit('/', 1)
    if len(parts) == 2:
        return pd.Series({'District': parts[0], 'Province': parts[1]})
    else:
        return pd.Series({'District': None, 'Province': parts[0]})

df[['District', 'Province']] = df['address3'].apply(split_district_province)

# Show results
df[['Address', 'address2', 'address3', 'District', 'Province']].head(25)


import re

def get_last_alnum_part(s):
    if pd.isna(s):
        return None
    # Split by non-alphanumeric character, take the last non-empty part
    parts = re.split(r'\W+', s)
    # Filter out empty strings and return the last part
    parts = [p for p in parts if p]
    return parts[-1] if parts else None

df['District'] = df['District'].apply(get_last_alnum_part)

# Show results
print(df[['Address', 'address2', 'address3', 'District', 'Province']].head(25))


def get_gym_type(url):
    url = str(url).lower()
    if "macone" in url:
        return "MAC/One" 
    elif "macstudio" in url:
        return "MACStudio"
    else:
        return "MACFit"

df['Type'] = df['Gym_URL'].apply(get_gym_type)

# Show results
print(df[['Gym_URL', 'Type']].head(25))