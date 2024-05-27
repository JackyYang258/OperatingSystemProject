#include<iostream>
#include<vector>
#include<queue>
#include<mutex>
#include<thread>
#include<semaphore>
#include<fstream>
#include<chrono>
using namespace std;

// 定义柜台数量、最大人数
const int counter_num = 3;
const int maxnum_customer = 20;

// 以结构体的形式将输入读入
struct customer_in
{
    int cus_no; // 顾客编号
    int time_in; // 进入时间
    int time_serve; // 需要服务的时间长度
};

// 以结构体的形式读出输出
struct customer_out
{
    double time_in; // 进入时间
    double time_beginserve; // 开始服务的时间
    int counter_NO; // 柜台号
    double time_served; // 结束服务时间
};

int customer_num = 0; // 顾客总数
int get_num = 0;

vector <customer_in> customers_in;
vector <customer_out> customers_out;
queue <int> wait_queue;

mutex mtx_counter[counter_num]; // 各柜台互斥锁
mutex mtx_get_num; // 排号机互斥锁
mutex mtx_output; // 输出互斥锁
counting_semaphore<maxnum_customer> sema_wait(0);

// 计时开始
chrono::time_point<chrono::system_clock> time_begin = chrono::system_clock::now();

// 顾客线程函数
void Customer(int PV) {
    this_thread::sleep_for(chrono::seconds(customers_in[PV].time_in)); // 模拟进入的时间

    // 占用取号机
    mtx_get_num.lock();

    chrono::time_point<chrono::system_clock> time_in = chrono::system_clock::now();
    customers_out[PV].time_in = chrono::duration<double>(time_in - time_begin).count();

    get_num ++;
    wait_queue.push(PV);

    mtx_output.lock();
    cout << "NO." << PV + 1 << " customer get number" << endl;
    mtx_output.unlock();

    mtx_get_num.unlock();
    sema_wait.release();

}

void Counter(int PV) {
    int cus_num;
    while (true)
    {   
        sema_wait.acquire();
        mtx_get_num.lock();

        cus_num = wait_queue.front();
        wait_queue.pop();
        mtx_get_num.unlock();
        
        chrono::time_point<chrono::system_clock> time_start = chrono::system_clock::now();
        this_thread::sleep_for(chrono::seconds(customers_in[cus_num].time_serve)); 
        chrono::time_point<chrono::system_clock> time_finish = chrono::system_clock::now();

        customers_out[cus_num].time_beginserve = chrono::duration<double>(time_start - time_begin).count();
        customers_out[cus_num].time_served = chrono::duration<double>(time_finish - time_begin).count();
        customers_out[cus_num].counter_NO = PV;
        if (wait_queue.empty() && get_num == customer_num)
            break;
    }
}

int main() {
    ifstream file_input;
    file_input.open("input.txt", ios::in);
    if (!file_input.is_open()) {
        cout << "input failed!" << endl;
        exit(0);
    }

    customer_in customer_input;
    while (file_input >> customer_input.cus_no >> customer_input.time_in >> customer_input.time_serve) {
        customers_in.push_back(customer_input);
        customer_num++;
    }
    customers_out.resize(customer_num);

    // 创建顾客线程
    vector<thread> customer_threads;
    for (int j = 0; j < customer_num; j++) {
        customer_threads.push_back(thread(Customer, j));
    }

    vector<thread> counter_threads;
    for (int j = 0; j < counter_num; j++) {
        counter_threads.push_back(thread(Counter, j));
    }

    // 等待所有顾客被服务完毕
    for (int j = 0; j < customer_num; j++) {
        customer_threads[j].join();
    }

    for (int j = 0; j < counter_num; j++) {
        counter_threads[j].join();
    }

    cout << "允许接待的最大顾客数量:" << maxnum_customer << endl;
    cout << "全体顾客接待情况：" << endl;
    cout << "顾客编号\t进入时间\t开始时间\t结束服务时间\t柜台号" << endl;

    // 输出顾客接待情况
    for (int k = 0; k < customer_num; k++) {
        cout << k << "\t\t" << customers_out[k].time_in << "\t\t" << customers_out[k].time_beginserve << "\t\t" << customers_out[k].time_served << "\t\t" << customers_out[k].counter_NO << endl;
    }

    file_input.close();
    return 0;
}
