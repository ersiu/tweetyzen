import configparser
Config = configparser.ConfigParser()
Config.read(".\\config.ini")





firstscore = 1
secondscore = 7
thirdscore = 8

highestscore = max((firstscore, secondscore, thirdscore))

print(highestscore)
