#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import logging.handlers
import sys

# Global

DEBUG = False


# Exceptions


class RunDependencyFailed(Exception):
    pass

class DeployFailed(Exception):
    pass

class RuleNameError(Exception):
    pass

class RuleNotFound(Exception):
    pass

# Decorators

def log_exception(func):

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            logger.exception(e)
            sys.exit(1)

    wrapper.__name__ = func.__name__
    return wrapper


def rule( *args, **kwargs ):
    return RuleDecorator(*args, **kwargs)

# Functions

def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    handler_sysout = logging.StreamHandler(sys.stdout)
    handler_syslog = logging.handlers.SysLogHandler('/dev/log')
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler_sysout.setFormatter(formatter)
    handler_syslog.setFormatter(formatter)
    root_logger.addHandler(handler_sysout)
    root_logger.addHandler(handler_syslog)


@log_exception
def start(rule, debug=False):
    global DEBUG
    DEBUG = debug
    r = rule.run()
    if not r:
        raise DeployFailed("Start rule not returned True")




# Classes

class Rule(object):

    rules_cache = {}

    def __init__(self, name, function):
        if not name in self.rules_cache:
            self.rules_cache[name] = self
        else:
            raise RuleNameError('Rule must have a unique name')

        self.name = name
        self.function = function
        self.dependencies = []
        self.executed = False
        self.call_on_failure = None


    @classmethod
    def get_rule_reference(cls, rule):
        try:
            return cls.rules_cache[str(rule)]
        except KeyError, e:
            raise RuleNotFound('Rule %s not found' % str(rule))



    def _run_deps(self):
        for dep in self.dependencies:
            dep = self.get_rule_reference(dep)
            if not dep.executed:
                r = dep.run()
                if not r:
                    raise RunDependencyFailed('Dependency must be return True, False is returned')



    @log_exception
    def run(self):

        self._run_deps()

        if DEBUG:
            logger.info('Debug mode: bypass rule.run for rule %s' % self.name)
            result = True
        else:
            result = self.function()

        self.executed = True

        if not result and self.call_on_failure:
            logger.info('Calling error_callback for rule %s' % self.name)
            callback = self.get_rule_reference(self.call_on_failure)
            result = callback.run()
        logger.info('Rule %s successfully performed' % self.name)
        return result


    def __str__(self):
        return self.name

    def __repr__(self):
        return "Rule(%s)" % self.name


    def add_dep(self, dependency):
        self.dependencies.append(dependency)


    def add_deps(self, list_dep):
        for dep in list_dep:
            self.add_dep(dep)


    def set_error_callback(self, callback):
        self.call_on_failure = callback





# Class Decorator


class RuleDecorator(object):

    def __init__(self, function = None, depends=None, on_failure=None):
        self.function = function
        self.depends = depends
        self.on_failure = on_failure
        self.rule = None
        if function:
            self._setup()

    def _setup(self):
        self.rule = Rule(self.function.__name__, self.function)
        if self.depends:
            try:
                self.rule.add_deps(self.depends)
            except TypeError, e : # not iterable, a single value
                self.rule.add_dep(self.depends)

        if self.on_failure:
            self.rule.set_error_callback(self.on_failure)
        return self.rule


    def __call__(self, function):
        self.function = function
        return self._setup()

    def __str__(self):
        return self.rule.name


    def run(self):
        return self.rule.run()





setup_logging()
logger = logging.getLogger(__name__)
