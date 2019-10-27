'''
mayaHooks uninstall and the core function it rely on are separate so it's way
easier to update mayaHooks itself.
'''
from __future__ import absolute_import, division, print_function

import collections
import json
import logging
import os

from .vendor.send2trash import send2trash


log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)

UTC_BUILD_DEFAULT = '2000-00-00 00:00:00.000000'


def compPath(a, b):
    ''' Returns true if two paths are the same. '''
    return os.path.normcase(os.path.normpath(a)) == os.path.normcase(os.path.normpath(b))


def settingsPath():
    ''' Returns the path of the settings file for mayaHooks. '''
    return os.environ['maya_app_dir'] + '/mayaHookSettings.json'


def loadSettings():
    ''' Returns the settings, an OrderedDict.  If the settings don't exist, the dict is empty. '''
    settingsFile = settingsPath()
    if os.path.exists(settingsFile):
        log.debug('Settings Exist: ' + settingsFile)
        
        # &&& Need to account for corrupted settings
        with open(settingsFile, 'r') as fid:
            existingSettings = json.load(fid, object_pairs_hook=collections.OrderedDict)
        
        return existingSettings
    
    return collections.OrderedDict()


def writeJson(settings):
    '''
    Convenience to write json with indent=4 and jsonified prior to opening so an error won't leave an empty file.
    '''
    text = json.dumps(settings, indent=4)
    with open(settingsPath(), 'w') as fid:
        fid.write(text)


def defaultScriptsPath(mayaVersion):
    '''
    Returns the script path, for either the versioned or all version or an empty
    string if the expected path isn't valid.
    
    Args:
        mayaVersion: Either 'common' or a number like '2019'
    '''
    if mayaVersion and mayaVersion != 'common':
        path = os.environ['maya_app_dir'] + '/' + str(mayaVersion) + '/scripts'
    else:
        path = os.environ['maya_app_dir'] + '/scripts'
        
    for p in os.environ['maya_script_path'].split(';'):
        if compPath(path, p):
            return path
    return ''


def getBuildTime():
    
    with open(os.path.dirname(__file__) + '-info/info.json', 'r') as fid:
        info = json.load(fid)
    
    return info.get('utc_build_time', UTC_BUILD_DEFAULT)


def uninstall(packageKey, mayaVersion):
    '''
    Delete the folders and mayaHooks registry entry.
    '''
    packagePath = defaultScriptsPath(mayaVersion) + '/' + packageKey
    infoPath = defaultScriptsPath(mayaVersion) + '/' + packageKey + '-info'
    
    if os.path.exists(packagePath):
        send2trash( os.path.normpath(packagePath) ) # On windows, send2trash requires backslashes.
    
    if os.path.exists(infoPath):
        send2trash( os.path.normpath(infoPath) )
    
    settings = loadSettings()
    try:
        del settings[mayaVersion][packageKey]
        # Only bother writing if a change actually happened
        writeJson(settings)
    except Exception:
        pass
    