#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' multi job module '

__author__ = 'Yuechen Yang'

import multiprocessing
from util.multi_processes import *
import util.vars as vs


class Multi_Processes(object):
    #conn = None
    #cur  = None

    def __init__(self):
        pass

    def __del__(self):
        pass

    def run_multi_process_job(self):
        pool = multiprocessing.Pool(vs.MULTI_PROCESS_NUMBER)
        result = []
        index = 0
        iterate_list = self.get_list()
        list_len = len(iterate_list)

        for list_index in iterate_list:
            index = index + 1
            result.append(pool.apply_async(self.process, args=(self.get_args() + (list_index, index, list_len))))

        pool.close()
        pool.join()

        return