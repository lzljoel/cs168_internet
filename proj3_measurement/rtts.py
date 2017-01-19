import json
import argparse
import subprocess
import utils
import matplotlib.pyplot as plot
from matplotlib.backends import backend_pdf
import re
import numpy as np

def run_ping(hostnames, num_packets, raw_ping_output_filename, aggregated_ping_output_filename):
    result = {}
    pingresult = {}
    for name in hostnames:
    	tempList = {}
    	curList = []
    	temp = {}
    	a = 0
        command = "ping -c {1} {0}".format(name, num_packets + 1)
        ping_output = subprocess.check_output(command, shell = True)
        processes = ping_output.split('\n')
        counter = 0
        for i in processes:
        	if i.startswith("PING") or i.endswith("loss") or i.startswith("round-trip") or i.startswith("---") or not i:
        		continue
        	elif i.startswith("Request"):
        		data = i.split()
        		temp[int(data[4])] = -1
        	elif num_packets in result and result[num_packets] != -1:
        		break
        	else:
        		data = i.split()
        		# print(data)
                if int(data[4][9:]) < num_packets:
                    temp[int(data[4][9:])] = float(data[6][5:])
        for i in temp:
        	curList.append(temp[i])
        # print(curList)
       	modifiedList = curList[:]
       	modifiedList.sort()
       	# print(modifiedList)
       	index = 0
       	for i in modifiedList:
       		if i > -1:
       			break
       		index += 1
       	modifiedList = modifiedList[index:]
    	median = np.median(modifiedList)
    	ping_max = max(modifiedList)
    	drop_rate = index/num_packets
    	tempList["drop_rate"] = drop_rate
    	tempList["max_rtt"] = ping_max
    	tempList["median_rtt"] = median

        result[name] = curList
        pingresult[name] = tempList

    r_file1 = open(aggregated_ping_output_filename,'w')
    json.dump(pingresult, r_file1)
    r_file = open(raw_ping_output_filename,'w')
    json.dump(result, r_file)


def plot_median_rtt_cdf(agg_ping_results_filename, output_cdf_filename):
    with open(agg_ping_results_filename) as data_file:    
        data = json.load(data_file)
    # templist = []
    # y_values = []
    # for name in data.keys():
    #     templist.append(data[name]["median_rtt"])
    # counter = 1
    # templist.sort()
    # print(templist)
    # for i in templist:
    #     y_values.append(counter/len(templist))
    #     counter += 1
    x_values = []
    for name in data.keys():
        x_values.append(data[name]["median_rtt"])
    x_values.sort()
    y_values = np.arange(len(x_values))/float(len(x_values))
    plot.plot(x_values, y_values, label="My data")
    plot.legend() # This shows the legend on the plot.
    plot.grid() # Show grid lines, which makes the plot easier to read.
    plot.xlabel("x axis!") # Label the x-axis.
    plot.ylabel("y axis!") # Label the y-axis.
    plot.show()
    my_filepath = output_cdf_filename
    with backend_pdf.PdfPages(my_filepath) as pdf:
        pdf.savefig()
def plot_ping_cdf(raw_ping_results_filename, output_cdf_filename):
    with open(raw_ping_results_filename) as data_file:    
        data = json.load(data_file)
    print("asdasdsada")
    for name in data.keys():
        x_values = data[name]
        x_values.sort()
    print(x_values)
    y_values = np.arange(0.0,1.0, 1.0/float(len(x_values)))
    # templist = []
    # y_values = []
    # for name in data.keys():
    #     templist = data[name]
    # templist.sort()
    # index = 0
    # for i in templist:
    #         if i > -1:
    #             break
    #         index += 1
    # templist = templist[index:]
    # counter = 1
    # print(templist)
    # for i in templist:
    #     y_values.append(counter/len(templist))
    #     counter += 1
    plot.plot(x_values,y_values, label="My data")
    plot.legend() # This shows the legend on the plot.
    plot.grid() # Show grid lines, which makes the plot easier to read.
    plot.xlabel("x axis!") # Label the x-axis.
    plot.ylabel("y axis!") # Label the y-axis.
    plot.show()
    my_filepath = output_cdf_filename
    with backend_pdf.PdfPages(my_filepath) as pdf:
        pdf.savefig()

if __name__ == "__main__":
    with open("alexa_top_100") as data_file:
        top100 =  [line.strip() for line in data_file.readlines()]
    run_ping(top100, 10, "rtt_a_raw.json", "rtt_a_agg.json")
    plot_median_rtt_cdf("rtt_a_agg.json", "part1-1.pdf")
    #plot_ping_cdf("rtt_b_raw.json", "part1-2.pdf")
