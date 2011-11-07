#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from nimbus.libs.commands import command
from nimbus.graphics.models import GraphicsManager

@command("--update-graphs-data")
def update_graphs_data():
    manager = GraphicsManager()
    manager.collect_data()


