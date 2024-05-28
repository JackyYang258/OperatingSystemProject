import os
import random
import multiprocessing
import time

smallest_length = 500000
start_time1 = 0
# 生成随机数数据文件
def generate_data_file(file_path, num):
    with open(file_path, 'w') as f:
        for _ in range(num):
            f.write(str(random.randint(1, 1000000)) + '\n')

# 快速排序算法的辅助函数，用于分割数组
def partition(arr, low, high, judge):
    time1 = time.time()
    i, j = low, high
    while i < j:
        while i < j and arr[j] >= arr[low]:
            j -= 1  # 从右向左找首个小于基准数的元素
        while i < j and arr[i] <= arr[low]:
            i += 1  # 从左向右找首个大于基准数的元素
        # 元素交换
        arr[i], arr[j] = arr[j], arr[i]
    # 将基准数交换至两子数组的分界线
    arr[i], arr[low] = arr[low], arr[i]
    if judge:
        print("partition time:", time.time()-time1)
    return i 

# 普通的快速排序函数
def quick_sort(arr, low, high):
    if low < high:
        pi = partition(arr, low, high, False)
        quick_sort(arr, low, pi - 1)
        quick_sort(arr, pi + 1, high)

# 递归快速排序函数，用于在递归的每一步创建子进程
def quick_sort_process(arr, low, high, lock):
    if low < high:
        left_process, right_process = None, None
        pi = partition(arr, low, high, True)
        # 创建子进程处理左边的数组
        if low < pi - 1:
            if pi - 1 - low < smallest_length:
                left = True
            else:
                left = False
                print(f"创建子进程处理数组[{low}, {pi - 1}]")
                print("time:", time.time()-start_time1)
                left_process = multiprocessing.Process(target=quick_sort_process, args=(arr, low, pi - 1, lock))
        # 创建子进程处理右边的数组
        if pi + 1 < high:
            if high - pi - 1 < smallest_length:
                right = True
            else:
                right = False
                print(f"创建子进程处理数组[{pi + 1}, {high}]")
                print("time:", time.time()-start_time1)
                right_process = multiprocessing.Process(target=quick_sort_process, args=(arr, pi + 1, high, lock))
        left_process.start() if left_process else None
        right_process.start() if right_process else None
        if left:
            start_time2 = time.time()
            quick_sort(arr, low, pi - 1)
            end_time2 = time.time()
            print(f"neibu zuo普通快速排序耗时：{end_time2 - start_time2:.2f}s", low, pi - 1)
        if right:
            start_time2 = time.time()
            quick_sort(arr, pi + 1, high)
            end_time2 = time.time()
            print(f"neibu you普通快速排序耗时：{end_time2 - start_time2:.2f}s", pi + 1, high)
        # 等待子进程完成
        left_process.join() if left_process else None
        right_process.join() if right_process else None
    
# 子进程处理数据并排序
def process_data_and_sort(shared_data, start, end, lock):
    quick_sort_process(shared_data, start, end - 1, lock)

if __name__ == "__main__":
    shared = False
    
    file_path = "data.txt"
    num_data = 1000000
    generate_data_file(file_path, num_data)
    with open(file_path, 'r') as f:
        data = [int(line.strip()) for line in f]

    shared_data = multiprocessing.Array('i', data)

    # 使用锁进行进程间同步
    lock = multiprocessing.Lock()
    start_time1 = time.time()
    # 创建主进程处理数据
    if shared:
        p = multiprocessing.Process(target=process_data_and_sort, args=(shared_data, 0, len(data)-1, lock))
    else:
        p = multiprocessing.Process(target=process_data_and_sort, args=(data, 0, len(data)-1, lock))
    print(f"创建主进程处理数组[0, {len(data) - 1}]")
    p.start()
    p.join()
    end_time1 = time.time()
    print(f"多进程快速排序耗时：{end_time1 - start_time1:.2f}s")
    
    with open(file_path, 'r') as f:
        data = [int(line.strip()) for line in f]
    start_time2 = time.time()
    quick_sort(data, 0, len(data)-1)
    end_time2 = time.time()
    print(f"普通快速排序耗时：{end_time2 - start_time2:.2f}s")
    
    # 从共享内存中读取排序后的数据
    sorted_data = list(shared_data)
    
    # 删除数据文件
    os.remove(file_path)