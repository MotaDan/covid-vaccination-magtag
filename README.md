# covid-vaccination-magtag
An extension to the adafruit covid vaccination magtag example. Allows for scrolling through states instead of being hardcoded. To use pull down the adafruit example code and replace the code.py file. https://learn.adafruit.com/adafruit-magtag-covid-vaccination-percent-tracker/code-the-vaccination-tracker

Every 24 hours will pull vaccination data from https://covid.cdc.gov/covid-data-tracker/COVIDData/getAjaxData?id=vaccination_data
The left and right buttons can be used to change which US State is being looked at. After an update is complete the lights at the top of the magtag will light up with the percentage of people vaccinated. While the lights are active the buttons can be used to more quickly change State with the the most recently pulled data.
