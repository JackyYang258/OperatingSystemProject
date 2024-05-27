import heapq

end_time = 0

class Process:
    pid = 0
    def __init__(self, arrival_time, exec_time, deadline):
        self.pid = Process.pid
        Process.pid += 1
        self.arrival_time = arrival_time
        self.start_time = None
        self.deadline = deadline
        self.remaining_exec_time = exec_time
        self.end_time = None
        self.period = None

    def __lt__(self, other):
        # 优先级高的进程优先级队列中权重更高
        if self.priority == other.priority:
            # 如果优先级相同，则截止时限早的进程权重更高
            return self.deadline < other.deadline
        return self.priority > other.priority
    
    def __repr__(self):
        return f"Process(id:{self.pid}, arrival:{self.arrival_time}, deadline:{self.deadline}, begin:{self.start_time}, end:{self.end_time})"

class RMS(Process):
    def __init__(self, arrival_time, exec_time, deadline, period = None):
        super().__init__(arrival_time, exec_time, deadline)
        self.period = period
        self.update_priority()
    
    def update_priority(self):
        if self.period:
            self.priority = 100 - self.period
        else:
            self.priority = 0

class EDF(Process):
    def __init__(self, arrival_time, exec_time, deadline):
        super().__init__(arrival_time, exec_time, deadline)
        self.update_priority()
    
    def update_priority(self):
        self.priority = -self.deadline

class LLF(Process):
    def __init__(self, arrival_time, exec_time, deadline):
        super().__init__(arrival_time, exec_time, deadline)
        self.update_priority()
    
    def update_priority(self):
        self.priority = self.remaining_exec_time - self.deadline
    
class Scheduler:
    def __init__(self, processes=None):
        self.ready_queue = []  # 准备执行的进程队列
        self.current_process = None  # 当前正在执行的进程
        self.current_time = 0  # 当前时间
        self.processes = processes

    def run(self):
        while self.current_time < end_time:
            for process in list(self.processes):
                if process.arrival_time <= self.current_time:
                    heapq.heappush(self.ready_queue, process)
                    processes.remove(process)
                    
            
            
            # 检查是否有更高优先级的进程到达
            if self.current_process and self.ready_queue:
                if self.current_process.priority < self.ready_queue[0].priority:
                    new_process = heapq.heappop(self.ready_queue)
                    self.preempt_current_process(new_process)
                    

            if not self.current_process and self.ready_queue:
                self.current_process = heapq.heappop(self.ready_queue)
                self.current_process.start_time = self.current_time

            if self.current_process:
                self.current_process.remaining_exec_time = self.current_process.remaining_exec_time - 1
                self.current_process.update_priority()
                if self.current_process.remaining_exec_time == 0:
                    self.current_process.end_time = self.current_time+1
                    print(self.current_process)
                    self.current_process = None
                elif self.current_process.deadline - 1 <= self.current_time:
                    print(f"Time {self.current_time+1}: Process {self.current_process.pid} misses deadline")
                    break
            
            self.current_time += 1

    def preempt_current_process(self, next_process):
        # 将当前进程放回就绪队列
        heapq.heappush(self.ready_queue, self.current_process)
        # 更新当前进程为更高优先级的进程
        self.current_process = next_process
        # 更新时间
        self.current_process.start_time = self.current_time

filename = "satisfied.txt"
print("=====================================")
print("EDF")
processes = set()
with open(filename, 'r') as file:
    end_time = int(file.readline())
    for line in file:
        fields = line.split()
        id = int(fields[0])
        is_periodic = int(fields[1]) == 1
        if is_periodic:
            arrival_time = int(fields[2])
            period = int(fields[3])
            exec_time = int(fields[4])
            # For periodic events, create an EDF for each period until max_time
            while arrival_time <= end_time:
                # The deadline is the beginning of the next period
                deadline = arrival_time + period
                processes.add(EDF(arrival_time=arrival_time, exec_time=exec_time, deadline=deadline))
                # The next arrival time is the beginning of the next period
                arrival_time += period
        else:
            arrival_time = int(fields[2])
            deadline = int(fields[3])
            exec_time = int(fields[4])
            processes.add(EDF(arrival_time=arrival_time, exec_time=exec_time, deadline=deadline))

# 实例化调度器
scheduler = Scheduler(processes)

# 运行调度器
scheduler.run()

print("=====================================")
print("RMS")
processes = set()
with open(filename, 'r') as file:
    end_time = int(file.readline())
    for line in file:
        fields = line.split()
        id = int(fields[0])
        is_periodic = int(fields[1]) == 1
        if is_periodic:
            arrival_time = int(fields[2])
            period = int(fields[3])
            exec_time = int(fields[4])
            # For periodic events, create an EDF for each period until max_time
            while arrival_time <= end_time:
                # The deadline is the beginning of the next period
                deadline = arrival_time + period
                processes.add(RMS(arrival_time=arrival_time, exec_time=exec_time, deadline=deadline, period=period))
                # The next arrival time is the beginning of the next period
                arrival_time += period
        else:
            arrival_time = int(fields[2])
            deadline = int(fields[3])
            exec_time = int(fields[4])
            processes.add(RMS(arrival_time=arrival_time, exec_time=exec_time, deadline=deadline))

# 实例化调度器
scheduler = Scheduler(processes)

# 运行调度器
scheduler.run()

print("=====================================")
print("LLF")
processes = set()
with open(filename, 'r') as file:
    end_time = int(file.readline())
    for line in file:
        fields = line.split()
        id = int(fields[0])
        is_periodic = int(fields[1]) == 1
        if is_periodic:
            arrival_time = int(fields[2])
            period = int(fields[3])
            exec_time = int(fields[4])
            # For periodic events, create an EDF for each period until max_time
            while arrival_time <= end_time:
                # The deadline is the beginning of the next period
                deadline = arrival_time + period
                processes.add(LLF(arrival_time=arrival_time, exec_time=exec_time, deadline=deadline))
                # The next arrival time is the beginning of the next period
                arrival_time += period
        else:
            arrival_time = int(fields[2])
            deadline = int(fields[3])
            exec_time = int(fields[4])
            processes.add(LLF(arrival_time=arrival_time, exec_time=exec_time, deadline=deadline))

# 实例化调度器
scheduler = Scheduler(processes)

# 运行调度器
scheduler.run()