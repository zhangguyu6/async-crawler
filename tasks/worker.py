from celery import Celery
broker = 'redis://127.0.0.1:6379/5'
backend = 'redis://127.0.0.1:6379/6'
app = Celery('crawler', backend=backend, broker=broker, include=['tasks'])

if __name__ == '__main__':
    app.start()
