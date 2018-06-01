import re
import glob
import os

def reset_timezones():
	directories = ["Monday", "Sunday", "Thursday", "Wednesday"]
	reg = re.compile(r'(?<=T)\d\d')
	reg2 = re.compile(r'\d\d(?=T)')
	print(reg)
	for directory in directories:
		file_list = glob.glob(directory + "/*/*.txt")
		for file in file_list:
			filename = os.path.basename(file)
			old_hour = re.search(reg, filename).group(0)
			new_hour = (int(old_hour) + 24 - 5) % 24
			old_day = re.search(reg2, filename).group(0)
			if int(old_hour) < 5:
				new_day = int(old_day) - 1
			else:
				new_day = int(old_day)
			new_hour_string = str(new_hour)
			new_day_string = str(new_day)
			if new_hour < 10:
				new_hour_string = "0" + new_hour_string
			print(filename + " -> " + re.sub(reg2, new_day_string, re.sub(reg, new_hour_string, filename)))
			os.rename(file, os.path.join(os.path.dirname(file), re.sub(reg2, new_day_string, re.sub(reg, new_hour_string, filename))))

reset_timezones()