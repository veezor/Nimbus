#!/usr/bin/env python
# -*- coding: UTF-8 -*-


def script_name(request):
    # return { 'script_name' : request.META['SCRIPT_NAME']} 
    return { 'script_name' : request.META['PATH_INFO']}


def status_header(request):
    # from random import choice
    # d = [{'status_header': {'status_name': 'ok', 'status_message': 'Normal'}},
    #      {'status_header': {'status_name': 'error', 'status_message': 'Erro'}}]
    # return choice(d)
    d = {'status_header': {'status_name': 'ok', 'status_message': 'Funcionamento Normal'}}
    return d


# Exemplo.
# def computers(request):
#     # return { 'script_name' : request.META['SCRIPT_NAME']} 
#     return { 'computers' : 12312}