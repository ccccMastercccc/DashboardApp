from axentra.kit import *

class App(Page):
    def __init__(self):
        super().__init__("Monitor")
        numcols = 20
        gainvol = [VolumeKnob("GAIN", color="#ff0000", value=0) for i in range(numcols)]
        HFvol = [VolumeKnob("HF", color="#ffffff", value=0) for i in range(numcols)]
        MFvol = [VolumeKnob("MF", color="#ffffff", value=0) for i in range(numcols)]
        LFvol = [VolumeKnob("LF", color="#ffffff", value=0) for i in range(numcols)]
        AUXvol = [VolumeKnob("AUX", value=0) for i in range(numcols)]
        FXvol = [VolumeKnob("FX", color="#ffff00", value=0) for i in range(numcols)]
        PANvol = [VolumeKnob("PAN", color="#c6c6c6", value=0) for i in range(numcols)]
        self.sliders = [VolumeSlider("MASTER", value=0) for i in range(numcols)]

        card = Card("control")
        row1 = Row(*(gainvol + [Spacer()]))
        row2 = Row(*(HFvol + [Spacer()]))
        row3 = Row(*(MFvol + [Spacer()]))
        row4 = Row(*(LFvol + [Spacer()]))
        row5 = Row(*(AUXvol + [Spacer()]))
        row6 = Row(*(FXvol + [Spacer()]))
        row7 = Row(*(PANvol + [Spacer()]))
        row10 = Row(*(self.sliders + [Spacer()]))

        card.add(row1)
        card.add(row2)
        card.add(row3)
        card.add(row4)
        card.add(row5)
        card.add(row6)
        card.add(row7)
        card.add(row10)
        self.add(card)
        
        self.sliders[6].changed.connect(lambda _value: self.refresh())

    def refresh(self):
        master4 = self.sliders[4]
        master5 = self.sliders[5]
        master6 = self.sliders[6]

        master4.set_value(100 - master6.value())
        master5.set_value(100 - master6.value())
        #print(master4)