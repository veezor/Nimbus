#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from nimbus.libs.commands import command
# from nimbus.graphics.models import GraphicsManager, Graphics
from nimbus.graphics.models import Graphics

@command("--update-graphs-data")
def update_graphs_data():
    u"""Atualiza os dados dos gráficos"""
    # manager = GraphicsManager()
    # manager.collect_data()
    manager = Graphics()
    manager.update_all()
    

