import requests
from datetime import datetime
import json
import pandas as pd
import scipy.stats as stats
import logging
from time import sleep
import os

year = 2018
month = 5
day=datetime.today().day
first_day = day
folder = ""
template = "An exception of type {0} occurred. Arguments:\n{1!r}"

def update_times(day):
	start_times = [datetime(year, month, day, hour=6, minute=0), datetime(year, month, day, hour=13, minute=00), datetime(year, month, day, hour=18, minute=0), datetime(year, month, day, hour=22, minute=0)]
	return start_times

start_times = update_times(first_day)

logging.basicConfig(level=logging.DEBUG, 
	format='%(asctime)s %(levelname)-8s %(message)s',
	datefmt='%Y-%m-%dT%H.%M.%S',
	filename='get_json.log',
	filemode="w+")
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

logging.info("Program started")
f = open("apikeys.txt")
url = 'https://traffic.cit.api.here.com/traffic/6.2/flow.json'
query = {
	# 19.4308, -99.1597 coordinates of Reforma-Insurgientes
	"prox": "19.4308, -99.1597, 3000",
	"app_id": f.readline(),
	"app_code": f.readline(),
	"units": "metric",
	"maxfunctionalclass": 4,
	"responseattributes": "sh,fc"
}


def main_loop():
	start_loop = datetime.now()
	try:
		r = requests.get(url, query, timeout=60)
	except requests.exceptions.RequestException as ex:
		message = template.format(type(ex).__name__, ex.args)
		logging.error(message)
	if r.status_code != 200:
		try:
			r.raise_for_status()
		except requests.exceptions.RequestException as ex:
			message = template.format(type(ex).__name__, ex.args)
			logging.error(message)
			logging.error(str(r.headers))
	else:
		try:
			data = r.json()

			record_time = data["CREATED_TIMESTAMP"].split("+")
			record_time = record_time[0]
			record_time = record_time.replace(":", ".")
			data = data["RWS"][0]["RW"]
			rows = []
			unique_coordinates = set()
			for roadway in data:
				flowlist = roadway["FIS"][0]["FI"]
				for flow in flowlist:
					row_entry = {"description": None, "position_code": None, "queuing_direction": None, "functional_class": None, "length": None, "start_point": None, "end_point": None, "path": None, "actual_speed": None, "freeflow_speed": None, "jam_factor": None, "certainty": None, "timestamp": None}
					row_entry["description"] = flow["TMC"]["DE"]
					row_entry["position_code"] = flow["TMC"]["PC"]
					row_entry["queuing_direction"] = flow["TMC"]["QD"]
					row_entry["length"] = flow["TMC"]["LE"]
					
					firstlink_coordinates = flow["SHP"][0]["value"][0].split(" ")
					lastlink_coordinates = flow["SHP"][-1]["value"][0].split(" ")
					row_entry["start_point"] = firstlink_coordinates[0]
					row_entry["end_point"] = lastlink_coordinates[1]
					unique_coordinates.add(firstlink_coordinates[0])
					unique_coordinates.add(lastlink_coordinates[1])
					pathstring = ""
					functional_classes = []
					for point in flow["SHP"]:
						coords = point["value"][0].split(" ")
						pathstring = pathstring + " " + coords[0]
						functional_classes.append(point["FC"])
					pathstring = pathstring + " " + lastlink_coordinates[1]
					row_entry["path"] = pathstring
					mode, count = stats.mode(functional_classes)
					row_entry["functional_class"] = mode[0]

					row_entry["actual_speed"] = flow["CF"][0]["SU"]
					row_entry["freeflow_speed"] = flow["CF"][0]["FF"]
					row_entry["jam_factor"] = flow["CF"][0]["JF"]
					row_entry["certainty"] = flow["CF"][0]["CN"]
					row_entry["timestamp"] = roadway["PBT"]
					rows.append(row_entry)

			cleaned_data = pd.DataFrame(rows, columns=["description", "position_code", "timestamp", "queuing_direction", "functional_class", "length", "start_point", "end_point", "path", "actual_speed", "freeflow_speed", "jam_factor", "certainty"])
			cleaned_data.to_csv(folder + "/" + record_time + '.txt', sep="\t", index=False)
			logging.debug("Data logged for: UTC " + record_time)
		except Exception as ex:
			message = template.format(type(ex).__name__, ex.args)
			logging.error(message)
	end_loop = datetime.now()
	delta = end_loop - start_loop
	sleep(180 - delta.total_seconds())


def sample(index):
	sample_number = 20
	if index == 1:
		sample_number = 60
	elif index == 3:
		sample_number = 80
	for i in range(sample_number):
		main_loop()


while day < first_day+7:
	for i in range(4):
		if day != first_day or i > 0:
			folder = start_times[i].strftime("%Y-%m-%dT%H.%M")
			if not os.path.exists(folder):
				os.makedirs(folder)
			curr_time = datetime.now()
			delta_t = start_times[i] - curr_time
			secs = delta_t.total_seconds()+1
			if (secs < 0):
				i = i + 1
				logging.warning("Sampling missed on day " + str(day) + " for index " + str(i))					
			else:
				logging.debug("Waiting " + str(secs/60) + " minutes to start sampling")
				sleep(secs)
				logging.info("Sampling started")
				sample(i)
				logging.info("Sampling finished for time interval starting at " + folder)
	day = day + 1
	start_times = update_times(day)