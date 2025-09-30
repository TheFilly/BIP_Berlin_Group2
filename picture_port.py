from pathlib import Path
import pandas as pd
import re
import math
import shutil
from typing import List, Iterable, Set

from helper.portFunctions import *
from helper.filePaths import *

start_row_list2 = 301
end_row_list2 = 600

start_row_list3 = 1
end_row_list3 = 500

rows_list2 = readColumns(metadata_liste2, start_row_list2, end_row_list2)
rows_list3 = readColumns(metadata_liste3, start_row_list3, end_row_list3)

for e_value, ca_value, cd_value, ce_value in rows_list2:
   year = transform_e_value(e_value)
   source_dir_year = Path(f"{source_pics}/{year}")
   pic_names = extract_jpg_filenames(cd_value)
   id = extractID(pic_names)
   copy_pictures(pic_names, source_dir_year, target_dir_list2)

for e_value, ca_value, cd_value, ce_value in rows_list2:
   year = transform_e_value(e_value)
   source_dir_year = Path(f"{source_pics}/{year}")
   pic_names = extract_jpg_filenames(cd_value)
   id = extractID(pic_names)
   copy_pictures(pic_names, source_dir_year, target_dir_list3)





