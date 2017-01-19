import json
import argparse
import subprocess
import utils
import numpy as np
import time

def run_traceroute(hostnames, num_packets, output_filename):
    r_file = open(output_filename,'w')
    for name in hostnames:
        command = "traceroute -a -q {1} {0} 2>&1".format(name, num_packets)
        trace_output = subprocess.check_output(command, shell = True)
        trace_output = trace_output.splitlines(True)
        r_file.writelines(trace_output[0:])

def parse_traceroute(raw_traceroute_filename, output_filename):
    f = open(raw_traceroute_filename)
    processes = f.read().split('\n')
    result = {}
    result["timestamp"] = str(time.time())
    for i in processes:
        # if i.startswith("traceroute"):
        #     temp = i.split()
        #     result[] = []
        # else:
        # multiple_router = False
        data = i.split()
        if data != []:
            if data[0] == "traceroute": #get website name from the first line
                name = data[2]
                result[name] = []
            if data[1] == "*":
                result[name].append([{"name": "None", "ip": "None", "ASN": "None"}])
            else:
                # result[name].append([])
                if data[0].startswith("["): 
                    # multiple_router = True  
                # if multiple_router:
                    for d in data:
                        if d[0] == "[":
                            result[name][-1].append({"name":str(data[data.index(d)+1]),\
                                "ip":str(data[data.index(d)+2][1:-1]),"ASN":d[3:-1]})
                else:
                    for d in data:
                        if d[0] == "[":
                            result[name].append([{"name":str(data[data.index(d)+1]),\
                                "ip":str(data[data.index(d)+2][1:-1]),"ASN":d[3:-1]}])
            # elif len(data) > 4 + num_packets: 
            # else:
            #     result[name].append([{"name":str(data[2]),"ip":str(data[2][1:-2]),"ASN":str(data[2][3:-2])}])
    r_file = open(output_filename,'w')
    json.dump(result, r_file)

# if __name__ == "__main__":
#     #experiment a
#     run_traceroute(["google.com", "facebook.com", "www.berkeley.edu", "allspice.lcs.mit.edu", "todayhumor.co.kr", "www.city.kobe.lg.jp", "www.vutbr.cz", "zanvarsity.ac.tz"],5,"experiment_a_out")
#     parse_traceroute("experiment_a_out", "tr_a.json")
#     #experiment b
#     #run_traceroute(["tpr-route-server.saix.net", "route-server.ip-plus.net", "route-views.oregon-ix.net", "route-server.eastern.allstream.com"], 2, "experiment_b_out")
#     #parse_traceroute("experiment_b_out", "tr_b.json")
    
#     #run_traceroute(["tpr-route-server.saix.net", "route-server.ip-plus.net", "route-views.oregon-ix.net", "route-server.eastern.allstream.com"], 2, "experiment_b_campus_out")
#     # parse_public_server_traceroute("experiment_b_route_servers_out", "public_test_out")
