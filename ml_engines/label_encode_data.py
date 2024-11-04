from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import numpy as np
import pandas as pd

'''
For all 
'''

# Load data
df = pd.read_csv('sales_data.csv')
# df = pd.read_csv('jb_sales.csv')

# Select columns with 'object' data type for label encoding
object_columns = df.select_dtypes(include=['object']).columns

# Initialize LabelEncoder
le = LabelEncoder()

# Apply label encoding to each object column
for col in object_columns:
    df[col] = le.fit_transform(df[col].astype(str))

# Impute missing values with the mean
imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
df_imputed = imputer.fit_transform(df)

# Convert the imputed data back to a DataFrame
df_imputed = pd.DataFrame(df_imputed, columns=df.columns)

# Save the encoded and imputed DataFrame to a new CSV file
encoded_file_path = 'encoded_file.csv'
df_imputed.to_csv(encoded_file_path, index=False)
