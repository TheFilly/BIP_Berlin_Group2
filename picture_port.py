from pathlib import Path
import pandas as pd
import re
import math
import shutil
from typing import List, Iterable, Set

from helper.portFunctions import *

# === Pfade ===
metadata_liste2 = Path("/Users/filly/Documents/Uni - HTW/IuG/Data/Objektdaten/liste2.xls") 
metadata_liste3 = Path("/Users/filly/Documents/Uni - HTW/IuG/Data/Objektdaten/liste3.xls") 
source_pics = Path("/Users/filly/Documents/Uni - HTW/IuG/Data/Objektbilder")
target_dir_list2 = Path("/Users/filly/Documents/Uni - HTW/IuG/Code/Pictures/List2")
target_dir_list3 = Path("/Users/filly/Documents/Uni - HTW/IuG/Code/Pictures/List3")
log_missing_pictures = Path("/Users/filly/Documents/Uni - HTW/IuG/Code/Pictures/missingPictures.txt")

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





