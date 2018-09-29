import threading
import time

import pyrealtime as prt


def get_input(_):
    print(threading.current_thread(), threading.main_thread())
    time.sleep(1)


def main():
    print(threading.current_thread(), threading.main_thread())
    in_main = prt.InputLayer(frame_generator=get_input)
    prt.LayerManager.session().run(main_thread=in_main)

if __name__ == "__main__":
    main()