import logging
import enum
import datetime
import re
import time
import pytz

logger = logging.getLogger()

class Day(enum.IntEnum):
    '''
    Day enumeration based on datetime.date.weekday()
    '''
    Mon = 0
    Tue = 1
    Wed = 2
    Thu = 3
    Fri = 4
    Sat = 6
    Sun = 7

class Schedule:
    '''
    Weekly schedule that can evaluate a target state against a timestamp.

    :param start_time: datetime.time object in HH:MM format
    :param stop_time: datetime.time object in HH:MM format
    :param time_zone: datetime.tzinfo object
    :param days: set of Day enums
    '''
    def __init__(self, start_time, stop_time, time_zone, days):
        self.start_time = start_time
        self.stop_time = stop_time

        self._validate_start_stop()

        self.time_zone = time_zone
        self.days = days

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        if self._is_validate_time_property(value):
            self._start_time = value
        else:
            raise TypeError('start_time must be a datetime.time object')

    @property
    def stop_time(self):
        return self._stop_time

    @stop_time.setter
    def stop_time(self, value):
        if self._is_validate_time_property(value):
            self._stop_time = value
        else:
            raise TypeError('stop_time must be a datetime.time object')

    @property
    def time_zone(self):
        return self._time_zone

    @time_zone.setter
    def time_zone(self, value):
        if isinstance(value, datetime.tzinfo):
            self._time_zone = value
        else:
            raise TypeError('time_zone must be a datetime.tzinfo object')

    @property
    def days(self):
        return self._days

    @days.setter
    def days(self, value):
        error_message = 'days must be a set of scheduler.Days'
        if not isinstance(value, set):
            raise TypeError(error_message)
        for item in value:
            if not isinstance(item, Day):
                raise TypeError(error_message)
        self._days = value

    def _is_validate_time_property(self, value):
        if value == None or isinstance(value, datetime.time):
            return True
        else:
            return False

    # TODO:
    #   Consider making this class immutable.
    #   Currently this function is not called when the start_time and
    #   stop_time setters are called. This can lead to an inconsistent
    #   object if the start_time or stop_time are set after creation.
    def _validate_start_stop(self):
        start = self.start_time
        stop = self.stop_time

        # At least one time must be set
        if not start and not stop:
            raise ValueError('start_time or stop_time must be set'.format())
        # Only one time being set is OK
        if not start or not stop:
            return
        # If both set, stop must be after start
        if stop <= start:
            raise ValueError('stop_time "{}" must be after start_time "{}"'.format(start, stop))

    def evaluate(self, timestamp):
        '''
        Evaluate a schedule against the provided timestamp

        :param timestamp: A naive datetime.datetime object
        :rvalue True, False or None based on the following
        Given a set of Days
            Return None if timestamp is not in the set of days

        Given a start and stop time
            Return None if timestamp is before start time
            Return True if timestamp is between start and stop time
            Return False if timestamp is after stop time

        Given a start time only
            Return None if timestamp is before start time
            Return True if timstamp is after start time

        Given a stop time only
            Return None if timestamp is before stop time
            Return False if timestamp is after stop time
        '''
        target = None

        # Validate timestamp
        if not isinstance(timestamp, datetime.datetime):
            raise TypeError('timestamp must be a datetime.datetime object')
        if timestamp.tzinfo is not None:
            raise ValueError('timestamp must be naive')

        # Localize the timestamp and get the day
        now = self._localize(timestamp.date(), timestamp.time(), self.time_zone)
        day = now.weekday()
        logger.debug('DAYS: {}'.format(self.days))
        logger.debug('DAY : {}'.format(day))

        # Localize the start and stop time, use the date from the provided time
        start = stop = None
        if self.start_time:
            start = self._localize(now.date(), self.start_time, self.time_zone)
            logger.debug('START: {} {}'.format(start, start.tzinfo))
        if self.stop_time:
            stop = self._localize(now.date(), self.stop_time, self.time_zone)
            logger.debug('STOP : {} {}'.format(stop, stop.tzinfo))
        logger.debug('NOW  : {} {}'.format(now, now.tzinfo))

        # Evaluate the schedule
        if day in self.days:
            if start and now > start:
                target = True

            if stop and now > stop:
                target = False

        logger.debug('TARGET: {}'.format(target))
        return target

    def _localize(self, date, time, time_zone):
        return time_zone.localize(datetime.datetime.combine(date, time))

    @classmethod
    def from_string(cls, schedule_string):
        '''
        Build a Schedule object based on a string representation.

        :param: cls: Schedule class
        :param: schedule_string: string represenation of a Schedule
        ;rtype: Schedule object
        '''
        schedule_tokens = cls._validate_format(schedule_string)

        start = cls._validate_time_string(schedule_tokens[0])
        stop = cls._validate_time_string(schedule_tokens[1])
        zone = cls._validate_time_zone_string(schedule_tokens[2])
        days = cls._validate_days_string(schedule_tokens[3])

        return cls(start, stop, zone, days)

    @staticmethod
    def _validate_format(schedule):
        '''Remove whitespace and ensure four fields separated by semicolon'''
        schedule_no_whitespace = re.sub('\s', '', schedule)
        schedule_tokens = schedule_no_whitespace.split(';')
        if len(schedule_tokens) != 4:
            raise ValueError('incorrect schedule "{}"'.format(schedule))
        return schedule_tokens

    @staticmethod
    def _validate_time_string(time_string):
        '''Ensure time in HH:MM format'''
        TIME_NONE = 'NONE'
        TIME_FORMAT = '%H:%M'

        if time_string.upper() == TIME_NONE:
            return None
        try:
            tm = time.strptime(time_string, TIME_FORMAT)
            return datetime.time(tm.tm_hour, tm.tm_min)
        except:
            raise ValueError('invalid time "{}", expected HH:MM'.format(time_string))

    @staticmethod
    def _validate_time_zone_string(time_zone):
        '''Ensure valid timezone'''
        try:
            return pytz.timezone(time_zone)
        except:
            raise ValueError('invalid timezone "{}"'.format(time_zone))

    @staticmethod
    def _validate_days_string(days_string):
        '''Ensure comma separated list on Day enumerations'''
        days = set()

        day_tokens = days_string.split(',')
        for day in day_tokens:
            try:
                days.add(Day[day])
            except:
                raise ValueError('invalid day "{}"'.format(day))

        return days


class Instance:
    '''
    Cloud provider compute instance representation that can change it's
    running state based a provided schedule and timestamp.

    :param id: unique string identifier for the instance
    :param running: boolean running state of the instance
    :param schedule: scheduler.Schedule object
    :param provider: cloud provider class that implements start and stop
    '''
    def __init__(self, id, running, schedule, provider = None):
        self.id = id
        self.running = running
        self.schedule = schedule
        self.provider = provider

    def evaluate_schedule(self, timestamp = None):
        '''Evaluate instance's schedule and change running state as required'''
        if timestamp == None:
            timestamp = datetime.datetime.utcnow()

        if self.schedule:
            target = self.schedule.evaluate(timestamp)
            logger.info('Instance [{}]: Running= {}, Target= {}'.format(self.id, self.running, target))

            if target is not None and target != self.running:
                logger.info('Instance [{}]: Changing Running to {}'.format(self.id, target))
                self._toggle_running()

    def _toggle_running(self):
        '''Change instance's running state based on it's current state'''
        if self.provider:
            start = self.provider.start
            stop = self.provider.stop
        else:
            start = self._start
            stop = self._stop

        if self.running:
            stop()
        else:
            start()

    def _stop(self):
        self.running = False

    def _start(self):
        self.running = True
