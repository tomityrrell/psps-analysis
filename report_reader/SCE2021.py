import tabula
import pandas as pd

input_path = "../data/2021/"
output_path = "../data/2021/"

tables = tabula.read_pdf(input_path, lattice=True, pages='23-34')

deenergization = pd.concat(tables[:6])
decision = pd.concat(tables[6:])

deenergization_columns = ['County', 'Circuit', 'POC *(Not Originally in Scope)', 'Isolation Device', 'Customers De‐Energized', 'Imminent De‐Energization Notification Sent', 'De‐Energized Date and Time', 'De‐energized Notification Sent', 'IC Approved Restoration Time', 'Imminent Re‐Energization Notification Sent', 'Re‐Energized (1st load)', 'Customers Re-Energized (1st load)', 'Re‐Energized (All load)', 'Customers Re‐Energized (All load)', 'Re‐energized Notification Sent', 'All Clear Notification']
decision_columns = ['County', 'Circuit', 'POC *(Not Originally in Scope)', 'Isolation Device', 'Customers De‐Energized', 'Reasons for De‐Energization', 'FPI Value', 'Trigger Percentage', 'Weather Station', 'Wind Sustained', 'Gust Sustained', 'Thresholds (Sustained/ Gust)', 'Adjusted Triggers (Sustained/ Gust)']

columns = {"deenergization": deenergization_columns, "decision": decision_columns}
frames = {"deenergization": deenergization, "decision": decision}

for k in frames:
    frames[k].dropna(how="all", axis=1, inplace=True)
    frames[k].dropna(how="any", axis=0, inplace=True)
    frames[k].replace('\r', ' ', regex=True, inplace=True)
    frames[k].reset_index(drop=True, inplace=True)
    frames[k].columns = columns[k]
    frames[k].to_csv("{}{}.csv".format(output_path, k), index=False)


