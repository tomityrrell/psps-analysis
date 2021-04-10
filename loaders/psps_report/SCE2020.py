import tabula
import pandas as pd
import os

input_path = "../../data/2020/"
output_path = "../../data/2020/"

file_pages = {
'SCE Dec 16-24 2020 PSPS Post Event Report.pdf' :   '16-19',
'SCE Dec 4-14 PSPS Post Event Report.pdf' :         '20-26',
'SCE Nov 14-18 2020 PSPS Post Event Report.pdf' :   '10-11',
'SCE Nov 24-28 2020 PSPS Post Event Report.pdf' :   '12-25',
'SCE Nov 29 2020 PSPS Post Event Report Final.pdf' :'18-25',
'SCE Nov 3-7 2020 PSPS Post Event Report.pdf' :     '9-10',
'SCE Oct 16 2020 PSPS Post Event Report.pdf' :      '8',
'SCE Oct 23-28 2020 PSPS Post Event Report.pdf' :   '15-19',
'SCE Sept 5-11 2020 PSPS Post Event Report.pdf' :   '12',
}

file_tables = {}
for filename in filter(lambda s: s.endswith(".pdf"), os.listdir()):
    tables = tabula.read_pdf("{}{}".format(input_path, filename), lattice=True, pages=file_pages[filename])
    file_tables[filename] = list(filter(lambda d: len(d.columns) > 10, tables))

decision_columns = ["Circuit", "Weather Station", "Wind Sustained", "Gust Sustained", "Thresholds (Sustained/ Gust)", "FPI Value", "Reasons for De-Energization"]

file_frames = {}
# post processing filtering
for filename in filter(lambda s: s.endswith(".pdf"), os.listdir()):
    for df in file_tables[filename]:
        df.dropna(how="all", axis=1, inplace=True)
        if len(df.columns) == 9:
            df.drop(df.columns[2], axis=1, inplace=True)
        if len(df.columns) == 8:
            df.drop(df.columns[1], axis=1, inplace=True)

        df.dropna(how="any", axis=0, inplace=True)

        df.replace('\r', ' ', regex=True, inplace=True)
        df.replace('•|\uf0b7', '\n', regex=True, inplace=True)
        df.replace(" MPH|FPI:\s*|\n|[.]$", '', regex=True, inplace=True)
        df.replace("-|‐", '/', regex=True, inplace=True)

        df.reset_index(drop=True, inplace=True)
        df.columns = decision_columns

    file_frames[filename] = pd.concat(file_tables[filename])
    file_frames[filename]["month"] = filename.split(" ")[1]
    file_frames[filename]["days"] = filename.split(" ")[2]
    file_frames[filename]["year"] = filename.split(" ")[3]

decision = pd.concat(file_frames.values())
decision.to_csv("decision_2020.csv", index=False)
