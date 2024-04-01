
import simpy
import os
import time
import csv

import ast
from tqdm import tqdm,trange
from utils import time_to_seconds,seconds_to_time
from utils import truncated_normal_numba
import pandas as pd
from ast import literal_eval
import argparse
from io import StringIO
parser=argparse.ArgumentParser(description="input and output files")

### input 
parser.add_argument("--train_time_table", type=str, default="train_time_table.csv")
parser.add_argument("--line_table", type=str, default="line.csv")
parser.add_argument("--station_list", type=str, default="station.csv")
parser.add_argument("--od_data", type=str, default="od_data.csv") # od_data.csv

### output
parser.add_argument("--output_train_dir", type=str, default="train")
parser.add_argument("--train_log", type=str, default="train_log.csv")
parser.add_argument("--output_station_train_dir",type=str,default="station_train")
parser.add_argument("--output_station_dir",type=str,default="station110")
parser.add_argument("--output_travel_chain", type=str, default="people_travel_chain.csv")
parser.add_argument("--all_log",default=True)
parser.add_argument("--log_file",type=str,default="logfile.csv",help="log the travel time of passengers")

args = parser.parse_args()
log_memory=StringIO()
log_writer=csv.writer(log_memory)
travel_memory=StringIO()
travel_chain=csv.writer(travel_memory)

if args.all_log==True:
    Folder_list = [args.output_station_dir,args.output_station_train_dir,args.output_train_dir]
    for folder in Folder_list:
        if not os.path.exists(folder):
            os.makedirs(folder)


env = simpy.Environment()

class Station:
    def __init__(self, env, id, line_name,channels_in,channels_out,walk_in=[],walk_out=[],walk_change=None):
        self.id = id
        self.env = env
        self.train_id = None
        self.line_name=line_name
        self.channels_in=channels_in
        self.channels_out=channels_out
        self.walk_in=walk_in
        self.walk_out=walk_out

        self.passengers_memory=StringIO()
        self.passengers_counter=csv.writer(self.passengers_memory)
        self.passengers_flow=StringIO()
        self.passengers_flow_counter=csv.writer(self.passengers_flow)
        for items in line_name:
            setattr(self,items,self.train_of_station(self.env,self,line=items))
        for name,channels_in1,channels_out1,walk_in1,walk_out1 in zip(line_name,channels_in,channels_out,walk_in,walk_out):
            setattr(self,name+"_walk",self.time_of_walk(self.env))
            for id,time in zip(channels_in1,walk_in1):
                setattr(getattr(self,name+"_walk"),"walk_inlist"+str(id),[])
               
                setattr(getattr(self,name+"_walk"),"walk_in"+str(id),getattr(self,name+"_walk").create_truncated_normal_function(time))
            for id,time in zip(channels_out1,walk_out1):
               
                setattr(getattr(self,name+"_walk"),"walk_outlist"+str(id),[])
                setattr(getattr(self,name+"_walk"),"walk_out"+str(id),getattr(self,name+"_walk").create_truncated_normal_function(time))
    
        if walk_change is not None:
            for name1,time_walk in zip(line_name,walk_change):
                for name2,time in zip(line_name,time_walk) : 
                        setattr(getattr(self,name1+"_walk"),name1+"_to_"+name2,getattr(self,name1+"_walk").create_truncated_normal_function(time))
        
        self.capacity = simpy.Container(self.env, init=0)  
        self.people_in=simpy.Container(self.env, init=0)
        self.env.process(self.passengers())
        self.env.process(self.counters())
    def counters(self):
        
        
        yield self.env.timeout(18000)
        while True:
            self.passengers_flow_counter.writerow([seconds_to_time(self.env.now),self.people_in.level])   
            self.people_in=simpy.Container(self.env, init=0)
            yield self.env.timeout(600)
            
            

                    
                
    class time_of_walk:
        def __init__(self,env):
            self.env=env
            self.timelist=[]
        
        def create_truncated_normal_function(self, params): 
           
            def truncated_normal():
        
                samples =truncated_normal_numba(params[0], params[1], params[2],params[3])
                
                return int(samples[0])
           
            return truncated_normal
            

    class train_of_station:
        def __init__(self, env, station,line):
            self.env = env
            self.line=line
            self.station = station
            self.train_id = None 
            self.train_in_station = self.env.event()
            self.train_attend_station_event = self.env.event()
            self.train_leave_station_event = self.env.event()
            self.train_state_memory=StringIO()
            self.train_state_log=csv.writer(self.train_state_memory)
            self.env.process(self.get_train())
           

        def get_train(self):
                
                while True:
                   
                    yield self.train_attend_station_event
                    self.train_in_station.succeed()
                 
                    if args.all_log==True:
                        self.train_state_log.writerow([f"{seconds_to_time(self.env.now)},{self.train_id.id},attend"])
                       
                 
                    yield self.train_leave_station_event
                 
                    if args.all_log==True:
                        self.train_state_log.writerow([f"{seconds_to_time(self.env.now)},{self.train_id.id},leave"])
                       
                    self.train_in_station = self.env.event()
                    self.train_id = None
                    self.train_leave_station_event = self.env.event()
        def train_log(self):
            yield self.env.timeout(86300)
            with open(f"{args.output_station_train_dir}/{self.station.id}_{self.line}.csv", 'a+') as station_log:
                self.train_state_content=self.train_state_memory.getvalue()
                station_log.write(self.train_state_content)
              
    def passengers(self):
        if args.all_log==True:
            yield self.env.timeout(18000)
            while True:
                yield self.env.timeout(60)
                self.passengers_counter.writerow([f"time:{seconds_to_time(self.env.now)},passengers:{self.capacity.level}"])

                    
class Train:
    def __init__(self, id, env, travel_line,linename,depart_time,stand_travel_time):
        self.id = id
        self.env = env
        self.line = line[travel_line]

        self.location = 0
        self.linename=linename
        self.station_now = eval(self.line[0])
        self.departure_time=depart_time
        self.stand_travel_time=stand_travel_time
        self.capacity = simpy.Container(self.env, init=0)
        self.passenger_on_train = self.passengers(self)
        self.env.process(self.leave())
        self.event_list=[]
        self.travel_state = self.env.event()
        self.stop_state = self.env.event()
    class passengers:
        def __init__(self, train):
            self.env = train.env
            self.train = train
            self.passengers_memory=StringIO()
            self.passengers_log=csv.writer(self.passengers_memory)

            self.env.process(self.log_passengers())
            
        def log_passengers(self):
            if args.all_log==True:
                yield self.env.timeout(18000)
                
                while True:
                   
                    self.passengers_log.writerow([f"time:{seconds_to_time(self.env.now)},passengers:{self.train.capacity.level}"])
                    yield self.train.stop_state 
                    yield self.train.travel_state
           
    def leave(self):
        yield self.env.timeout(self.departure_time)
        getattr(self.station_now, self.linename).train_attend_station_event.succeed()
        setattr(getattr(eval(self.line[self.location]),self.linename),"train_id",self) 
        self.event_list.append(f"attend_time:{seconds_to_time(self.env.now)}\tlocation:{eval(self.line[self.location]).id}\t")
        yield self.env.timeout(self.stand_travel_time[0][0])
        self.stop_state.succeed() 
        setattr(getattr(self.station_now, self.linename),"train_attend_station_event",self.env.event())
        getattr(self.station_now, self.linename).train_leave_station_event.succeed()
        self.event_list.append(f"leave_time:{seconds_to_time(self.env.now)}\tlocation:{eval(self.line[self.location]).id}\t")
        self.env.process(self.travel())
    def travel(self):
        while self.location < (len(self.line) - 2):
            yield self.env.timeout(self.stand_travel_time[self.location][1])
            self.travel_state.succeed()
            self.location += 1
            self.station_now = eval(self.line[self.location])
            getattr(self.station_now, self.linename).train_attend_station_event.succeed()
            setattr(getattr(eval(self.line[self.location]), self.linename), "train_id", self)
            self.event_list.append(f"attend_time:{seconds_to_time(self.env.now)}\tlocation:{eval(self.line[self.location]).id}\t")
            self.stop_state=self.env.event() 
            yield self.env.timeout(self.stand_travel_time[self.location][0])
            self.stop_state.succeed() 
            self.travel_state=self.env.event()
            setattr(getattr(self.station_now, self.linename), "train_attend_station_event", self.env.event())
            getattr(self.station_now, self.linename).train_leave_station_event.succeed()
            self.event_list.append(f"leave_time:{seconds_to_time(self.env.now)}\tlocation:{eval(self.line[self.location]).id}\t")
        self.stop_state=self.env.event()
        yield self.env.timeout(self.stand_travel_time[self.location][1])
        self.travel_state.succeed()
        self.location += 1
        self.station_now = eval(self.line[self.location])
        self.event_list.append(f"attend_time:{seconds_to_time(self.env.now)}\tlocation:{eval(self.line[self.location]).id}\t")
        yield self.env.timeout(self.stand_travel_time[self.location][0])
        self.travel_state=self.env.event()
        self.stop_state.succeed()
        self.event_list.append(f"leave_time:{seconds_to_time(self.env.now)}\tlocation:{eval(self.line[self.location]).id}\t")
        if args.all_log==True:
            self.passenger_content=self.passenger_on_train.passengers_memory.getvalue()
            with open(f"{args.output_train_dir}/{self.id}passengers.txt", "a+") as log:
                log.write(self.passenger_content)
            

            with open(f"{args.train_log}","a+") as log:
                log.write(f"{self.id}\t")
                for items in self.event_list:
                    log.write(items)
                log.write("\n")

class Person:
    def __init__(self, id, env, origin_time, station_in,channel_in, station_out, channel_out, line_on,line_off,line_change=None,station_change=None,odcost=None):
        self.id = id
        self.env = env
        self.time = origin_time
        self.station_in = eval(station_in)
        self.train = None
        self.station_out = station_out
        self.channel_in = channel_in
        self.channel_out = channel_out
        self.location = None
        self.line_on=line_on
        self.line_now=line_on
        self.line_off=line_off
        self.station_change=station_change
        self.line_change=line_change
        self.travel_start_time=origin_time
        self.travel_event=[]
        self.odcost=odcost
      
        if self.station_change is not None:
       
            self.change_times=len(self.station_change)
          
            self.has_changed=0
        self.env.process(self.on_station())
 
    def on_station(self):
    
        yield self.env.timeout(self.time)
   
        self.station_in.capacity.put(1)
        self.station_in.people_in.put(1)

        self.travel_event.append(f"time:{seconds_to_time(self.env.now)},passenger_attend_station:{getattr(self.station_in,'id')},")
 
        self.walk_in_time=getattr(getattr(self.station_in,self.line_on+"_walk"),"walk_in"+str(self.channel_in))()
        
        getattr(self.station_in,self.line_on+"_walk"),"walk_in"+str(self.channel_in)
        yield self.env.timeout(getattr(getattr(self.station_in,self.line_on+"_walk"),"walk_in"+str(self.channel_in))())
  
        self.travel_event.append(f"time:{seconds_to_time(self.env.now)},attend_stage,")
  
        self.location = getattr(self.station_in,self.line_on)
 

        self.env.process(self.on_train())


    def on_train(self):
      
        yield self.location.train_in_station
        self.train = self.location.train_id
      
        self.travel_event.append(f"time:{seconds_to_time(self.env.now)},attend:{getattr(self.train,'id')},")
    
        self.station_in.capacity.get(1)
    
        self.train.capacity.put(1)
      
        if self.station_change is not None:           
            if self.has_changed<self.change_times:
                self.line_now=self.line_change[self.has_changed]
                self.env.process(self.passenger_travel(self.station_change[self.has_changed]))
            else:
                self.env.process(self.passenger_travel(self.station_out))
        else:
            self.env.process(self.passenger_travel(self.station_out))

    def passenger_travel(self,destination):
        if destination in self.train.line:
            while self.train.station_now.id != destination:
                
                yield self.train.stop_state
                yield self.train.travel_state
            self.location = destination
            if self.station_change is not None: 
                if self.has_changed<self.change_times:
                    self.location = getattr(eval(destination),self.line_change[self.has_changed]) 
            self.env.process(self.off_train(destination))
        else:
            while self.train.station_now.id != self.train.line[-1]:
                yield self.train.stop_state
                yield self.train.travel_state
            self.travel_event.append(f"time:{seconds_to_time(self.env.now)},attend_station:{self.train.line[-1]},")
            self.location=getattr(eval(self.train.line[-1]),self.line_now)
            self.env.process(self.on_train())
  
    def off_train(self,destination):
    
        self.travel_event.append(f"time:{seconds_to_time(self.env.now)},attend_station:{self.train.station_now.id},")
        self.train.capacity.get(1)
        eval(destination).capacity.put(1)
        eval(destination).people_in.put(1)

        if self.location==self.station_out:
            self.down_train_time=self.env.now
            yield self.env.timeout(getattr(getattr(self.station_in,self.line_on+"_walk"),"walk_out"+str(self.channel_out))())
            
            eval(destination).capacity.get(1)
            
            self.travel_event.append(f"time:{seconds_to_time(self.env.now)},leave_station:{self.location},")
   
            self.cost_time=self.env.now-self.travel_start_time
            
            log_writer.writerow([self.id,self.odcost,self.cost_time])
            
            
       
            
            if args.all_log==True:
                travel_chain.writerow([self.id,self.travel_event])

            del self

        else:
     
            yield self.env.timeout(getattr(getattr(eval(destination),self.line_on+"_walk"),self.line_on+"_to_"+self.line_change[self.has_changed])())
            self.travel_event.append(f"time:{seconds_to_time(self.env.now)},pass_transfer_passage:{destination},")
       
            self.station_in=eval(destination)
            self.has_changed+=1
            self.line_on=self.line_change[self.has_changed-1]
      
            self.env.process(self.on_train())
          

stations=[]
with open(args.station_list) as f:
    reader = csv.reader(f)
    for row in reader:
        station=Station(env=env,id=str(row[0]),line_name=row[1].split(","),channels_in=ast.literal_eval(row[2]), channels_out=ast.literal_eval(row[3]),walk_in=ast.literal_eval(row[5]),walk_out=ast.literal_eval(row[6]),walk_change=ast.literal_eval(row[7]) if row[7] != '' else None)
        stations.append(station)
        globals()[station.id] = station

line={}
line_travel_time = {}
with open(args.line_table) as f:
    reader = csv.reader(f)
    for items in reader:
        line[items[0]]=items[1].split(",")

train_list = []
csv_file_path = args.train_time_table
df = pd.read_csv(csv_file_path,header=None)

for index,row in df.iterrows(): 

    train_list.append(Train(id=index,env=env,travel_line=row[1],linename=row[2],depart_time=time_to_seconds(row[0]),stand_travel_time=literal_eval(row[3])))

people = []
with open(args.od_data) as f:
    memory_file = f.read()
memory_file = StringIO(memory_file)
memory_file_content = csv.reader(memory_file)

for row in tqdm(memory_file_content ): 
        people.append(Person(id=row[0], env=env, origin_time=int(row[2]), station_in=row[6],channel_in=row[7], station_out=row[8],channel_out=row[9],line_on=row[10],line_off=row[11],line_change=ast.literal_eval(row[12]) if row[12] != '' else None,station_change=ast.literal_eval(row[13]) if row[13] != '' else None,odcost=int(row[5])))
memory_file.close()
class timecounters:
    def __init__(self,env):
        self.env = env
        self.time=self.env.process(self.time_pass())
    def time_pass(self):
        yield self.env.timeout(18000)
        for _ in trange(68400):
                yield self.env.timeout(1)
time1=timecounters(env)
env.run(until=86400)
timec1=time.time()
log_content = log_memory.getvalue()
with open(args.log_file, 'a+', newline='') as file:
    file.write(log_content)


log_memory.close()

travel_content = travel_memory.getvalue()
with open(args.output_travel_chain,'a+', newline='') as file:
    file.write(travel_content)


travel_memory.close()

for items in stations:
    passengers_content=items.passengers_memory.getvalue()
    with open(f'{args.output_station_dir}/{items.id}.txt', 'w') as file:
        file.write(passengers_content)
    flow_content=items.passengers_flow.getvalue()
    with open(f'{args.output_station_dir}/{items.id}_count.txt',"w") as file:
        file.write(flow_content)
    items.passengers_memory.close()
timec2=time.time()
print(timec2-timec1)


