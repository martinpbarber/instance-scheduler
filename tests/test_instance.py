import context
import unittest

import logging

import pytz
import datetime

from scheduler import Instance, Schedule, Day

DEFAULT_ID = 0

DEFAULT_START = datetime.time(hour=10,minute=0)
DEFAULT_STOP = datetime.time(hour=22,minute=0)
DEFAULT_ZONE = pytz.timezone('UTC')
DEFAULT_DAYS = set([
    Day.Mon,
    Day.Tue,
    Day.Wed,
    Day.Thu,
    Day.Fri,
    Day.Sat,
    Day.Sun
])
DEFAULT_SCHEDULE = Schedule(DEFAULT_START, DEFAULT_STOP, DEFAULT_ZONE, DEFAULT_DAYS)

NO_START_SCHEDULE = Schedule(None, DEFAULT_STOP, DEFAULT_ZONE, DEFAULT_DAYS)
NO_STOP_SCHEDULE = Schedule(DEFAULT_START, None, DEFAULT_ZONE, DEFAULT_DAYS)

logger = logging.getLogger()
logger.setLevel(logging.WARNING)
logger.addHandler(logging.StreamHandler())

class InstanceTestCase(unittest.TestCase):
    """
        Unit tests for Instance
    """

    ######################################################################
    # Test Success
    ######################################################################
    def test_create_running(self):
        '''
            Create a RUNNING instance
        '''
        running = True
        inst = Instance(DEFAULT_ID, running, DEFAULT_SCHEDULE)
        self.assertTrue(inst)
        self.assertEqual(inst.id, DEFAULT_ID)
        self.assertEqual(inst.running, running)
        self.assertEqual(inst.schedule, DEFAULT_SCHEDULE)

    def test_create_stopped(self):
        '''
            Create a STOPPED instance
        '''
        running = False
        inst = Instance(DEFAULT_ID, running, DEFAULT_SCHEDULE)
        self.assertTrue(inst)
        self.assertEqual(inst.id, DEFAULT_ID)
        self.assertEqual(inst.running, running)
        self.assertEqual(inst.schedule, DEFAULT_SCHEDULE)

    def test_running_time_before_start(self):
        '''
            Verify a RUNNING instance continues to run when
            timestamp is before the schedule start time
        '''
        running = True
        inst = Instance(DEFAULT_ID, running, DEFAULT_SCHEDULE)

        timestamp = datetime.datetime(2018, 4, 23, 0, 0)
        inst.evaluate_schedule(timestamp)
        self.assertEqual(inst.running, True)

    def test_running_time_between_start_stop(self):
        '''
            Verify a RUNNING instance continues to run when
            timestamp is between the schedule start and stop times
        '''
        running = True
        inst = Instance(DEFAULT_ID, running, DEFAULT_SCHEDULE)

        timestamp = datetime.datetime(2018, 4, 23, 12, 0)
        inst.evaluate_schedule(timestamp)
        self.assertEqual(inst.running, True)

    def test_running_time_after_stop(self):
        '''
            Verify a RUNNING instance is stopped when
            timestamp is after the schedule stop time
        '''
        running = True
        inst = Instance(DEFAULT_ID, running, DEFAULT_SCHEDULE)

        timestamp = datetime.datetime(2018, 4, 23, 23, 0)
        inst.evaluate_schedule(timestamp)
        self.assertEqual(inst.running, False)

    def test_stopped_time_before_start(self):
        '''
            Verify a STOPPED instance stays stopped when
            timestamp is before the schedule start time
        '''
        running = False
        inst = Instance(DEFAULT_ID, running, DEFAULT_SCHEDULE)

        timestamp = datetime.datetime(2018, 4, 23, 0, 0)
        inst.evaluate_schedule(timestamp)
        self.assertEqual(inst.running, False)

    def test_stopped_time_between_start_stop(self):
        '''
            Verify a STOPPED instance is started when
            timestamp is between the schedule start and stop times
        '''
        running = False
        inst = Instance(DEFAULT_ID, running, DEFAULT_SCHEDULE)

        timestamp = datetime.datetime(2018, 4, 23, 12, 0)
        inst.evaluate_schedule(timestamp)
        self.assertEqual(inst.running, True)

    def test_stopped_time_after_stop(self):
        '''
            Verify a STOPPED instance stays stopped when
            timestamp is after the schedule stop time
        '''
        running = False
        inst = Instance(DEFAULT_ID, running, DEFAULT_SCHEDULE)

        timestamp = datetime.datetime(2018, 4, 23, 23, 0)
        inst.evaluate_schedule(timestamp)
        self.assertEqual(inst.running, False)

    def test_running_no_start_time_before_stop(self):
        '''
            Verify a RUNNING instance continues to run when
            timestamp is before the schedule stop time
        '''
        running = True
        inst = Instance(DEFAULT_ID, running, NO_START_SCHEDULE)

        timestamp = datetime.datetime(2018, 4, 23, 0, 0)
        inst.evaluate_schedule(timestamp)
        self.assertEqual(inst.running, True)

    def test_running_no_start_time_after_stop(self):
        '''
            Verify a RUNNING instance is stopped when
            timestamp is after the schedule stop time
        '''
        running = True
        inst = Instance(DEFAULT_ID, running, NO_START_SCHEDULE)

        timestamp = datetime.datetime(2018, 4, 23, 23, 0)
        inst.evaluate_schedule(timestamp)
        self.assertEqual(inst.running, False)

    def test_stopped_no_start_time_before_stop(self):
        '''
            Verify a STOPPED instance stays stopped when
            timestamp is before the schedule stop time
        '''
        running = False
        inst = Instance(DEFAULT_ID, running, NO_START_SCHEDULE)

        timestamp = datetime.datetime(2018, 4, 23, 0, 0)
        inst.evaluate_schedule(timestamp)
        self.assertEqual(inst.running, False)

    def test_stopped_no_start_time_after_stop(self):
        '''
            Verify a STOPPED instance stays stopped when
            timestamp is after the schedule stop time
        '''
        running = False
        inst = Instance(DEFAULT_ID, running, NO_START_SCHEDULE)

        timestamp = datetime.datetime(2018, 4, 23, 23, 0)
        inst.evaluate_schedule(timestamp)
        self.assertEqual(inst.running, False)

    def test_running_no_stop_time_before_start(self):
        '''
            Verify a RUNNING instance continues to run when
            timestamp is before the schedule start time
        '''
        running = True
        inst = Instance(DEFAULT_ID, running, NO_STOP_SCHEDULE)

        timestamp = datetime.datetime(2018, 4, 23, 0, 0)
        inst.evaluate_schedule(timestamp)
        self.assertEqual(inst.running, True)

    def test_running_no_stop_time_after_start(self):
        '''
            Verify a RUNNING instance continues to run when
            timestamp is after the schedule start time
        '''
        running = True
        inst = Instance(DEFAULT_ID, running, NO_STOP_SCHEDULE)

        timestamp = datetime.datetime(2018, 4, 23, 23, 0)
        inst.evaluate_schedule(timestamp)
        self.assertEqual(inst.running, True)

    def test_stopped_no_stop_time_before_start(self):
        '''
            Verify a STOPPED instance stays stopped when
            timestamp is before the schedule start time
        '''
        running = False
        inst = Instance(DEFAULT_ID, running, NO_STOP_SCHEDULE)

        timestamp = datetime.datetime(2018, 4, 23, 0, 0)
        inst.evaluate_schedule(timestamp)
        self.assertEqual(inst.running, False)

    def test_stopped_no_stop_time_after_start(self):
        '''
            Verify a STOPPED instance is started when
            timestamp is after the schedule start time
        '''
        running = False
        inst = Instance(DEFAULT_ID, running, NO_STOP_SCHEDULE)

        timestamp = datetime.datetime(2018, 4, 23, 12, 0)
        inst.evaluate_schedule(timestamp)
        self.assertEqual(inst.running, True)

if __name__ == '__main__':
    unittest.main()
