from pathlib import Path
import pandas as pd
import re
import math
import shutil
from typing import List, Iterable, Set

import helper.portFunctions as portFunc
import helper.filePaths as filePaths

start_row_list2 = 301
end_row_list2 = 600

start_row_list3 = 1
end_row_list3 = 500

rows_list2 = portFunc.readColumns(filePaths.metadata_liste2, start_row_list2, end_row_list2)
rows_list3 = portFunc.readColumns(filePaths.metadata_liste3, start_row_list3, end_row_list3)

for e_value, ca_value, cd_value, ce_value in rows_list2:
   year = portFunc.transform_e_value(e_value)
   source_dir_year = Path(f"{filePaths.source_pics}/{year}")
   pic_names = portFunc.extract_jpg_filenames(cd_value)
   id = portFunc.extractID(pic_names)
   portFunc.copy_pictures(pic_names, source_dir_year, filePaths.target_dir_list2)

for e_value, ca_value, cd_value, ce_value in rows_list2:
   year = portFunc.transform_e_value(e_value)
   source_dir_year = Path(f"{filePaths.source_pics}/{year}")
   pic_names = portFunc.extract_jpg_filenames(cd_value)
   id = portFunc.extractID(pic_names)
   portFunc.copy_pictures(pic_names, source_dir_year, filePaths.target_dir_list3)





