from pathlib import Path
import pandas as pd
import re
import math
import shutil
from typing import List, Iterable, Set

import helper.portFunctions as portFunc
import helper.filePaths as paths
import helper.dictFunctions as df

start_row_list2 = 301
end_row_list2 = 600

start_row_list3 = 1
end_row_list3 = 500

rows_list2 = portFunc.readColumns(paths.metadata_liste2, start_row_list2, end_row_list2)
rows_list3 = portFunc.readColumns(paths.metadata_liste3, start_row_list3, end_row_list3)


db = df.load_db(paths.store_path)

for e_value, ca_value, cd_value, ce_value in rows_list2:
   year = portFunc.transform_e_value(e_value)
   source_dir_year = Path(f"{paths.source_pics}/{year}")
   pic_names = portFunc.extract_jpg_filenames(cd_value)
   picId = portFunc.extractID(pic_names)
   if len(picId) > 0:
    key = picId.pop()
    print(f"List 2 - {key}")
   copied, missing, newLog = portFunc.copy_pictures(pic_names, source_dir_year, paths.target_dir_list2)
   if copied > 0:
    df.upsert_record(db, key, ce_value, ca_value, pic_names)
    df.save_db(db, paths.store_path)
    print(db[key])
   else:
    print(f"not found {key} anzahl {copied}")

for e_value, ca_value, cd_value, ce_value in rows_list3:
   year = portFunc.transform_e_value(e_value)
   source_dir_year = Path(f"{paths.source_pics}/{year}")
   pic_names = portFunc.extract_jpg_filenames(cd_value)
   picId = portFunc.extractID(pic_names)
   if len(picId) > 0:
    key = picId.pop()
    print(f"List 3 -  {key}")
    copied, missing, newLog = portFunc.copy_pictures(pic_names, source_dir_year, paths.target_dir_list3)
   if copied > 0:
    df.upsert_record(db, key, ce_value, ca_value, pic_names)
    df.save_db(db, paths.store_path)
    print(db[key])
   else:
    print(f"not found {key} anzahl {copied}")


   





