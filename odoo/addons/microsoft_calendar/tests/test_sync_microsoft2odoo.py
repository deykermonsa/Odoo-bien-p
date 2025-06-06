# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.microsoft_calendar.utils.microsoft_calendar import MicrosoftCalendarService, MicrosoftEvent
from odoo.exceptions import ValidationError
import pytz
from datetime import datetime, date
from odoo.tests.common import TransactionCase
from dateutil.relativedelta import relativedelta


class TestSyncMicrosoft2Odoo(TransactionCase):

    @property
    def now(self):
        return pytz.utc.localize(datetime.now()).isoformat()

    def setUp(self):
        super().setUp()
        self.recurrence_id = 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA'
        values = [
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"ZS2uEVAVyU6BMZ3m6cHmtgAACyq4xQ=="', 'createdDateTime': '2020-05-06T07:03:49.1444085Z', 'lastModifiedDateTime': '2020-05-06T07:00:00Z', 'changeKey': 'ZS2uEVAVyU6BMZ3m6cHmtgAACyq4xQ==', 'categories': [], 'originalStartTimeZone': 'Romance Standard Time', 'originalEndTimeZone': 'Romance Standard Time', 'iCalUId': '040000008200E00074C5B7101A82E00800000000874F057E7423D601000D848B1B7F8C', 'reminderMinutesBeforeStart': 15, 'isReminderOn': True, 'hasAttachments': False, 'subject': 'My recurrent event', 'bodyPreview': '', 'importance': 'normal', 'sensitivity': 'normal', 'isAllDay': False, 'isCancelled': False, 'isOrganizer': True, 'IsRoomRequested': False, 'AutoRoomBookingStatus': 'None', 'responseRequested': True, 'seriesMasterId': None, 'showAs': 'busy', 'type': 'seriesMaster', 'webLink': 'https://outlook.live.com/owa/?itemid=AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFAAALLLTEAAAA&exvsurl=1&path=/calendar/item', 'onlineMeetingUrl': None, 'isOnlineMeeting': False, 'onlineMeetingProvider': 'unknown', 'AllowNewTimeProposals': True, 'IsDraft': False, 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'responseStatus': {'response': 'organizer', 'time': '0001-01-01T00:00:00Z'}, 'body': {'contentType': 'html', 'content': ''}, 'start': {'dateTime': '2020-05-03T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-03T16:00:00.0000000', 'timeZone': 'UTC'}, 'location': {'displayName': '', 'locationType': 'default', 'uniqueIdType': 'unknown', 'address': {}, 'coordinates': {}}, 'locations': [], 'recurrence': {'pattern': {'type': 'daily', 'interval': 1, 'month': 0, 'dayOfMonth': 0, 'firstDayOfWeek': 'sunday', 'index': 'first'}, 'range': {'type': 'endDate', 'startDate': '2020-05-03', 'endDate': '2020-05-05', 'recurrenceTimeZone': 'Romance Standard Time', 'numberOfOccurrences': 0}}, 'attendees': [], 'organizer': {'emailAddress': {'name': 'outlook_7BA43549E5FD4413@outlook.com', 'address': 'outlook_7BA43549E5FD4413@outlook.com'}}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAALKrjF"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX7vTsS0AARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAAEA==', 'start': {'dateTime': '2020-05-03T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-03T16:00:00.0000000', 'timeZone': 'UTC'}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAALKrjF"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX774WtQAAAEYAAAJAcu19N72jSr9Rp1mE2xWABwBlLa4RUBXJToExnebpwea2AAACAQ0AAABlLa4RUBXJToExnebpwea2AAAACyy0xAAAABA=', 'start': {'dateTime': '2020-05-04T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-04T16:00:00.0000000', 'timeZone': 'UTC'}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAALKrjF"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX8IdBHsAARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAAEA==', 'start': {'dateTime': '2020-05-05T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-05T16:00:00.0000000', 'timeZone': 'UTC'}}
        ]
        self.single_event = [
            {
                '@odata.type': '#microsoft.graph.event',
                '@odata.etag': 'W/"AAAAA"',
                'type': 'singleInstance',
                'id': "CCCCC",
                'start': {
                    'dateTime': '2020-05-05T14:30:00.0000000',
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': '2020-05-05T16:00:00.0000000',
                    'timeZone': 'UTC'
                },
                'location': {
                    'displayName': "a meeting room at Odoo"
                }
            }
        ]

        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(values))

        self.datetime_future = pytz.utc.localize(datetime.now() + relativedelta(days=1)).isoformat()

    def sync(self, events):

        self.env['calendar.event']._sync_microsoft2odoo(events)

    def test_new_microsoft_recurrence(self):

        recurrence = self.env['calendar.recurrence'].search([('microsoft_id', '=', self.recurrence_id)])
        events = recurrence.calendar_event_ids
        self.assertTrue(recurrence, "It should have created an recurrence")
        self.assertEqual(len(events), 3, "It should have created 3 events")
        self.assertEqual(recurrence.base_event_id, events[0])
        self.assertEqual(events.mapped('name'), ['My recurrent event', 'My recurrent event', 'My recurrent event'])
        self.assertFalse(events[0].allday)
        self.assertEqual(events[0].start, datetime(2020, 5, 3, 14, 30))
        self.assertEqual(events[0].stop, datetime(2020, 5, 3, 16, 00))
        self.assertEqual(events[1].start, datetime(2020, 5, 4, 14, 30))
        self.assertEqual(events[1].stop, datetime(2020, 5, 4, 16, 00))
        self.assertEqual(events[2].start, datetime(2020, 5, 5, 14, 30))
        self.assertEqual(events[2].stop, datetime(2020, 5, 5, 16, 00))

    def test_microsoft_recurrence_delete_one_event(self):
        values = [
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"ZS2uEVAVyU6BMZ3m6cHmtgAADIaZKQ=="', 'createdDateTime': '2020-05-06T07:03:49.1444085Z', 'lastModifiedDateTime': self.datetime_future, 'changeKey': 'ZS2uEVAVyU6BMZ3m6cHmtgAADIaZKQ==', 'categories': [], 'originalStartTimeZone': 'Romance Standard Time', 'originalEndTimeZone': 'Romance Standard Time', 'iCalUId': '040000008200E00074C5B7101A82E00800000000874F057E7423D601000000000000000010000000C6918C4B44D2D84586351FEC8B1B7F8C', 'reminderMinutesBeforeStart': 15, 'isReminderOn': True, 'hasAttachments': False, 'subject': 'My recurrent event', 'bodyPreview': '', 'importance': 'normal', 'sensitivity': 'normal', 'isAllDay': False, 'isCancelled': False, 'isOrganizer': True, 'IsRoomRequested': False, 'AutoRoomBookingStatus': 'None', 'responseRequested': True, 'seriesMasterId': None, 'showAs': 'busy', 'type': 'seriesMaster', 'webLink': 'https://outlook.live.com/owa/?itemid=AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA&exvsurl=1&path=/calendar/item', 'onlineMeetingUrl': None, 'isOnlineMeeting': False, 'onlineMeetingProvider': 'unknown', 'AllowNewTimeProposals': True, 'IsDraft': False, 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'responseStatus': {'response': 'organizer', 'time': '0001-01-01T00:00:00Z'}, 'body': {'contentType': 'html', 'content': ''}, 'start': {'dateTime': '2020-05-03T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-03T16:00:00.0000000', 'timeZone': 'UTC'}, 'location': {'displayName': '', 'locationType': 'default', 'uniqueIdType': 'unknown', 'address': {}, 'coordinates': {}}, 'locations': [], 'recurrence': {'pattern': {'type': 'daily', 'interval': 1, 'month': 0, 'dayOfMonth': 0, 'firstDayOfWeek': 'sunday', 'index': 'first'}, 'range': {'type': 'endDate', 'startDate': '2020-05-03', 'endDate': '2020-05-05', 'recurrenceTimeZone': 'Romance Standard Time', 'numberOfOccurrences': 0}}, 'attendees': [], 'organizer': {'emailAddress': {'name': 'outlook_7BA43549E5FD4413@outlook.com', 'address': 'outlook_7BA43549E5FD4413@outlook.com'}}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMhpkp"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX7vTsS0AARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAAEA==', 'start': {'dateTime': '2020-05-03T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-03T16:00:00.0000000', 'timeZone': 'UTC'}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMhpkp"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX8IdBHsAARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAAEA==', 'start': {'dateTime': '2020-05-05T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-05T16:00:00.0000000', 'timeZone': 'UTC'}}
        ]

        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(values))

        recurrence = self.env['calendar.recurrence'].search([('microsoft_id', '=', self.recurrence_id)])
        events = self.env['calendar.event'].search([('recurrence_id', '=', recurrence.id)], order='start asc')
        self.assertTrue(recurrence, "It should keep the recurrence")
        self.assertEqual(len(events), 2, "It should keep 2 events")
        self.assertEqual(recurrence.base_event_id, events[0])
        self.assertEqual(events.mapped('name'), ['My recurrent event', 'My recurrent event'])

    def test_microsoft_recurrence_change_name_one_event(self):
        values = [
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"ZS2uEVAVyU6BMZ3m6cHmtgAADIaZKQ=="', 'createdDateTime': '2020-05-06T07:03:49.1444085Z', 'lastModifiedDateTime': self.datetime_future, 'changeKey': 'ZS2uEVAVyU6BMZ3m6cHmtgAADIaZKQ==', 'categories': [], 'originalStartTimeZone': 'Romance Standard Time', 'originalEndTimeZone': 'Romance Standard Time', 'iCalUId': '040000008200E00074C5B7101A82E00800000000874F057E7423D601000000000000000010000000C6918C4B44D2D84586351FEC8B1B7F8C', 'reminderMinutesBeforeStart': 15, 'isReminderOn': True, 'hasAttachments': False, 'subject': 'My recurrent event', 'bodyPreview': '', 'importance': 'normal', 'sensitivity': 'normal', 'isAllDay': False, 'isCancelled': False, 'isOrganizer': True, 'IsRoomRequested': False, 'AutoRoomBookingStatus': 'None', 'responseRequested': True, 'seriesMasterId': None, 'showAs': 'busy', 'type': 'seriesMaster', 'webLink': 'https://outlook.live.com/owa/?itemid=AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA&exvsurl=1&path=/calendar/item', 'onlineMeetingUrl': None, 'isOnlineMeeting': False, 'onlineMeetingProvider': 'unknown', 'AllowNewTimeProposals': True, 'IsDraft': False, 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'responseStatus': {'response': 'organizer', 'time': '0001-01-01T00:00:00Z'}, 'body': {'contentType': 'html', 'content': ''}, 'start': {'dateTime': '2020-05-03T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-03T16:00:00.0000000', 'timeZone': 'UTC'}, 'location': {'displayName': '', 'locationType': 'default', 'uniqueIdType': 'unknown', 'address': {}, 'coordinates': {}}, 'locations': [], 'recurrence': {'pattern': {'type': 'daily', 'interval': 1, 'month': 0, 'dayOfMonth': 0, 'firstDayOfWeek': 'sunday', 'index': 'first'}, 'range': {'type': 'endDate', 'startDate': '2020-05-03', 'endDate': '2020-05-05', 'recurrenceTimeZone': 'Romance Standard Time', 'numberOfOccurrences': 0}}, 'attendees': [], 'organizer': {'emailAddress': {'name': 'outlook_7BA43549E5FD4413@outlook.com', 'address': 'outlook_7BA43549E5FD4413@outlook.com'}}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMhpkp"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX7vTsS0AARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAAEA==', 'start': {'dateTime': '2020-05-03T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-03T16:00:00.0000000', 'timeZone': 'UTC'}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"ZS2uEVAVyU6BMZ3m6cHmtgAADIaZKQ=="', 'createdDateTime': '2020-05-06T08:01:32.4884797Z', 'lastModifiedDateTime': self.datetime_future, 'changeKey': 'ZS2uEVAVyU6BMZ3m6cHmtgAADIaZKQ==', 'categories': [], 'originalStartTimeZone': 'Romance Standard Time', 'originalEndTimeZone': 'Romance Standard Time', 'iCalUId': '040000008200E00074C5B7101A82E00807E40504874F057E7423D601000000000000000010000000C6918C4B44D2D84586351FEC8B1B7F8C', 'reminderMinutesBeforeStart': 15, 'isReminderOn': True, 'hasAttachments': False, 'subject': 'My recurrent event 2', 'bodyPreview': '', 'importance': 'normal', 'sensitivity': 'normal', 'originalStart': '2020-05-04T14:30:00Z', 'isAllDay': False, 'isCancelled': False, 'isOrganizer': True, 'IsRoomRequested': False, 'AutoRoomBookingStatus': 'None', 'responseRequested': True, 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'showAs': 'busy', 'type': 'exception', 'webLink': 'https://outlook.live.com/owa/?itemid=AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX774WtQAAAEYAAAJAcu19N72jSr9Rp1mE2xWABwBlLa4RUBXJToExnebpwea2AAACAQ0AAABlLa4RUBXJToExnebpwea2AAAACyy0xAAAABA%3D&exvsurl=1&path=/calendar/item', 'onlineMeetingUrl': None, 'isOnlineMeeting': False, 'onlineMeetingProvider': 'unknown', 'AllowNewTimeProposals': True, 'IsDraft': False, 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX774WtQAAAEYAAAJAcu19N72jSr9Rp1mE2xWABwBlLa4RUBXJToExnebpwea2AAACAQ0AAABlLa4RUBXJToExnebpwea2AAAACyy0xAAAABA=', 'responseStatus': {'response': 'organizer', 'time': '0001-01-01T00:00:00Z'}, 'body': {'contentType': 'html', 'content': ''}, 'start': {'dateTime': '2020-05-04T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-04T16:00:00.0000000', 'timeZone': 'UTC'}, 'location': {'displayName': '', 'locationType': 'default', 'uniqueIdType': 'unknown', 'address': {}, 'coordinates': {}}, 'locations': [], 'attendees': [], 'organizer': {'emailAddress': {'name': 'outlook_7BA43549E5FD4413@outlook.com', 'address': 'outlook_7BA43549E5FD4413@outlook.com'}}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMhpkp"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX8IdBHsAARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAAEA==', 'start': {'dateTime': '2020-05-05T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-05T16:00:00.0000000', 'timeZone': 'UTC'}}
        ]

        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(values))

        recurrence = self.env['calendar.recurrence'].search([('microsoft_id', '=', self.recurrence_id)])
        events = self.env['calendar.event'].search([('recurrence_id', '=', recurrence.id)], order='start asc')
        self.assertTrue(recurrence, "It should have created an recurrence")
        self.assertEqual(len(events), 3, "It should have created 3 events")
        self.assertEqual(recurrence.base_event_id, events[0])
        self.assertEqual(events.mapped('name'), ['My recurrent event', 'My recurrent event 2', 'My recurrent event'])

    def test_microsoft_recurrence_change_name_all_event(self):
        values = [
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"ZS2uEVAVyU6BMZ3m6cHmtgAADIaZKQ=="', 'createdDateTime': '2020-05-06T07:03:49.1444085Z', 'lastModifiedDateTime': self.datetime_future, 'changeKey': 'ZS2uEVAVyU6BMZ3m6cHmtgAADIaZKQ==', 'categories': [], 'originalStartTimeZone': 'Romance Standard Time', 'originalEndTimeZone': 'Romance Standard Time', 'iCalUId': '040000008200E00074C5B7101A82E00800000000874F057E7423D601000000000000000010000000C6918C4B44D2D84586351FEC8B1B7F8C', 'reminderMinutesBeforeStart': 15, 'isReminderOn': True, 'hasAttachments': False, 'subject': 'My recurrent event 2', 'bodyPreview': '', 'importance': 'normal', 'sensitivity': 'normal', 'isAllDay': False, 'isCancelled': False, 'isOrganizer': True, 'IsRoomRequested': False, 'AutoRoomBookingStatus': 'None', 'responseRequested': True, 'seriesMasterId': None, 'showAs': 'busy', 'type': 'seriesMaster', 'webLink': 'https://outlook.live.com/owa/?itemid=AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA&exvsurl=1&path=/calendar/item', 'onlineMeetingUrl': None, 'isOnlineMeeting': False, 'onlineMeetingProvider': 'unknown', 'AllowNewTimeProposals': True, 'IsDraft': False, 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'responseStatus': {'response': 'organizer', 'time': '0001-01-01T00:00:00Z'}, 'body': {'contentType': 'html', 'content': ''}, 'start': {'dateTime': '2020-05-03T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-03T16:00:00.0000000', 'timeZone': 'UTC'}, 'location': {'displayName': '', 'locationType': 'default', 'uniqueIdType': 'unknown', 'address': {}, 'coordinates': {}}, 'locations': [], 'recurrence': {'pattern': {'type': 'daily', 'interval': 1, 'month': 0, 'dayOfMonth': 0, 'firstDayOfWeek': 'sunday', 'index': 'first'}, 'range': {'type': 'endDate', 'startDate': '2020-05-03', 'endDate': '2020-05-05', 'recurrenceTimeZone': 'Romance Standard Time', 'numberOfOccurrences': 0}}, 'attendees': [], 'organizer': {'emailAddress': {'name': 'outlook_7BA43549E5FD4413@outlook.com', 'address': 'outlook_7BA43549E5FD4413@outlook.com'}}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMhpkp"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX7vTsS0AARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAAEA==', 'start': {'dateTime': '2020-05-03T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-03T16:00:00.0000000', 'timeZone': 'UTC'}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMhpkp"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX774WtQAAAEYAAAJAcu19N72jSr9Rp1mE2xWABwBlLa4RUBXJToExnebpwea2AAACAQ0AAABlLa4RUBXJToExnebpwea2AAAACyy0xAAAABA=', 'start': {'dateTime': '2020-05-04T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-04T16:00:00.0000000', 'timeZone': 'UTC'}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMhpkp"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX8IdBHsAARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAAEA==', 'start': {'dateTime': '2020-05-05T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-05T16:00:00.0000000', 'timeZone': 'UTC'}}
        ]

        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(values))

        recurrence = self.env['calendar.recurrence'].search([('microsoft_id', '=', self.recurrence_id)])
        events = self.env['calendar.event'].search([('recurrence_id', '=', recurrence.id)], order='start asc')
        self.assertTrue(recurrence, "It should keep the recurrence")
        self.assertEqual(len(events), 3, "It should keep the 3 events")
        self.assertEqual(recurrence.base_event_id, events[0])
        self.assertEqual(events.mapped('name'), ['My recurrent event 2', 'My recurrent event 2', 'My recurrent event 2'])

    def test_microsoft_recurrence_change_date_one_event(self):
        values = [
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"ZS2uEVAVyU6BMZ3m6cHmtgAADIaZPA=="', 'createdDateTime': '2020-05-06T07:03:49.1444085Z', 'lastModifiedDateTime': self.datetime_future, 'changeKey': 'ZS2uEVAVyU6BMZ3m6cHmtgAADIaZPA==', 'categories': [], 'originalStartTimeZone': 'Romance Standard Time', 'originalEndTimeZone': 'Romance Standard Time', 'iCalUId': '040000008200E00074C5B7101A82E00800000000874F057E7423D601000000000000000010000000C6918C4B44D2D84586351FEC8B1B7F8C', 'reminderMinutesBeforeStart': 15, 'isReminderOn': True, 'hasAttachments': False, 'subject': 'My recurrent event', 'bodyPreview': '', 'importance': 'normal', 'sensitivity': 'normal', 'isAllDay': False, 'isCancelled': False, 'isOrganizer': True, 'IsRoomRequested': False, 'AutoRoomBookingStatus': 'None', 'responseRequested': True, 'seriesMasterId': None, 'showAs': 'busy', 'type': 'seriesMaster', 'webLink': 'https://outlook.live.com/owa/?itemid=AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA&exvsurl=1&path=/calendar/item', 'onlineMeetingUrl': None, 'isOnlineMeeting': False, 'onlineMeetingProvider': 'unknown', 'AllowNewTimeProposals': True, 'IsDraft': False, 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'responseStatus': {'response': 'organizer', 'time': '0001-01-01T00:00:00Z'}, 'body': {'contentType': 'html', 'content': ''}, 'start': {'dateTime': '2020-05-03T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-03T16:00:00.0000000', 'timeZone': 'UTC'}, 'location': {'displayName': '', 'locationType': 'default', 'uniqueIdType': 'unknown', 'address': {}, 'coordinates': {}}, 'locations': [], 'recurrence': {'pattern': {'type': 'daily', 'interval': 1, 'month': 0, 'dayOfMonth': 0, 'firstDayOfWeek': 'sunday', 'index': 'first'}, 'range': {'type': 'endDate', 'startDate': '2020-05-03', 'endDate': '2020-05-05', 'recurrenceTimeZone': 'Romance Standard Time', 'numberOfOccurrences': 0}}, 'attendees': [], 'organizer': {'emailAddress': {'name': 'outlook_7BA43549E5FD4413@outlook.com', 'address': 'outlook_7BA43549E5FD4413@outlook.com'}}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMhpk8"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX7vTsS0AARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAAEA==', 'start': {'dateTime': '2020-05-03T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-03T16:00:00.0000000', 'timeZone': 'UTC'}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"ZS2uEVAVyU6BMZ3m6cHmtgAADIaZPA=="', 'createdDateTime': '2020-05-06T08:41:52.1067613Z', 'lastModifiedDateTime': self.datetime_future, 'changeKey': 'ZS2uEVAVyU6BMZ3m6cHmtgAADIaZPA==', 'categories': [], 'originalStartTimeZone': 'Romance Standard Time', 'originalEndTimeZone': 'Romance Standard Time', 'iCalUId': '040000008200E00074C5B7101A82E00807E40504874F057E7423D601000000000000000010000000C6918C4B44D2D84586351FEC8B1B7F8C', 'reminderMinutesBeforeStart': 15, 'isReminderOn': True, 'hasAttachments': False, 'subject': 'My recurrent event', 'bodyPreview': '', 'importance': 'normal', 'sensitivity': 'normal', 'originalStart': '2020-05-04T14:30:00Z', 'isAllDay': False, 'isCancelled': False, 'isOrganizer': True, 'IsRoomRequested': False, 'AutoRoomBookingStatus': 'None', 'responseRequested': True, 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'showAs': 'busy', 'type': 'exception', 'webLink': 'https://outlook.live.com/owa/?itemid=AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX774WtQAAAEYAAAJAcu19N72jSr9Rp1mE2xWABwBlLa4RUBXJToExnebpwea2AAACAQ0AAABlLa4RUBXJToExnebpwea2AAAACyy0xAAAABA%3D&exvsurl=1&path=/calendar/item', 'onlineMeetingUrl': None, 'isOnlineMeeting': False, 'onlineMeetingProvider': 'unknown', 'AllowNewTimeProposals': True, 'IsDraft': False, 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX774WtQAAAEYAAAJAcu19N72jSr9Rp1mE2xWABwBlLa4RUBXJToExnebpwea2AAACAQ0AAABlLa4RUBXJToExnebpwea2AAAACyy0xAAAABA=', 'responseStatus': {'response': 'organizer', 'time': '0001-01-01T00:00:00Z'}, 'body': {'contentType': 'html', 'content': ''}, 'start': {'dateTime': '2020-05-04T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-04T17:00:00.0000000', 'timeZone': 'UTC'}, 'location': {'displayName': '', 'locationType': 'default', 'uniqueIdType': 'unknown', 'address': {}, 'coordinates': {}}, 'locations': [], 'attendees': [], 'organizer': {'emailAddress': {'name': 'outlook_7BA43549E5FD4413@outlook.com', 'address': 'outlook_7BA43549E5FD4413@outlook.com'}}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMhpk8"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX8IdBHsAARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAAEA==', 'start': {'dateTime': '2020-05-05T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-05T16:00:00.0000000', 'timeZone': 'UTC'}}
        ]

        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(values))

        recurrence = self.env['calendar.recurrence'].search([('microsoft_id', '=', self.recurrence_id)])
        events = self.env['calendar.event'].search([('recurrence_id', '=', recurrence.id)], order='start asc')
        special_event = self.env['calendar.event'].search([('microsoft_id', '=', 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX774WtQAAAEYAAAJAcu19N72jSr9Rp1mE2xWABwBlLa4RUBXJToExnebpwea2AAACAQ0AAABlLa4RUBXJToExnebpwea2AAAACyy0xAAAABA=')])
        self.assertTrue(recurrence, "It should have created an recurrence")
        self.assertTrue(special_event, "It should have created an special event")
        self.assertEqual(len(events), 3, "It should have created 3 events")
        self.assertTrue(special_event in events)
        self.assertEqual(recurrence.base_event_id, events[0])
        self.assertEqual(events.mapped('name'), ['My recurrent event', 'My recurrent event', 'My recurrent event'])
        event_not_special = events - special_event
        self.assertEqual(event_not_special[0].start, datetime(2020, 5, 3, 14, 30))
        self.assertEqual(event_not_special[0].stop, datetime(2020, 5, 3, 16, 00))
        self.assertEqual(event_not_special[1].start, datetime(2020, 5, 5, 14, 30))
        self.assertEqual(event_not_special[1].stop, datetime(2020, 5, 5, 16, 00))
        self.assertEqual(special_event.start, datetime(2020, 5, 4, 14, 30))
        self.assertEqual(special_event.stop, datetime(2020, 5, 4, 17, 00))

    def test_microsoft_recurrence_delete_first_event(self):
        values = [
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"ZS2uEVAVyU6BMZ3m6cHmtgAADI/Bnw=="', 'createdDateTime': '2020-05-06T07:03:49.1444085Z', 'lastModifiedDateTime': self.datetime_future, 'changeKey': 'ZS2uEVAVyU6BMZ3m6cHmtgAADI/Bnw==', 'categories': [], 'originalStartTimeZone': 'Romance Standard Time', 'originalEndTimeZone': 'Romance Standard Time', 'iCalUId': '040000008200E00074C5B7101A82E00800000000874F057E7423D601000000000000000010000000C6918C4B44D2D84586351FEC8B1B7F8C', 'reminderMinutesBeforeStart': 15, 'isReminderOn': True, 'hasAttachments': False, 'subject': 'My recurrent event', 'bodyPreview': '', 'importance': 'normal', 'sensitivity': 'normal', 'isAllDay': False, 'isCancelled': False, 'isOrganizer': True, 'IsRoomRequested': False, 'AutoRoomBookingStatus': 'None', 'responseRequested': True, 'seriesMasterId': None, 'showAs': 'busy', 'type': 'seriesMaster', 'webLink': 'https://outlook.live.com/owa/?itemid=AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA&exvsurl=1&path=/calendar/item', 'onlineMeetingUrl': None, 'isOnlineMeeting': False, 'onlineMeetingProvider': 'unknown', 'AllowNewTimeProposals': True, 'IsDraft': False, 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'responseStatus': {'response': 'organizer', 'time': '0001-01-01T00:00:00Z'}, 'body': {'contentType': 'html', 'content': ''}, 'start': {'dateTime': '2020-05-03T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-03T16:00:00.0000000', 'timeZone': 'UTC'}, 'location': {'displayName': '', 'locationType': 'default', 'uniqueIdType': 'unknown', 'address': {}, 'coordinates': {}}, 'locations': [], 'recurrence': {'pattern': {'type': 'daily', 'interval': 1, 'month': 0, 'dayOfMonth': 0, 'firstDayOfWeek': 'sunday', 'index': 'first'}, 'range': {'type': 'endDate', 'startDate': '2020-05-03', 'endDate': '2020-05-05', 'recurrenceTimeZone': 'Romance Standard Time', 'numberOfOccurrences': 0}}, 'attendees': [], 'organizer': {'emailAddress': {'name': 'outlook_7BA43549E5FD4413@outlook.com', 'address': 'outlook_7BA43549E5FD4413@outlook.com'}}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMj8Gf"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX774WtQAAAEYAAAJAcu19N72jSr9Rp1mE2xWABwBlLa4RUBXJToExnebpwea2AAACAQ0AAABlLa4RUBXJToExnebpwea2AAAACyy0xAAAABA=', 'start': {'dateTime': '2020-05-04T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-04T16:00:00.0000000', 'timeZone': 'UTC'}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMj8Gf"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX8IdBHsAARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAAEA==', 'start': {'dateTime': '2020-05-05T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-05T16:00:00.0000000', 'timeZone': 'UTC'}}
        ]

        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(values))

        recurrence = self.env['calendar.recurrence'].search([('microsoft_id', '=', self.recurrence_id)])
        events = self.env['calendar.event'].search([('recurrence_id', '=', recurrence.id)], order='start asc')
        self.assertTrue(recurrence, "It should have created an recurrence")
        self.assertEqual(len(events), 2, "It should left 2 events")
        self.assertEqual(recurrence.base_event_id, events[0])
        self.assertEqual(events[0].start, datetime(2020, 5, 4, 14, 30))
        self.assertEqual(events[0].stop, datetime(2020, 5, 4, 16, 00))
        self.assertEqual(events[1].start, datetime(2020, 5, 5, 14, 30))
        self.assertEqual(events[1].stop, datetime(2020, 5, 5, 16, 00))

        # Now we delete lastest event in Outlook.
        values = [
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"ZS2uEVAVyU6BMZ3m6cHmtgAADI/Bpg=="', 'createdDateTime': '2020-05-06T07:03:49.1444085Z', 'lastModifiedDateTime': self.datetime_future, 'changeKey': 'ZS2uEVAVyU6BMZ3m6cHmtgAADI/Bpg==', 'categories': [], 'originalStartTimeZone': 'Romance Standard Time', 'originalEndTimeZone': 'Romance Standard Time', 'iCalUId': '040000008200E00074C5B7101A82E00800000000874F057E7423D601000000000000000010000000C6918C4B44D2D84586351FEC8B1B7F8C', 'reminderMinutesBeforeStart': 15, 'isReminderOn': True, 'hasAttachments': False, 'subject': 'My recurrent event', 'bodyPreview': '', 'importance': 'normal', 'sensitivity': 'normal', 'isAllDay': False, 'isCancelled': False, 'isOrganizer': True, 'IsRoomRequested': False, 'AutoRoomBookingStatus': 'None', 'responseRequested': True, 'seriesMasterId': None, 'showAs': 'busy', 'type': 'seriesMaster', 'webLink': 'https://outlook.live.com/owa/?itemid=AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA&exvsurl=1&path=/calendar/item', 'onlineMeetingUrl': None, 'isOnlineMeeting': False, 'onlineMeetingProvider': 'unknown', 'AllowNewTimeProposals': True, 'IsDraft': False, 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'responseStatus': {'response': 'organizer', 'time': '0001-01-01T00:00:00Z'}, 'body': {'contentType': 'html', 'content': ''}, 'start': {'dateTime': '2020-05-03T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-03T16:00:00.0000000', 'timeZone': 'UTC'}, 'location': {'displayName': '', 'locationType': 'default', 'uniqueIdType': 'unknown', 'address': {}, 'coordinates': {}}, 'locations': [], 'recurrence': {'pattern': {'type': 'daily', 'interval': 1, 'month': 0, 'dayOfMonth': 0, 'firstDayOfWeek': 'sunday', 'index': 'first'}, 'range': {'type': 'endDate', 'startDate': '2020-05-03', 'endDate': '2020-05-05', 'recurrenceTimeZone': 'Romance Standard Time', 'numberOfOccurrences': 0}}, 'attendees': [], 'organizer': {'emailAddress': {'name': 'outlook_7BA43549E5FD4413@outlook.com', 'address': 'outlook_7BA43549E5FD4413@outlook.com'}}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMj8Gm"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX774WtQAAAEYAAAJAcu19N72jSr9Rp1mE2xWABwBlLa4RUBXJToExnebpwea2AAACAQ0AAABlLa4RUBXJToExnebpwea2AAAACyy0xAAAABA=', 'start': {'dateTime': '2020-05-04T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-04T16:00:00.0000000', 'timeZone': 'UTC'}}
        ]

        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(values))

        events = self.env['calendar.event'].search([('recurrence_id', '=', recurrence.id)], order='start asc')
        self.assertEqual(len(events), 1, "It should have created 1 events")
        self.assertEqual(recurrence.base_event_id, events[0])

        # Now, we change end datetime of recurrence in Outlook, so all recurrence is recreated (even deleted events)
        values = [
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"ZS2uEVAVyU6BMZ3m6cHmtgAADI/Bqg=="', 'createdDateTime': '2020-05-06T07:03:49.1444085Z', 'lastModifiedDateTime': self.datetime_future, 'changeKey': 'ZS2uEVAVyU6BMZ3m6cHmtgAADI/Bqg==', 'categories': [], 'originalStartTimeZone': 'Romance Standard Time', 'originalEndTimeZone': 'Romance Standard Time', 'iCalUId': '040000008200E00074C5B7101A82E00800000000874F057E7423D601000000000000000010000000C6918C4B44D2D84586351FEC8B1B7F8C', 'reminderMinutesBeforeStart': 15, 'isReminderOn': True, 'hasAttachments': False, 'subject': 'My recurrent event', 'bodyPreview': '', 'importance': 'normal', 'sensitivity': 'normal', 'isAllDay': False, 'isCancelled': False, 'isOrganizer': True, 'IsRoomRequested': False, 'AutoRoomBookingStatus': 'None', 'responseRequested': True, 'seriesMasterId': None, 'showAs': 'busy', 'type': 'seriesMaster', 'webLink': 'https://outlook.live.com/owa/?itemid=AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA&exvsurl=1&path=/calendar/item', 'onlineMeetingUrl': None, 'isOnlineMeeting': False, 'onlineMeetingProvider': 'unknown', 'AllowNewTimeProposals': True, 'IsDraft': False, 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'responseStatus': {'response': 'organizer', 'time': '0001-01-01T00:00:00Z'}, 'body': {'contentType': 'html', 'content': ''}, 'start': {'dateTime': '2020-05-03T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-03T16:30:00.0000000', 'timeZone': 'UTC'}, 'location': {'displayName': '', 'locationType': 'default', 'uniqueIdType': 'unknown', 'address': {}, 'coordinates': {}}, 'locations': [], 'recurrence': {'pattern': {'type': 'daily', 'interval': 1, 'month': 0, 'dayOfMonth': 0, 'firstDayOfWeek': 'sunday', 'index': 'first'}, 'range': {'type': 'endDate', 'startDate': '2020-05-03', 'endDate': '2020-05-05', 'recurrenceTimeZone': 'Romance Standard Time', 'numberOfOccurrences': 0}}, 'attendees': [], 'organizer': {'emailAddress': {'name': 'outlook_7BA43549E5FD4413@outlook.com', 'address': 'outlook_7BA43549E5FD4413@outlook.com'}}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMj8Gq"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX7vTsS0AARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAAEA==', 'start': {'dateTime': '2020-05-03T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-03T16:30:00.0000000', 'timeZone': 'UTC'}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMj8Gq"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX774WtQAAAEYAAAJAcu19N72jSr9Rp1mE2xWABwBlLa4RUBXJToExnebpwea2AAACAQ0AAABlLa4RUBXJToExnebpwea2AAAACyy0xAAAABA=', 'start': {'dateTime': '2020-05-04T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-04T16:30:00.0000000', 'timeZone': 'UTC'}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMj8Gq"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX8IdBHsAARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAAEA==', 'start': {'dateTime': '2020-05-05T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-05T16:30:00.0000000', 'timeZone': 'UTC'}}
        ]

        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(values))

        events = self.env['calendar.event'].search([('recurrence_id', '=', recurrence.id)], order='start asc')
        self.assertEqual(len(events), 3, "It should have created 3 events")
        self.assertEqual(recurrence.base_event_id, events[0])
        self.assertEqual(events.mapped('name'), ['My recurrent event', 'My recurrent event', 'My recurrent event'])
        self.assertEqual(events[0].start, datetime(2020, 5, 3, 14, 30))
        self.assertEqual(events[0].stop, datetime(2020, 5, 3, 16, 30))
        self.assertEqual(events[1].start, datetime(2020, 5, 4, 14, 30))
        self.assertEqual(events[1].stop, datetime(2020, 5, 4, 16, 30))
        self.assertEqual(events[2].start, datetime(2020, 5, 5, 14, 30))
        self.assertEqual(events[2].stop, datetime(2020, 5, 5, 16, 30))

    def test_microsoft_recurrence_split_recurrence(self):
        values = [
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"ZS2uEVAVyU6BMZ3m6cHmtgAADI/Dig=="', 'createdDateTime': '2020-05-06T07:03:49.1444085Z', 'lastModifiedDateTime': self.datetime_future, 'changeKey': 'ZS2uEVAVyU6BMZ3m6cHmtgAADI/Dig==', 'categories': [], 'originalStartTimeZone': 'Romance Standard Time', 'originalEndTimeZone': 'Romance Standard Time', 'iCalUId': '040000008200E00074C5B7101A82E00800000000874F057E7423D601000000000000000010000000C6918C4B44D2D84586351FEC8B1B7F8C', 'reminderMinutesBeforeStart': 15, 'isReminderOn': True, 'hasAttachments': False, 'subject': 'My recurrent event', 'bodyPreview': '', 'importance': 'normal', 'sensitivity': 'normal', 'isAllDay': False, 'isCancelled': False, 'isOrganizer': True, 'IsRoomRequested': False, 'AutoRoomBookingStatus': 'None', 'responseRequested': True, 'seriesMasterId': None, 'showAs': 'busy', 'type': 'seriesMaster', 'webLink': 'https://outlook.live.com/owa/?itemid=AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA&exvsurl=1&path=/calendar/item', 'onlineMeetingUrl': None, 'isOnlineMeeting': False, 'onlineMeetingProvider': 'unknown', 'AllowNewTimeProposals': True, 'IsDraft': False, 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'responseStatus': {'response': 'organizer', 'time': '0001-01-01T00:00:00Z'}, 'body': {'contentType': 'html', 'content': ''}, 'start': {'dateTime': '2020-05-03T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-03T16:30:00.0000000', 'timeZone': 'UTC'}, 'location': {'displayName': '', 'locationType': 'default', 'uniqueIdType': 'unknown', 'address': {}, 'coordinates': {}}, 'locations': [], 'recurrence': {'pattern': {'type': 'daily', 'interval': 1, 'month': 0, 'dayOfMonth': 0, 'firstDayOfWeek': 'sunday', 'index': 'first'}, 'range': {'type': 'endDate', 'startDate': '2020-05-03', 'endDate': '2020-05-03', 'recurrenceTimeZone': 'Romance Standard Time', 'numberOfOccurrences': 0}}, 'attendees': [], 'organizer': {'emailAddress': {'name': 'outlook_7BA43549E5FD4413@outlook.com', 'address': 'outlook_7BA43549E5FD4413@outlook.com'}}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"ZS2uEVAVyU6BMZ3m6cHmtgAADI/Dkw=="', 'createdDateTime': '2020-05-06T13:24:10.0507138Z', 'lastModifiedDateTime': self.datetime_future, 'changeKey': 'ZS2uEVAVyU6BMZ3m6cHmtgAADI/Dkw==', 'categories': [], 'originalStartTimeZone': 'Romance Standard Time', 'originalEndTimeZone': 'Romance Standard Time', 'iCalUId': '040000008200E00074C5B7101A82E008000000001A4457A0A923D601000000000000000010000000476AE6084FD718418262DA1AE3E41411', 'reminderMinutesBeforeStart': 15, 'isReminderOn': True, 'hasAttachments': False, 'subject': 'My recurrent event', 'bodyPreview': '', 'importance': 'normal', 'sensitivity': 'normal', 'isAllDay': False, 'isCancelled': False, 'isOrganizer': True, 'IsRoomRequested': False, 'AutoRoomBookingStatus': 'None', 'responseRequested': True, 'seriesMasterId': None, 'showAs': 'busy', 'type': 'seriesMaster', 'webLink': 'https://outlook.live.com/owa/?itemid=AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAAMkgQrAAAA&exvsurl=1&path=/calendar/item', 'onlineMeetingUrl': None, 'isOnlineMeeting': False, 'onlineMeetingProvider': 'unknown', 'AllowNewTimeProposals': True, 'IsDraft': False, 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAAMkgQrAAAA', 'responseStatus': {'response': 'organizer', 'time': '0001-01-01T00:00:00Z'}, 'body': {'contentType': 'html', 'content': ''}, 'start': {'dateTime': '2020-05-04T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-04T17:00:00.0000000', 'timeZone': 'UTC'}, 'location': {'displayName': '', 'locationType': 'default', 'uniqueIdType': 'unknown', 'address': {}, 'coordinates': {}}, 'locations': [], 'recurrence': {'pattern': {'type': 'daily', 'interval': 1, 'month': 0, 'dayOfMonth': 0, 'firstDayOfWeek': 'sunday', 'index': 'first'}, 'range': {'type': 'endDate', 'startDate': '2020-05-04', 'endDate': '2020-05-06', 'recurrenceTimeZone': 'Romance Standard Time', 'numberOfOccurrences': 0}}, 'attendees': [], 'organizer': {'emailAddress': {'name': 'outlook_7BA43549E5FD4413@outlook.com', 'address': 'outlook_7BA43549E5FD4413@outlook.com'}}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMj8OK"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX7vTsS0AARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAAEA==', 'start': {'dateTime': '2020-05-03T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-03T16:30:00.0000000', 'timeZone': 'UTC'}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMj8OT"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAAMkgQrAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX774WtQAAAEYAAAJAcu19N72jSr9Rp1mE2xWABwBlLa4RUBXJToExnebpwea2AAACAQ0AAABlLa4RUBXJToExnebpwea2AAAADJIEKwAAABA=', 'start': {'dateTime': '2020-05-04T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-04T17:00:00.0000000', 'timeZone': 'UTC'}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"ZS2uEVAVyU6BMZ3m6cHmtgAADI/Dkw=="', 'createdDateTime': '2020-05-06T13:25:05.9240043Z', 'lastModifiedDateTime': self.datetime_future, 'changeKey': 'ZS2uEVAVyU6BMZ3m6cHmtgAADI/Dkw==', 'categories': [], 'originalStartTimeZone': 'Romance Standard Time', 'originalEndTimeZone': 'Romance Standard Time', 'iCalUId': '040000008200E00074C5B7101A82E00807E405051A4457A0A923D601000000000000000010000000476AE6084FD718418262DA1AE3E41411', 'reminderMinutesBeforeStart': 15, 'isReminderOn': True, 'hasAttachments': False, 'subject': 'My recurrent event 2', 'bodyPreview': '', 'importance': 'normal', 'sensitivity': 'normal', 'originalStart': '2020-05-05T14:30:00Z', 'isAllDay': False, 'isCancelled': False, 'isOrganizer': True, 'IsRoomRequested': False, 'AutoRoomBookingStatus': 'None', 'responseRequested': True, 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAAMkgQrAAAA', 'showAs': 'busy', 'type': 'exception', 'webLink': 'https://outlook.live.com/owa/?itemid=AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX8IdBHsAARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAAMkgQrAAAAEA%3D%3D&exvsurl=1&path=/calendar/item', 'onlineMeetingUrl': None, 'isOnlineMeeting': False, 'onlineMeetingProvider': 'unknown', 'AllowNewTimeProposals': True, 'IsDraft': False, 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX8IdBHsAARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAAMkgQrAAAAEA==', 'responseStatus': {'response': 'organizer', 'time': '0001-01-01T00:00:00Z'}, 'body': {'contentType': 'html', 'content': ''}, 'start': {'dateTime': '2020-05-05T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-05T17:00:00.0000000', 'timeZone': 'UTC'}, 'location': {'displayName': '', 'locationType': 'default', 'uniqueIdType': 'unknown', 'address': {}, 'coordinates': {}}, 'locations': [], 'attendees': [], 'organizer': {'emailAddress': {'name': 'outlook_7BA43549E5FD4413@outlook.com', 'address': 'outlook_7BA43549E5FD4413@outlook.com'}}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAABlLa4RUBXJToExnebpwea2AAAMj8OT"', 'seriesMasterId': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAAMkgQrAAAA', 'type': 'occurrence', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoBUQAICADX8VBriIAARgAAAkBy7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAAMkgQrAAAAEA==', 'start': {'dateTime': '2020-05-06T14:30:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2020-05-06T17:00:00.0000000', 'timeZone': 'UTC'}}
        ]

        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(values))
        recurrence_1 = self.env['calendar.recurrence'].search([('microsoft_id', '=', self.recurrence_id)])
        recurrence_2 = self.env['calendar.recurrence'].search([('microsoft_id', '=', 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAAMkgQrAAAA')])

        events_1 = self.env['calendar.event'].search([('recurrence_id', '=', recurrence_1.id)], order='start asc')
        events_2 = self.env['calendar.event'].search([('recurrence_id', '=', recurrence_2.id)], order='start asc')
        self.assertTrue(recurrence_1, "It should have created an recurrence")
        self.assertTrue(recurrence_2, "It should have created an recurrence")
        self.assertEqual(len(events_1), 1, "It should left 1 event")
        self.assertEqual(len(events_2), 3, "It should have created 3 events")
        self.assertEqual(recurrence_1.base_event_id, events_1[0])
        self.assertEqual(recurrence_2.base_event_id, events_2[0])
        self.assertEqual(events_1.mapped('name'), ['My recurrent event'])
        self.assertEqual(events_2.mapped('name'), ['My recurrent event', 'My recurrent event 2', 'My recurrent event'])
        self.assertEqual(events_1[0].start, datetime(2020, 5, 3, 14, 30))
        self.assertEqual(events_1[0].stop, datetime(2020, 5, 3, 16, 30))
        self.assertEqual(events_2[0].start, datetime(2020, 5, 4, 14, 30))
        self.assertEqual(events_2[0].stop, datetime(2020, 5, 4, 17, 00))
        self.assertEqual(events_2[1].start, datetime(2020, 5, 5, 14, 30))
        self.assertEqual(events_2[1].stop, datetime(2020, 5, 5, 17, 00))
        self.assertEqual(events_2[2].start, datetime(2020, 5, 6, 14, 30))
        self.assertEqual(events_2[2].stop, datetime(2020, 5, 6, 17, 00))

    def test_microsoft_recurrence_delete(self):
        recurrence_id = self.env['calendar.recurrence'].search([('microsoft_id', '=', self.recurrence_id)])
        event_ids = self.env['calendar.event'].search([('recurrence_id', '=', recurrence_id.id)], order='start asc').ids
        values = [{'@odata.type': '#microsoft.graph.event', 'id': 'AQ8PojGtrADQATM3ZmYAZS0yY2MAMC00MDg1LTAwAi0wMAoARgAAA0By7X03vaNKv1GnWYTbFYAHAGUtrhFQFclOgTGd5unB5rYAAAIBDQAAAGUtrhFQFclOgTGd5unB5rYAAAALLLTEAAAA', '@removed': {'reason': 'deleted'}}]

        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(values))

        recurrence = self.env['calendar.recurrence'].search([('microsoft_id', '=', self.recurrence_id)])
        events = self.env['calendar.event'].browse(event_ids).exists()
        self.assertFalse(recurrence, "It should remove recurrence")
        self.assertFalse(events, "It should remove all events")

    def test_attendees_must_have_email(self):
        """
        Synching with a partner without mail raises a ValidationError because Microsoft don't accept attendees without one.
        """
        MicrosoftCal = MicrosoftCalendarService(self.env['microsoft.service'])
        partner = self.env['res.partner'].create({
            'name': 'SuperPartner',
        })
        event = self.env['calendar.event'].create({
            'name': "SuperEvent",
            'start': datetime(2020, 3, 16, 11, 0),
            'stop': datetime(2020, 3, 16, 13, 0),
            'partner_ids': [(4, partner.id)],
        })
        with self.assertRaises(ValidationError):
            event._sync_odoo2microsoft(MicrosoftCal)

    def test_cancel_occurence_of_recurrent_event(self):
        """ The user is invited to a recurrent event. When synced, all events are present, there are three occurrences:
            - 07/15/2021, 15:00-15:30
            - 07/16/2021, 15:00-15:30
            - 07/17/2021, 15:00-15:30
        Then, the organizer cancels the second occurrence -> The latter should not be displayed anymore
        """
        microsoft_id = 'AQMkADAwATM3ZmYAZS0zZmMyLWYxYjQtMDACLTAwCgBGAAADZ59RIxdyh0Kt-MXfyCpfwAcApynKRnkCyUmnqILQHcLZEQAAAgENAAAApynKRnkCyUmnqILQHcLZEQAAAARKsSQAAAA='
        # self.env.user.partner_id.email = "odoo_bf_user01@outlook.com"
        first_sync_values = [
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"pynKRnkCyUmnqILQHcLZEQAABElcNQ=="', 'createdDateTime': '2021-07-15T14:47:40.2996962Z', 'lastModifiedDateTime': '2021-07-15T14:47:40.3783507Z', 'changeKey': 'pynKRnkCyUmnqILQHcLZEQAABElcNQ==', 'categories': [], 'transactionId': None, 'originalStartTimeZone': 'Romance Standard Time', 'originalEndTimeZone': 'Romance Standard Time', 'iCalUId': '040000008200E00074C5B7101A82E00800000000B35B3B5A8879D70100000000000000001000000008A0949F4EC0A1479E4ED178D87EF679', 'reminderMinutesBeforeStart': 15, 'isReminderOn': True, 'hasAttachments': False, 'subject': 'Recurrent Event 1646', 'bodyPreview': '', 'importance': 'normal', 'sensitivity': 'normal', 'isAllDay': False, 'isCancelled': False, 'isOrganizer': False, 'IsRoomRequested': False, 'AutoRoomBookingStatus': 'None', 'responseRequested': True, 'seriesMasterId': None, 'showAs': 'tentative', 'type': 'seriesMaster', 'webLink': 'https://outlook.live.com/owa/?itemid=AQMkADAwATM3ZmYAZS0zZmMyLWYxYjQtMDACLTAwCgBGAAADZ59RIxdyh0Kt%2FMXfyCpfwAcApynKRnkCyUmnqILQHcLZEQAAAgENAAAApynKRnkCyUmnqILQHcLZEQAAAARKsSQAAAA%3D&exvsurl=1&path=/calendar/item', 'onlineMeetingUrl': None, 'isOnlineMeeting': False, 'onlineMeetingProvider': 'unknown', 'allowNewTimeProposals': True, 'OccurrenceId': None, 'isDraft': False, 'hideAttendees': False, 'CalendarEventClassifications': [], 'AutoRoomBookingOptions': None, 'onlineMeeting': None, 'id': microsoft_id, 'responseStatus': {'response': 'notResponded', 'time': '0001-01-01T00:00:00Z'}, 'body': {'contentType': 'html', 'content': ''}, 'start': {'dateTime': '2021-07-15T15:00:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2021-07-15T15:30:00.0000000', 'timeZone': 'UTC'}, 'location': {'displayName': '', 'locationType': 'default', 'uniqueIdType': 'unknown', 'address': {}, 'coordinates': {}}, 'locations': [], 'recurrence': {'pattern': {'type': 'daily', 'interval': 1, 'month': 0, 'dayOfMonth': 0, 'firstDayOfWeek': 'sunday', 'index': 'first'}, 'range': {'type': 'endDate', 'startDate': '2021-07-15', 'endDate': '2021-07-17', 'recurrenceTimeZone': 'Romance Standard Time', 'numberOfOccurrences': 0}}, 'attendees': [{'type': 'required', 'status': {'response': 'none', 'time': '0001-01-01T00:00:00Z'}, 'emailAddress': {'name': 'Odoo02 Outlook02', 'address': 'odoo_bf_user02@outlook.com'}}, {'type': 'required', 'status': {'response': 'none', 'time': '0001-01-01T00:00:00Z'}, 'emailAddress': {'name': 'Odoo01 Outlook01', 'address': 'odoo_bf_user01@outlook.com'}}], 'organizer': {'emailAddress': {'name': 'Odoo02 Outlook02', 'address': 'odoo_bf_user02@outlook.com'}}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAACnKcpGeQLJSaeogtAdwtkRAAAESVw1"', 'seriesMasterId': ('%s' % microsoft_id), 'type': 'occurrence', 'id': 'AQMkADAwATM3ZmYAZS0zZmMyLWYxYjQtMDACLTAwCgFRAAgIANlHI305wABGAAACZ59RIxdyh0Kt-MXfyCpfwAcApynKRnkCyUmnqILQHcLZEQAAAgENAAAApynKRnkCyUmnqILQHcLZEQAAAARKsSQAAAAQ', 'start': {'dateTime': '2021-07-15T15:00:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2021-07-15T15:30:00.0000000', 'timeZone': 'UTC'}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAACnKcpGeQLJSaeogtAdwtkRAAAESVw1"', 'seriesMasterId': microsoft_id, 'type': 'occurrence', 'id': 'AQMkADAwATM3ZmYAZS0zZmMyLWYxYjQtMDACLTAwCgFRAAgIANlH7KejgABGAAACZ59RIxdyh0Kt-MXfyCpfwAcApynKRnkCyUmnqILQHcLZEQAAAgENAAAApynKRnkCyUmnqILQHcLZEQAAAARKsSQAAAAQ', 'start': {'dateTime': '2021-07-16T15:00:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2021-07-16T15:30:00.0000000', 'timeZone': 'UTC'}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAACnKcpGeQLJSaeogtAdwtkRAAAESVw1"', 'seriesMasterId': microsoft_id, 'type': 'occurrence', 'id': 'AQMkADAwATM3ZmYAZS0zZmMyLWYxYjQtMDACLTAwCgFRAAgIANlItdINQABGAAACZ59RIxdyh0Kt-MXfyCpfwAcApynKRnkCyUmnqILQHcLZEQAAAgENAAAApynKRnkCyUmnqILQHcLZEQAAAARKsSQAAAAQ', 'start': {'dateTime': '2021-07-17T15:00:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2021-07-17T15:30:00.0000000', 'timeZone': 'UTC'}}
        ]
        second_sync_values = [
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"pynKRnkCyUmnqILQHcLZEQAABElcUw=="', 'createdDateTime': '2021-07-15T14:47:40.2996962Z', 'lastModifiedDateTime': '2021-07-15T14:51:25.2560888Z', 'changeKey': 'pynKRnkCyUmnqILQHcLZEQAABElcUw==', 'categories': [], 'transactionId': None, 'originalStartTimeZone': 'Romance Standard Time', 'originalEndTimeZone': 'Romance Standard Time', 'iCalUId': '040000008200E00074C5B7101A82E00800000000B35B3B5A8879D70100000000000000001000000008A0949F4EC0A1479E4ED178D87EF679', 'reminderMinutesBeforeStart': 15, 'isReminderOn': True, 'hasAttachments': False, 'subject': 'Recurrent Event 1646', 'bodyPreview': '', 'importance': 'normal', 'sensitivity': 'normal', 'isAllDay': False, 'isCancelled': False, 'isOrganizer': False, 'IsRoomRequested': False, 'AutoRoomBookingStatus': 'None', 'responseRequested': True, 'seriesMasterId': None, 'showAs': 'tentative', 'type': 'seriesMaster', 'webLink': 'https://outlook.live.com/owa/?itemid=AQMkADAwATM3ZmYAZS0zZmMyLWYxYjQtMDACLTAwCgBGAAADZ59RIxdyh0Kt%2FMXfyCpfwAcApynKRnkCyUmnqILQHcLZEQAAAgENAAAApynKRnkCyUmnqILQHcLZEQAAAARKsSQAAAA%3D&exvsurl=1&path=/calendar/item', 'onlineMeetingUrl': None, 'isOnlineMeeting': False, 'onlineMeetingProvider': 'unknown', 'allowNewTimeProposals': True, 'OccurrenceId': None, 'isDraft': False, 'hideAttendees': False, 'CalendarEventClassifications': [], 'id': microsoft_id, 'responseStatus': {'response': 'notResponded', 'time': '0001-01-01T00:00:00Z'}, 'body': {'contentType': 'html', 'content': ''}, 'start': {'dateTime': '2021-07-15T15:00:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2021-07-15T15:30:00.0000000', 'timeZone': 'UTC'}, 'location': {'displayName': '', 'locationType': 'default', 'uniqueIdType': 'unknown', 'address': {}, 'coordinates': {}}, 'locations': [], 'recurrence': {'pattern': {'type': 'daily', 'interval': 1, 'month': 0, 'dayOfMonth': 0, 'firstDayOfWeek': 'sunday', 'index': 'first'}, 'range': {'type': 'endDate', 'startDate': '2021-07-15', 'endDate': '2021-07-17', 'recurrenceTimeZone': 'Romance Standard Time', 'numberOfOccurrences': 0}}, 'attendees': [{'type': 'required', 'status': {'response': 'none', 'time': '0001-01-01T00:00:00Z'}, 'emailAddress': {'name': 'Odoo02 Outlook02', 'address': 'odoo_bf_user02@outlook.com'}}, {'type': 'required', 'status': {'response': 'none', 'time': '0001-01-01T00:00:00Z'}, 'emailAddress': {'name': 'Odoo01 Outlook01', 'address': 'odoo_bf_user01@outlook.com'}}], 'organizer': {'emailAddress': {'name': 'Odoo02 Outlook02', 'address': 'odoo_bf_user02@outlook.com'}}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAACnKcpGeQLJSaeogtAdwtkRAAAESVxT"', 'seriesMasterId': microsoft_id, 'type': 'occurrence', 'id': 'AQMkADAwATM3ZmYAZS0zZmMyLWYxYjQtMDACLTAwCgFRAAgIANlHI305wABGAAACZ59RIxdyh0Kt-MXfyCpfwAcApynKRnkCyUmnqILQHcLZEQAAAgENAAAApynKRnkCyUmnqILQHcLZEQAAAARKsSQAAAAQ', 'start': {'dateTime': '2021-07-15T15:00:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2021-07-15T15:30:00.0000000', 'timeZone': 'UTC'}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"pynKRnkCyUmnqILQHcLZEQAABElcUw=="', 'createdDateTime': '2021-07-15T14:51:25.1366139Z', 'lastModifiedDateTime': '2021-07-15T14:51:25.136614Z', 'changeKey': 'pynKRnkCyUmnqILQHcLZEQAABElcUw==', 'categories': [], 'transactionId': None, 'originalStartTimeZone': 'Romance Standard Time', 'originalEndTimeZone': 'Romance Standard Time', 'iCalUId': '040000008200E00074C5B7101A82E00807E50710B35B3B5A8879D70100000000000000001000000008A0949F4EC0A1479E4ED178D87EF679', 'reminderMinutesBeforeStart': 15, 'isReminderOn': True, 'hasAttachments': False, 'subject': 'Canceled: Recurrent Event 1646', 'bodyPreview': '', 'importance': 'high', 'sensitivity': 'normal', 'originalStart': '2021-07-16T15:00:00Z', 'isAllDay': False, 'isCancelled': True, 'isOrganizer': False, 'IsRoomRequested': False, 'AutoRoomBookingStatus': 'None', 'responseRequested': True, 'seriesMasterId': microsoft_id, 'showAs': 'free', 'type': 'exception', 'webLink': 'https://outlook.live.com/owa/?itemid=AQMkADAwATM3ZmYAZS0zZmMyLWYxYjQtMDACLTAwCgFRAAgIANlH7KejgABGAAACZ59RIxdyh0Kt%2FMXfyCpfwAcApynKRnkCyUmnqILQHcLZEQAAAgENAAAApynKRnkCyUmnqILQHcLZEQAAAARKsSQAAAAQ&exvsurl=1&path=/calendar/item', 'onlineMeetingUrl': None, 'isOnlineMeeting': False, 'onlineMeetingProvider': 'unknown', 'allowNewTimeProposals': True, 'OccurrenceId': ('OID.%s.2021-07-16' % microsoft_id), 'isDraft': False, 'hideAttendees': False, 'CalendarEventClassifications': [], 'id': 'AQMkADAwATM3ZmYAZS0zZmMyLWYxYjQtMDACLTAwCgFRAAgIANlH7KejgABGAAACZ59RIxdyh0Kt-MXfyCpfwAcApynKRnkCyUmnqILQHcLZEQAAAgENAAAApynKRnkCyUmnqILQHcLZEQAAAARKsSQAAAAQ', 'responseStatus': {'response': 'notResponded', 'time': '0001-01-01T00:00:00Z'}, 'body': {'contentType': 'html', 'content': '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">\r\n<meta name="Generator" content="Microsoft Exchange Server">\r\n<!-- converted from text -->\r\n<style><!-- .EmailQuote { margin-left: 1pt; padding-left: 4pt; border-left: #800000 2px solid; } --></style></head>\r\n<body>\r\n<font size="2"><span style="font-size:11pt;"><div class="PlainText">&nbsp;</div></span></font>\r\n</body>\r\n</html>\r\n'}, 'start': {'dateTime': '2021-07-16T15:00:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2021-07-16T15:30:00.0000000', 'timeZone': 'UTC'}, 'location': {'displayName': '', 'locationType': 'default', 'uniqueIdType': 'unknown', 'address': {}, 'coordinates': {}}, 'locations': [], 'attendees': [{'type': 'required', 'status': {'response': 'none', 'time': '0001-01-01T00:00:00Z'}, 'emailAddress': {'name': 'Odoo02 Outlook02', 'address': 'odoo_bf_user02@outlook.com'}}, {'type': 'required', 'status': {'response': 'none', 'time': '0001-01-01T00:00:00Z'}, 'emailAddress': {'name': 'Odoo01 Outlook01', 'address': 'odoo_bf_user01@outlook.com'}}], 'organizer': {'emailAddress': {'name': 'Odoo02 Outlook02', 'address': 'odoo_bf_user02@outlook.com'}}},
            {'@odata.type': '#microsoft.graph.event', '@odata.etag': 'W/"DwAAABYAAACnKcpGeQLJSaeogtAdwtkRAAAESVxT"', 'seriesMasterId': microsoft_id, 'type': 'occurrence', 'id': 'AQMkADAwATM3ZmYAZS0zZmMyLWYxYjQtMDACLTAwCgFRAAgIANlItdINQABGAAACZ59RIxdyh0Kt-MXfyCpfwAcApynKRnkCyUmnqILQHcLZEQAAAgENAAAApynKRnkCyUmnqILQHcLZEQAAAARKsSQAAAAQ', 'start': {'dateTime': '2021-07-17T15:00:00.0000000', 'timeZone': 'UTC'}, 'end': {'dateTime': '2021-07-17T15:30:00.0000000', 'timeZone': 'UTC'}}
        ]

        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(first_sync_values))
        recurrent_event = self.env['calendar.recurrence'].search([('microsoft_id', '=', 'AQMkADAwATM3ZmYAZS0zZmMyLWYxYjQtMDACLTAwCgBGAAADZ59RIxdyh0Kt-MXfyCpfwAcApynKRnkCyUmnqILQHcLZEQAAAgENAAAApynKRnkCyUmnqILQHcLZEQAAAARKsSQAAAA=')])
        self.assertEqual(len(recurrent_event.calendar_event_ids), 3)

        # Need to cheat on the write date, otherwise the second sync won't update the events
        recurrent_event.write_date = datetime(2021, 7, 15, 14, 00)

        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(second_sync_values))
        self.assertEqual(len(recurrent_event.calendar_event_ids), 2)
        self.assertEqual(recurrent_event.calendar_event_ids[0].start, datetime(2021, 7, 15, 15, 00))
        self.assertEqual(recurrent_event.calendar_event_ids[0].stop, datetime(2021, 7, 15, 15, 30))
        self.assertEqual(recurrent_event.calendar_event_ids[1].start, datetime(2021, 7, 17, 15, 00))
        self.assertEqual(recurrent_event.calendar_event_ids[1].stop, datetime(2021, 7, 17, 15, 30))

        events = recurrent_event.calendar_event_ids.sorted(key=lambda e: e.start)
        self.assertEqual(events[0].start, datetime(2021, 7, 15, 15, 00))
        self.assertEqual(events[0].stop, datetime(2021, 7, 15, 15, 30))
        self.assertEqual(events[1].start, datetime(2021, 7, 17, 15, 00))
        self.assertEqual(events[1].stop, datetime(2021, 7, 17, 15, 30))

    def test_use_classic_location(self):
        ms_event = self.single_event

        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(ms_event))

        event = self.env['calendar.event'].search([("microsoft_id", "=", ms_event[0]["id"])])
        self.assertEqual(event.location, ms_event[0]["location"]["displayName"])

    def test_use_url_location(self):
        ms_event = self.single_event
        ms_event[0]["location"]["displayName"] = "https://mylocation.com/meeting-room"

        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(ms_event))

        event = self.env['calendar.event'].search([("microsoft_id", "=", ms_event[0]["id"])])
        self.assertEqual(event.location, ms_event[0]["location"]["displayName"])

    def test_use_specific_virtual_location(self):
        """
        If the location of the Outlook event is a specific virtual location (such as a video Teams meeting),
        use it as videocall location.
        """
        ms_event = self.single_event
        ms_event[0]["location"]["displayName"] = "https://teams.microsoft.com/l/meeting/1234"

        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(ms_event))

        event = self.env['calendar.event'].search([("microsoft_id", "=", ms_event[0]["id"])])
        self.assertEqual(event.location, False)
        self.assertEqual(event.videocall_location, ms_event[0]["location"]["displayName"])

    def test_outlook_event_has_online_meeting_url(self):
        ms_event = self.single_event
        ms_event[0].update({
            'isOnlineMeeting': True,
            'onlineMeeting': {'joinUrl': 'https://video-meeting.com/1234'}
        })

        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(ms_event))

        event = self.env['calendar.event'].search([("microsoft_id", "=", ms_event[0]["id"])])
        self.assertEqual(event.videocall_location, ms_event[0]["onlineMeeting"]["joinUrl"])

    def test_event_reminder_emails_with_microsoft_id(self):
        """
        Odoo shouldn't send email reminders for synced events.
        Test that events synced to Microsoft (with a `microsoft_id`)
        are excluded from email alarm notifications.
        """
        now = datetime.now()
        start = now - relativedelta(minutes=30)
        end = now + relativedelta(hours=2)
        alarm = self.env['calendar.alarm'].create({
            'name': 'Alarm',
            'alarm_type': 'email',
            'interval': 'minutes',
            'duration': 30,
        })
        ms_event = self.single_event
        ms_event[0].update({
            'isOnlineMeeting': True,
            'alarm_id': alarm.id,
            'start': {
                'dateTime': pytz.utc.localize(start).isoformat(),
                'timeZone': 'Europe/Brussels'
            },
            'reminders': {'overrides': [{"method": "email", "minutes": 30}], 'useDefault': False},
            'end': {
                'dateTime': pytz.utc.localize(end).isoformat(),
                'timeZone': 'Europe/Brussels'
            },
        })
        self.env['calendar.event']._sync_microsoft2odoo(MicrosoftEvent(ms_event))
        events_by_alarm = self.env['calendar.alarm_manager']._get_events_by_alarm_to_notify('email')
        self.assertFalse(events_by_alarm, "Events with microsoft_id should not trigger reminders")
