import random

import pyrealtime as prt
import time


class Keyboard(prt.ProducerMixin, prt.SynchronousLayer):

    def get_input(self, block_for_input=False):
        if random.randint(0, 100) > 95:
            return random.randint(0, 100)


class RenderTest2(prt.TransformMixin, prt.SynchronousLayer):

    def transform(self, data):
        print(data)

    def update(self):
        # print("update2")
        time.sleep(0.001)



def main():
    keyboard = Keyboard()
    remote_keyboard = Keyboard()

    keyboard_combo = prt.MergeLayer(None, trigger=prt.LayerTrigger.FASTEST)
    keyboard_combo.set_input(keyboard, "physical")
    keyboard_combo.set_input(remote_keyboard, "remote")

    RenderTest2(keyboard_combo)

    prt.PrintLayer(keyboard)

    prt.LayerManager.session().run()


if __name__ == "__main__":
    main()
