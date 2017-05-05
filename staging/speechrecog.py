import asyncio


import speech_recognition as sr

# obtain audio from the microphone
# r = sr.Recognizer()
# with sr.Microphone(sample_rate=8000) as source:
#     while True:
#         print("Say something!")
#         audio = r.listen(source)

#         print('Listen done')

#         try:
#             print("Got: " + r.recognize_google(audio, language='es-ES'))
#         except sr.UnknownValueError:
#             print("Sphinx could not understand audio")
#         except sr.RequestError as e:
#             print("Sphinx error; {0}".format(e))


class Bot:
    def __init__(self, loop):
        self.loop = loop

    @asyncio.coroutine
    def send(self, msg):
        raise NotImplementedError()

    @asyncio.coroutine
    def recv(self):
        raise NotImplementedError()


import threading


class Voice(Bot):
    def __init__(self, loop):
        super().__init__(loop)
        self.r = sr.Recognizer()
        self.m = sr.Microphone()

    @asyncio.coroutine
    def recv(self):
        result_future = asyncio.Future()

        def threaded_listen():
            with self.m as s:
                try:
                    audio = self.r.listen(s)
                    text = self.r.recognize_google(audio, language="es-ES")
                    self.loop.call_soon_threadsafe(result_future.set_result, text)
                except Exception as e:
                    self.loop.call_soon_threadsafe(result_future.set_exception,
                                                   e)

        listener_thread = threading.Thread(target=threaded_listen)
        listener_thread.daemon = True
        listener_thread.start()
        x = yield from result_future
        return x


@asyncio.coroutine
def handler(loop, bots):
    coros = [x.get() for x in bots]

    while True:
        completed, pending = yield from asyncio.wait(coros)
        results = [t.result() for t in completed]
        print('results: {}'.format(results))
        print(pending)
        if not pending:
            break


def main():
    loop = asyncio.get_event_loop()
    bots = [Voice(loop)]
    loop.run_until_complete(handler(loop, bots))


if __name__ == '__main__':
    main()
