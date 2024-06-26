#include<iostream>
#include<vector>
#include<queue>
#include<mutex>
#include<thread>
#include<semaphore>
#include<fstream>
#include<chrono>
using namespace std;

// define numbers
const int counter_num = 3;
const int maxnum_customer = 20; // max num of customer in wait

// define structures
// input of customer
struct customer_in
{
    int cus_no; 
    int time_in; 
    int time_serve; 
};

struct customer_out
{
    double time_in; 
    double time_beginserve; 
    int counter_NO; 
    double time_served; // time when finish serve
};

int customer_num = 0; 
int get_num = 0;
int queue_length = 0;

vector <customer_in> customers_in;
vector <customer_out> customers_out;
queue <int> wait_queue;

mutex mtx_get_num; // mutex of customer number
mutex mtx_output; // mutex of output
counting_semaphore<maxnum_customer> sema_wait(0); // semaphor of waiting customer(P) counter(V)

// set start time
chrono::time_point<chrono::system_clock> time_begin = chrono::system_clock::now();

// process of customer
void Customer(int PV) {
    this_thread::sleep_for(chrono::seconds(customers_in[PV].time_in)); // wait for arrive 

    mtx_get_num.lock();

    chrono::time_point<chrono::system_clock> time_in = chrono::system_clock::now();
    customers_out[PV].time_in = chrono::duration<double>(time_in - time_begin).count();

    get_num ++;
    if (queue_length < maxnum_customer) {
        queue_length ++;
    }
    else {
        mtx_output.lock();
        cout << "NO." << PV + 1 << " customer is leaving" << endl;
        mtx_output.unlock();
        mtx_get_num.unlock();
        return;
    }
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

    //start threads
    vector<thread> customer_threads;
    for (int j = 0; j < customer_num; j++) {
        customer_threads.push_back(thread(Customer, j));
    }

    vector<thread> counter_threads;
    for (int j = 0; j < counter_num; j++) {
        counter_threads.push_back(thread(Counter, j));
    }

    // wait all threads to end
    for (int j = 0; j < customer_num; j++) {
        customer_threads[j].join();
    }

    for (int j = 0; j < counter_num; j++) {
        counter_threads[j].join();
    }

    cout << "max number of customer:" << maxnum_customer << endl;
    cout << "serve information" << endl;
    cout << "No\ttime_in\tserve_start\tserve_end\tcounter NO." << endl;

    // ����˿ͽӴ����
    for (int k = 0; k < customer_num; k++) {
        cout << k << "\t\t" << customers_out[k].time_in << "\t\t" << customers_out[k].time_beginserve << "\t\t" << customers_out[k].time_served << "\t\t" << customers_out[k].counter_NO << endl;
    }

    file_input.close();
    return 0;
}
