import pandas as pd
from mapsplotlib import mapsplot as mplt

def string_to_coordinate_pair(input):
	spl = input.split(",")
	return (float(spl[0]), float(spl[1]))

f = open("googlemapskey.txt")
apikey = f.readline()[0:-1]
mplt.register_api_key(apikey)

data = pd.read_csv("2018-05-24T04.59.44.000.in", sep="\t", index_col=False, encoding="ISO-8859-1")
points = set()

for idx, row in data.iterrows():
	split = row["path"].split(" ")
	#print(split)
	path = [string_to_coordinate_pair(x) for x in split[1:]]
	points |= set([path[0], path[-1]])
print(len(points))
dct = {'latitude': [], 'longitude': []}
for point in points:
	dct['latitude'].append(point[0])
	dct['longitude'].append(point[1])
df = pd.DataFrame(data=dct)
mplt.density_plot(df['latitude'], df['longitude'])