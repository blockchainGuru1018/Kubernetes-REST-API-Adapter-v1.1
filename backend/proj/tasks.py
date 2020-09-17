from __future__ import absolute_import, unicode_literals

from proj.celery import app


@app.task
def long_running_operation():
    print('11111111111111111111111111111111111111')
    return {True}


# @app.task
# def mul(x, y):
#     print('2222222222222222222222222222222222222222')
#     return x * y
#
#
# @app.task
# def xsum(numbers):
#     print('33333333333333333333333333333333333333333')
#     return sum(numbers)
