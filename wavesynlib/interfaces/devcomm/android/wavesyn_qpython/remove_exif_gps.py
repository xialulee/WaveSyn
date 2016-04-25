#-*-coding:utf8;-*-
#qpy:2
#qpy:kivy
"""
@Author: Feng-cong Li 
@Date: 2016-04-25
"""
from jnius import autoclass
import androidhelper

droid = androidhelper.Android()
ExifInterface = autoclass('android.media.ExifInterface')

def pick_photo():
  result = droid.startActivityForResult('android.intent.action.PICK', type='image/*')
  ret = {}
  ret['uri'] = uri = result.result['data']
  attr = droid.queryContent(uri)
  ret['path'] = attr.result[0]['_data']
  return ret
  
  
def set_gps(path, latitude, longitude, altitude):
  exif = ExifInterface(path)
  exif.setAttribute(ExifInterface.TAG_GPS_LATITUDE, latitude)
  exif.setAttribute(ExifInterface.TAG_GPS_LONGITUDE, longitude)
  exif.setAttribute(ExifInterface.TAG_GPS_ALTITUDE, altitude)
  exif.saveAttributes()


if __name__ == '__main__':
  path = pick_photo()['path']
  set_gps(path, '0/1,0/1,0/1', '0/1,0/1,0/1', '0/1')