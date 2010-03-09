#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os, cairoplot
from backup_corporativo.bkp.bacula import Bacula, BaculaDatabase
from backup_corporativo.bkp import utils, models


from backup_corporativo.bkp.sql_queries import ( JOB_STAT_RAW_QUERY, 
                                                 JOB_STAT_GET_N_LAST_WITH_NAME, 
                                                 JOB_STAT_GET_N_LAST,
                                                 JOB_STAT_GET_N_LAST_FROM_CLIENT )  

IMAGENS_DIR = "templates/bkp/static/imagens/"

KBYTES = 1024
MBYTES = 1024 * KBYTES

def bytes_to_mbytes(size):
    return size / MBYTES


class Data(object):

    def __init__(self, item):
        self.mbytes = bytes_to_mbytes(item["JobBytes"])
        self.date = item["RealEndTime"]

    @property
    def day(self):
        return (self.date.day, self.date.month, self.date.year)

    @property
    def day_as_str(self):
        return "/".join( str(i) for i in  self.day )



def average(items):
    items = [item.mbytes for item in items]
    return float(sum(items))/len(items)



def get_items_from_db(query, **options):
    baculadb = BaculaDatabase()
    cursor = baculadb.execute(query % options)
    result = utils.dictfetch(cursor)
    result = [ Data(item) for item in result ]
    return result



def get_last_jobs_items(size=10):
    return get_items_from_db( JOB_STAT_GET_N_LAST,
                                        size=size)


def get_last_items_from_procedure( procedure, size=10):
    return get_items_from_db( JOB_STAT_GET_N_LAST_WITH_NAME,
                                        name=procedure.procedure_bacula_name(), 
                                        size=size)

def get_last_items_from_computer( computer, size=10):
    return get_items_from_db( JOB_STAT_GET_N_LAST_FROM_CLIENT,
                                        client_name=computer.computer_bacula_name(), 
                                        size=size)



def to_string(obj):
    return "/".join(map(str, obj[::-1]))




def generate_graph( name,  items ):
    x_labels = [ obj.day_as_str for obj in items ]
    items_data = [ obj.mbytes for obj in items ]
    data = [ [x] for x in items_data ]
    max_value = max(items_data)
    step  = max_value / 5
    y_labels = [  ("%.2f MB" % (step*x)) for x in xrange(6)  ]  
    cairoplot.vertical_bar_plot( "%s%s.png" % (IMAGENS_DIR, name), 
                                 data, 640, 480, border=20, display_values=True,
                                 colors = ["gray"], rounded_corners = True,
                                 grid=True, x_labels = x_labels, y_labels=y_labels)




def generate_procedure_graph(procedure, name=None, size=10):
    if not name:
        name = procedure.procedure_bacula_name()
    else:
        name = name 
    
    items = get_last_items_from_procedure(procedure, size)

    if items:
        generate_graph( name, items)
        return True
    else:
        return False


def generate_computer_graph(computer, name=None, size=10):
    if not name:
        name = computer.computer_bacula_name()
    else:
        name = name 
    
    items = get_last_items_from_computer(computer, size)

    if items:
        generate_graph( name, items)
        return True
    else:
        return False


def generate_jobs_graph(name="jobs", size=10):
    items = get_last_jobs_items(size)

    if items:
        generate_graph(name, items)
        return True
    else:
        return False


def update_diskusage_graph(filename=IMAGENS_DIR+"disk.png"):
    info = os.statvfs("/")
    total = info.f_bsize * info.f_blocks
    free = info.f_bsize * info.f_bfree
    used = total - free
    cairoplot.pie_plot( filename, 
                        {"used" : used, "free" : free}, 
                        480, 320,
                        gradient = True,
                        shadow = True,
                        colors = [ "lime", "blue" ]) 









