import sys
import psycopg2
from queue import Queue
from threading import Thread
import time



from EnRoute_job_9c import work_on_ros

#ms = 'LU'
# allFUA = 'URAU_RG_'+ms#'URAU_RG_2011_2014_F' #vector file within the grass db
path_to_gdb="/SERVER_DATA/inputs/ua/v2012/UATL_2012.gdb"
path_to_esm ='/SERVER_DATA/inputs/esm/'

#create a list from a pg table needs the connection string and the ms (if we want to loop over the cities of one ms)

def city_list (conn_string,ms=None):
# def city_list(conn_string, ms):

    conn_string = conn_string #"dbname='d3-natcapes' user='zuliagrgrass' host='d3-natcapes.jrc.it' password='grass'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    list_name =[]
    if ms is None:
        cursor.execute("SELECT * FROM ecos.urau_rg_2011_2014_f *;")
        rows = cursor.fetchall()
        for row in rows:
            file = row[1]
            list_name.append(file[:7])
        return list_name
    else:
        cursor.execute("SELECT * FROM ecos.urau_rg_2011_2014_f where first_ms_c = '" + ms + "';")
        rows = cursor.fetchall()

        for row in rows:
            file = row[1]
            list_name.append(file[:7])
        return list_name

    conn.commit()
    conn.close()

#this function starts the multi-thread for a specific function in a class
# import_ua(self, path_gdb,name_city):
def runthread(queue):
    while True:
        city, ms = queue.get()
        fc = work_on_ros() #chiama la classe
        fc.ros_component(city,ms) #chiama la funzione

        print 'Task queque '+ city  + 'done'
        queue.task_done()

start_time = time.time()
#this is the main code for a list of cities starts the computation using a number of thread
def main():
    ms = str(sys.argv[1]) #'LU'
    #ms='DE'

    lista_citta = city_list("dbname='d3-natcapes' user='zuliagrgrass' host='d3-natcapes.jrc.it' password='grass'", ms)


    queue = Queue (maxsize=0)

    for x in range(1):
        worker =Thread (target =runthread, args=(queue,))
        worker.setDaemon(True)
        worker.start()

    for city in lista_citta:

        queue.put((city, ms))

    queue.join()

    print("--- %s seconds ---" % (time.time() - start_time))

    print "fine"



if __name__=="__main__":
    main()

