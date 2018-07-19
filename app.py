import logging
import multiprocessing as mp

from data import LapData
from incoming import read_incoming_tags
from outgoing import send_outgoing_notifications

logging.basicConfig(
    filename='relay.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(module)s %(message)s'
)


if __name__ == '__main__':
    logging.info('starting')
    incoming_tags_q = mp.Queue()
    incoming_tags_proc = mp.Process(target=read_incoming_tags, args=(incoming_tags_q, 8889), name='incoming')
    incoming_tags_proc.start()

    outgoing_notifications_q = mp.Queue()
    outgoing_notifications_proc = mp.Process(target=send_outgoing_notifications, 
        args=(outgoing_notifications_q, 8890))
    outgoing_notifications_proc.start()

    data = LapData()
    data.deserialize('test.pickle')

    while True:
        tag = incoming_tags_q.get()
        notification = data.increment_laps(tag)
        if notification:
            logging.info('tag: %d laps: %d', notification['tag'], notification['laps'])
            outgoing_notifications_q.put(notification)

    incoming_tags_proc.join()
    outgoing_notification_proc.join()
    data.serialize()
    logging.info('exiting')