"""threading模块中提供了5种最常见的锁，下面是按照功能进行划分：

同步锁：lock（一次只能放行一个），同步锁一次只能放行一个线程，一个被加锁的线程在运行时不会将执行权交出去，
只有当该线程被解锁时才会将执行权通过系统调度交由其他线程。

方法	                                            描述
threading.Lock()	                            返回一个同步锁对象
lockObject.acquire(blocking=True, timeout=1)	上锁，当一个线程在执行被上锁代码块时，将不允许切换到其他线程运行，默认锁失效时间为1秒
lockObject.release()	                        解锁，当一个线程在执行未被上锁代码块时，将允许系统根据策略自行切换到其他线程中运行
lockObject.locaked()	                        判断该锁对象是否处于上锁状态，返回一个布尔值

递归锁：rlock（一次只能放行一个），递归锁是同步锁的一个升级版本，在同步锁的基础上可以做到连续重复使用多次acquire()
后再重复使用多次release()的操作，但是一定要注意加锁次数和解锁次数必须一致，否则也将引发死锁现象。

方法	                                            描述
threading.RLock()	                            返回一个递归锁对象
lockObject.acquire(blocking=True, timeout=1)	上锁，当一个线程在执行被上锁代码块时，将不允许切换到其他线程运行，默认锁失效时间为1秒
lockObject.release()	                        解锁，当一个线程在执行未被上锁代码块时，将允许系统根据策略自行切换到其他线程中运行
lockObject.locaked()	                        判断该锁对象是否处于上锁状态，返回一个布尔值


条件锁：condition（一次可以放行任意个），条件锁是在递归锁的基础上增加了能够暂停线程运行的功能。
并且我们可以使用wait()与notify()来控制线程执行的个数。

方法	                                            描述
threading.Condition()                           返回一个条件锁对象
lockObject.acquire(blocking=True, timeout=1)	上锁，当一个线程在执行被上锁代码块时，将不允许切换到其他线程运行，默认锁失效时间为1秒
lockObject.release()	                        解锁，当一个线程在执行未被上锁代码块时，将允许系统根据策略自行切换到其他线程中运行
lockObject.wait(timeout=None)	                将当前线程设置为“等待”状态，只有该线程接到“通知”或者超时时间到期之后才会继续运行，在“等待”状态下的线程将允许系统根据策略自行切换到其他线程中运行
lockObject.wait_for(predicate, timeout=None)	将当前线程设置为“等待”状态，只有该线程的predicate返回一个True或者超时时间到期之后才会继续运行，在“等待”状态下的线程将允许系统根据策略自行切换到其他线程中运行。注意：predicate参数应当传入一个可调用对象，且返回结果为bool类型
lockObject.notify(n=1)	                        通知一个当前状态为“等待”的线程继续运行，也可以通过参数n通知多个
lockObject.notify_all()	                        通知所有当前状态为“等待”的线程继续运行


事件锁：event（一次全部放行），事件锁是基于条件锁来做的，它与条件锁的区别在于一次只能放行全部，不能放行任意个数量的子线程继续运行。

方法	                                            描述
threading.Event()	                            返回一个事件锁对象
lockObject.clear()	                            将事件锁设为红灯状态，即所有线程暂停运行
lockObject.is_set()	                            用来判断当前事件锁状态，红灯为False，绿灯为True
lockObject.set()	                            将事件锁设为绿灯状态，即所有线程恢复运行
lockObject.wait(timeout=None)	                将当前线程设置为“等待”状态，只有该线程接到“绿灯通知”或者超时时间到期之后才会继续运行，在“等待”状态下的线程将允许系统根据策略自行切换到其他线程中运行

信号量锁：semaphore（一次可以放行特定个），信号量锁也是根据条件锁来做的，它与条件锁和事件锁的区别如下：
    条件锁：一次可以放行任意个处于“等待”状态的线程
    事件锁：一次可以放行全部的处于“等待”状态的线程
    信号量锁：通过规定，成批的放行特定个处于“上锁”状态的线程

方法	                                             描述
threading.Semaphore()	                         返回一个信号量锁对象
lockObject.acquire(blocking=True, timeout=1)	 上锁，当一个线程在执行被上锁代码块时，将不允许切换到其他线程运行，默认锁失效时间为1秒
lockObject.release()	                         解锁，当一个线程在执行未被上锁代码块时，将允许系统根据策略自行切换到其他线程中运行

list、tuple、dict本身就属于线程安全，对这三种容器操作，不必考虑线程安全问题。
"""
import threading


def add():
    global num
    for i in range(10_000_000):
        num += 1


def sub():
    global num
    for i in range(10_000_000):
        num -= 1


def lock_add():
    with lock:
        global num
        for i in range(10_000_000):
            num += 1


def lock_sub():
    with lock:
        global num
        for i in range(10_000_000):
            num -= 1


def rlock_add():
    with rlock:
        global num
        for i in range(10_000_000):
            num += 1


def rlock_sub():
    with rlock:
        global num
        for i in range(10_000_000):
            num -= 1


def task():
    global currentRunThreadNumber
    thName = threading.currentThread().name
    condLock.acquire()  # 上锁
    print("start and wait run thread : %s" % thName)
    condLock.wait()  # 暂停线程运行、等待唤醒
    currentRunThreadNumber += 1
    print("carry on run thread : %s" % thName)
    condLock.release()  # 解锁


def event_task():
    thName = threading.currentThread().name
    print("start and wait run thread : %s" % thName)
    eventLock.wait()  # 暂停运行，等待绿灯
    print("green light, %s carry on run" % thName)
    print("red light, %s stop run" % thName)
    eventLock.wait()  # 暂停运行，等待绿灯
    print("green light, %s carry on run" % thName)
    print("sub thread %s run end" % thName)


def semaphore_task():
    thName = threading.currentThread().name
    with semaLock:
        print("run sub thread %s" % thName)
        time.sleep(3)



if __name__ == "__main__":
    # 不考虑线程安全
    num = 0
    subThread01 = threading.Thread(target=add)
    subThread02 = threading.Thread(target=sub)
    subThread01.start()
    subThread02.start()
    subThread01.join()
    subThread02.join()
    print("num result : %s" % num)
    # 1.使用同步锁
    num = 0
    lock = threading.Lock()
    subThread03 = threading.Thread(target=lock_add)
    subThread04 = threading.Thread(target=lock_sub)
    subThread03.start()
    subThread04.start()
    subThread03.join()
    subThread04.join()
    print("Lock num result : %s" % num)
    # 2.同步锁
    num = 0
    rlock = threading.RLock()
    subThread05 = threading.Thread(target=rlock_add)
    subThread06 = threading.Thread(target=rlock_sub)
    subThread05.start()
    subThread06.start()
    subThread05.join()
    subThread06.join()
    print("Rlock num result : %s" % num)
    # 3.条件锁
    condLock = threading.Condition()
    currentRunThreadNumber = 0
    maxSubThreadNumber = 10
    for i in range(maxSubThreadNumber):
        subThreadIns = threading.Thread(target=task)
        subThreadIns.start()

    while currentRunThreadNumber < maxSubThreadNumber:
        print("Please enter the number of threads that need to be notified to run：")
        notifyNumber = int(input())
        condLock.acquire()
        condLock.notify(notifyNumber)  # 放行
        condLock.release()
    print("main thread run end")
    # 4.事件锁
    eventLock = threading.Event()
    maxSubThreadNumber = 3
    for i in range(maxSubThreadNumber):
        subThreadIns = threading.Thread(target=event_task)
        subThreadIns.start()
    eventLock.set()  # 设置为绿灯
    eventLock.clear()  # 设置为红灯
    eventLock.set()  # 设置为绿灯
    # 5.信号量锁
    import time
    maxSubThreadNumber = 6
    semaLock = threading.Semaphore(2)
    for i in range(maxSubThreadNumber):
        subThreadIns = threading.Thread(target=semaphore_task)
        subThreadIns.start()


