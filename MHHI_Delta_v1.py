# Import packages
import os
import getpass
import pandas as pd 

# Change directory to where the script is located

full_path = os.path.realpath(__file__)
file_path = os.path.dirname(full_path)

os.chdir(file_path)

# STEP 1 | List firms and market shares
companies_csv = pd.read_csv('INPUT_companies.csv')

# STEP 2 | List investors' ownership percentages 
investors_csv = pd.read_csv('INPUT_investor_ownership.csv')

# STEP 3 | Catalogue potential competitive pairings 

# Create dataframe to store results of potential competitive pairings
company_pairs_df = pd.DataFrame(columns=['Pair', 'Company 1', 'Company 2', 'Cross Market Share Product', 'Cross MHHI-Delta'])

# Calculate the number of pairs there will be of two companies. 
# Number of permutations (without repetitions)	nPr = n! / (n−r)! 

def recur_factorial(n):
   if n == 1:
    return n
   elif n < 1:
    return ("NA")
   else:
    return n*recur_factorial(n-1)

company_pairs_total = recur_factorial(companies_csv.index[-1]+1) / recur_factorial(companies_csv.index[-1]-1)

print('Total number of company pairs:')
print(company_pairs_total)

# Find all permutations of two companies and save to dataframe. 

counter = 0

for company_outer in companies_csv.index[0:]:
    for company_inner in companies_csv.index[0:]:
        if company_outer != company_inner:
            company_pairs_df.loc[counter, 'Pair'] = str(companies_csv.loc[company_inner, 'Companies']) + ' | ' + str(companies_csv.loc[company_outer, 'Companies'])
            company_pairs_df.loc[counter, 'Company 1'] = companies_csv.loc[company_inner, 'Companies']
            company_pairs_df.loc[counter, 'Company 2'] = companies_csv.loc[company_outer, 'Companies']
            # STEP 7 | "Multiply the market shares of the two firms"
            company_pairs_df.loc[counter, 'Cross Market Share Product'] = companies_csv.loc[company_inner, 'MarketShare'] * companies_csv.loc[company_outer, 'MarketShare']
            counter += 1
        else:
            continue

# STEP 4 & 5 | "Figure numerator for determining cross-MHHI-delta's." For each investor and each pairing of firms, multiply the nvestor's \
# percentage ownership of the two firms in each pairing. 

ownership_product_df = pd.DataFrame(columns=['Pair', 'Company 1', 'Company 2', 'Cross MHHI-Delta Numerator', 'Cross MHHI-Delta Denominator'])

counter = 0

for owner in investors_csv.index[0:]:
    for pair in company_pairs_df.index[0:]:
        value = investors_csv.loc[owner, company_pairs_df.loc[pair, 'Company 1']] * investors_csv.loc[owner, company_pairs_df.loc[pair, 'Company 2']]  
        ownership_product_df.loc[pair, investors_csv.loc[owner, 'Owner']] = value
        ownership_product_df.loc[pair, 'Pair'] = company_pairs_df.loc[pair, 'Pair']
        ownership_product_df.loc[pair, 'Company 1'] = company_pairs_df.loc[pair, 'Company 1']
        ownership_product_df.loc[pair, 'Company 2'] = company_pairs_df.loc[pair, 'Company 2']
        counter += 1

# "For each pairing, sum the amounts from item four across all investors that are invested in both firms. (This will be the numerator in \
# the fraction used in Step 7 to determine the pairing’s cross-MHHI∆.)"

ownership_product_df['Total'] = ownership_product_df.iloc[:, :].sum(axis=1)

# Copy-paste cross market share product from previous dataframe. 

ownership_product_df['Cross Market Share Product'] = company_pairs_df['Cross Market Share Product']

ownership_product_df.to_csv('OUTPUT_ownership_product.csv')

#STEP 6 | "For the first firm in each pairing (the one whose incentive to compete with the other is under consideration), sum the squares \ 
# of the ownership percentages of that firm held by each investor. (This will be the denominator of the fraction used in Step 7 to determine \ 
# the pairing’s cross-MHHI∆.)"

# Create dataframe to store results

companies = list(investors_csv.columns[1:])
investors = list(investors_csv.index[1:])

investors_csv_squared = pd.DataFrame(columns=[companies])

# Square (^2) each investor's ownership in each company 

for column in companies:
    investors_csv_squared[column] = investors_csv[column]**2

investors_csv_squared['Investors'] = investors_csv['Owner']

# "Sum the squares of the ownership percentages of that firm held by each investor."

investors_csv_squared.loc['Total', :] = investors_csv_squared.iloc[:, :].sum(axis=0)

# STEP 7 | Figure the cross-MHHI∆ for each pairing of firms by doing the following: Multiply the market shares of the two firms, and then multiply \
# the resulting product times a fraction consisting of the relevant numerator (from Step 5) divided by the relevant denominator (from Step 6).

counter = 0

for company_pair in ownership_product_df.index[0:]:
   ownership_product_df.loc[company_pair, 'Cross MHHI-Delta Numerator'] = (ownership_product_df.loc[company_pair, 'Cross Market Share Product'] * ownership_product_df.loc[company_pair, 'Total']) 
   value_denom = investors_csv_squared.loc['Total', ownership_product_df.loc[company_pair, 'Company 1']]
   value_denom = float(value_denom)
   ownership_product_df.loc[company_pair, 'Cross MHHI-Delta Denominator'] = value_denom
   counter += 1

#STEP 8 | "Add together the cross-MHHI∆s for each pairing of firms in the market."
#STEP 9 | "Multiply that amount times 10,000."

ownership_product_df['MHHI-Delta Final'] = ownership_product_df['Cross MHHI-Delta Numerator'] / ownership_product_df['Cross MHHI-Delta Denominator']

MHHI_delta = ownership_product_df['MHHI-Delta Final'].sum() * 10000

print('MHHI-Delta calculated as:')

print(MHHI_delta)
