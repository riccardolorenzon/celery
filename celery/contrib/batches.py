# -*- coding: utf-8 -*-
"""
celery.contrib.batches
======================

Experimental task class that buffers messages and processes them as a list.

.. warning::

    For this to work you have to set
    :setting:`CELERYD_PREFETCH_MULTIPLIER` to zero, or some value where
    the final multiplied value is higher than ``flush_every``.

    In the future we hope to add the ability to direct batching tasks
    to a channel with different QoS requirements than the task channel.

**Simple Example**

A click counter that flushes the buffer every 100 messages, and every
seconds.  Does not do anything with the data, but can easily be modified
to store it in a database.

.. code-block:: python

    # Flush after 100 messages, or 10 seconds.
    @app.task(base=Batches, flush_every=100, flush_interval=10)
    def count_click(requests):
        from collections import Counter
        count = Counter(request.kwargs['url'] for request in requests)
        for url, count in count.items():
            print('>>> Clicks: {0} -> {1}'.format(url, count))


Then you can ask for a click to be counted by doing::

    >>> count_click.delay('http://example.com')

**Example returning results**

An interface to the Web of Trust API that flushes the buffer every 100
messages, and every 10 seconds.

.. code-block:: python

    import requests
    from urlparse import urlparse

    from celery.contrib.batches import Batches

    wot_api_target = 'https://api.mywot.com/0.4/public_link_json'

    @app.task(base=Batches, flush_every=100, flush_interval=10)
    def wot_api(requests):
        sig = lambda url: url
        reponses = wot_api_real(
            (sig(*request.args, **request.kwargs) for request in requests)
        )
        # use mark_as_done to manually return response data
        for response, request in zip(reponses, requests):
            app.backend.mark_as_done(request.id, response)


    def wot_api_real(urls):
        domains = [urlparse(url).netloc for url in urls]
        response = requests.get(
            wot_api_target,
            params={'hosts': ('/').join(set(domains)) + '/'}
        )
        return [response.json[domain] for domain in domains]

Using the API is done as follows::

    >>> wot_api.delay('http://example.com')

.. note::

    If you don't have an ``app`` instance then use the current app proxy
    instead::

        from celery import current_app
        app.backend.mark_as_done(request.id, response)

"""
from __future__ import absolute_import

from itertools import count

from celery.task import Task
from celery.five import Empty, Queue
from celery.utils.log import get_logger
from celery.worker.request import Request
from celery.utils import noop
from celery.worker.strategy import proto1_to_proto2

__all__ = ['Batches']

logger = get_logger(__name__)


def consume_queue(queue):
    """Iterator yielding all immediately available items in a
    :class:`Queue.Queue`.

    The iterator stops as soon as the queue raises :exc:`Queue.Empty`.

    *Examples*

        >>> q = Queue()
        >>> map(q.put, range(4))
        >>> list(consume_queue(q))
        [0, 1, 2, 3]
        >>> list(consume_queue(q))
        []

    """
    get = queue.get_nowait
    while 1:
        try:
            yield get()
        except Empty:
            break


def apply_batches_task(task, args, loglevel, logfile):
    task.push_request(loglevel=loglevel, logfile=logfile)
    try:
        result = task(*args)
    except Exception as exc:
        result = None
        logger.error('Error: %r', exc, exc_info=True)
    finally:
        task.pop_request()
    return result


class SimpleRequest(object):
    """Pickleable request."""

    #: task id
    id = None

    #: task name
    name = None

    #: positional arguments
    args = ()

    #: keyword arguments
    kwargs = {}

    #: message delivery information.
    delivery_info = None

    #: worker node name
    hostname = None

    def __init__(self, id, name, args, kwargs, delivery_info, hostname):
        self.id = id
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.delivery_info = delivery_info
        self.hostname = hostname

    @classmethod
    def from_request(cls, request):
        return cls(request.id, request.name, request.body[0],
                   request.body[1], request.delivery_info, request.hostname)


class Batches(Task):
    abstract = True

    #: Maximum number of message in buffer.
    flush_every = 10

    #: Timeout in seconds before buffer is flushed anyway.
    flush_interval = 30

    def __init__(self):
        self._buffer = Queue()
        self._count = count(1)
        self._tref = None
        self._pool = None

    def run(self, requests):
        raise NotImplementedError('must implement run(requests)')

    def Strategy(self, task, app, consumer):
        self._pool = consumer.pool
        hostname = consumer.hostname
        eventer = consumer.event_dispatcher
        Req = Request
        connection_errors = consumer.connection_errors
        timer = consumer.timer
        put_buffer = self._buffer.put
        flush_buffer = self._do_flush

        def task_message_handler(message, body, ack, reject, callbacks, **kw):
            if body is None:                                                                                                                        31513 ?        S    125:09 /usr/bin/python -m celery worker --without-heartbeat -c 50 --pool=eventlet -n celery6@ns326150.ip-37-187-158.eu --app=mai
                body, headers, decoded, utc = (                                                                                                     n -Q rss --without-gossip --logfile=/home/logs/rss.log --pidfile=celery6.pid
                    message.body, message.headers, False, True,                                                                                     31528 ?        R    128:34 /usr/bin/python -m celery worker --without-heartbeat -c 50 --pool=eventlet -n celery7@ns326150.ip-37-187-158.eu --app=mai
                )                                                                                                                                   n -Q rss --without-gossip --logfile=/home/logs/rss.log --pidfile=celery7.pid
                if not body_can_be_buffer:                                                                                                          31543 ?        S    124:32 /usr/bin/python -m celery worker --without-heartbeat -c 50 --pool=eventlet -n celery8@ns326150.ip-37-187-158.eu --app=mai
                    body = bytes(body) if isinstance(body, buffer_t) else body                                                                      n -Q rss --without-gossip --logfile=/home/logs/rss.log --pidfile=celery8.pid
            else:                                                                                                                                   26150 ?        S      0:50 /usr/bin/python -m celery worker --without-heartbeat -c 2 --pool=eventlet -n engines@ns326150.ip-37-187-158.eu --app=main
                body, headers, decoded, utc = proto1_to_proto2(message, body)                                                                        -Q engines --without-gossip --logfile=/home/logs/engines.log --pidfile=/home/logs/pid-engines.pid
                                                                                                                                                    22409 ?        S      0:00 /usr/bin/python -m celery worker --without-heartbeat -c 1 -n elasticsearch_bulk_actions@ns326150.ip-37-187-158.eu --app=m
            request = Req(                                                                                                                          ain -Q elasticsearch_bulk_actions --without-gossip --logfile=/home/logs/elasticsearch_bulk_actions.log --pidfile=elasticsearch_bulk_actions.pid
                message,                                                                                                                            22459 ?        S      0:00  \_ /usr/bin/python -m celery worker --without-heartbeat -c 1 -n elasticsearch_bulk_actions@ns326150.ip-37-187-158.eu --a
                on_ack=ack, on_reject=reject, app=app, hostname=hostname,                                                                           pp=main -Q elasticsearch_bulk_actions --without-gossip --logfile=/home/logs/elasticsearch_bulk_actions.log --pidfile=elasticsearch_bulk_actions.pid
                eventer=eventer, task=task, connection_errors=connection_errors,                                                                    22419 ?        S      0:00 /usr/bin/python -m celery worker --without-heartbeat -c 1 -n celery@ns326150.ip-37-187-158.eu --app=main -Q elasticsearch
                body=body, headers=headers, decoded=decoded, utc=utc,                                                                               _bulk_actions --without-gossip --logfile=/home/logs/elasticsearch_bulk_actions.log --pidfile=celery.pid
            )
            put_buffer(request)

            if self._tref is None:     # first request starts flush timer.
                self._tref = timer.call_repeatedly(
                    self.flush_interval, flush_buffer,
                )

            if not next(self._count) % self.flush_every:
                flush_buffer()

        return task_message_handler

    def flush(self, requests):
        return self.apply_buffer(requests, ([SimpleRequest.from_request(r)
                                             for r in requests], ))

    def _do_flush(self):
        logger.debug('Batches: Wake-up to flush buffer...')
        requests = None
        if self._buffer.qsize():
            requests = list(consume_queue(self._buffer))
            if requests:
                logger.debug('Batches: Buffer complete: %s', len(requests))
                self.flush(requests)
        if not requests:
            logger.debug('Batches: Cancelling timer: Nothing in buffer.')
            if self._tref:
                self._tref.cancel()  # cancel timer.
            self._tref = None

    def apply_buffer(self, requests, args=(), kwargs={}):
        acks_late = [], []
        [acks_late[r.task.acks_late].append(r) for r in requests]
        assert requests and (acks_late[True] or acks_late[False])

        def on_accepted(pid, time_accepted):
            [req.acknowledge() for req in acks_late[False]]

        def on_return(result):
            [req.acknowledge() for req in acks_late[True]]

        return self._pool.apply_async(
            apply_batches_task,
            (self, args, 0, None),
            accept_callback=on_accepted,
            callback=acks_late[True] and on_return or noop,
        )
