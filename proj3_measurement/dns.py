import json
import argparse
import subprocess
import utils
import re
import numpy as np

def run_dig(hostname_filename, output_filename, dns_query_server=None):
    result = []
    tempresult = []
    boolean = False
    for name in hostname_filename:
        returndict = {}
        if dns_query_server == None:
            command = "dig +trace +tries=1 +nofail {0}".format(name)
        else:
            command = "dig {0} @{1}".format(name, dns_query_server)
            boolean = True
    ping_output = subprocess.check_output(command, shell = True)
    processes = ping_output.split('\n')        
    if boolean:
        querytime = int(processes[-6].split()[-2])
    for i in processes:
        data = i.split()
        if not i:
            continue
        elif data[2] == "IN":
            resultdict = {}
            resultdict["Queried name"] = data[0]
            resultdict["Data"] = data[4]
            resultdict["Type"] = data[3]
            resultdict["TTL"] = int(data[1])
            tempresult.append(resultdict)

        elif i[2] == str("<"):
            returndict["Name"] = data[-1]
            returndict["Success"] = True
            returndict["Queries"] = []
        elif i[3] == str("R"):
            tempdict = {}
            tempdict["Time in millis"] = int(data[-2])
            tempdict["Answer"] = tempresult
            tempresult = []
            returndict["Queries"].append(tempdict)
        elif boolean and data[1] == "MSG":
            tempdict = {}
            tempdict["Time in millis"] = querytime
            tempdict["Answer"] = tempresult
            tempresult = []
            returndict["Queries"].append(tempdict)
    result.append(returndict)
    r_file1 = open(output_filename,'w')
    json.dump(result, r_file1)

def get_average_ttls(filename):
    with open(filename) as data_file:    
        data = json.load(data_file)
    avg_ttls = []
    root_servers = []
    tld_servers = []
    others = []
    terminating_entries = []
    avg_root = []
    avg_tld = []
    avg_others = []
    avg_terminating = []
    for d in data:
        for q in d["Queries"]:
            for answer in q["Answers"]:
                if "root" in answer["Data"]:
                    root_servers.append(answer["TTL"])
                elif "tld" in answer["Data"]:
                    tld_servers.append(answer["TTL"])
                elif answer["Type"] == "CNAME" or answer["Type"] == "A":
                    terminating_entries.append(answer["TTL"])
                else:
                    others.append(answer["TTL"])   
            avg_root.append(np.mean(root_servers))
            avg_tld.append(np.mean(tld_servers))
            avg_others.append(np.mean(others))        
            avg_terminating.append(np.mean(terminating_entries))
    avg_ttls.append(np.mean(avg_root))
    avg_ttls.append(np.mean(avg_tld))
    avg_ttls.append(np.mean(avg_others))
    avg_ttls.append(np.mean(avg_terminating))
    return avg_ttls


def get_average_times(filename):
    with open(filename) as data_file:    
        data = json.load(data_file)
    avg_times = []
    final_request = []
    resolve_times = []
    for d in data:
        for q in d["Queries"]:
            travel_time = 0
            for answer in q["Answers"]:
                if answer["Type"] == "CNAME" or answer["Type"] == "A":
                    final_request.append(q["Time in millis"])
                else:
                    travel_time += q["Time in millis"]
            resolve_times.append(travel_time)
    avg_times.append(resolve_times)
    avg_times.append(np.mean(final_request))
    return avg_times

def generate_time_cdfs(json_filename, output_filename):
    pass

def count_different_dns_responses(filename1, filename2):
    difference = [] #returned list
    return difference









