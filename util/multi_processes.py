#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' multi job module '

__author__ = 'Yuechen Yang'

import multiprocessing
from util import vars as vs
from util import process_job

class Multi_Processes(object):
    #conn = None
    #cur  = None

    def __init__(self):
        pass

    def __del__(self):
        pass

    def start_multi_process_job(self, process_job):
        pool = multiprocessing.Pool(vs.MULTI_PROCESS_NUMBER)
        result = []
        index = 0
        iterate_list = process_job.get_list()
        list_len = len(iterate_list)

        for list_index in iterate_list:
            index = index + 1
            result.append(pool.apply_async(process_job.process, args=(process_job.get_args() + (list_index, index, list_len))))

        pool.close()
        pool.join()

        return