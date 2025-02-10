import configparser as cfgParser
import os


#------------------------------------------------------------------------------

#https://python101.pythonlibrary.org/chapter14_config_parser.html
configFileName='tlorem.ini'

def setDefaultIni():
    
    if os.path.exists(configFileName):
        return
    
    ini=cfgParser.ConfigParser()
    ini['default']={'apath' : os.getcwd(),  #application path
                    'inpath': '',   #input data directory path
                    'outpath': '',    #output data directory path                    
                    }
    
    ini['font.title']={'name' : 'Helvetica',
                       'size' : '14',
                       'weight': 'normal'}
    
    ini['font.default']={'name' : 'Helvetica',
                         'size' : '12',
                         'weight': 'normal'}
        
    ini['data.reduction']={'name' : 'none',
                           'fromTo' : '0:-1'}
    
    ini['calibration.pixe']={'onoff' : '0',
                             'angle' : 'random',
                             'doze'  : '10',
                             'ula'   : '4470',
                             'uma'   : '1040',
                             'A'     : '0.0224',
                             'B'     : '-0.15',
                             'C'     :  '1'
                            }
    
    ini['data.filtering']={'name' : 'none',
                           'rank' : '3',
                           'size' : '100'}
    
    ini['wavelet.prms']={'family'  : 'Daubechies db',
                         'name' : 'db4',
                         'levels': '8',
                         }
    
    with open(configFileName,'w') as configfile:
        ini.write(configfile)


def getConfig(path):    
    #if not os.path.exists(path):
    #    create_config(path)

    config = cfgParser.ConfigParser()
    config.read(path)
    return config

def getValue(section,key):
    """
    Print out a setting
    """
    config = getConfig(configFileName)
    value = config.get(section, key)
    #msg = "{section} {setting} is {value}".format(section=section, setting=key, value=value)
    #print(msg)
    return value

def setValue(section, key, value):
    """
    Update a setting
    """
    config = getConfig(configFileName)
    config.set(section, key, value)
    with open(configFileName, "w") as config_file:
        config.write(config_file)
